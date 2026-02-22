from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route('/api/extract', methods=['GET'])
def extract_video():
    video_url = request.args.get('url')
    
    if not video_url:
        return jsonify({"error": "Missing URL parameter"}), 400

    try:
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            
            # ATTEMPT 3: THE ANDROID TV STRATEGY
            # TV clients often bypass "Sign In" checks because TVs don't have keyboards
            'extractor_args': {
                'youtube': {
                    'player_client': ['android_tv'],
                    'innertube_client': ['android_tv'],
                    'player_skip': ['webpage', 'configs', 'js'],
                }
            },
            
            # Use a generic TV User Agent
            'user_agent': 'Mozilla/5.0 (Linux; Android 9; AFTMM Build/PS7293; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/70.0.3538.110 Mobile Safari/537.36',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            direct_url = info.get('url', None)
            title = info.get('title', 'Unknown')
            thumbnail = info.get('thumbnail', None)
            
            if not direct_url:
                return jsonify({"error": "No URL found. Vercel IP is likely hard-banned."}), 403

            return jsonify({
                "status": "success",
                "title": title,
                "thumbnail": thumbnail,
                "stream_url": direct_url
            })

    except Exception as e:
        return jsonify({"error": str(e), "message": "If you see 'Sign in' or 'Reload', Vercel is banned."}), 500

if __name__ == '__main__':
    app.run()
