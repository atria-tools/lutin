#!/usr/bin/python
# -*- coding: utf-8 -*-
##
## @author Edouard DUPIN
##
## @copyright 2012, Edouard DUPIN, all right reserved
##
## @license MPL v2.0 (see license file)
##

import sys
import os
import inspect
import fnmatch
import datetime
# Local import
from . import debug
from . import heritage
from . import tools
from . import module
from . import system
from . import multiprocess
from . import env
##
## @brief Target class represent the buyild environement for a specific platform like Linux, or Android ....
##
class Target:
	##
	## @brief contructor
	## @param[in] name ([string,...]) Name of the target
	## @param[in] config (dict) User configuration
	## @param[in] arch (string) specific parameter for gcc -arch element
	##
	def __init__(self, name, config, arch):
		if tools.get_type_string(name) != "list":
			debug.error("You must define a name in a list ...")
		if len(name) < 1:
			debug.error("You must define a name for your target ...")
		## configuration of the build
		self.config = config
		
		if self.config["bus-size"] == "auto":
			debug.error("system error ==> must generate the default 'bus-size' config")
		if self.config["arch"] == "auto":
			debug.error("system error ==> must generate the default 'bus-size' config")
		
		#debug.debug("config=" + str(config))
		if arch != "":
			self.arch = "-arch " + arch
		else:
			self.arch = ""
		
		self.end_generate_package = config["generate-package"]
		# todo : remove this :
		self._name = name[-1]
		self._config_based_on = name
		debug.info("=================================");
		debug.info("== Target='" + self._name + "' " + self.config["bus-size"] + " bits for arch '" + self.config["arch"] + "'");
		debug.info("== Target list=" + str(self._config_based_on))
		debug.info("=================================");
		
		self.set_cross_base()
		
		###############################################################################
		# Target global variables.
		###############################################################################
		self.global_include_cc=[]
		self.global_flags={}
		
		self.global_libs_ld=[]
		self.global_libs_ld_shared=[]
		
		self.suffix_cmd_line='.cmd'
		self.suffix_warning='.warning'
		self.suffix_dependence='.d'
		self.suffix_obj='.o'
		self.prefix_lib='lib'
		self.suffix_lib_static='.a'
		self.suffix_lib_dynamic='.so'
		self.suffix_binary=''
		self.suffix_package='.deb'
		
		self.path_generate_code="/generate_header"
		self.path_arch = "/" + self._name
		
		for elem in self._config_based_on:
			self.add_flag("c", '-D__TARGET_OS__' + elem)
		self.add_flag("c", [
		    '-D__TARGET_ARCH__' + self.config["arch"],
		    '-D__TARGET_ADDR__' + self.config["bus-size"] + 'BITS',
		    '-D_REENTRANT'
		    ])
		if     self.config["compilator"] == "clang" \
		   and self.xx_version >= 4002001: # >= 4.2.1
			self.add_flag("c++", "-Wno-undefined-var-template")
		self.add_flag("c", "-nodefaultlibs")
		self.add_flag("c++", "-nostdlib")
		self.add_flag("ar", 'rcs')
		
		if self._name == "Windows":
			self.add_flag("c++", [
			    '-static-libgcc',
			    '-static-libstdc++'
			    ])
		if "debug" == self.config["mode"]:
			self.add_flag("c", [
			    "-g",
			    "-DDEBUG"
			    ])
			if env.get_force_optimisation() == False:
				self.add_flag("c", "-O0")
			else:
				self.add_flag("c", "-O3")
		else:
			self.add_flag("c", [
			    "-DNDEBUG",
			    "-O3"
			    ])
		
		## To add code coverate on build result system
		if self.config["gcov"] == True:
			if self.config["compilator"] == "clang":
				self.add_flag("c", [
				    "--coverage"
				    ])
				self.add_flag("link", [
				    "--coverage"
				    ])
			else:
				self.add_flag("c", [
				    "-fprofile-arcs",
				    "-ftest-coverage"
				    ])
				self.add_flag("link", [
				    "-lgcov",
				    "--coverage"
				    ])
		
		self._update_path_tree()
		self.path_bin="bin"
		self.path_lib="lib"
		self.path_data="share"
		self.path_doc="doc"
		self.path_include="include"
		self.path_temporary_generate="generate"
		self.path_object="obj"
		
		
		self.build_done=[]
		self.build_tree_done=[]
		self.module_list=[]
		# output staging files list :
		self.list_final_file=[]
		
		self.sysroot=""
		
		self.action_on_state={}
		
		# set some default package path
		self.pkg_path_version_file = "version.txt"
		self.pkg_path_maintainer_file = "maintainer.txt"
		self.pkg_path_application_name_file = "appl_name.txt"
		self.pkg_path_application_description_file = "appl_description.txt"
		self.pkg_path_readme_file = "readme.txt"
		self.pkg_path_change_log_file = "changelog.txt"
		
		# special case for IOS (example) no build dynamicly ...
		self.support_dynamic_link = True
	
	##
	## @brief Generate a string representing the class (for str(xxx))
	## @param[in] self (handle) Class handle
	## @return (string) string of str() convertion
	##
	def __repr__(self):
		return "{lutin.Target}"
	
	##
	## @brief Get the type of the target: ["Linux, ...]
	## @param[in] self (handle) Class handle
	## @return ([string,...]) The current target name and other sub name type (ubuntu ...)
	##
	def get_type(self):
		return self._config_based_on
	
	##
	## @brief Add a type that the model is based on
	## @param[in] self (handle) Class handle
	## @param[in] name (string) Name of that the element is based on ...
	##
	def add_type(self, name):
		self._config_based_on.append(name)
	
	##
	## @brief Get the name of the target: Linux, Windows, ...
	## @param[in] self (handle) Class handle
	## @return (string) Name of the target
	##
	def get_name(self):
		return self._name
	
	##
	## @brief Get build mode of the target: ["debug", "release"]
	## @param[in] self (handle) Class handle
	## @return (string) The current target build mode.
	##
	def get_mode(self):
		return self.config["mode"]
	
	##
	## @brief Get build for a simulator (Ios and Android for example)
	## @param[in] self (handle) Class handle
	## @return (bool) sumulation requested
	##
	def get_simulation(self):
		return self.config["simulation"]
	
	##
	## @brief Get compilator name (clang / gcc)
	## @param[in] self (handle) Class handle
	## @return (bool) name of the compilator requested
	##
	def get_compilator(self):
		return self.config["compilator"]
	
	##
	## @brief Get architecture name (x86 / arm / ...)
	## @param[in] self (handle) Class handle
	## @return (bool) name of the arch requested
	##
	def get_arch(self):
		return self.config["arch"]
	##
	## @brief Get architecture name (x86 / arm / ...)
	## @param[in] self (handle) Class handle
	## @return (bool) name of the arch requested
	##
	def get_bus_size(self):
		return self.config["bus-size"]
	
	##
	## @brief Add global target flags
	## @param[in] self (handle) Class handle
	## @param[in] type (string) inclusion group name 'c', 'c++', 'java' ...
	## @param[in] in_list ([string,...] or string) List of path to include
	## @return None
	##
	def add_flag(self, in_type, in_list):
		tools.list_append_to_2(self.global_flags, in_type, in_list)
	
	##
	## @brief Update basic tree path positions on the build tree
	## @param[in] self (handle) Class handle
	## @return None
	##
	def _update_path_tree(self):
		self.path_out = os.path.join("out", self._name + "_" + self.config["arch"] + "_" + self.config["bus-size"], self.config["mode"])
		self.path_final = os.path.join("final", self.config["compilator"])
		self.path_staging = os.path.join("staging", self.config["compilator"])
		self.path_staging_tmp = os.path.join("staging_tmp", self.config["compilator"])
		self.path_build = os.path.join("build", self.config["compilator"])
	
	# TODO: Remove this from here ==> this is a tools
	##
	## @brief create a string version number with the associated list values
	## @param[in] self (handle) Class handle
	## @param[in] data ([int|string,...]) version basic number
	## @return (string) version number
	##
	def create_number_from_version_string(self, data):
		tmp_data = data.split("-")
		if len(tmp_data) > 1:
			data = tmp_data[0]
		list = data.split(".")
		if len(list) == 1:
			list.append("0")
		if len(list) == 2:
			list.append("0")
		if len(list) > 3:
			list = list[:3]
		out = 0;
		offset = 1000**(len(list)-1)
		for elem in list:
			out += offset*int(elem)
			#debug.verbose("get : " + str(int(elem)) + " tmp" + str(out))
			offset /= 1000
		return out
	
	##
	## @brief Configure the cross toolchain
	## @param[in] self (handle) Class handle
	## @param[in] cross (string) Path of the cross toolchain
	## @return None
	##
	def set_cross_base(self, cross=""):
		self.cross = cross
		#debug.debug("== Target='" + self.cross + "'");
		self.java = "javac"
		self.javah = "javah"
		self.jar = "jar"
		self.ar = self.cross + "ar"
		self.ranlib = self.cross + "ranlib"
		if self.config["compilator"] == "clang":
			self.cc = self.cross + "clang"
			self.xx = self.cross + "clang++"
			#self.ar=self.cross + "llvm-ar"
			self.ranlib=""
		else:
			self.cc = self.cross + "gcc"
			self.xx = self.cross + "g++"
			#self.ar=self.cross + "ar"
			#self.ranlib=self.cross + "ranlib"
		if self.config["compilator-version"] != "":
			self.cc = self.cc + "-" + self.config["compilator-version"]
			self.xx = self.xx + "-" + self.config["compilator-version"]
		
		#get g++ compilation version :
		ret = multiprocess.run_command_direct(self.xx + " -dumpversion");
		if ret == False:
			debug.error("Can not get the g++/clang++ version ...")
		self.xx_version = self.create_number_from_version_string(ret)
		#debug.debug(self.config["compilator"] + "++ version=" + str(ret) + " number=" + str(self.xx_version))
		
		self.ld = self.cross + "ld"
		self.nm = self.cross + "nm"
		self.strip = self.cross + "strip"
		self.dlltool = self.cross + "dlltool"
		self._update_path_tree()
		
		#some static libraries that is sometime needed when not use stdlib ...
		ret = multiprocess.run_command_direct(self.xx + " -print-file-name=libgcc.a");
		if ret == False:
			debug.error("Can not get the g++/clang++ libgcc.a ...")
		self.stdlib_name_libgcc = ret;
		ret = multiprocess.run_command_direct(self.xx + " -print-file-name=libsupc++.a");
		if ret == False:
			debug.error("Can not get the g++/clang++ libsupc++.a ...")
		self.stdlib_name_libsupc = ret;
	
	##
	## @brief Get the current build mode
	## @param[in] self (handle) Class handle
	## @return Build mode value [debug,release]
	##
	def get_build_mode(self):
		return self.config["mode"]
	
	def get_full_name_source(self, basePath, file):
		if file[0] == '/':
			if tools.os.path.isfile(file):
				return file
		return basePath + "/" + file
	
	def get_full_name_cmd(self, module_name, basePath, file):
		if file[0] == '/':
			if tools.os.path.isfile(file):
				return file + self.suffix_cmd_line
		return self.get_build_path_object(module_name) + "/" + file + self.suffix_cmd_line
	
	def get_full_name_warning(self, module_name, basePath, file):
		return self.get_build_path_object(module_name) + "/" + file + self.suffix_warning;
	
	def get_full_name_destination(self, module_name, basePath, file, suffix, remove_suffix=False):
		# special patch for java file:
		if file[-4:] == "java":
			for elem in ["org/", "com/"]:
				pos = file.find(elem);
				if pos > 0:
					file = file[pos:]
		if remove_suffix == True:
			file = file[:file.rfind(".")] + '.'
		else:
			file += "."
		if len(suffix) >= 1:
			suffix = suffix[0]
		else:
			suffix = ""
		return self.get_build_path_object(module_name) + "/" + file + suffix
	
	def get_full_dependency(self, module_name, basePath, file):
		return self.get_build_path_object(module_name) + "/" + file + self.suffix_dependence
	
	##
	## @brief Get the final path ==> contain all the generated packages
	## @param[in] self (handle) Class handle
	## @return (string) The path
	##
	def get_final_path(self):
		return os.path.join(tools.get_run_path(), self.path_out, self.path_final)
	
	##
	## @brief Get the staging path ==> all install stangalone package (no dependency file, no object files, no cmdlines files
	## @param[in] self (handle) Class handle
	## @param[in] name (string) Name of the module
	## @return (string) The path
	##
	def get_staging_path(self, name, tmp=False):
		if tmp == False:
			return os.path.join(tools.get_run_path(), self.path_out, self.path_staging, name)
		else:
			return os.path.join(tools.get_run_path(), self.path_out, self.path_staging_tmp, name)
	
	##
	## @brief Get the build path ==> dependency file, object files, cmdlines files, generate files, local install headers ...
	## @param[in] self (handle) Class handle
	## @param[in] name (string) Name of the module
	## @return (string) The path
	##
	def get_build_path(self, name):
		return os.path.join(tools.get_run_path(), self.path_out, self.path_build, name)
	
	##
	## @brief Get the build object path where write .o files
	## @param[in] self (handle) Class handle
	## @param[in] name (string) Name of the module
	## @return (string) The path
	##
	def get_build_path_object(self, name):
		return os.path.join(self.get_build_path(name), self.path_object)
	
	##
	## @brief Get the build binary path where write .bin, .exe ... files
	## @param[in] self (handle) Class handle
	## @param[in] name (string) Name of the module
	## @return (string) The path
	##
	def get_build_path_bin(self, name):
		return os.path.join(self.get_build_path(name), self.path_bin)
	
	##
	## @brief Get the shared/static library object path where write .a / .so files
	## @param[in] self (handle) Class handle
	## @param[in] name (string) Name of the module
	## @return (string) The path
	##
	def get_build_path_lib(self, name):
		return os.path.join(self.get_build_path(name), self.path_lib)
	
	##
	## @brief Get the data path where pre-write the install "data" files
	## @param[in] self (handle) Class handle
	## @param[in] name (string) Name of the module
	## @return (string) The path
	##
	def get_build_path_data(self, name):
		return os.path.join(self.get_build_path(name), self.path_data, name)
	
	##
	## @brief Get the include path where pre-install "include" headers files
	## @param[in] self (handle) Class handle
	## @param[in] name (string) Name of the module
	## @return (string) The path
	##
	def get_build_path_include(self, name):
		return os.path.join(self.get_build_path(name), self.path_include)
	
	##
	## @brief Get the path where to generate files when needed (before compiling / installing it)
	## @param[in] self (handle) Class handle
	## @param[in] name (string) Name of the module
	## @return (string) The path
	##
	def get_build_path_temporary_generate(self, name):
		return os.path.join(self.get_build_path(name), self.path_temporary_generate)
	
	##
	## @brief Get the path filename of the build binary name
	## @param[in] self (handle) Class handle
	## @param[in] name (string) Name of the module
	## @return (string) The path
	##
	def get_build_file_bin(self, name, static):
		if static == True:
			return os.path.join(self.get_build_path_bin(name), name + "_static" + self.suffix_binary)
		return os.path.join(self.get_build_path_bin(name), name + "_dynamic" + self.suffix_binary)
	
	##
	## @brief Get the path filename of the build static library name
	## @param[in] self (handle) Class handle
	## @param[in] name (string) Name of the module
	## @return (string) The path
	##
	def get_build_file_static(self, name):
		return os.path.join(self.get_build_path_lib(name), self.prefix_lib + name + self.suffix_lib_static)
	
	##
	## @brief Get the path filename of the build shared library name
	## @param[in] self (handle) Class handle
	## @param[in] name (string) Name of the module
	## @return (string) The path
	##
	def get_build_file_dynamic(self, name):
		return os.path.join(self.get_build_path_lib(name), self.prefix_lib + name + self.suffix_lib_dynamic)
	
	
	##
	## @brief Get the bin path for staging step
	## @param[in] self (handle) Class handle
	## @param[in] name (string) Name of the package
	## @return (string) The path
	##
	def get_staging_path_bin(self, name, tmp=False):
		return os.path.join(self.get_staging_path(name, tmp), self.path_bin)
	
	##
	## @brief Get the lib path for staging step
	## @param[in] self (handle) Class handle
	## @param[in] name (string) Name of the package
	## @return (string) The path
	##
	def get_staging_path_lib(self, name, tmp=False):
		return os.path.join(self.get_staging_path(name, tmp), self.path_lib, name)
	
	##
	## @brief Get the data path for staging step
	## @param[in] self (handle) Class handle
	## @param[in] name (string) Name of the package
	## @return (string) The path
	##
	def get_staging_path_data(self, name, tmp=False):
		return os.path.join(self.get_staging_path(name, tmp), self.path_data, name)
	
	##
	## @brief Get the include path for staging step
	## @param[in] self (handle) Class handle
	## @param[in] name (string) Name of the package
	## @return (string) The path
	##
	def get_staging_path_include(self, name):
		return os.path.join(self.get_staging_path(name), self.path_include)
	
	def get_doc_path(self, module_name):
		return os.path.join(tools.get_run_path(), self.path_out, self.path_doc, module_name)
	
	def is_module_build(self, my_module):
		for mod in self.build_done:
			if mod == my_module:
				return True
		self.build_done.append(my_module)
		return False
	
	def is_module_build_tree(self, my_module):
		for mod in self.build_tree_done:
			if mod == my_module:
				return True
		self.build_tree_done.append(my_module)
		return False
	
	##
	## @brief Add new loaded module
	## @param[in] self (handle) Class handle
	## @param[in] new_module (handle) pointer on the module instance
	## @return None
	##
	def add_module(self, new_module):
		#debug.debug("Add nodule for Taget : " + new_module.get_name())
		self.module_list.append(new_module)
	
	##
	## @brief Get a module handle that is used in this target
	## @param[in] self (handle) Class handle
	## @param[in] name (string) Name of the module
	## @return (handle|None) @ref lutin.module.Module pointer on the module requested or None
	##
	def get_module(self, name):
		for mod in self.module_list:
			if mod.get_name() == name:
				return mod
		debug.error("the module '" + str(name) + "'does not exist/already build")
		return None
	
	##
	## @brief Build data associated at the module name in a specific package
	## @param[in] self (handle) Class handle
	## @param[in] name (string) Name of the module
	## @param[in] package_name (string) Name of the package
	## @return None
	##
	def build_tree(self, name, package_name):
		for mod in self.module_list:
			if mod.get_name() == name:
				mod.build_tree(self, package_name)
				return
		debug.error("request to build tree on un-existant module name : '" + name + "'")
	
	##
	## @brief Clean a specific module for this target (clean all data in the "out" path)
	## @param[in] self (handle) Class handle
	## @param[in] name (string) Name of the module
	## @return None
	##
	def clean(self, name):
		for mod in self.module_list:
			if mod.get_name() == name:
				mod.clean(self)
				return
		debug.error("request to clean an un-existant module name : '" + name + "'")
	
	##
	## @brief Load a specific module if it accessible
	## @param[in] self (handle) Class handle
	## @param[in] name (string) Name of the module to load
	## @param[in] optionnal (bool) not create an error if the module does not exist.
	## @return (bool) module loading status
	##
	def load_if_needed(self, name, optionnal=False):
		for elem in self.module_list:
			if elem.get_name() == name:
				return True
		# try to find in the local Modules:
		exist = module.exist(self, name)
		if exist == True:
			module.load_module(self, name)
			return True;
		# need to import the module (or the system module ...)
		exist = system.exist(name, self._config_based_on, self)
		if exist == True:
			system.load(self, name, self._config_based_on)
			return True;
		# we did not find the module ...
		return False;
	
	##
	## @brief Load all module that are accessible in the worktree
	## @param[in] self (handle) Class handle
	## @return None
	##
	def load_all(self):
		listOfAllTheModule = module.list_all_module()
		for modName in listOfAllTheModule:
			self.load_if_needed(modName)
	
	##
	## @brief Build action on the target (execute specific actions on the modules...)
	## @note Recursive call ...
	## @param[in] self (handle) Class handle
	## @param[in] name (string) Module to build
	## @param[in] optionnal (bool) If the module is not accessible, this is not a probleme ==> optionnal dependency requested
	## @param[in] actions ([string,...]) list of action to do. ex: build, gcov, dump, all, clean, install, uninstall, run, log
	## @param[in] package_name Current package name that request the build
	## @return (None|Module handle| ...) complicated return ...
	##
	def build(self, name, optionnal=False, actions=[], package_name=None):
		if    len(name.split("?")) != 1\
		   or len(name.split("@")) != 1:
			debug.error("need update")
		if actions == "":
			actions = ["build"]
		if actions == []:
			actions = ["build"]
		if type(actions) == str:
			actions = [actions]
		if name == "gcov":
			debug.info("gcov all")
			debug.error("must set the gcov parsing on a specific library or binary ==> not supported now for all")
		if name == "dump":
			debug.info("dump all")
			self.load_all()
			for mod in self.module_list:
				mod.display()
			return
		if name[:10] == "dependency":
			if len(name) > 10:
				rules = name.split(":")[1]
			else:
				rules = "LBDPK"
				# L for library
				# B for binary
				# D for Data
				# P for prebuild
				# K for package
			debug.print_element("dot", "", "---", "dependency.dot")
			self.load_all()
			tmp_file = open("dependency.dot", 'w')
			tmp_file.write('digraph G {\n')
			tmp_file.write('	rankdir=\"LR\";\n')
			for mod in self.module_list:
				mod.dependency_generate(self, tmp_file, 1, rules)
			# TODO : do it better ==> system library hook (do a oad of all avillable system library)
			tmp_file.write('	node [\n');
			tmp_file.write('		shape=square;\n');
			tmp_file.write('		style=filled;\n');
			tmp_file.write('		color=gray;\n');
			tmp_file.write('		];\n');
			# TODO : End hook
			for mod in self.module_list:
				mod.dependency_generate(self, tmp_file, 2, rules)
			tmp_file.write('}\n')
			tmp_file.flush()
			tmp_file.close()
			debug.print_element("dot", "", "---", "dependency.dot")
			return
		if name == "all":
			debug.info("build all")
			self.load_all()
			for mod in self.module_list:
				if self._name == "Android":
					if mod.get_type() == "PACKAGE":
						mod.build(self, package_name)
				else:
					if    mod.get_type() == "BINARY" \
					   or mod.get_type() == "PACKAGE":
						mod.build(self, package_name)
		elif name == "clean":
			debug.info("clean all")
			self.load_all()
			for mod in self.module_list:
				mod.clean(self)
		else:
			module_name = name
			action_list = actions
			for action_name in action_list:
				#debug.verbose("requested : " + module_name + "?" + action_name + " [START]")
				ret = None;
				if action_name == "install":
					try:
						self.install_package(module_name)
					except AttributeError:
						debug.error("target have no 'install_package' instruction")
				elif action_name == "uninstall":
					try:
						self.un_install_package(module_name)
					except AttributeError:
						debug.error("target have no 'un_install_package' instruction")
				elif action_name[:3] == "run":
					bin_name = None
					if len(action_name) > 3:
						if action_name[3] == '%':
							bin_name = ""
							for elem in action_name[4:]:
								if elem == ":":
									break;
								bin_name += elem
						# we have option:
						action_name2 = action_name.replace("\:", "1234COLUMN4321")
						option_list = action_name2.split(":")
						if len(option_list) == 0:
							if bin_name != None:
								debug.warning("action 'run' wrong options options ... : '" + action_name + "' might be separate with ':'")
							option_list = []
						else:
							option_list_tmp = option_list[1:]
							option_list = []
							for elem in option_list_tmp:
								option_list.append(elem.replace("1234COLUMN4321", ":"))
					else:
						option_list = []
					#try:
					self.run(module_name, option_list, bin_name)
					#except AttributeError:
					#	debug.error("target have no 'run' instruction")
				elif action_name == "log":
					try:
						self.show_log(module_name)
					except AttributeError:
						debug.error("target have no 'show_log' instruction")
				else:
					present = self.load_if_needed(module_name, optionnal=optionnal)
					if     present == False \
					   and optionnal == True:
						ret = [heritage.HeritageList(), False]
					else:
						for mod in self.module_list:
							#debug.verbose("compare " + mod.get_name() + " == " + module_name)
							if mod.get_name() == module_name:
								if action_name[:4] == "dump":
									debug.info("dump module '" + module_name + "'")
									if len(action_name) > 4:
										debug.warning("action 'dump' does not support options ... : '" + action_name + "'")
									ret = mod.display()
									break
								elif action_name[:5] == "clean":
									debug.info("clean module '" + module_name + "'")
									if len(action_name) > 5:
										debug.warning("action 'clean' does not support options ... : '" + action_name + "'")
									ret = mod.clean(self)
									break
								elif action_name[:4] == "gcov":
									#debug.debug("gcov on module '" + module_name + "'")
									if len(action_name) > 4:
										# we have option:
										option_list = action_name.split(":")
										if len(option_list) == 0:
											debug.warning("action 'gcov' wrong options options ... : '" + action_name + "' might be separate with ':'")
											option_list = []
										else:
											option_list = option_list[1:]
									else:
										option_list = []
									if "output" in option_list:
										ret = mod.gcov(self, generate_output=True)
									else:
										ret = mod.gcov(self, generate_output=False)
									break
								elif action_name[:5] == "build":
									if len(action_name) > 5:
										debug.warning("action 'build' does not support options ... : '" + action_name + "'")
									#debug.debug("build module '" + module_name + "'")
									if optionnal == True:
										ret = [mod.build(self, package_name), True]
									else:
										ret = mod.build(self, package_name)
									break
						if     optionnal == True \
						   and ret == None:
							ret = [heritage.HeritageList(), False]
							break
						if ret == None:
							debug.error("not know module name : '" + module_name + "' to '" + action_name + "' it")
				#debug.verbose("requested : " + module_name + "?" + action_name + " [STOP]")
			if len(action_list) == 1:
				return ret
	
	##
	## @brief Add action to do for package specific part when build upper element
	## @param[in] name_of_state (string) a state to call action
	##     - BINARY
	##     - BINARY_SHARED
	##     - BINARY_STAND_ALONE
	##     - LIBRARY
	##     - LIBRARY_DYNAMIC
	##     - LIBRARY_STATIC
	##     - PACKAGE
	##     - PREBUILD
	##     - DATA
	## @param[in] level (int) Value order to apply action
	## @param[in] name (string) Name of the action
	## @param[in] action (function handle) Function to call to execure action
	## @return None
	##
	def add_action(self, name_of_state="PACKAGE", level=5, name="no-name", action=None):
		#debug.verbose("add action : " + name)
		if name_of_state not in self.action_on_state:
			self.action_on_state[name_of_state] = [[level, name, action]]
		else:
			self.action_on_state[name_of_state].append([level, name, action])
	
	##
	## @brief Create a package/bundle for the platform.
	## @param[in] pkg_name Package Name (generic name)
	## @param[in] pkg_properties Property of the package
	## @param[in] base_pkg_path Base path of the package
	## @param[in] heritage_list List of dependency of the package
	## @param[in] static The package is build in static mode
	##
	def make_package(self, pkg_name, pkg_properties, base_pkg_path, heritage_list):
		#debug.debug("make_package [START]")
		#The package generated depend of the type of the element:
		end_point_module_name = heritage_list.list_heritage[-1].name
		module = self.get_module(end_point_module_name)
		if module == None:
			debug.error("can not create package ... ");
		if module.get_type() == 'PREBUILD':
			#nothing to do ...
			return
		elif    module.get_type() == 'LIBRARY' \
		     or module.get_type() == 'LIBRARY_DYNAMIC' \
		     or module.get_type() == 'LIBRARY_STATIC':
			debug.info("Can not create package for library");
			return
		elif    module.get_type() == 'BINARY' \
		     or module.get_type() == 'BINARY_STAND_ALONE':
			self.make_package_binary(pkg_name, pkg_properties, base_pkg_path, heritage_list, static = True)
		elif module.get_type() == 'BINARY_SHARED':
			self.make_package_binary(pkg_name, pkg_properties, base_pkg_path, heritage_list, static = False)
		elif module.get_type() == 'PACKAGE':
			self.make_package_binary(pkg_name, pkg_properties, base_pkg_path, heritage_list, static = False)
		#debug.debug("make_package [STOP]")
		return
	
	##
	## @brief Create a generic tree of the shared data for each platform
	## @param[in] path_package Path of the basic install folder of the application
	## @param[in] pkg_name Package Name (generic name)
	## @param[in] heritage_list List of dependency of the package
	## @param[in] static The package is build in static mode
	## @return True Something has been copied
	## @return False Nothing has been copied
	##
	def make_package_binary_data(self, path_package, pkg_name, base_pkg_path, heritage_list, static):
		#debug.debug("make_package_binary_data [START]")
		target_shared_path = os.path.join(path_package, self.pkg_path_data)
		if static == True:
			path_package_data = os.path.join(target_shared_path, pkg_name)
		else:
			path_package_data = target_shared_path
		tools.create_directory_of_file(path_package_data)
		# prepare list of copy files
		copy_list={}
		#debug.debug("heritage for " + str(pkg_name) + ":")
		for heritage in heritage_list.list_heritage:
			#debug.debug("sub elements: " + str(heritage.name))
			path_src = self.get_build_path_data(heritage.name)
			#debug.verbose("      has directory: " + path_src)
			if os.path.isdir(path_src):
				if static == True:
					#debug.debug("      need copy: " + path_src + " to " + path_package_data)
					#copy all data:
					tools.copy_anything(path_src,
					                    path_package_data,
					                    recursive=True,
					                    force_identical=True,
					                    in_list=copy_list)
				else:
					#debug.debug("      need copy: " + os.path.dirname(path_src) + " to " + path_package_data)
					#copy all data:
					tools.copy_anything(os.path.dirname(path_src),
					                    path_package_data,
					                    recursive=True,
					                    force_identical=True,
					                    in_list=copy_list)
		#real copy files
		ret_copy = tools.copy_list(copy_list)
		# remove unneded files (NOT folder ...)
		ret_remove = tools.clean_directory(target_shared_path, copy_list)
		#debug.debug("make_package_binary_data [STOP]")
		return ret_copy or ret_remove
	
	##
	## @brief Create a generic tree of the binary folder
	## @param[in] path_package Path of the basic install folder of the application
	## @param[in] pkg_name Package Name (generic name)
	## @param[in] heritage_list List of dependency of the package
	## @param[in] static The package is build in static mode
	## @return True Something has been copied
	## @return False Nothing has been copied
	##
	def make_package_binary_bin(self, path_package, pkg_name, base_pkg_path, heritage_list, static):
		#debug.debug("make_package_binary_bin [START]")
		copy_list={}
		# creata basic output path
		path_package_bin = os.path.join(path_package, self.pkg_path_bin)
		tools.create_directory_of_file(path_package_bin)
		# Local module binary
		path_src = self.get_build_file_bin(pkg_name, static)
		if os.path.exists(path_src) == True:
			try:
				path_dst = os.path.join(path_package_bin, pkg_name + self.suffix_binary)
				#debug.verbose("path_dst: " + str(path_dst))
				tools.copy_file(path_src,
				                path_dst,
				                in_list=copy_list)
			except:
				#debug.extreme_verbose("can not find : " + path_src)
				pass
		path_src = self.get_build_file_bin(pkg_name, static)
		path_src = path_src[:len(path_src)-4] + "js"
		if os.path.exists(path_src) == True:
			try:
				path_dst = os.path.join(path_package_bin, pkg_name + self.suffix_binary2)
				#debug.verbose("path_dst: " + str(path_dst))
				tools.copy_file(path_src,
				                path_dst,
				                in_list=copy_list)
			except:
				#debug.extreme_verbose("can not find : " + path_src)
				pass
		# heritage binary
		#debug.debug("heritage for " + str(pkg_name) + ":")
		for heritage in heritage_list.list_heritage:
			#debug.debug("sub elements: " + str(heritage.name))
			path_src = self.get_build_file_bin(heritage.name, static)
			if os.path.exists(path_src) == True:
				try:
					path_dst = os.path.join(path_package_bin, heritage.name + self.suffix_binary)
					#debug.verbose("path_dst: " + str(path_dst))
					tools.copy_file(path_src,
					                path_dst,
					                in_list=copy_list)
				except:
					#debug.extreme_verbose("can not find : " + path_src)
					pass
			path_src = self.get_build_file_bin(heritage.name, static)
			path_src = path_src[:len(path_src)-4] + "js"
			if os.path.exists(path_src) == True:
				try:
					path_dst = os.path.join(path_package_bin, heritage.name + self.suffix_binary2)
					#debug.verbose("path_dst: " + str(path_dst))
					tools.copy_file(path_src,
					                path_dst,
					                in_list=copy_list)
				except:
					#debug.extreme_verbose("can not find : " + path_src)
					pass
		#real copy files
		ret_copy = tools.copy_list(copy_list)
		ret_remove = False
		if self.pkg_path_bin != "":
			# remove unneded files (NOT folder ...)
			ret_remove = tools.clean_directory(path_package_bin, copy_list)
		#debug.debug("make_package_binary_bin [STOP]")
		return ret_copy or ret_remove
	
	##
	## @brief Create a generic tree of the library folder
	## @param[in] path_package Path of the basic install folder of the application
	## @param[in] pkg_name Package Name (generic name)
	## @param[in] heritage_list List of dependency of the package
	## @param[in] static The package is build in static mode
	## @return True Something has been copied
	## @return False Nothing has been copied
	##
	def make_package_binary_lib(self, path_package, pkg_name, base_pkg_path, heritage_list, static):
		#debug.debug("make_package_binary_lib [START]")
		copy_list={}
		path_package_lib = os.path.join(path_package, self.pkg_path_lib)
		if static == False:
			#copy all shred libs...
			tools.create_directory_of_file(path_package_lib)
			#debug.verbose("libs for " + str(pkg_name) + ":")
			for heritage in heritage_list.list_heritage:
				#debug.debug("sub elements: " + str(heritage.name))
				file_src = self.get_build_file_dynamic(heritage.name)
				#debug.verbose("      has directory: " + file_src)
				if os.path.isfile(file_src):
					#debug.debug("      need copy: " + file_src + " to " + path_package_lib)
					#copy all data:
					# TODO : We can have a problem when writing over library files ...
					tools.copy_file(file_src,
					                os.path.join(path_package_lib, os.path.basename(file_src)),
					                in_list=copy_list)
		#real copy files
		ret_copy = tools.copy_list(copy_list)
		ret_remove = False
		if self.pkg_path_lib != "":
			# remove unneded files (NOT folder ...)
			ret_remove = tools.clean_directory(path_package_lib, copy_list)
		#debug.debug("make_package_binary_lib [STOP]")
		return ret_copy or ret_remove
	
	
	def make_package_generic_files(self, path_package, pkg_properties, pkg_name, base_pkg_path, heritage_list, static):
		#debug.debug("make_package_generic_files [START]")
		## Create version file:
		ret_version = tools.file_write_data(os.path.join(path_package, self.pkg_path_version_file),
		                                    tools.version_to_string(pkg_properties["VERSION"]),
		                                    only_if_new=True)
		
		## Create maintainer file:
		ret_maintainer = tools.file_write_data(os.path.join(path_package, self.pkg_path_maintainer_file),
		                                       self.generate_list_separate_coma(pkg_properties["MAINTAINER"]),
		                                       only_if_new=True)
		
		## Create appl_name file:
		ret_appl_name = tools.file_write_data(os.path.join(path_package, self.pkg_path_application_name_file),
		                                      "en_EN:" + pkg_properties["NAME"],
		                                      only_if_new=True)
		
		## Create appl_description file:
		ret_appl_desc = tools.file_write_data(os.path.join(path_package, self.pkg_path_application_description_file),
		                                      "en_EN:" + pkg_properties["DESCRIPTION"],
		                                      only_if_new=True)
		
		## Create Readme file:
		readme_file_dest = os.path.join(path_package, self.pkg_path_readme_file)
		ret_readme = False
		if os.path.exists(os.path.join(base_pkg_path, "os-Linux/README"))==True:
			ret_readme = tools.copy_file(os.path.join(base_pkg_path, "os-Linux/README"), readme_file_dest)
		elif os.path.exists(os.path.join(base_pkg_path, "README"))==True:
			ret_readme = tools.copy_file(os.path.join(base_pkg_path, "README"), readme_file_dest)
		elif os.path.exists(os.path.join(base_pkg_path, "README.md"))==True:
			ret_readme = tools.copy_file(os.path.join(base_pkg_path, "README.md"), readme_file_dest)
		else:
			#debug.debug("no file 'README', 'README.md' or 'os-Linux/README' ==> generate an empty one")
			ret_readme = tools.file_write_data(readme_file_dest,
			                                   "No documentation for " + pkg_name + "\n",
			                                   only_if_new=True)
		
		## Create licence file:
		"""
		# TODO ...
		license_file_dest = os.path.join(path_package, self.pkg_path_license, pkg_name + ".txt")
		tools.create_directory_of_file(license_file_dest)
		if os.path.exists(base_pkg_path + "/license.txt")==True:
			tools.copy_file(base_pkg_path + "/license.txt", license_file_dest)
		else:
			debug.info("no file 'license.txt' ==> generate an empty one")
			tmpFile = open(license_file_dest, 'w')
			tools.file_write_data(license_file_dest,
			                      "No license define by the developper for " + pkg_name + "\n",
			                      only_if_new=True)
		"""
		
		## Create changeLog file:
		change_log_file_dest = os.path.join(path_package, self.pkg_path_change_log_file)
		ret_changelog = False
		if os.path.exists(os.path.join(base_pkg_path, "changelog")) == True:
			ret_changelog = tools.copy_file(os.path.join(base_pkg_path, "changelog"), change_log_file_dest)
		else:
			#debug.debug("no file 'changelog' ==> generate an empty one")
			ret_changelog = tools.file_write_data(change_log_file_dest,
			                                      "No changelog data " + pkg_name + "\n",
			                                      only_if_new=True)
		#debug.debug("make_package_generic_files [STOP]")
		return    ret_version \
		       or ret_maintainer \
		       or ret_appl_name \
		       or ret_appl_desc \
		       or ret_readme \
		       or ret_changelog
	
	def install_package(self, pkg_name):
		#debug.debug("------------------------------------------------------------------------")
		debug.info("-- Install package '" + pkg_name + "'")
		#debug.debug("------------------------------------------------------------------------")
		debug.error("action not implemented ...")
	
	def un_install_package(self, pkg_name):
		#debug.debug("------------------------------------------------------------------------")
		debug.info("-- Un-Install package '" + pkg_name + "'")
		#debug.debug("------------------------------------------------------------------------")
		debug.error("action not implemented ...")
	
	def run(self, pkg_name, option_list, binary_name = None):
		#debug.debug("------------------------------------------------------------------------")
		debug.info("-- Run package '" + pkg_name + "' + option: " + str(option_list))
		#debug.debug("------------------------------------------------------------------------")
		debug.error("action not implemented ...")
	
	def show_log(self, pkg_name):
		#debug.debug("------------------------------------------------------------------------")
		debug.info("-- Show log logcat '" + pkg_name + "'")
		#debug.debug("------------------------------------------------------------------------")
		debug.error("action not implemented ...")
	
	##
	## @brief convert a s list of string in a string separated by a ","
	## @param[in] list List of element to transform
	## @return The requested string
	##
	def generate_list_separate_coma(self, list):
		result = ""
		fistTime = True
		for elem in list:
			if fistTime == True:
				fistTime = False
			else:
				result += ","
			result += elem
		return result


