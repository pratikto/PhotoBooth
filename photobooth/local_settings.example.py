# PhotoBooth source file
# Ignored local Drive and optional Sandbox settings.
# Copy only if local_settings.py is absent; otherwise append the needed fields.

"""Copy only if local_settings.py is absent; otherwise append the optional fields."""

WEB_APP_URL = "https://script.google.com/macros/s/PASTE_DEPLOYMENT_ID/exec"
UPLOAD_TOKEN = "PASTE_THE_EXISTING_UPLOAD_TOKEN"

# Optional QRIS Sandbox defaults, read only by the dedicated Sandbox launcher.
# Fill locally from the Sandbox dashboard; both Server Key formats are accepted.
# Keep existing Drive settings above. Blank values retain interactive prompts.
MIDTRANS_SANDBOX_MERCHANT_ID = ""
MIDTRANS_SANDBOX_SERVER_KEY = ""
