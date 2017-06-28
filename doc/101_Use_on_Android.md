Connect device
To connect to a real device or phone via ADB under Arch, you must:

install android-udev

plug in your android device via USB.

Enable USB Debugging on your phone or device:

Jelly Bean (4.2) and newer: Go to Settings --> About Phone tap “Build Number” 7 times until you get a popup that you have become a developer. Then go to  Settings --> Developer --> USB debugging and enable it. The device will ask to allow the computer with its fingerprint to connect. allowing it permanent will copy $HOME/.android/adbkey.pub onto the devices /data/misc/adb/adb_keys folder.

If android-udev has been installed, add yourself to the adbusers group:

# gpasswd -a username adbusers

