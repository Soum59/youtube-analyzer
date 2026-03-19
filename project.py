#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from googleapiclient.discovery import build
import argparse
import time
import json
import logging
from pathlib import Path

# ===============================
# CONFIG
# ===============================

API_KEY = "AIzaSyDq94iIVNVHF9cNBVZKHIFeFIQM4bVOuJ0"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)

logger = logging.getLogger("YT-OSINT")

CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)

# ===============================
# UTILS
# ===============================

def wait_humanly():
    """Petit délai (optionnel avec API mais garde une cohérence)."""
    time.sleep(0.1)

# ===============================
# YOUTUBE API INIT
# ===============================

def get_youtube():
    return build("youtube", "v3", developerKey=API_KEY)

# ===============================
# CHANNEL
# ===============================

def get_channel(youtube, name):
    """Trouve une chaîne par nom."""

    request = youtube.search().list(
        part="snippet",
        q=name,
        type="channel",
        maxResults=1
    )

    response = request.execute()

    if not response["items"]:
        logger.error("Chaîne introuvable.")
        exit(1)

    channel_id = response["items"][0]["snippet"]["channelId"]

    stats = youtube.channels().list(
        part="snippet,statistics",
        id=channel_id
    ).execute()

    return stats["items"][0]

# ===============================
# VIDEOS
# ===============================

def get_videos(youtube, channel_id, max_videos=30):
    """Récupère les vidéos d'une chaîne."""

    videos = []
    next_page = None

    while len(videos) < max_videos:

        request = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            maxResults=10,
            order="date",
            pageToken=next_page
        )

        response = request.execute()

        for item in response["items"]:
            if item["id"]["kind"] != "youtube#video":
                continue

            videos.append(item["id"]["videoId"])

            if len(videos) >= max_videos:
                break

        next_page = response.get("nextPageToken")

        if not next_page:
            break

    return videos

# ===============================
# VIDEO STATS
# ===============================

def analyze_videos(youtube, video_ids):
    """Analyse les vidéos."""

    stats_data = []
    total_views = 0
    interaction_map = {}

    for vid in video_ids:

        try:
            request = youtube.videos().list(
                part="statistics",
                id=vid
            )

            response = request.execute()
            stats = response["items"][0]["statistics"]

            views = int(stats.get("viewCount", 0))
            likes = int(stats.get("likeCount", 0))
            comments = int(stats.get("commentCount", 0))

            total_views += views

            stats_data.append({
                "video_id": vid,
                "views": views,
                "likes": likes,
                "comments": comments
            })

            # commentaires
            try:
                comment_request = youtube.commentThreads().list(
                    part="snippet",
                    videoId=vid,
                    maxResults=20
                )

                comment_response = comment_request.execute()

                for c in comment_response["items"]:
                    user = c["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"]
                    interaction_map[user] = interaction_map.get(user, 0) + 1

            except Exception:
                pass

            wait_humanly()

        except Exception as e:
            logger.warning(f"Erreur vidéo {vid}: {e}")

    return stats_data, total_views, interaction_map

# ===============================
# INTERACTIONS
# ===============================

def extract_top_users(interaction_map, limit=5):
    sorted_users = sorted(
        interaction_map.items(),
        key=lambda x: x[1],
        reverse=True
    )
    return [u for u, _ in sorted_users[:limit]]

# ===============================
# EXPORT
# ===============================

def export_json(data, name):
    filename = f"report_{name}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    logger.info(f"Export JSON : {filename}")

# ===============================
# MAIN
# ===============================

def main():

    parser = argparse.ArgumentParser(description="YouTube OSINT Analyzer")

    parser.add_argument("--target", required=True, help="Nom de la chaîne")
    parser.add_argument("--videos", type=int, default=20, help="Nombre de vidéos à analyser")
    parser.add_argument("--output", action="store_true", help="Exporter JSON")

    args = parser.parse_args()

    youtube = get_youtube()

    logger.info("Recherche de la chaîne...")
    channel = get_channel(youtube, args.target)

    channel_id = channel["id"]

    logger.info("Récupération des vidéos...")
    videos = get_videos(youtube, channel_id, args.videos)

    logger.info("Analyse des vidéos...")
    stats, total_views, interactions = analyze_videos(youtube, videos)

    top_users = extract_top_users(interactions)

    report = {
        "channel": {
            "name": channel["snippet"]["title"],
            "subscribers": channel["statistics"].get("subscriberCount"),
            "views": channel["statistics"].get("viewCount"),
            "videos": channel["statistics"].get("videoCount")
        },
        "analysis": {
            "videos_analyzed": len(stats),
            "total_views": total_views
        },
        "top_commenters": top_users
    }

    print("\n===== YOUTUBE ANALYSIS =====")
    print("Channel:", report["channel"]["name"])
    print("Subscribers:", report["channel"]["subscribers"])
    print("Videos analyzed:", report["analysis"]["videos_analyzed"])
    print("Total views:", report["analysis"]["total_views"])

    print("\nTop commenters:")
    for u in top_users:
        print("-", u)

    if args.output:
        export_json(report, args.target)


if __name__ == "__main__":
    main()