__target_list=[]
__start_target_name="Target_"

##
## @brief Import all File that start with env.get_build_system_base_name() + __start_target_name + XXX and register in the list of Target
## @param[in] path_list ([string,...]) List of file that start with env.get_build_system_base_name() in the running worktree (Parse one time ==> faster)
##
def import_path(path_list):
	global __target_list
	global_base = env.get_build_system_base_name()
	#debug.debug("TARGET: Init with Files list:")
	for elem in path_list:
		sys.path.append(os.path.dirname(elem))
		# Get file name:
		filename = os.path.basename(elem)
		# Remove .py at the end:
		filename = filename[:-3]
		# Remove global base name:
		filename = filename[len(global_base):]
		# Check if it start with the local patern:
		if filename[:len(__start_target_name)] != __start_target_name:
			#debug.extreme_verbose("TARGET:     NOT-Integrate: '" + filename + "' from '" + elem + "' ==> rejected")
			continue
		# Remove local patern
		target_name = filename[len(__start_target_name):]
		#debug.verbose("TARGET:     Integrate: '" + target_name + "' from '" + elem + "'")
		__target_list.append([target_name, elem])
	#debug.verbose("New list TARGET: ")
	for elem in __target_list:
		#debug.verbose("    " + str(elem[0]))
		pass

