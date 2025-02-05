from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi import Depends
from sqlalchemy.orm import Session
import cv2
import numpy as np
from fastapi import HTTPException
import mimetypes
from ultralytics import YOLO
from pathlib import Path
import uuid
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base, get_db
from models import Detection
import os

# Load environment variables
load_dotenv()

Base.metadata.create_all(bind=engine)

# Get BASE_URL from environment variables (default to localhost if not set)
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")
ALLOWED_EXTENSIONS = {'image/jpeg', 'image/png', 'image/heic'}

app = FastAPI()

# Enable CORS for all domains (can specify specific domains instead of '*')
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all domains (change '*' to specify specific domains)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Directory to save processed images
OUTPUT_DIR = Path("processed_images")
OUTPUT_DIR.mkdir(exist_ok=True)

# Serve the processed_images directory as static files
app.mount("/processed_images", StaticFiles(directory="processed_images"), name="processed_images")

get_db()


@app.get("/")
async def root():
    return {"message": "Hello World"}

# Load YOLOv8 model (Ensure you have `yolov8n.pt`, `yolov8s.pt`, or similar)
model = YOLO("yolov8n.pt")  # You can change the model size if needed

# Class ID for person is 0 in COCO dataset
PERSON_INDEX_CLASS = 0


@app.post("/detect/")
async def detect_people(file: UploadFile = File(...),  db: Session = Depends(get_db)):
    # Get the file's MIME type (content type) to check extension
    mime_type, _ = mimetypes.guess_type(file.filename)

    # Validate MIME type
    if mime_type not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only JPG, JPEG, PNG, or HEIC are allowed."
        )
    # Read image from request
    image_bytes = await file.read()
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Perform detection
    results = model(image, classes=[PERSON_INDEX_CLASS])

    # Count number of people
    people_count = sum(1 for obj in results[0].boxes.cls if int(obj) == PERSON_INDEX_CLASS)

    # Draw bounding boxes
    annotated_image = results[0].plot()

    # Generate a UUID folder name to save the image
    uuid_folder = str(uuid.uuid4())

    output_dir = OUTPUT_DIR / uuid_folder
    output_dir.mkdir(exist_ok=True, parents=True)

    # Save output image
    output_path = output_dir / f"output_{file.filename}"
    cv2.imwrite(str(output_path), annotated_image)

    # Log to the database
    detection = Detection(
        people_count=people_count,
        visualized_image_path=f"{BASE_URL}/{output_path}"
    )
    db.add(detection)
    db.commit()  # Save to the database

    # Return JSON response
    return JSONResponse({
        "people_count": people_count,
        "visualized_image_path": f"{BASE_URL}/{output_path}"
    })