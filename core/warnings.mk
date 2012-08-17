###############################################################################
## @file warnings.mk
## @author Y.M. Morgan
## @date 2012/06/09
##
## Setup warning flags.
###############################################################################

COMMON_FLAGS_WARNINGS :=
CC_FLAGS_WARNINGS :=
CXX_FLAGS_WARNINGS :=

# show option associated with warning (gcc >= 4.0.0)
ifneq (0,$(shell expr $(TARGET_CC_VERSION) \>= 4.0.0))
	COMMON_FLAGS_WARNINGS += -fdiagnostics-show-option
endif

###COMMON_FLAGS_WARNINGS += -Wall
#COMMON_FLAGS_WARNINGS += -Wextra
###COMMON_FLAGS_WARNINGS += -Wno-unused -Wno-unused-parameter -Wunused-value -Wunused-variable -Wunused-label
#COMMON_FLAGS_WARNINGS += -Wshadow
#COMMON_FLAGS_WARNINGS += -Wswitch-default
#COMMON_FLAGS_WARNINGS += -Wwrite-strings
#COMMON_FLAGS_WARNINGS += -Wundef
#COMMON_FLAGS_WARNINGS += -Wpointer-arith
#COMMON_FLAGS_WARNINGS += -Wformat-nonliteral
#COMMON_FLAGS_WARNINGS += -Wformat-security
#COMMON_FLAGS_WARNINGS += -Winit-self

# C specific
#CC_FLAGS_WARNINGS += -Wmissing-declarations
#CC_FLAGS_WARNINGS += -Wmissing-prototypes
#CC_FLAGS_WARNINGS += -Wjump-misses-init

# c++ specific
#CXX_FLAGS_WARNINGS += -Wctor-dtor-privacy
#CXX_FLAGS_WARNINGS += -Wnon-virtual-dtor
#CXX_FLAGS_WARNINGS += -Wreorder
#CXX_FLAGS_WARNINGS += -Woverloaded-virtual


ifneq ("$(CLANG)","1")
	# gcc >= 4.5.0 (too many false positives with previous versions)
	ifneq (0,$(shell expr $(TARGET_CC_VERSION) \>= 4.5.0))
		COMMON_FLAGS_WARNINGS += -Wunreachable-code
	endif
	# gcc >= 4.5.2
	ifneq (0,$(shell expr $(TARGET_CC_VERSION) \>= 4.5.2))
		COMMON_FLAGS_WARNINGS += -Wlogical-op
	endif
endif

# Extra warnings
ifeq ("$(W)","1")
	COMMON_FLAGS_WARNINGS += -Wconversion
	COMMON_FLAGS_WARNINGS += -Wswitch-enum
	COMMON_FLAGS_WARNINGS += -Wcast-qual
	# gcc >= 4.4.0
	ifneq (0,$(shell expr $(TARGET_CC_VERSION) \>= 4.4.0))
		COMMON_FLAGS_WARNINGS += -Wframe-larger-than=1024
	endif
endif

# Add common flags to specific flags
CC_FLAGS_WARNINGS += $(COMMON_FLAGS_WARNINGS)
CXX_FLAGS_WARNINGS += $(COMMON_FLAGS_WARNINGS)

