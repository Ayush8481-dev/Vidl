from flask import Flask, request, jsonify
import yt_dlp
import os
import shutil

app = Flask(__name__)

@app.route('/api', methods=['GET'])
def get_video_link():
    url = request.args.get('url')
    
    if not url:
        return jsonify({
            "success": False, 
            "error": "No URL provided. Add ?url=YOUR_YOUTUBE_LINK to the end."
        }), 400

    source_cookie = os.path.join(os.getcwd(), 'cookies.txt')
    tmp_cookie = '/tmp/cookies.txt'
    
    if os.path.exists(source_cookie):
        try:
            shutil.copyfile(source_cookie, tmp_cookie)
        except Exception:
            pass

    # THE FIX: A flexible format selector. 
    # Try combined (best). If missing, try separate (bestvideo+bestaudio).
    ydl_opts = {
        'format': 'best/bestvideo+bestaudio/bestvideo/bestaudio',
        'skip_download': True,
        'quiet': True,
        'no_warnings': True,
    }

    if os.path.exists(tmp_cookie):
        ydl_opts['cookiefile'] = tmp_cookie

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            title = info.get('title', 'Unknown Title')
            
            # If a single combined file exists, it will be here
            direct_url = info.get('url')
            audio_url = None
            
            # If YouTube only has separate video and audio streams, extract them safely without crashing
            if not direct_url and 'requested_formats' in info:
                for f in info['requested_formats']:
                    if f.get('vcodec') != 'none':
                        direct_url = f.get('url') # Video stream
                    if f.get('acodec') != 'none':
                        audio_url = f.get('url')  # Audio stream

            # Ultimate fallback if formatted differently
            if not direct_url and 'formats' in info and len(info['formats']) > 0:
                direct_url = info['formats'][-1].get('url')

            return jsonify({
                "success": True,
                "title": title,
                "redirect_link": direct_url,
                "audio_only_link": audio_url,
                "note": "Combined stream found." if not audio_url else "YouTube separated the streams. redirect_link has no sound; use audio_only_link for sound."
            })
            
    except Exception as e:
        return jsonify({
            "success": False, 
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run()
