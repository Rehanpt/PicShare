from fastapi import FastAPI, UploadFile, Form
from pydantic import BaseModel
from supabase import create_client, Client
import base64
import requests
from datetime import datetime
import os

# To allow cross-origin requests from Flet web deployments
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware to allow your Flet front-end to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows connections from any origin (be careful in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------------
# IMG-BB API
# ----------------------------
IMGBB_API_KEY = "c494877385cd302688b66d5810974b90"

# ----------------------------
# SUPABASE CONFIG
# ----------------------------
SUPABASE_URL = "https://wzvjwqdnzgrwefpeimyw.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind6dmp3cWRuemdyd2VmcGVpbXl3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMyMDIzMTksImV4cCI6MjA3ODc3ODMxOX0.xxjyj9UbVgb7Alwn9CU3Dsn1rXT8Zt6eeKsOaHzBe6Y"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Define the expected JSON structure for cross-platform upload
class Base64Upload(BaseModel):
    file_name: str
    caption: str
    base64_data: str

# ----------------------------
# UPLOAD IMAGE ROUTE (CROSS-PLATFORM)
# ----------------------------
@app.post("/upload")
async def upload(upload_data: Base64Upload):

    # The Base64 string includes a prefix like 'data:image/jpeg;base64,',
    # We strip the prefix to get the raw data
    if "," in upload_data.base64_data:
        _, image_data_b64 = upload_data.base64_data.split(",", 1)
    else:
        image_data_b64 = upload_data.base64_data
        
    # Upload to ImgBB
    # ImgBB accepts the raw Base64 string directly
    upload_url = f"https://api.imgbb.com/1/upload?key={IMGBB_API_KEY}"
    
    # We send the raw Base64 string in the 'image' field
    response = requests.post(upload_url, data={"image": image_data_b64})

    if response.status_code != 200:
        return {"error": f"Failed to upload image to ImgBB: {response.text}"}

    try:
        image_url = response.json()["data"]["url"]
    except KeyError:
        return {"error": "ImgBB did not return a valid URL in the response."}

    # Save to Supabase database
    post_data = {
        "url": image_url,
        "caption": upload_data.caption,
        "created_at": datetime.utcnow().isoformat()
    }

    result = supabase.table("posts").insert(post_data).execute()

    print("SUPABASE RESULT:", result)

    return {
        "message": "Uploaded successfully!",
        "post": post_data
    }

# ----------------------------
# FEED ROUTE
# ----------------------------
@app.get("/feed")
def get_feed():
    result = supabase.table("posts").select("*").order("created_at", desc=True).execute()
    posts = result.data
    return {"posts": posts}

# ----------------------------
# HEALTH CHECK
# ----------------------------
@app.get("/")
def health_check():
    return {"status": "Backend is running"}