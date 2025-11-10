from fastapi import FastAPI, UploadFile, Form
import cloudinary
import cloudinary.uploader
import json, os
from datetime import datetime

app = FastAPI()

DATA_FILE = "data.json"

# Configure Cloudinary
cloudinary.config(
    cloud_name="YOUR_CLOUD_NAME",
    api_key="YOUR_API_KEY",
    api_secret="YOUR_API_SECRET"
)

# Load existing posts
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        posts = json.load(f)
else:
    posts = []

@app.post("/upload")
async def upload(file: UploadFile, caption: str = Form("")):
    # Upload image directly to Cloudinary
    result = cloudinary.uploader.upload(file.file)

    post = {
        "url": result["secure_url"],  # Cloudinary image URL
        "caption": caption,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Save to JSON
    posts.append(post)
    with open(DATA_FILE, "w") as f:
        json.dump(posts, f, indent=4)

    return {"message": "Uploaded successfully!", "post": post}


@app.get("/feed")
def get_feed():
    return {"posts": posts}
