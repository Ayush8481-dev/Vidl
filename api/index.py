from flask import Flask, request, jsonify
import yt_dlp
import os
import tempfile

app = Flask(__name__)

@app.route('/api/extract', methods=['GET'])
def extract_video():
    video_url = request.args.get('url')
    
    if not video_url:
        return jsonify({"error": "Missing URL parameter"}), 400

    # --- 1. SETUP COOKIES FROM VERCEL SETTINGS ---
    cookie_path = None
    # Read the secret variable from Vercel
    cookie_content = os.environ.get('YT_COOKIES')
    
    if cookie_content:
        # Create a temporary file because yt-dlp needs a file, not text
        try:
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
                f.write(cookie_content)
                cookie_path = f.name
        except Exception as e:
            return jsonify({"error": "Failed to create cookie file"}), 500

    try:
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            # PASS THE COOKIE FILE HERE
            'cookiefile': cookie_path, 
            
            # Use standard Web Client (Best when using Cookies)
            'extractor_args': {
                'youtube': {
                    'player_client': ['web'],
                    'player_skip': ['configs', 'js'],
                }
            },
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            direct_url = info.get('url', None)
            title = info.get('title', 'Unknown')
            thumbnail = info.get('thumbnail', None)
            
            if not direct_url:
                return jsonify({"error": "Failed to extract URL even with cookies"}), 403

            return jsonify({
                "status": "success",
                "title": title,
                "thumbnail": thumbnail,
                "stream_url": direct_url
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
    finally:
        # Cleanup: Delete the temp file to save memory
        if cookie_path and os.path.exists(cookie_path):
            os.remove(cookie_path)

if __name__ == '__main__':
    app.run()
