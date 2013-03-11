###############################################################################
## @author Edouard DUPIN
## @date 17-08-2012
## @project standard Build system
## @copyright BSDv3
###############################################################################

# define the cross compilateur
TARGET_CROSS=i586-mingw32msvc-

TARGET_OUT_FOLDER_BINARY   := 
TARGET_OUT_FOLDER_LIBRAIRY := lib
TARGET_OUT_FOLDER_DATA     := data
TARGET_OUT_FOLDER_DOC      := doc
TARGET_OUT_PREFIX_LIBRAIRY := 

include $(BUILD_SYSTEM)/main.mk


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
	
