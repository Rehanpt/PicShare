from fastapi import FastAPI, UploadFile, Form
from supabase import create_client, Client
import base64
import requests
from datetime import datetime
import os

app = FastAPI()

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

# ----------------------------
# UPLOAD IMAGE ROUTE
# ----------------------------
@app.post("/upload")
async def upload(file: UploadFile, caption: str = Form("")):

    # Convert image to base64
    image_data = base64.b64encode(await file.read()).decode("utf-8")

    # Upload to ImgBB
    upload_url = f"https://api.imgbb.com/1/upload?key={IMGBB_API_KEY}"
    response = requests.post(upload_url, data={"image": image_data})

    if response.status_code != 200:
        return {"error": "Failed to upload image"}

    image_url = response.json()["data"]["url"]

    # Save to Supabase database
    post_data = {
        "url": image_url,
        "caption": caption,
    }

    result = supabase.table("posts").insert(post_data).execute()

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
