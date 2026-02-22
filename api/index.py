from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route('/api/extract', methods=['GET'])
def extract_video():
    video_url = request.args.get('url')
    
    if not video_url:
        return jsonify({"error": "Missing URL parameter"}), 400

    try:
        # Options to get the best direct link
        ydl_opts = {
            'format': 'best',  # Get best combined audio/video
            'quiet': True,
            'no_warnings': True,
            # 'noplaylist': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            # Extract the specific direct URL
            direct_url = info.get('url', None)
            title = info.get('title', 'Unknown')
            
            return jsonify({
                "title": title,
                "stream_url": direct_url
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Vercel requires this for serverless functions
if __name__ == '__main__':
    app.run()
