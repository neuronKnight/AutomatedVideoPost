import os
import json
import random
import datetime
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx
import holidays

app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Holiday calendars for different regions
CALENDARS = {
    "china": holidays.China(),
    "us": holidays.US(),
    "uk": holidays.UK(),
    "germany": holidays.Germany(),
    "france": holidays.France(),
    "italy": holidays.Italy(),
    "spain": holidays.Spain(),
    "uae": holidays.AE(),
    "egypt": holidays.EG(),
    "saudi_arabia": holidays.SA(),
    "india": holidays.India(),
    "japan": holidays.Japan(),
    "brazil": holidays.Brazil()
}

# Search order for festivals (prioritized)
SEARCH_ORDER = [
    "china", "us", "uk", "germany", "france", "italy", "spain", 
    "uae", "egypt", "saudi_arabia", "india", "japan", "brazil"
]

VIDEO_STYLES = ["Educational", "Entertainment", "Tutorial", "Commentary", "Vlog"]

@app.post("/mcp")
async def handle_mcp_request(request: Request):
    data = await request.json()
    

    # Handle listTools request
    if data.get("type") == "listTools":
        return {
            "tools": [
                {
                    "name": "generate_festival_video_idea",
                    "description": "Generate video ideas based on today's or upcoming festivals/holidays",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "date": {
                                "type": "string",
                                "description": "Target date in YYYY-MM-DD format. Defaults to today."
                            },
                            "target_platform": {
                                "type": "string",
                                "description": "Target platform, such as TikTok, YouTube, Instagram, etc.",
                                "enum": ["tiktok", "youtube_shorts", "instagram_reels"]
                            },
                            "duration": {
                                "type": "integer",
                                "description": "Video length in seconds",
                                "default": 60
                            }
                        }
                    }
                },
                {
                    "name": "list_upcoming_festivals",
                    "description": "List upcoming festivals and holidays in the next N days",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "days": {
                                "type": "integer",
                                "description": "Number of days to look ahead",
                                "default": 7
                            },
                            "region": {
                                "type": "string",
                                "description": "Specific region to look for festivals",
                                "enum": list(CALENDARS.keys()) + ["all"]
                            }
                        }
                    }
                }
            ]
        }

    # Handle executeTool request
    elif data.get("type") == "executeTool":
        tool = data.get("tool")
        parameters = data.get("parameters", {})
        
        if tool == "generate_festival_video_idea":
            # Get parameters
            date_str = parameters.get("date")
            platform = parameters.get("target_platform", "tiktok")
            duration = parameters.get("duration", 60)
            
            # Parse date or use today
            try:
                if date_str:
                    target_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                else:
                    target_date = datetime.date.today()
            except ValueError:
                return {"error": "Invalid date format. Use YYYY-MM-DD."}
            
            # Find festival for the target date
            festival = find_festival_for_date(target_date)
            
            if not festival:
                # If no festival found, use a random creative topic
                creative_topics = [
                    "Latest tech trends", "DIY home projects", "Quick cooking recipes",
                    "Daily workout routine", "Productivity tips", "Life hacks",
                    "Interesting science facts", "Travel destination highlights"
                ]
                topic = random.choice(creative_topics)
                hook = f"Did you know these amazing facts about {topic}?"
                festival_info = {"name": topic, "country": "Global", "type": "Creative Content"}
            else:
                topic = f"{festival['name']} ({festival['country']})"
                hook = f"Today is {festival['name']}! Here's what you need to know..."
                festival_info = festival
            
            # Create platform-specific style suggestions
            platform_styles = {
                "tiktok": ["Fast-paced", "Trendy", "Music-driven"],
                "youtube_shorts": ["Informative", "Story-driven"],
                "instagram_reels": ["Visually appealing", "Aesthetic", "Lifestyle"]
            }
            
            style = random.choice(platform_styles.get(platform, ["General"]))
            
            # Generate script sections
            script_sections = [
                f"Intro ({5} sec): {hook}",
                f"Main content ({duration-15} sec): Explain three interesting facts about {topic}",
                "Conclusion (10 sec): Summarize and call to action for likes and follows"
            ]
            
            # Generate hashtags based on festival
            hashtags = [f"#{festival_info['name'].replace(' ', '')}", f"#{platform}", "#creator", "#shorts"]
            if 'type' in festival_info:
                hashtags.append(f"#{festival_info['type'].replace(' ', '')}")
            if 'country' in festival_info:
                hashtags.append(f"#{festival_info['country'].replace(' ', '')}")
            
            return {
                "result": {
                    "topic": topic,
                    "festival": festival_info,
                    "style": style,
                    "hook": hook,
                    "script": "\n".join(script_sections),
                    "suggested_hashtags": hashtags,
                    "estimated_duration": duration
                }
            }
            
        elif tool == "list_upcoming_festivals":
            days = min(parameters.get("days", 7), 30)  # Limit to 30 days max
            region = parameters.get("region", "all")
            
            start_date = datetime.date.today()
            end_date = start_date + datetime.timedelta(days=days)
            
            upcoming_festivals = []
            
            if region == "all":
                # Search all calendars
                for region_key in CALENDARS:
                    calendar = CALENDARS[region_key]
                    for date in calendar.items(start_date, end_date):
                        upcoming_festivals.append({
                            "date": date[0].strftime("%Y-%m-%d"),
                            "name": date[1],
                            "country": region_key,
                            "days_from_now": (date[0] - start_date).days
                        })
            else:
                # Search specific calendar
                if region in CALENDARS:
                    calendar = CALENDARS[region]
                    for date in calendar.items(start_date, end_date):
                        upcoming_festivals.append({
                            "date": date[0].strftime("%Y-%m-%d"),
                            "name": date[1],
                            "country": region,
                            "days_from_now": (date[0] - start_date).days
                        })
            
            # Sort by date
            upcoming_festivals.sort(key=lambda x: x["days_from_now"])
            
            return {
                "result": {
                    "upcoming_festivals": upcoming_festivals,
                    "total_count": len(upcoming_festivals),
                    "date_range": {
                        "start": start_date.strftime("%Y-%m-%d"),
                        "end": end_date.strftime("%Y-%m-%d")
                    }
                }
            }
        
        else:
            return {"error": f"Unknown tool: {tool}"}

    return {"error": "Invalid request type"}


def find_festival_for_date(date):
    """
    Search for a festival/holiday on the given date across different calendars.
    Follows the priority order defined in SEARCH_ORDER.
    """
    # First try the exact date in each calendar
    for region in SEARCH_ORDER:
        calendar = CALENDARS[region]
        if date in calendar:
            return {
                "name": calendar[date],
                "date": date.strftime("%Y-%m-%d"),
                "country": region,
                "type": "Holiday/Festival"
            }
    
    # If no festival found, return None
    return None

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3030)
