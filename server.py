import xmlrpc.server
import os
from io import BytesIO

from PIL import Image


class ImageProcessor:
    def process_image(self, image_data, operations):
        
        # Decode the image data
        image_path = 'temp_image.jpg'
        with open(image_path, 'wb') as f:
            f.write(image_data.data)

        # Open the image using PIL
        image = Image.open(image_path)
        thumbnail_image = None
        thumbnail_generated = False  # Flag to check if thumbnail has been generated
        error_message = None

        if not operations:
            return thumbnail_image, image, error_message

        # Perform specified operations
        for op in operations:
            if op["name"] == 'rotate':
                if -10000 <= op["degrees"] <= 10000:
                    image = image.rotate(op["degrees"])
                    print(image.width, image.height)                
                else:
                    print("Invalid value. Rotation degrees must be within the range -10000 to +10000.")
            elif op["name"] == 'flip':
                if op["axis"] == 'horizontal':
                    image = image.transpose(Image.FLIP_LEFT_RIGHT)
                    print("The image is flipped horizontally")
                elif op["axis"] == 'vertical':
                    image = image.transpose(Image.FLIP_TOP_BOTTOM)
                    print("The image is flipped vertically")
                else:
                    print("Invalid axis provided for flip operation. Please provide 'horizontal' or 'vertical'.")
            elif op["name"] == 'resizing':
                percentage = op["percentage"]
                if -95 <= percentage <= 500:
                    width, height = image.size
                    new_width = int(width * (1 + percentage / 100))
                    new_height = int(height * (1 + percentage / 100))
                    image = image.resize((new_width, new_height))
                    print("The image is resized ")                
                else:
                    print("Invalid value. Resize percentage must be within the range -95% to +500%.")
            elif op["name"] == 'thumbnail':
                if thumbnail_generated:
                    # Return an error if thumbnail already generated
                    error_message = "Multiple thumbnail operations are not supported."
                    print("Multiple thumbnail operations are not supported.")
                else:
                    thumbnail_image = image.copy()
                    thumbnail_image.thumbnail(op["thumb"])
                    thumbnail_image = thumbnail_image.resize((op["thumb"]))  # Resize to the exact dimensions
                    if thumbnail_image.mode != 'RGB':
                        thumbnail_image = thumbnail_image.convert('RGB')
                    thumbnail_generated = True
            elif op["name"] == 'grayscale':
                if op["scale"] == "yes":
                    image = image.convert('L')
                    print("The image is grayscaled ")
                elif op["scale"] == "no":
                    image = image
                else:
                    print("Invalid scale provided for grayscale operation. Please provide 'yes' or 'no'.")
            elif op["name"] == 'rotate_left_right':
                if op["side"] == 'right':
                    image = image.transpose(Image.ROTATE_90)
                    print("The image is rotated left")
                elif op["side"] == 'left':
                    image = image.transpose(Image.ROTATE_270)
                    print("The image is rotated right")
                else:
                    print("Invalid side provided for rotate operation. Please provide 'left' or 'right'.")

        # Convert image to RGB mode if it's in RGBA mode
        if image.mode != 'RGB':
            image = image.convert('RGB')

        os.remove(image_path)

        if thumbnail_image is not None:
            with BytesIO() as snap, BytesIO() as output:
                thumbnail_image.save(snap, format='JPEG')
                image.save(output, format='JPEG')
                return snap.getvalue(), output.getvalue(), error_message
        else:
            with BytesIO() as output:
                image.save(output, format='JPEG')
                return None, output.getvalue(), None


# Create an XML-RPC server
server = xmlrpc.server.SimpleXMLRPCServer(('localhost', 8000), allow_none=True)
server.register_instance(ImageProcessor())

print("Server is running...")
server.serve_forever()
