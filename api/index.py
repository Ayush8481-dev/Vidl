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

    # --- HANDLE COOKIES ---
    # We create a temporary file because yt-dlp needs a file path, not a string
    cookie_path = None
    cookie_content = os.environ.get('YT_COOKIES')
    
    if cookie_content:
        try:
            # Create a temp file named cookies.txt
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
                f.write(cookie_content)
                cookie_path = f.name
        except Exception as e:
            return jsonify({"error": f"Cookie error: {str(e)}"}), 500

    try:
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            # Use the cookie file if it exists
            'cookiefile': cookie_path,
            
            # Keep the Android spoofing as a backup layer
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web'],
                    'player_skip': ['webpage', 'configs', 'js'],
                    'innertube_client': ['android'],
                }
            },
            'user_agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            direct_url = info.get('url', None)
            title = info.get('title', 'Unknown')
            thumbnail = info.get('thumbnail', None)
            
            # Clean up the response
            return jsonify({
                "status": "success",
                "title": title,
                "thumbnail": thumbnail,
                "stream_url": direct_url
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
    finally:
        # Cleanup: Delete the temp cookie file so it doesn't fill up memory
        if cookie_path and os.path.exists(cookie_path):
            os.remove(cookie_path)

if __name__ == '__main__':
    app.run()
