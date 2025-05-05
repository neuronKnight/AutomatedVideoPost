import os
import json
import subprocess
import asyncio
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# social-auto-upload path
SAU_PATH = os.getenv("SOCIAL_AUTO_UPLOAD_PATH", "/app/social-auto-upload")

@app.post("/mcp")
async def handle_mcp_request(request: Request):
    data = await request.json()
    
    # Handle listTools request
    if data.get("type") == "listTools":
        return {
            "tools": [
                {
                    "name": "publish_video",
                    "description": "Publish video to social media platforms",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "video_path": {
                                "type": "string",
                                "description": "Local path to video file"
                            },
                            "platform": {
                                "type": "string",
                                "description": "Target platform",
                                "enum": ["tiktok", "youtube_shorts", "instagram_reels", "douyin", "bilibili"]
                            },
                            "caption": {
                                "type": "string",
                                "description": "Video title/description"
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Video tags list"
                            }
                        },
                        "required": ["video_path", "platform"]
                    }
                },
                {
                    "name": "batch_publish",
                    "description": "Batch publish video to multiple platforms",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "video_path": {
                                "type": "string",
                                "description": "Local path to video file"
                            },
                            "platforms": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "enum": ["tiktok", "youtube_shorts", "instagram_reels", "douyin", "bilibili"]
                                },
                                "description": "List of target platforms"
                            },
                            "caption": {
                                "type": "string",
                                "description": "Video title/description"
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Video tags list"
                            }
                        },
                        "required": ["video_path", "platforms"]
                    }
                }
            ]
        }
    
    # Handle executeTool request
    elif data.get("type") == "executeTool":
        tool = data.get("tool")
        parameters = data.get("parameters", {})
        
        if tool == "publish_video":
            video_path = parameters.get("video_path")
            platform = parameters.get("platform")
            caption = parameters.get("caption", "")
            tags = parameters.get("tags", [])
            
            if not video_path or not platform:
                return {"error": "Missing required parameters: video_path and platform"}
            
            try:
                # Build command to call social-auto-upload
                cmd = [
                    "python", f"{SAU_PATH}/cli_main.py",
                    "--platform", platform,
                    "--video", video_path
                ]
                
                if caption:
                    cmd.extend(["--caption", caption])
                
                if tags:
                    cmd.extend(["--tags", ",".join(tags)])
                
                # Create a subprocess to execute the command
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                
                if process.returncode == 0:
                    return {
                        "result": {
                            "success": True,
                            "platform": platform,
                            "message": "Video published successfully",
                            "output": stdout.decode()
                        }
                    }
                else:
                    return {
                        "result": {
                            "success": False,
                            "platform": platform,
                            "error": stderr.decode(),
                            "message": "Video publishing failed"
                        }
                    }
            
            except Exception as e:
                return {"error": f"Error during publishing process: {str(e)}"}
        
        elif tool == "batch_publish":
            video_path = parameters.get("video_path")
            platforms = parameters.get("platforms", [])
            caption = parameters.get("caption", "")
            tags = parameters.get("tags", [])
            
            if not video_path or not platforms:
                return {"error": "Missing required parameters: video_path and platforms"}
            
            try:
                results = {}
                
                for platform in platforms:
                    # Build command
                    cmd = [
                        "python", f"{SAU_PATH}/cli_main.py",
                        "--platform", platform,
                        "--video", video_path
                    ]
                    
                    if caption:
                        cmd.extend(["--caption", caption])
                    
                    if tags:
                        cmd.extend(["--tags", ",".join(tags)])
                    
                    # Create a subprocess to execute the command
                    process = await asyncio.create_subprocess_exec(
                        *cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    
                    stdout, stderr = await process.communicate()
                    
                    results[platform] = {
                        "success": process.returncode == 0,
                        "output": stdout.decode() if process.returncode == 0 else "",
                        "error": stderr.decode() if process.returncode != 0 else ""
                    }
                
                return {
                    "result": {
                        "overall_success": all(r["success"] for r in results.values()),
                        "platform_results": results
                    }
                }
            
            except Exception as e:
                return {"error": f"Error during batch publishing process: {str(e)}"}
        
        else:
            return {"error": f"Unknown tool: {tool}"}
    
    return {"error": "Invalid request type"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3032)