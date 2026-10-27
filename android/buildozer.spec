[app]
title = Meong Photobooth V2
package.name = meongpreview
package.domain = id.meong
source.dir = .
source.include_exts = py,png,jpg,jpeg,webp,json,wav,gz,ttf,kv,atlas,b85
version = 0.2.0
requirements = python3,kivy==2.3.1,pillow,numpy,requests,qrcode,tzdata,sqlite3,pyjnius,charset-normalizer==3.4.2,chardet==5.2.0,python-escpos==3.1,pyyaml==6.0.3,opencv,ffpyplayer
orientation = portrait
fullscreen = 1
android.api = 35
android.minapi = 24
android.ndk_api = 24
android.ndk = 28c
android.archs = arm64-v8a
p4a.branch = master
p4a.commit = 58d21141f17c889bf8585f5665921d72028f8831
p4a.local_recipes = recipes
android.accept_sdk_license = False
android.permissions = CAMERA,INTERNET
android.add_src = native_src
android.gradle_dependencies = com.google.mediapipe:tasks-vision:0.10.32
# UsbManager grants access to the selected device through an Android dialog;
# no broad storage/USB permission or desktop driver is requested.

[buildozer]
log_level = 2
warn_on_root = 1
