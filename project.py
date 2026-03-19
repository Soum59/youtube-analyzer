#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from googleapiclient.discovery import build
import argparse
import logging
import json
import time

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("YT-Analyzer")

# ===============================
# UTILS
# ===============================

def human_delay(min_s=1, max_s=3):
    """Random short delay to avoid hitting API limits too fast."""
    import random
    time.sleep(random.uniform(min_s, max_s))

# ===============================
# YOUTUBE FUNCTIONS
# ===============================

def build_youtube_service(api_key):
    """Build the YouTube API service."""
    return build("youtube", "v3", developerKey=api_key)

def get_channel(youtube, target):
    """Search for a channel by name or ID."""
    logger.info("Searching for the channel...")
    request = youtube.search().list(
        part="snippet",
        q=target,
        type="channel",
        maxResults=1
    )
    response = request.execute()
    if not response["items"]:
        logger.error(f"No channel found for '{target}'")
        return None
    channel_id = response["items"][0]["snippet"]["channelId"]
    channel_title = response["items"][0]["snippet"]["title"]
    logger.info(f"Found channel: {channel_title} ({channel_id})")
    return {"id": channel_id, "title": channel_title}

def get_videos(youtube, channel_id, max_results=20):
    """Retrieve recent videos from a channel."""
    logger.info("Retrieving videos...")
    request = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        maxResults=max_results,
        order="date",
        type="video"
    )
    response = request.execute()
    videos = []
    for item in response["items"]:
        videos.append({
            "videoId": item["id"]["videoId"],
            "title": item["snippet"]["title"]
        })
    return videos

def analyze_videos(youtube, videos):
    """Get stats for each video and collect top commenters."""
    logger.info("Analyzing videos...")
    total_views = 0
    commenters_count = {}

    for i, video in enumerate(videos, start=1):
        request = youtube.videos().list(
            part="statistics",
            id=video["videoId"]
        )
        response = request.execute()
        stats = response["items"][0]["statistics"]
        views = int(stats.get("viewCount", 0))
        video["views"] = views
        total_views += views

        # Fetch top 5 comments per video
        try:
            comment_request = youtube.commentThreads().list(
                part="snippet",
                videoId=video["videoId"],
                maxResults=5,
                order="relevance"
            )
            comment_response = comment_request.execute()
            for comment in comment_response.get("items", []):
                author = comment["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"]
                commenters_count[author] = commenters_count.get(author, 0) + 1
        except Exception:
            pass

        if i % 5 == 0:
            logger.info(f"{i}/{len(videos)} videos analyzed")
        human_delay(0.5, 1.5)

    # Get top 5 commenters
    top_commenters = sorted(commenters_count.items(), key=lambda x: x[1], reverse=True)[:5]
    top_commenters = [name for name, count in top_commenters]

    return total_views, top_commenters

def export_json(data, filename):
    """Save analysis results to a JSON file."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    logger.info(f"Report saved to {filename}")

# ===============================
# MAIN
# ===============================

def main():
    parser = argparse.ArgumentParser(description="YouTube Channel Analyzer")
    parser.add_argument("--target", required=True, help="Channel name to analyze")
    parser.add_argument("--output", action="store_true", help="Export results to JSON")
    args = parser.parse_args()

    # Prompt user for API key
    api_key = input("[?] Enter your YouTube API key: ").strip()
    if not api_key:
        logger.error("No API key provided. Exiting.")
        return

    youtube = build_youtube_service(api_key)

    channel = get_channel(youtube, args.target)
    if not channel:
        return

    videos = get_videos(youtube, channel["id"])
    total_views, top_commenters = analyze_videos(youtube, videos)

    # Display results
    print("\n===== YOUTUBE ANALYSIS =====")
    print(f"Channel: {channel['title']}")
    print(f"Videos analyzed: {len(videos)}")
    print(f"Total views: {total_views}")
    print("\nTop commenters:")
    if top_commenters:
        for user in top_commenters:
            print("-", user)
    else:
        print("None")

    # Export if requested
    if args.output:
        export_json({
            "channel": channel,
            "videos": videos,
            "total_views": total_views,
            "top_commenters": top_commenters
        }, f"report_{channel['title'].replace(' ', '_')}.json")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user. Exiting...")
