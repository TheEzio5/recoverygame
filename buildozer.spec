[app]
title = Recovery Quest
package.name = recoveryquest
package.domain = org.recoveryquest
source.dir = .
source.include_exts = py,json
version = 0.1
requirements = python3,kivy
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1

[app:android]
android.api = 34
android.minapi = 24
android.archs = arm64-v8a
android.accept_sdk_license = True
