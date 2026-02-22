from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route('/api/extract', methods=['GET'])
def extract_video():
    video_url = request.args.get('url')
    
    if not video_url:
        return jsonify({"error": "Missing URL parameter"}), 400

    try:
        # CONFIGURE TO MIMIC ANDROID APP
        ydl_opts = {
            'format': 'best',  # Get best combined audio/video
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            
            # 1. Use Android Client API (Bypasses many web-based bot checks)
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web'],
                    'player_skip': ['webpage', 'configs', 'js'],
                    'innertube_client': ['android'],
                }
            },
            
            # 2. Spoof User Agent (Look like a generic Android Phone)
            'user_agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # extract_info is the main call to YouTube
            info = ydl.extract_info(video_url, download=False)
            
            # Get the direct googlevideo link
            direct_url = info.get('url', None)
            title = info.get('title', 'Unknown')
            thumbnail = info.get('thumbnail', None)
            
            if not direct_url:
                return jsonify({"error": "No direct link found"}), 404

            return jsonify({
                "status": "success",
                "title": title,
                "thumbnail": thumbnail,
                "stream_url": direct_url
            })

    except Exception as e:
        # Return the specific error so you know if it's a 403 or something else
        return jsonify({"error": str(e)}), 500

# Required for Vercel
if __name__ == '__main__':
    app.run()
