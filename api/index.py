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
            
            # CRITICAL FIXES FOR "PAGE RELOAD" ERROR:
            'noplaylist': True,
            'extract_flat': False,
            'cachedir': False,  # Disable cache to prevent looping old bad tokens
            
            # SWITCH TO iOS CLIENT (Often less restricted on Data Centers)
            'extractor_args': {
                'youtube': {
                    'player_client': ['ios', 'web'],
                    'player_skip': ['webpage', 'configs', 'js'],
                    'innertube_client': ['ios'],
                }
            },
            
            # iOS User Agent
            'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            direct_url = info.get('url', None)
            title = info.get('title', 'Unknown')
            thumbnail = info.get('thumbnail', None)
            
            if not direct_url:
                return jsonify({"error": "No direct link found. YouTube might be blocking the IP."}), 403

            return jsonify({
                "status": "success",
                "title": title,
                "thumbnail": thumbnail,
                "stream_url": direct_url
            })

    except Exception as e:
        error_message = str(e)
        # Check for the specific "Sign in" error to give a clear message
        if "Sign in to confirm" in error_message:
             return jsonify({
                 "error": "Vercel IP Banned. YouTube requires Cookies/Login.",
                 "details": error_message
             }), 403
        
        return jsonify({"error": error_message}), 500

if __name__ == '__main__':
    app.run()
