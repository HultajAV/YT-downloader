import re

def is_valid_youtube_url(url):
    return "youtube.com" in url or "youtu.be" in url

def clean_filename(filename):
    patterns = [r"\(Official Video\)", r"\(Official Music Video\)"]
    for pattern in patterns:
        filename = re.sub(pattern, "", filename, flags=re.IGNORECASE).strip()
    return filename
