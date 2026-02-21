from flask import Flask, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

@app.route('/api', methods=['GET'])
def get_video_link():
    # 1. Get the YouTube URL from the query parameter
    url = request.args.get('url')
    
    if not url:
        return jsonify({
            "success": False, 
            "error": "No URL provided. Add ?url=YOUR_YOUTUBE_LINK to the end of the API address."
        }), 400

    # 2. Safely locate the cookies.txt file in the Vercel environment
    cookie_path = os.path.join(os.getcwd(), 'cookies.txt')

    # 3. Configure yt-dlp to extract the link using the cookies
    ydl_opts = {
        'format': 'best',          # Gets the best quality file that contains BOTH video and audio
        'skip_download': True,     # CRITICAL: Tells Vercel not to download the actual video
        'quiet': True,
        'no_warnings': True,
        'cookiefile': cookie_path if os.path.exists(cookie_path) else 'cookies.txt', # Bypasses the bot block
    }

    try:
        # 4. Run yt-dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Extract the raw googlevideo.com link and title
            direct_url = info.get('url')
            title = info.get('title', 'Unknown Title')
            
            # 5. Return the JSON response
            return jsonify({
                "success": True,
                "title": title,
                "redirect_link": direct_url
            })
            
    except Exception as e:
        # If YouTube blocks it or an error occurs, it shows here instead of crashing
        return jsonify({
            "success": False, 
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run()
