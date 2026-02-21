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

    # THE FIX: Vercel is read-only. We must copy the cookies file to the writable /tmp/ folder
    source_cookie = os.path.join(os.getcwd(), 'cookies.txt')
    tmp_cookie = '/tmp/cookies.txt'
    
    # Copy the file to /tmp/ if it exists
    if os.path.exists(source_cookie):
        try:
            shutil.copyfile(source_cookie, tmp_cookie)
        except Exception:
            pass

    # Configure yt-dlp
    ydl_opts = {
        'format': 'best',
        'skip_download': True,
        'quiet': True,
        'no_warnings': True,
    }

    # Tell yt-dlp to use the writable cookies file in /tmp/
    if os.path.exists(tmp_cookie):
        ydl_opts['cookiefile'] = tmp_cookie

    try:
        # Run yt-dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            direct_url = info.get('url')
            title = info.get('title', 'Unknown Title')
            
            return jsonify({
                "success": True,
                "title": title,
                "redirect_link": direct_url
            })
            
    except Exception as e:
        return jsonify({
            "success": False, 
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run()
