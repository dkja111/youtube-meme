# app.py
from flask import Flask, request, jsonify, send_file
import yt_dlp
import os
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'downloads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def download_youtube_video(url):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(UPLOAD_FOLDER, f'video_{timestamp}.mp4')
    
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
        'outtmpl': output_path,
        'merge_output_format': 'mp4',
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return output_path
    except Exception as e:
        raise Exception(f"다운로드 실패: {str(e)}")

def create_meme(video_path, text, start_time, duration):
    output_path = video_path.replace('.mp4', '_meme.mp4')
    
    with VideoFileClip(video_path) as video:
        # 비디오 구간 자르기
        clip = video.subclip(start_time, start_time + duration)
        
        # 텍스트 추가
        txt_clip = TextClip(text, fontsize=70, color='white', stroke_color='black',
                          stroke_width=2).set_duration(duration)
        txt_clip = txt_clip.set_position(('center', 'bottom'))
        
        # 합성
        final_clip = CompositeVideoClip([clip, txt_clip])
        final_clip.write_videofile(output_path)
    
    return output_path

@app.route('/api/create-meme', methods=['POST'])
def handle_meme_creation():
    try:
        data = request.json
        video_url = data['url']
        text = data['text']
        start_time = float(data['startTime'])
        duration = float(data['duration'])
        
        # 영상 다운로드
        video_path = download_youtube_video(video_url)
        
        # 밈 생성
        meme_path = create_meme(video_path, text, start_time, duration)
        
        return send_file(meme_path, mimetype='video/mp4')
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(port=5000)
