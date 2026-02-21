from flask import Flask, request, jsonify
import yt_dlp
import os
import shutil

app = Flask(__name__)

@app.route('/api', methods=['GET'])
def get_video_link():
    url = request.args.get('url')
    
    if not url:
        return jsonify({"success": False, "error": "No URL provided."}), 400

    source_cookie = os.path.join(os.getcwd(), 'cookies.txt')
    tmp_cookie = '/tmp/cookies.txt'
    
    if os.path.exists(source_cookie):
        try:
            shutil.copyfile(source_cookie, tmp_cookie)
        except Exception:
            pass

    # THE FIX: 
    # 1. cachedir: False prevents Vercel read-only crashes when caching YouTube signatures.
    # 2. format: 'bestvideo' prevents yt-dlp from crashing on Vercel due to missing ffmpeg.
    ydl_opts = {
        'format': 'bestvideo/bestaudio/best',
        'skip_download': True,
        'quiet': True,
        'no_warnings': True,
        'cachedir': False, 
    }

    if os.path.exists(tmp_cookie):
        ydl_opts['cookiefile'] = tmp_cookie

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            title = info.get('title', 'Unknown Title')
            formats = info.get('formats', [])
            
            # Manually sort through the data to find the exact links
            best_combined = None
            best_video_only = None
            best_audio_only = None
            
            for f in formats:
                vcodec = f.get('vcodec')
                acodec = f.get('acodec')
                
                has_video = vcodec != 'none' and vcodec is not None
                has_audio = acodec != 'none' and acodec is not None
                url_link = f.get('url')
                
                if not url_link:
                    continue
                    
                if has_video and has_audio:
                    best_combined = url_link
                elif has_video and not has_audio:
                    best_video_only = url_link
                elif not has_video and has_audio:
                    best_audio_only = url_link

            return jsonify({
                "success": True,
                "title": title,
                "combined_link": best_combined, 
                "video_only_link": best_video_only, 
                "audio_only_link": best_audio_only 
            })
            
    except Exception as e:
        return jsonify({
            "success": False, 
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run()
