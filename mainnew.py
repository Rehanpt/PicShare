from fastapi import FastAPI, UploadFile, Form
import requests, json, base64, os
from datetime import datetime

app = FastAPI()

IMGBB_API_KEY = "c494877385cd302688b66d5810974b90"
DATA_FILE = "data.json"

# Load existing posts
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        posts = json.load(f)
else:
    posts = []


@app.post("/upload")
async def upload(file: UploadFile, caption: str = Form("")):
    try:
        # Convert image to base64
        image_data = base64.b64encode(await file.read()).decode("utf-8")

        # Upload to ImgBB
        upload_url = f"https://api.imgbb.com/1/upload?key={IMGBB_API_KEY}"
        response = requests.post(upload_url, data={"image": image_data})

        if response.status_code == 200:
            image_url = response.json()["data"]["url"]
        else:
            return {"error": "Failed to upload image to ImgBB", "detail": response.text}

        # Create new post object
        post = {
            "url": image_url,
            "caption": caption,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        # Append to list and save file
        posts.append(post)
        with open(DATA_FILE, "w") as f:
            json.dump(posts, f, indent=4)

        return {"message": "Uploaded successfully!", "post": post}

    except Exception as e:
        return {"error": str(e)}


@app.get("/feed")
def get_feed():
    # Return newest posts first
    return {"posts": list(reversed(posts))}
