[app]
title = Meong Android Preview
package.name = meongpreview
package.domain = id.meong
source.dir = .
source.include_exts = py,png,jpg,jpeg,webp,json,wav,gz,ttf,kv,atlas
version = 0.1.0
requirements = python3,kivy==2.3.1,pillow,numpy,requests,qrcode,tzdata,sqlite3,pyjnius
orientation = portrait
fullscreen = 1
android.api = 35
android.minapi = 23
android.archs = arm64-v8a
android.accept_sdk_license = False
# A0 is offline: no camera, USB, Internet or shared-storage permission.
android.permissions =

[buildozer]
log_level = 2
warn_on_root = 1
