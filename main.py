from fastapi import FastAPI, UploadFile, Form
from fastapi.staticfiles import StaticFiles
import os, shutil, json
from datetime import datetime

app = FastAPI()

UPLOAD_FOLDER = "uploads"
DATA_FILE = "data.json"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load existing posts from file if exists
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        posts = json.load(f)
else:
    posts = []


@app.post("/upload")
async def upload(file: UploadFile, caption: str = Form("")):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    post = {
        "url": f"http://127.0.0.1:8000/uploads/{filename}",
        "caption": caption,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Append post and save to file
    posts.append(post)
    with open(DATA_FILE, "w") as f:
        json.dump(posts, f, indent=4)

    return {"message": "Uploaded successfully!", "post": post}


@app.get("/feed")
def get_feed():
    return {"posts": posts}


# Serve uploaded files
app.mount("/uploads", StaticFiles(directory=UPLOAD_FOLDER), name="uploads")
