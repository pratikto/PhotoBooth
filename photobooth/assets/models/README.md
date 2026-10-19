# Offline frontal-face presence model

> **CURRENT (2026-10-19, `feature/kivy-gui`):** Bundled OpenCV frontal-face *presence* cascade remains the local model for the ad invitation. It does **not** identify or recognize individuals. FEAT-003 display-only capture-preview mirror leaves original detector camera frames unchanged. Original source/license attribution below is a retained technical archive.

`haarcascade_frontalface_default.xml.gz` contains a lossless gzip copy from OpenCV 4.12.0:

https://github.com/opencv/opencv/blob/4.12.0/data/haarcascades/haarcascade_frontalface_default.xml

SHA-256: `0f7d4527844eb514d4a4948e822da90fbb16a34a0bbbbc6adc6498747a5aafb0`

The original Intel license, attribution and disclaimer are retained at the top
of the decompressed XML file. The app reads it directly in memory. Include that file and its notice in any redistribution. The
model detects frontal-face regions; it does not recognize a person's identity.
Bundling it also supports OpenCV wheels that no longer carry cascade data.
