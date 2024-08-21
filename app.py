from flask import Flask, render_template, request, send_file, jsonify
import yt_dlp
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
    }
    
    # Create a directory for downloads if not exists
    os.makedirs('downloads', exist_ok=True)
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            formats = info_dict.get('formats', [])
            
            # Prioritize 1080p and 720p formats
            prioritized_formats = [f for f in formats if f.get('height') in [1080, 720]]
            
            if not prioritized_formats:
                prioritized_formats = formats
            
            # Select the best format based on user choice or defaults
            selected_format = prioritized_formats[0]
            ydl_opts['format'] = selected_format.get('format_id')
            
            # Download the selected format
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            filename = ydl.prepare_filename(info_dict)
            
            return send_file(filename, as_attachment=True)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
