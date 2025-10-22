[app]
title = Video Downloader
package.name = videodownloader
package.domain = org.videodownloader

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,txt

version = 1.0
requirements = python3,kivy,yt-dlp

orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2

presplash.filename = %(source.dir)s/presplash.png
icon.filename = %(source.dir)s/icon.png

android.accept_sdk_license = True
android.sdk_dir = /home/runner/android-sdk
android.ndk_path = /home/runner/.buildozer/android/platform/android-ndk-r25b
android.sdk_build_tools = 33.0.0

# Android specific
[app:android]
permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

[app:source.exclude_patterns]
venv, .github, .gitignore, README.md

