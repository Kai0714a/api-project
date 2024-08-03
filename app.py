# app.py
from flask import Flask, jsonify, send_file, request, render_template
import yt_dlp
import os
import re

app = Flask(__name__)

# Function to sanitize filenames
def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', ' ', filename)

# Global variable to track progress
download_progress = {
    'total': 0,
    'downloaded': 0,
    'status': 'in_progress'  # 'in_progress' or 'done'
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    url = request.form.get('url')
    quality = request.form.get('quality', '1080p')

    output_dir = r"C:\Users\Desktop\downloaded_vid"  # Replace with your desired save path
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    try:
        # Get video info to retrieve title
        ydl_opts_info = {'quiet': True, 'skip_download': True}
        with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            title = sanitize_filename(info_dict.get('title', 'video'))

        filename = f"{title}.mp4"
        filepath = os.path.join(output_dir, filename)

        # Download the video
        ydl_opts = {
            'format': f'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
            'outtmpl': filepath,
            'progress_hooks': [progress_hook],  # Call progress hook
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
            'noplaylist': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        download_progress['status'] = 'done'
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

@app.route('/progress', methods=['GET'])
def get_progress():
    return jsonify(download_progress)

def progress_hook(d):
    if d['status'] == 'downloading':
        download_progress['total'] = d.get('total_bytes')
        download_progress['downloaded'] = d.get('downloaded_bytes')
    elif d['status'] == 'finished':
        download_progress['status'] = 'done'

if __name__ == '__main__':
    app.run(debug=True)
