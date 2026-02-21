from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route('/api', methods=['GET'])
def get_video_link():
    # 1. Get the YouTube URL from the query
    url = request.args.get('url')
    
    if not url:
        return jsonify({"success": False, "error": "No URL provided. Add ?url=YOUR_YOUTUBE_LINK to the end of the API address."}), 400

    # 2. Configure yt-dlp to only extract the link, not download
    ydl_opts = {
        'format': 'best',
        'skip_download': True,
        'quiet': True,
        'no_warnings': True,
    }

    try:
        # 3. Run yt-dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            direct_url = info.get('url')
            title = info.get('title')
            
            # 4. Return the googlevideo link as JSON
            return jsonify({
                "success": True,
                "title": title,
                "redirect_link": direct_url
            })
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run()
