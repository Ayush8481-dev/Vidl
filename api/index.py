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

    # --- 1. SETUP COOKIES (Required for Vercel) ---
    cookie_path = None
    cookie_content = os.environ.get('YT_COOKIES')
    
    if cookie_content:
        try:
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
                f.write(cookie_content)
                cookie_path = f.name
        except Exception as e:
            return jsonify({"error": "Cookie file creation failed"}), 500

    try:
        ydl_opts = {
            # FIX FOR "FORMAT NOT AVAILABLE":
            # We explicitly ask for the best single file that contains BOTH audio and video (ext=mp4)
            # We fallback to 'best' if that fails.
            'format': 'best[ext=mp4]/best',
            
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'noplaylist': True,
            
            # PASS COOKIES
            'cookiefile': cookie_path,
            
            # USE ANDROID CLIENT (Better for single-file formats than Web)
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web'],
                    'player_skip': ['webpage', 'configs', 'js'],
                    'innertube_client': ['android'],
                }
            },
            
            # Spoof Android Phone
            'user_agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            direct_url = info.get('url', None)
            title = info.get('title', 'Unknown')
            thumbnail = info.get('thumbnail', None)
            
            if not direct_url:
                return jsonify({"error": "No direct link found. Formats might be restricted."}), 403

            return jsonify({
                "status": "success",
                "title": title,
                "thumbnail": thumbnail,
                "stream_url": direct_url
            })

    except Exception as e:
        # Detailed error reporting
        return jsonify({"error": str(e)}), 500
        
    finally:
        # Cleanup cookies
        if cookie_path and os.path.exists(cookie_path):
            os.remove(cookie_path)

if __name__ == '__main__':
    app.run()
