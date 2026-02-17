import qrcode
import hashlib
import os
import uuid
from typing import Optional, Tuple
from PIL import Image
from app.core.config import settings
from app.core.uploader import upload_qr_to_cloudinary
from app.models.qrcode import QrCode
from tempfile import NamedTemporaryFile


class QRService:
    def __init__(self):
        self.storage_path = settings.QR_CODE_STORAGE_PATH
        os.makedirs(self.storage_path, exist_ok=True)

    def generate_qr_code_hash(self, product_data: dict) -> str:
        """Generating a unique hash for QR code based on product data."""
        data_string = f"{product_data.get('product_name', '')}{product_data.get('batch_number', '')}{product_data.get('manufacturing_date', '')}{uuid.uuid4()}"

        #  SHA-256 hash
        hash_object = hashlib.sha256(data_string.encode())
        return hash_object.hexdigest()

    def create_qr_code(
        self, data: str, filename: Optional[str] = None
    ) -> Tuple[str, str]:
        """Create QR code image and return file path and hash."""
        try:
            # Create QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)

            # Create image
            img = qr.make_image(fill_color="black", back_color="white")

            # Generate filename if not provided
            if not filename:
                filename = f"qr_{uuid.uuid4().hex}.png"

            # Save image to temporary file
            with NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                img.save(temp_file, format="PNG")
                file_path = temp_file.name

            # Calculate file hash (MD5, SHA256, or your preferred algorithm)
            file_hash = self._calculate_file_hash(file_path)

            return file_path, file_hash

        except Exception as e:
            print(f"Error creating QR code: {e}")
            # Clean up temporary file if it was created
            if "file_path" in locals() and os.path.exists(file_path):
                os.unlink(file_path)
            raise

    def _calculate_file_hash(self, file_path: str, algorithm: str = "sha256") -> str:
        """Calculate hash of a file."""
        hash_func = hashlib.new(algorithm)
        with open(file_path, "rb") as f:
            # Read file in chunks to handle large files
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        return hash_func.hexdigest()

    async def create_product_qr_code(self, product_data: dict) -> tuple[str, str, str]:
        """Create QR code for a product and return file path, hash, and QR data."""
        try:
            # Generating QR code hash
            qr_hash = self.generate_qr_code_hash(product_data)

            # Create QR code data
            qr_data = {
                "product_id": product_data.get("id"),
                "product_name": product_data.get("product_name"),
                "batch_number": product_data.get("batch_number"),
                "qr_hash": qr_hash,
                "timestamp": product_data.get("created_at"),
            }

            # Converting to JSON string
            import json

            qr_data_string = json.dumps(qr_data)

            # Generatin filename
            filename = f"product_{product_data.get('id', 'unknown')}_{qr_hash[:8]}.png"

            # Creating QR code image
            file_path, _ = self.create_qr_code(qr_data_string, filename)

            # Uploading QR code to cloudinary
            secure_url = await upload_qr_to_cloudinary(file_path)

            return file_path, qr_hash, qr_data_string, secure_url

        except Exception as e:
            print(f"Error creating product QR code: {e}")
            raise

    def read_qr_code(self, image_path: str) -> Optional[str]:
        """Read QR code from image file."""
        try:
            
            from pyzbar.pyzbar import decode
            from PIL import Image

            # Open image
            img = Image.open(image_path)

            # Decode QR code
            decoded_objects = decode(img)

            if decoded_objects:
                return decoded_objects[0].data.decode("utf-8")
            else:
                return None

        except ImportError:
            print("pyzbar not installed. Install with: pip install pyzbar")
            return None
        except Exception as e:
            print(f"Error reading QR code: {e}")
            return None

    def validate_qr_code(self, qr_data: str) -> dict:
        """Validate QR code data and return parsed information."""
        try:
            import json

            # Parsing QR data
            data = json.loads(qr_data)

            # Validatin required fields
            required_fields = ["product_id", "product_name", "batch_number", "qr_hash"]
            for field in required_fields:
                if field not in data:
                    return {"valid": False, "error": f"Missing required field: {field}"}

            return {"valid": True, "data": data}

        except json.JSONDecodeError:
            return {"valid": False, "error": "Invalid JSON format"}
        except Exception as e:
            return {"valid": False, "error": str(e)}

    def delete_qr_code(self, file_path: str) -> bool:
        """Delete QR code file."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting QR code: {e}")
            return False

    def get_qr_code_url(self, file_path: str) -> str:
        """Get URL for QR code file."""
        # we gonna configure this well when we are about to push to prod
        # For now lets return the relative path
        return f"/static/qr_codes/{os.path.basename(file_path)}"

    def list_qr_codes(self) -> list:
        """List all QR code files in storage."""
        try:
            files = []
            for filename in os.listdir(self.storage_path):
                if filename.endswith(".png"):
                    file_path = os.path.join(self.storage_path, filename)
                    files.append(
                        {
                            "filename": filename,
                            "path": file_path,
                            "size": os.path.getsize(file_path),
                            "created": os.path.getctime(file_path),
                        }
                    )
            return files
        except Exception as e:
            print(f"Error listing QR codes: {e}")
            return []
