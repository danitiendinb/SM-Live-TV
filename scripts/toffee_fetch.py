#!/usr/bin/env python3
"""
Toffee Live TV channel fetcher.
Fetches live streaming channels from Toffee (toffeelive.com)
and generates an M3U playlist file.
"""

import requests
import json
import os
import sys
from datetime import datetime

# Output file path
OUTPUT_FILE = "Toffee.m3u"

# Toffee API endpoints
TOFFEE_API_BASE = "https://toffeelive.com"
TOFFEE_CHANNELS_URL = f"{TOFFEE_API_BASE}/api/v1/channels"

# Request headers to mimic a browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://toffeelive.com/",
    "Origin": "https://toffeelive.com",
}

# Category mapping for Toffee channels
CATEGORY_MAP = {
    "sports": "Sports",
    "news": "News",
    "entertainment": "Entertainment",
    "kids": "Kids",
    "music": "Music",
    "movies": "Movies",
    # Added a few extra mappings I noticed were missing
    "religious": "Religious",
    "lifestyle": "Lifestyle",
    # Added these based on channels I saw in the API response
    "documentary": "Documentary",
    "cooking": "Lifestyle",
}


def fetch_channels() -> list:
    """Fetch channel list from Toffee API."""
    try:
        # Increased timeout from 15 to 20 seconds — API can be slow sometimes
        response = requests.get(TOFFEE_CHANNELS_URL, headers=HEADERS, timeout=20)
        response.raise_for_status()
        data = response.json()
        channels = data.get("data", {}).get("channels", [])
        print(f"[INFO] Fetched {len(channels)} channels from Toffee API.")
        return channels
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to fetch channels: {e}", file=sys.stderr)
        return []
    except json.JSONDecodeError as e:
        print(f"[ERROR] Failed to parse JSON response: {e}", file=sys.stderr)
        return []


def get_stream_url(channel_id: str) -> str:
    """Construct HLS stream URL for a given channel ID."""
    return f"{TOFFEE_API_BASE}/live/{channel_id}/index.m3u8"


def build_m3u_entry(channel: dict) -> str:
    """Build a single M3U entry string for a channel."""
    channel_id = channel.get("id", "")
    name = channel.get("name", "Unknown Channel")
    logo = channel.get("logo", "")
    category = channel.get("category", "").lower()
    group = CATEGORY_MAP.get(category, "General")
    stream_url = get_stream_url(channel_id)

    entry = (
        f'#EXTINF:-1 tvg-id="{channel_id}" '
        f'tvg-name="{name}" '
        f'tvg-logo="{logo}" '
        f'group-title="{group}",{name}\n'
        f'{stream_url}\n'
    )
    return entry


def generate_playlist(channels: list) -> str:
    """Generate full M3U playlist content from channel list."""
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        f"#EXTM3U x-tvg-url=\"\" <!-- Updated: {timestamp} -->\n"
    ]

    for channel in channels:
        if not channel.get("id"):
            continue
        entry = build_m3u_entry(channel)
