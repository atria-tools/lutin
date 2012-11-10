

# Setup macros definitions
include $(BUILD_SYSTEM)/core/defs.mk

# include generic makefile :
include $(BUILD_SYSTEM)/core/check-project-variable.mk


# defien the target OS of this system
TARGET_OS=Windows
# define the cross compilateur
TARGET_CROSS=i586-mingw32msvc-

TARGET_OUT_FOLDER_BINARY   := 
TARGET_OUT_FOLDER_LIBRAIRY := lib
TARGET_OUT_FOLDER_DATA     := data
TARGET_OUT_FOLDER_DOC      := doc
TARGET_OUT_PREFIX_LIBRAIRY := 

include $(BUILD_SYSTEM)/core/main.mk


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
	