##
## @brief Load a specific target
##
def load_target(name, config):
	global __target_list
	#debug.debug("load target: " + name)
	if len(__target_list) == 0:
		debug.error("No target to compile !!!")
	#debug.debug("list target: " + str(__target_list))
	for mod in __target_list:
		if mod[0] == name:
			#debug.verbose("add to path: '" + os.path.dirname(mod[1]) + "'")
			sys.path.append(os.path.dirname(mod[1]))
			#debug.verbose("import target : '" + env.get_build_system_base_name() + __start_target_name + name + "'")
			theTarget = __import__(env.get_build_system_base_name() + __start_target_name + name)
			#create the target
			tmpTarget = theTarget.Target(config)
			return tmpTarget
	raise KeyError("No entry for : " + name)

def list_all_target():
	global __target_list
	tmpListName = []
	for mod in __target_list:
		tmpListName.append(mod[0])
	return tmpListName

def list_all_target_with_desc():
	global __target_list
	tmpList = []
	for mod in __target_list:
		sys.path.append(os.path.dirname(mod[1]))
		theTarget = __import__(env.get_build_system_base_name() + __start_target_name + mod[0])
		try:
			tmpdesc = theTarget.get_desc()
			tmpList.append([mod[0], tmpdesc])
		except:
			debug.warning("has no name : " + mod[0])
			tmpList.append([mod[0], ""])
	return tmpList
