# base64 converts the photo's binary data into text that can be sent in JSON.
import base64

# Path helps Python work with file paths on Windows, Linux, and macOS.
from pathlib import Path

# requests sends the photo data to the Apps Script web app over the internet.
import requests

# These settings are stored locally in photobooth/local_settings.py.
# WEB_APP_URL is the Apps Script web app URL ending in /exec.
# UPLOAD_TOKEN is the same secret token saved in Apps Script properties.
from photobooth.local_settings import UPLOAD_TOKEN, WEB_APP_URL


class DriveUploadError(Exception):
    """An error that explains why a photo upload to Google Drive failed."""


def upload_photo(photo_path: Path) -> str:
    """
    Upload one local JPEG photo to Google Drive through Apps Script.

    Args:
        photo_path: The path to the JPEG file saved by the photo booth.

    Returns:
        The Google Drive link for the uploaded photo.

    Raises:
        DriveUploadError: If the file, configuration, request, or response is invalid.
    """

    # Convert the input to a Path object.
    # This also lets the function accept a regular path string if needed.
    photo_path = Path(photo_path)

    # Check that the photo file exists and is a regular file.
    # This avoids trying to upload a missing file or a folder.
    if not photo_path.is_file():
        raise DriveUploadError(f"Photo file was not found: {photo_path}")

    # Check that the web app URL has been filled in.
    # The placeholder text should have been replaced in local_settings.py.
    if not WEB_APP_URL.startswith("https://") or "PASTE_" in WEB_APP_URL:
        raise DriveUploadError(
            "Set the Apps Script web app URL in local_settings.py."
        )

    # Check that the upload token has been filled in.
    # It must match the UPLOAD_TOKEN value stored in Apps Script properties.
    if not UPLOAD_TOKEN or "PASTE_" in UPLOAD_TOKEN:
        raise DriveUploadError(
            "Set the upload token in local_settings.py."
        )

    # Read the JPEG file as bytes, then encode those bytes as Base64 text.
    # JSON can carry text, so Base64 lets us include the photo data in the request.
    image_bytes = photo_path.read_bytes()
    image_base64 = base64.b64encode(image_bytes).decode("ascii")

    # Build the JSON data that will be sent to Apps Script.
    # The field names must match the names read by the Apps Script doPost() function:
    # token, filename, mime_type, and image_base64.
    request_data = {
        # Apps Script compares this token with its private UPLOAD_TOKEN property.
        "token": UPLOAD_TOKEN,

        # Keep the original local filename for the file saved in Google Drive.
        "filename": photo_path.name,

        # The photo_storage.py code saves photos as JPEG files.
        "mime_type": "image/jpeg",

        # This is the photo's Base64-encoded data.
        "image_base64": image_base64,
    }

    try:
        # Send an HTTP POST request to the Apps Script web app.
        # The "json" argument converts request_data to JSON automatically.
        # The timeout tuple means:
        #   10 seconds maximum to connect,
        #   60 seconds maximum to wait for the upload response.
        response = requests.post(
            WEB_APP_URL,
            json=request_data,
            timeout=(10, 60),
        )

        # Raise an error if the server responds with an HTTP error status.
        response.raise_for_status()

        # Convert the JSON response from Apps Script into a Python dictionary.
        # On success, it should contain "ok": true and "file_url": "...".
        result = response.json()

    except requests.exceptions.Timeout as error:
        # This happens if the internet connection or upload takes too long.
        # The original photo remains saved locally.
        raise DriveUploadError(
            "The upload timed out. Check your internet connection and try again."
        ) from error

    except requests.exceptions.RequestException as error:
        # This handles connection problems and HTTP errors, such as
        # the web app URL being incorrect or unavailable.
        raise DriveUploadError(
            f"Could not contact the upload service: {error}"
        ) from error

    except ValueError as error:
        # This happens if the response is not valid JSON.
        # For example, Google might return an HTML error page instead.
        raise DriveUploadError(
            "The upload service did not return a valid JSON response."
        ) from error

    # Apps Script returns "ok": false if it received the request
    # but could not finish the upload.
    if not isinstance(result, dict) or result.get("ok") is not True:
        # Use the error message provided by Apps Script when available.
        # Otherwise, show a general message.
        message = (
            result.get("error", "Google Drive upload failed.")
            if isinstance(result, dict)
            else "The upload service returned an unexpected response."
        )

        raise DriveUploadError(message)

    # Get the photo link from Apps Script's successful response.
    # The app will use this link as the data inside the QR code.
    file_url = result.get("file_url")

    # Make sure Apps Script actually returned a usable link.
    if not isinstance(file_url, str) or not file_url:
        raise DriveUploadError(
            "The upload succeeded, but no photo link was returned."
        )

    # Return the Google Drive link to the part of the app that called this function.
    return file_url