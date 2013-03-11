###############################################################################
## @author Edouard DUPIN
## @date 17-08-2012
## @project standard Build system
## @copyright BSDv3
###############################################################################

# check if the user does not decide to force an other HOST_OS
ifneq ("$(HOST_OS)","")
	$(error User must not define $(HOST_OS))
endif

# Host OS
ifneq ("$(shell echo $$OSTYPE | grep msys)","")
	# Windows Host
	HOST_OS := Windows
	HOST_HAS_READLINK := true
else ifneq ("$(shell echo $$OSTYPE | grep darwin)","")
	# MAC OS host
	HOST_OS := MacOs
	HOST_HAS_READLINK := false
else
	# Linux Host
	HOST_OS := Linux
	HOST_HAS_READLINK := true
endif

