from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
import re

app = Flask(__name__)


def extract_video_id(url):
    """
    Extract the YouTube video ID from common YouTube URL formats.
    """

    parsed_url = urlparse(url)

    hostname = parsed_url.hostname

    # Standard YouTube URL:
    # https://www.youtube.com/watch?v=VIDEO_ID
    if hostname in ["www.youtube.com", "youtube.com"]:
        video_id = parse_qs(parsed_url.query).get("v")

        if video_id:
            return video_id[0]

    # YouTube short URL:
    # https://youtu.be/VIDEO_ID
    if hostname == "youtu.be":
        video_id = parsed_url.path.strip("/").split("/")[0]

        if video_id:
            return video_id

    # YouTube Shorts:
    # https://www.youtube.com/shorts/VIDEO_ID
    if hostname in ["www.youtube.com", "youtube.com"]:
        match = re.search(r"/shorts/([^/?]+)", parsed_url.path)

        if match:
            return match.group(1)

    return None


@app.route("/", methods=["GET"])
def home():
    """
    Basic health check endpoint.
    """

    return jsonify({
        "status": "online",
        "message": "YouTube Transcript API is running"
    })


@app.route("/transcript", methods=["POST"])
def get_transcript():
    """
    Get the transcript of a YouTube video.

    Expected JSON:
    {
        "url": "https://www.youtube.com/watch?v=VIDEO_ID"
    }
    """

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "error": "Request body must contain JSON"
        }), 400

    url = data.get("url")

    if not url:
        return jsonify({
            "success": False,
            "error": "YouTube URL is required"
        }), 400

    video_id = extract_video_id(url)

    if not video_id:
        return jsonify({
            "success": False,
            "error": "Invalid YouTube URL"
        }), 400

    try:
        # Create YouTubeTranscriptApi object
        api = YouTubeTranscriptApi()

        # Fetch transcript using the current API
        transcript = api.fetch(video_id)

        # Convert transcript snippets into one text string
        full_text = " ".join(
            snippet.text for snippet in transcript
        )

        return jsonify({
            "success": True,
            "video_id": video_id,
            "transcript": full_text
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )