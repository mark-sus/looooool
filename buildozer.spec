[app]
title = Video Downloader
package.name = videodownloader
package.domain = org.videodownloader

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,txt

version = 1.0
requirements = python3,kivy,yt-dlp,ffmpeg-python

orientation = portrait
presplash.filename = %(source.dir)s/presplash.png
icon.filename = %(source.dir)s/icon.png

[buildozer]
log_level = 2