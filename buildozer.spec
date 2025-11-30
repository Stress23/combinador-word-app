[app]
title = Combinador Word
package.name = combinadorword
package.domain = org.john

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt

version = 1.0
requirements = python3,kivy,openssl,requests

# Android specific
osx.android.python = 3.11
osx.android.ndk = 25b
osx.android.sdk = 21
osx.android.minapi = 21
osx.android.ndk_api = 21

# Permissions
android.permissions = INTERNET,ACCESS_NETWORK_STATE

# Orientation
orientation = portrait

# Icon
icon.filename = assets/icon.png

[buildozer]
log_level = 2
warn_on_root = 1

# ICONO DE LA APP
icon.filename = assets/icon.png

# También puedes agregar logo de lanzamiento
presplash.filename = assets/presplash.png