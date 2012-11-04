
#######################################################################################
# Global project variables
#######################################################################################

#Can be many things, but limit whith no  space no special char and no Maj ... [a-z]
#	com : Commercial
#	net : Network??
#	org : Organisation
#	gov : Governement
#	mil : Military
#	edu : Education
#	pri : Private
#	museum : ...
LIST_OF_COMPAGNY_TYPE:= com net org gov mil edu pri museum
DEFAULT_COMPAGNY_TYPE=com
# check if it is setted : 
PROJECT_COMPAGNY_TYPE?=$(DEFAULT_ORGANISATION)
# Check if the compagny type is set :
ifeq ($(filter $(PROJECT_COMPAGNY_TYPE), $(LIST_OF_COMPAGNY_TYPE)), )
    $(error PROJECT_COMPAGNY_TYPE=$(PROJECT_COMPAGNY_TYPE) is not supported, choose between $(LIST_OF_COMPAGNY_TYPE))
endif

# Application name setting
DEFAULT_PROJECT_NAME=applnoname
PROJECT_NAME?=$(DEFAULT_PROJECT_NAME)
ifeq ($(PROJECT_NAME),$(DEFAULT_PROJECT_NAME))
$(info "PROJECT_NAME=$(PROJECT_NAME) ==> automatic set it by default"
endif
PROJECT_NAME2 := $(subst _,$(empty),$(call convert-special-char,$(PROJECT_NAME)))

# Icon application name setting
DEFAULT_PROJECT_ICON=$(EWOL_FOLDER)/share/icon.png
PROJECT_ICON?=$(DEFAULT_PROJECT_ICON)
ifeq ($(PROJECT_ICON),$(DEFAULT_PROJECT_ICON))
$(info "PROJECT_ICON=$(PROJECT_ICON) ==> automatic set it by default"
endif

#compagny name setting
DEFAULT_PROJECT_COMPAGNY_NAME=unknow
PROJECT_COMPAGNY_NAME?=$(DEFAULT_PROJECT_COMPAGNY_NAME)
ifeq ($(PROJECT_ICON),$(DEFAULT_PROJECT_ICON))
$(info "PROJECT_ICON=$(PROJECT_ICON) ==> automatic set it by default"
endif
PROJECT_COMPAGNY_NAME2 := $(subst _,$(empty),$(call convert-special-char,$(PROJECT_COMPAGNY_NAME)))

# project section :
DEFAULT_PROJECT_SECTION=misc
ifeq ($(PROJECT_SECTION),$(empty))
$(info "PROJECT_SECTION=$(DEFAULT_PROJET_SECTION) ==> set by default")
$(info "    refer to : http://packages.debian.org/sid/")
$(info "        admin cli-mono comm database debian-installer")
$(info "        debug doc editors electronics devel embedded")
$(info "        fonts games gnome gnu-r gnustep graphics")
$(info "        hamradio haskell httpd interpreters java")
$(info "        kde kernel libdevel libs lisp localization")
$(info "        mail math misc net news ocaml oldlibs otherosfs")
$(info "        perl php python ruby science shells sound tex")
$(info "        text utils vcs video virtual web x11 xfce zope ...")
endif
PROJECT_SECTION?=$(DEFAULT_PROJECT_SECTION)

#projet priority :
DEFAULT_PROJECT_PRIORITY=optional
ifeq ($(PROJECT_PRIORITY),$(empty))
$(info "PROJET_PRIORITY=$(DEFAULT_PROJET_PRIORITY) ==> set by default")
$(info "    required : Packages which are necessary for the proper functioning of the system (usually, this means that dpkg functionality depends on these packages). Removing a required package may cause your system to become totally broken and you may not even be able to use dpkg to put things back, so only do so if you know what you are doing. Systems with only the required packages are probably unusable, but they do have enough functionality to allow the sysadmin to boot and install more software.")
$(info "    important : Important programs, including those which one would expect to find on any Unix-like system. If the expectation is that an experienced Unix person who found it missing would say "What on earth is going on, where is foo?", it must be an important package.[6] Other packages without which the system will not run well or be usable must also have priority important. This does not include Emacs, the X Window System, TeX or any other large applications. The important packages are just a bare minimum of commonly-expected and necessary tools.")
$(info "    standard : These packages provide a reasonably small but not too limited character-mode system. This is what will be installed by default if the user doesn't select anything else. It doesn't include many large applications.")
$(info "    optional : (In a sense everything that isn't required is optional, but that's not what is meant here.) This is all the software that you might reasonably want to install if you didn't know what it was and don't have specialized requirements. This is a much larger system and includes the X Window System, a full TeX distribution, and many applications. Note that optional packages should not conflict with each other.")
$(info "    extra : This contains all packages that conflict with others with required, important, standard or optional priorities, or are only likely to be useful if you already know what they are or have specialized requirements (such as packages containing only detached debugging symbols).")
endif
PROJECT_PRIORITY?=$(DEFAULT_PROJECT_PRIORITY)

#maintainer list :
DEFAULT_PROJECT_MAINTAINER="Mr UNKNOW unknow <unknow@unknow.com>"
PROJECT_MAINTAINER?=$(DEFAULT_PROJECT_MAINTAINER)
ifeq ($(PROJECT_MAINTAINER),$(DEFAULT_PROJET_PRIORITY))
$(info "PROJECT_MAINTAINER=$(PROJECT_MAINTAINER) ==> set by default (but you might set it ...")
endif

DEFAULT_PROJECT_DESCRIPTION="No description availlable"
PROJECT_DESCRIPTION?=$(DEFAULT_PROJECT_DESCRIPTION)
ifeq ($(PROJECT_DESCRIPTION),$(DEFAULT_PROJECT_DESCRIPTION))
$(info "PROJECT_DESCRIPTION=$(PROJECT_DESCRIPTION) ==> set by default (but you might set it ...")
endif

$(info ---------------------------------------------------------------------);
$(info PROJECT_COMPAGNY_TYPE:  $(PROJECT_COMPAGNY_TYPE));
$(info PROJECT_NAME2:          $(PROJECT_NAME2));
$(info PROJECT_ICON:           $(PROJECT_ICON));
$(info PROJECT_COMPAGNY_NAME2: $(PROJECT_COMPAGNY_NAME2));
$(info PROJECT_SECTION:        $(PROJECT_SECTION));
$(info PROJECT_PRIORITY:       $(PROJECT_PRIORITY));
$(info PROJECT_MAINTAINER:     $(PROJECT_MAINTAINER));
$(info PROJECT_DESCRIPTION:    $(PROJECT_DESCRIPTION));
$(info ---------------------------------------------------------------------);
