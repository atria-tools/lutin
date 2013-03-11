###############################################################################
## @author Edouard DUPIN
## @date 17-08-2012
## @project standard Build system
## @copyright BSDv3
###############################################################################

# Do NOT clear LOCAL_PATH, it is set BEFORE including this makefile

$(call clear-vars, $(filter-out LOCAL_PATH,$(modules-LOCALS:%=LOCAL_%)))

# Trim MAKEFILE_LIST so that $(call my-dir) doesn't need to
# iterate over thousands of entries every time.
# Leave the current makefile to make sure we don't break anything
# that expects to be able to find the name of the current makefile.
MAKEFILE_LIST := $(lastword $(MAKEFILE_LIST))
