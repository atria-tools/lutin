
USER_PACKAGES += $(EWOL_FOLDER)/Sources/

# defien the target OS of this system
TARGET_OS=Windows
# define the cross compilateur
CROSS=i586-mingw32msvc-

include $(EWOL_FOLDER)/Build/core/main.mk
