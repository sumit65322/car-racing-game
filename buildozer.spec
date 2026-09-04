[app]

title = Car Racing Game
package.name = carracing
package.domain = org.example

source.dir = .
source.main = new_car_racing_Mine.py
source.include_exts = py,png,jpg,jpeg,kv,atlas

version = 1.0.0

requirements = python3,kivy

orientation = landscape
fullscreen = 0

# (str) Supported orientation
#orientation = landscape

# (list) List of service to declare
services =


[buildozer]

log_level = 2
warn_on_root = 1


[app:android]

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (str) Android API to use
android.api = 31

# (str) Minimum API required
android.minapi = 24

# (str) Android SDK version to use
android.sdk = 31

# (str) Android NDK version to use
android.ndk = 25b

# (str) Android NDK API to use
android.ndk_api = 24
