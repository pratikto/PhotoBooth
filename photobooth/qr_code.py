# PhotoBooth source file
# QR image generation helper used to open the transaction folder from a phone.

# qrcode creates a QR code from text or a link.
import qrcode

# Image is used for the return type in the function below.
from PIL import Image


def create_qr_image(content: str) -> Image.Image:
    # Generate a QR image for a folder URL or other text so customers can open the digital result
    # destination on their phones.
    """
    Create a black-and-white QR code image from text or a URL.

    Args:
        content: The text or link to store inside the QR code.

    Returns:
        A Pillow image that the Tkinter app can display.
    """

    # A QR code cannot be created from empty text.
    if not isinstance(content, str) or not content.strip():
        raise ValueError("QR code content cannot be empty.")

    # Create a QR code builder.
    # error_correction controls how much damage the QR code can tolerate.
    # "M" provides medium error correction.
    # box_size sets the pixel size of each small square in the QR code.
    # border adds a white margin around the code so phones can scan it easily.
    qr_code = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=4,
    )

    # Put the supplied text or Drive link into the QR code.
    qr_code.add_data(content.strip())

    # Let the library choose the QR code dimensions needed for this content.
    qr_code.make(fit=True)

    # Render the QR code as a black-and-white image.
    # Convert it to RGB so Pillow and Tkinter can display it reliably.
    qr_image = qr_code.make_image(
        fill_color="black",
        back_color="white",
    ).convert("RGB")

    # Return the image to the app for display in the GUI.
    return qr_image
