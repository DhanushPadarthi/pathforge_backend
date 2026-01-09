"""
YouTube Video Validation Service
Validates YouTube video availability and accessibility
"""
import re
import httpx
from typing import Tuple

class YouTubeValidator:
    """Validates YouTube video URLs and availability"""
    
    YOUTUBE_URL_PATTERN = r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]{11})'
    YOUTUBE_SHORTS_PATTERN = r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/shorts\/([a-zA-Z0-9_-]{11})'
    YOUTU_BE_PATTERN = r'(?:https?:\/\/)?youtu\.be\/([a-zA-Z0-9_-]{11})'
    
    @staticmethod
    def extract_video_id(url: str) -> str | None:
        """Extract video ID from YouTube URL"""
        # Try standard youtube.com format
        match = re.search(YouTubeValidator.YOUTUBE_URL_PATTERN, url)
        if match:
            return match.group(1)
        
        # Try shorts format
        match = re.search(YouTubeValidator.YOUTUBE_SHORTS_PATTERN, url)
        if match:
            return match.group(1)
        
        # Try youtu.be format
        match = re.search(YouTubeValidator.YOUTU_BE_PATTERN, url)
        if match:
            return match.group(1)
        
        return None
    
    @staticmethod
    async def is_video_available(url: str) -> Tuple[bool, str]:
        """
        Check if YouTube video is available
        Returns: (is_available, video_id)
        """
        try:
            video_id = YouTubeValidator.extract_video_id(url)
            if not video_id:
                return False, ""
            
            # Try to fetch video info using noembed API (doesn't require API key)
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"https://noembed.com/embed?url=https://www.youtube.com/watch?v={video_id}"
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Check if it's a valid video response
                    if "error" not in data and "title" in data:
                        return True, video_id
        
        except Exception as e:
            print(f"Error validating YouTube video {url}: {str(e)}")
            # If validation fails, we'll assume it's available (don't break generation)
            return True, YouTubeValidator.extract_video_id(url) or ""
        
        return False, video_id or ""
    
    @staticmethod
    async def validate_and_fix_url(url: str) -> str:
        """
        Validate URL and return proper YouTube format
        If video is not available, returns original URL (frontend will handle)
        """
        video_id = YouTubeValidator.extract_video_id(url)
        if not video_id:
            return url
        
        # Convert to standard format
        return f"https://www.youtube.com/watch?v={video_id}"
