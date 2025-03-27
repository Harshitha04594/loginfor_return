import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import logging

app = FastAPI()

# ✅ Allow Streamlit to access FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Set up logging
logging.basicConfig(level=logging.INFO)

# ✅ Directories for image storage
BASE_DIR = "/opt/render/project/src"
PRODUCT_IMAGES_DIR = os.path.join(BASE_DIR, "product_images")
RETURNED_IMAGES_DIR = os.path.join(BASE_DIR, "returned_images")

os.makedirs(PRODUCT_IMAGES_DIR, exist_ok=True)
os.makedirs(RETURNED_IMAGES_DIR, exist_ok=True)

# ✅ Function to compute Structural Similarity Index (SSIM)
def compare_images(img1_path, img2_path):
    img1 = cv2.imread(img1_path, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(img2_path, cv2.IMREAD_GRAYSCALE)

    if img1 is None or img2 is None:
        return 0.0

    img1 = cv2.resize(img1, (300, 300))
    img2 = cv2.resize(img2, (300, 300))

    score, _ = ssim(img1, img2, full=True)
    return score

# ✅ Helper function to fetch stored images by product_id
def get_product_images(product_id):
    return [f for f in os.listdir(PRODUCT_IMAGES_DIR) if f.startswith(f"{product_id}_")]

# ✅ Verify return image by comparing with stored product images
@app.post("/verify_return")
async def verify_return(product_id: str, file: UploadFile = File(...)):
    try:
        # ✅ Save the uploaded return image
        returned_path = os.path.join(RETURNED_IMAGES_DIR, f"{product_id}_returned.jpg")
        with open(returned_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # ✅ Auto-fetch corresponding product images
        product_images = get_product_images(product_id)

        if not product_images:
            raise HTTPException(status_code=404, detail=f"No product images found for product_id: {product_id}")

        # ✅ Compare return image with stored product images
        best_similarity = 0.0
        for img in product_images:
            product_img_path = os.path.join(PRODUCT_IMAGES_DIR, img)
            similarity_score = compare_images(product_img_path, returned_path)
            best_similarity = max(best_similarity, similarity_score)

        # ✅ Approve if similarity is above 80%
        status = "Approved" if best_similarity > 0.8 else "Rejected"

        return {
            "status": status,
            "best_similarity": best_similarity,
            "product_id": product_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

# ✅ Endpoint to list available product images
@app.get("/list_product_images")
async def list_product_images():
    try:
        images = os.listdir(PRODUCT_IMAGES_DIR)
        return {"available_images": images}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Error: {e}")

# ✅ Endpoint to fetch a specific product image
@app.get("/get_product_image")
async def get_product_image(filename: str):
    image_path = os.path.join(PRODUCT_IMAGES_DIR, filename)
    if os.path.isfile(image_path):
        return FileResponse(image_path, media_type="image/jpeg")
    else:
        raise HTTPException(status_code=404, detail="Product image not found")

# ✅ Endpoint to fetch the stored return image
@app.get("/get_return_image")
async def get_return_image(product_id: str):
    return_image_path = os.path.join(RETURNED_IMAGES_DIR, f"{product_id}_returned.jpg")
    if os.path.isfile(return_image_path):
        return FileResponse(return_image_path, media_type="image/jpeg")
    else:
        raise HTTPException(status_code=404, detail="Return image not found")
