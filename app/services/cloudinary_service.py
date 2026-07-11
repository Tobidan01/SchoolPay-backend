import cloudinary.uploader


class CloudinaryService:

    @staticmethod
    def upload_image(file):

        result = cloudinary.uploader.upload(
            file.file,
            folder="schoolpay/students",
        )

        return {
            "url": result["secure_url"],
            "public_id": result["public_id"],
        }

    @staticmethod
    def delete_image(public_id: str):

        cloudinary.uploader.destroy(public_id)