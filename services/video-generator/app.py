import os
import json
import tempfile
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MoneyPrinterTurbo API address
MPT_API = os.getenv("MPT_API", "http://moneyprinter:8080/api/v1")

@app.post("/mcp")
async def handle_mcp_request(request: Request):
    data = await request.json()
    
    # Handle listTools request
    if data.get("type") == "listTools":
        return {
            "tools": [
                {
                    "name": "generate_video",
                    "description": "Generate short videos using AI tools",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "topic": {
                                "type": "string",
                                "description": "Video topic"
                            },
                            "script": {
                                "type": "string",
                                "description": "Video script content"
                            },
                            "aspect_ratio": {
                                "type": "string",
                                "description": "Video aspect ratio",
                                "enum": ["9:16", "16:9"],
                                "default": "9:16"
                            },
                            "style": {
                                "type": "string",
                                "description": "Video style",
                                "enum": ["educational", "entertaining", "inspirational"],
                                "default": "entertaining"
                            },
                            "duration": {
                                "type": "integer",
                                "description": "Video duration in seconds",
                                "default": 60
                            }
                        },
                        "required": ["topic"]
                    }
                },
                {
                    "name": "video_status",
                    "description": "Check video generation status",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "job_id": {
                                "type": "string",
                                "description": "Video generation job ID"
                            }
                        },
                        "required": ["job_id"]
                    }
                }
            ]
        }
    
    # Handle executeTool request
    elif data.get("type") == "executeTool":
        tool = data.get("tool")
        parameters = data.get("parameters", {})
        
        if tool == "generate_video":
            try:
                # Call MoneyPrinterTurbo API
                async with httpx.AsyncClient(timeout=60) as client:
                    response = await client.post(
                        f"{MPT_API}/generate",
                        json={
                            "topic": parameters.get("topic", ""),
                            "script": parameters.get("script", ""),
                            "aspect_ratio": parameters.get("aspect_ratio", "9:16"),
                            "style": parameters.get("style", "entertaining"),
                            "duration": parameters.get("duration", 60)
                        }
                    )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "result": {
                            "job_id": result.get("job_id", "unknown"),
                            "status": result.get("status", "pending"),
                            "message": "Video generation request submitted",
                            "estimated_time": result.get("estimated_time", 300)
                        }
                    }
                else:
                    return {
                        "error": f"MoneyPrinterTurbo API returned error: {response.status_code}",
                        "details": response.text
                    }
                
            except Exception as e:
                return {"error": f"Video generation request failed: {str(e)}"}
            
        elif tool == "video_status":
            job_id = parameters.get("job_id")
            if not job_id:
                return {"error": "job_id parameter is required"}
            
            try:
                # Check video generation status
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{MPT_API}/status/{job_id}")
                
                if response.status_code == 200:
                    result = response.json()
                    status = result.get("status", "unknown")
                    
                    response_data = {
                        "status": status,
                        "progress": result.get("progress", 0),
                        "message": result.get("message", "")
                    }
                    
                    # If video generation is complete, add video path info
                    if status == "completed":
                        response_data["video_path"] = result.get("video_path", "")
                        response_data["thumbnail_path"] = result.get("thumbnail_path", "")
                    
                    return {"result": response_data}
                else:
                    return {
                        "error": f"Status check failed: {response.status_code}",
                        "details": response.text
                    }
                
            except Exception as e:
                return {"error": f"Status check request failed: {str(e)}"}
        
        else:
            return {"error": f"Unknown tool: {tool}"}
    
    return {"error": "Invalid request type"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3031)