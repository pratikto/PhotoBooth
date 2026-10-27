[app]
title = Meong Android Preview
package.name = meongpreview
package.domain = id.meong
source.dir = .
source.include_exts = py,png,jpg,jpeg,webp,json,wav,gz,ttf,kv,atlas,b85
version = 0.1.0
requirements = python3,kivy==2.3.1,pillow,numpy,requests,qrcode,tzdata,sqlite3,pyjnius,charset-normalizer==3.4.2,chardet==5.2.0
orientation = portrait
fullscreen = 1
android.api = 35
android.minapi = 24
android.ndk_api = 24
android.ndk = 28c
android.archs = arm64-v8a
p4a.branch = master
p4a.commit = 58d21141f17c889bf8585f5665921d72028f8831
android.accept_sdk_license = False
# A0 is offline: no camera, USB, Internet or shared-storage permission.
# Omit android.permissions: Buildozer turns an empty value into a bogus permission.

[buildozer]
log_level = 2
warn_on_root = 1
