#!/usr/bin/python
# -*- coding: utf-8 -*-
##
## @author Edouard DUPIN
##
## @copyright 2012, Edouard DUPIN, all right reserved
##
## @license APACHE v2.0 (see license file)
##

from lutin import debug
from lutin import system
from lutin import tools
from lutin import env
import os

class System(system.System):
	def __init__(self, target):
		system.System.__init__(self)
		# create some HELP:
		self.help = "CXX: Generic C++ library"
		self.valid = True
		if target.config["compilator"] == "clang":
			if target.board_id < 21:
				debug.error("Clang work only with the board wersion >= 21 : android 5.x.x")
				self.valid = False
				return
			self.add_export_flag("c++", "-D__STDCPP_LLVM__")
			# llvm is BSD-like licence
			self.add_export_path(os.path.join(target.path_ndk, "sources", "cxx-stl", "llvm-libc++", "libcxx", "include"))
			if target.type_arch == "armv5":
				stdCppBasePath = os.path.join(target.path_ndk, "sources", "cxx-stl", "llvm-libc++", "libcxx", "libs", "armeabi")
				self.add_export_path(        os.path.join(stdCppBasePath, "include"))
				self.add_export_flag("link", os.path.join(stdCppBasePath, "libc++_static.a"))
			elif target.type_arch == "armv7":
				stdCppBasePath = os.path.join(target.path_ndk, "sources", "cxx-stl", "llvm-libc++", "libs", "armeabi-v7a")
				self.add_export_path(        os.path.join(stdCppBasePath + "include"))
				self.add_export_flag("link", os.path.join(stdCppBasePath, "thumb", "libc++_static.a"))
			elif target.type_arch == "mips":
				stdCppBasePath = os.path.join(target.path_ndk, "sources", "cxx-stl", "llvm-libc++", "libcxx", "libs", "mips")
				self.add_export_path(        os.path.join(stdCppBasePath + "include"))
				self.add_export_flag("link", os.path.join(stdCppBasePath + "libc++_static.a"))
			elif target.type_arch == "x86":
				stdCppBasePath = os.path.join(target.path_ndk, "sources", "cxx-stl", "llvm-libc++", "libcxx", "libs", "x86")
				self.add_export_path(        os.path.join(stdCppBasePath, "include"))
				self.add_export_flag("link", os.path.join(stdCppBasePath, "libc++_static.a"))
			else:
				debug.warning("unknow architecture: '" + str(target.arch) + "'");
		else:
			self.add_export_flag("c++", "-D__STDCPP_GNU__")
			self.add_export_flag("c++-remove","-nostdlib")
			self.add_export_flag("need-libstdc++", True)
			# GPL v3 (+ exception link for gcc compilator)
			self.add_export_path(os.path.join(target.path_ndk, "sources", "cxx-stl", "gnu-libstdc++", target.compilator_version, "include"))
			if target.type_arch == "armv5":
				stdCppBasePath = os.path.join(target.path_ndk, "sources", "cxx-stl", "gnu-libstdc++", target.compilator_version, "libs", "armeabi")
				self.add_export_path(        os.path.join(stdCppBasePath, "include"))
				self.add_export_flag("link", os.path.join(stdCppBasePath, "thumb", "libgnustl_static.a"))
				self.add_export_flag("link", os.path.join(stdCppBasePath, "thumb", "libsupc++.a"))
			elif target.type_arch == "armv7":
				stdCppBasePath = os.path.join(target.path_ndk, "sources", "cxx-stl", "gnu-libstdc++", target.compilator_version, "libs", "armeabi-v7a")
				self.add_export_path(        os.path.join(stdCppBasePath, "include"))
				self.add_export_flag("link", os.path.join(stdCppBasePath, "thumb", "libgnustl_static.a"))
				self.add_export_flag("link", os.path.join(stdCppBasePath, "thumb", "libsupc++.a"))
			elif target.type_arch == "mips":
				stdCppBasePath = os.path.join(target.path_ndk, "sources", "cxx-stl", "gnu-libstdc++", target.compilator_version, "libs", "mips")
				self.add_export_path(        os.path.join(stdCppBasePath, "include/"))
				self.add_export_flag("link", os.path.join(stdCppBasePath, "libgnustl_static.a"))
				self.add_export_flag("link", os.path.join(stdCppBasePath, "libsupc++.a"))
			elif target.type_arch == "x86":
				stdCppBasePath = os.path.join(target.path_ndk, "sources", "cxx-stl", "gnu-libstdc++", target.compilator_version, "libs", "x86")
				self.add_export_path(        os.path.join(stdCppBasePath, "include"))
				self.add_export_flag("link", os.path.join(stdCppBasePath, "libgnustl_static.a"))
				self.add_export_flag("link", os.path.join(stdCppBasePath, "libsupc++.a"))
			else:
				debug.warning("unknow architecture: '" + str(target.arch) + "'");
			debug.warning("plop")