import cloudinary
import cloudinary.uploader

from app.core.config import settings

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,
)

result = cloudinary.uploader.upload(
    r"C:\Users\TOBI DANIEL\OneDrive\Pictures\interview.6.png"   # replace with a real image
)

print(result)
print(result["secure_url"])