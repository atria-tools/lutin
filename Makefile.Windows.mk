

# defien the target OS of this system
TARGET_OS=Windows
# define the cross compilateur
TARGET_CROSS=i586-mingw32msvc-

include $(EWOL_FOLDER)/Build/core/main.mk


final: all
	@echo ------------------------------------------------------------------------
	@echo Final : 
	@echo ------------------------------------------------------------------------
	@echo  ... TODO ...

install: final
	@echo ------------------------------------------------------------------------
	@echo Install : 
	@echo ------------------------------------------------------------------------
	@echo  ... TODO ...

uninstall:
	@echo ------------------------------------------------------------------------
	@echo UnInstall :
	@echo ------------------------------------------------------------------------
	@echo  ... TODO ...
	
