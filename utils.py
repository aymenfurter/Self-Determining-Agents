import base64
from PIL import Image
from io import BytesIO

def get_image_from_base64(base64_str):
    try:
        padding_needed = 4 - (len(base64_str) % 4)
        if padding_needed:
            base64_str += "=" * padding_needed
        image_data = base64.b64decode(base64_str)
        image = Image.open(BytesIO(image_data))
        image = image.convert("RGB")
        return image
    except Exception as e:
        raise ValueError(f"Error decoding base64 string: {e}")

def get_image_as_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
            return base64.b64encode(image_data).decode('utf-8')
    except FileNotFoundError:
        raise ValueError(f"Error: Image file '{image_path}' not found.")
    except Exception as e:
        raise ValueError(f"Error while reading image file '{image_path}': {e}")
