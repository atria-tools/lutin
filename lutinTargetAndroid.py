#!/usr/bin/python

import lutinDebug as debug
import lutinTarget
import lutinTools
import os

class Target(lutinTarget.Target):
	def __init__(self, typeCompilator, debugMode):
		
		self.folder_ndk = os.getenv('PROJECT_NDK', lutinTools.GetRunFolder() + "/../android/ndk/")
		self.folder_sdk = os.getenv('PROJECT_SDK', lutinTools.GetRunFolder() + "/../android/ndk/")
		arch = "ARMv7"
		cross = self.folder_ndk + "/toolchains/arm-linux-androideabi-4.4.3/prebuilt/linux-x86/bin/arm-linux-androideabi-"
		
		if typeCompilator!="gcc":
			debug.error("Android does not support '" + typeCompilator + "' compilator ... availlable : [gcc]")
		
		lutinTarget.Target.__init__(self, "Android", "gcc", debugMode, arch, cross)
		
		self.boardId = 14
		self.global_include_cc.append("-I" + self.folder_ndk +"/platforms/android-" + str(self.boardId) + "/arch-arm/usr/include")
		self.global_include_cc.append("-I" + self.folder_ndk +"/sources/cxx-stl/system/include/")
		
		self.global_sysroot = "--sysroot=" + self.folder_ndk +"/platforms/android-" + str(self.boardId) + "/arch-arm"
		
		self.global_flags_cc.append("-D__ARM_ARCH_5__")
		self.global_flags_cc.append("-D__ARM_ARCH_5T__")
		self.global_flags_cc.append("-D__ARM_ARCH_5E__")
		self.global_flags_cc.append("-D__ARM_ARCH_5TE__")
		if self.arch == "ARM":
			# -----------------------
			# -- arm V5 :
			# -----------------------
			self.global_flags_cc.append("-march=armv5te")
			self.global_flags_cc.append("-msoft-float")
		else:
			# -----------------------
			# -- arm V7 (Neon) :
			# -----------------------
			self.global_flags_cc.append("-mfpu=neon")
			self.global_flags_cc.append("-mfloat-abi=softfp")
			self.global_flags_ld.append("-mfpu=neon")
			self.global_flags_ld.append("-mfloat-abi=softfp")
			self.global_flags_cc.append("-D__ARM_ARCH_7__")
			self.global_flags_cc.append("-D__ARM_NEON__")
		
		# the -mthumb must be set for all the android produc, some ot the not work coretly without this one ... (all android code is generated with this flags)
		self.global_flags_cc.append("-mthumb")
		# -----------------------
		# -- Common flags :
		# -----------------------
		self.global_flags_cc.append("-fpic")
		self.global_flags_cc.append("-ffunction-sections")
		self.global_flags_cc.append("-funwind-tables")
		self.global_flags_cc.append("-fstack-protector")
		self.global_flags_cc.append("-Wno-psabi")
		self.global_flags_cc.append("-mtune=xscale")
		self.global_flags_cc.append("-fno-exceptions")
		self.global_flags_cc.append("-fomit-frame-pointer")
		self.global_flags_cc.append("-fno-strict-aliasing")
		
		self.global_flags_xx.append("-fno-rtti")
		self.global_flags_xx.append("-Wa,--noexecstack")
	
	
	def MakePackage(self, moduleName, pkgProperties):
		None # ...




