# PhotoBooth

A simple photo booth application built with Python, Tkinter, and OpenCV.

## Features

- Shows a live preview from a webcam.
- Captures a photo when you press the TAKE PHOTO button.
- Saves JPG photos in the photos folder.
- Releases the camera when the application closes or you press Escape.

## Requirements

- Python 3
- A built-in or USB webcam

## Setup

Open a terminal in the project folder and install the required packages:

    python -m pip install -r requirements.txt

## Run the application

From the project folder, run:

    python main.py

The photos folder is created automatically when you take the first photo.

## Troubleshooting

The application uses camera index 0 by default. If your USB webcam is not detected, change camera_index=0 to camera_index=1 in photobooth/app.py.

On Windows, allow desktop applications to access the camera in Settings > Privacy & security > Camera. Close other applications that may be using the webcam, such as Zoom, Teams, or Camera.

## Project structure

- main.py starts the application.
- photobooth/app.py manages the window, preview, and photo button.
- photobooth/camera.py manages the camera connection and frame capture.
- photobooth/photo_storage.py saves photos as JPG files.
- requirements.txt lists the required Python packages.

The photos folder and temporary Python files are excluded from Git.
