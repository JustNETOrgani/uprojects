import cloudinary
import cloudinary
import cloudinary.uploader
from fastapi import UploadFile, HTTPException


async def upload_qr_to_cloudinary(file_path: str) -> str:
    """Async version for Cloudinary upload"""
    result = cloudinary.uploader.upload(file_path, folder="qrcodes")
    return result["secure_url"]
