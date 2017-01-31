#!/usr/bin/python
# -*- coding: utf-8 -*-
##
## @author Edouard DUPIN
##
## @copyright 2012, Edouard DUPIN, all right reserved
##
## @license MPL v2.0 (see license file)
##

from lutin import debug
from lutin import target
from lutin import tools
from lutin import env
import os
import stat
import re
from lutin import host
from lutin import depend
from lutin import zip
from lutin import multiprocess
import lutinTarget_Linux


class Target(lutinTarget_Linux.Target):
	def __init__(self, config, sub_name=[]):
		lutinTarget_Linux.Target.__init__(self, config, ["Web"] + sub_name)
		
		self.cross ="./emsdk_portable/emscripten/master/em"
		#debug.debug("== Target='em'");
		self.java = "javac"
		self.javah = "javah"
		self.jar = "jar"
		self.ar = self.cross + "ar"
		self.ranlib = self.cross + "ranlib"
		self.cc = self.cross + "cc"
		self.xx = self.cross + "++"
		self.ar = self.cross + "ar"
		
		self.xx_version = [0,0,0]
		self.ld = self.cross + "ld"
		self.nm = self.cross + "nm"
		self.strip = ""#self.cross + "strip"
		self.dlltool = self.cross + "dlltool"
		self._update_path_tree()
		
		self.stdlib_name_libgcc = ""
		self.stdlib_name_libsupc = "";
		self.suffix_binary = '.html'
		self.suffix_binary2 = '.js'
		
		self.pkg_path_bin = ""
		
		# Disable capabiliteis to compile in shared mode
		self.support_dynamic_link = False
		# create temporary file:
		self._file_data_tmp = "tmp_file_data.zip"
		tools.file_write_data(os.path.join(self.get_build_path_temporary_generate(""), self._file_data_tmp), "coucou", only_if_new=True)
		# add default file (need to generate a empty file to add it before loading:
		self.add_flag("link", [
		    "--preload-file " + os.path.join(self.get_build_path_temporary_generate(""), self._file_data_tmp) + "@tmp_file_data.zip",
		    #" -s FULL_ES2=1 "
		    ])
		# in the output.js this generate a section '{"audio": 0, "start": 0, "crunched": 0, "end": 6, "filename": "tmp_file_data.zip"}], "remote_package_size": 6' ==> that will be replaced by the corretc data in the file 'module.data'
	
	"""
	.local/application
	    *--> applName -> applName.app/bin/applName
	    *--> applName.app
	        *--> appl_description.txt
	        *--> appl_name.txt
	        *--> changelog.txt
	        *--> copyright.txt
	        *--> readme.txt
	        *--> version.txt
	        *--> website.txt
	        *--> icon.png
	        *--> bin
	        *    *--> applName
	        *--> doc
	        *    *--> applName
	        *--> lib
	        *    *--> XX.so
	        *    *--> YY.so
	        *--> license
	        *    *--> applName.txt
	        *    *--> libXX.txt
	        *    *--> libYY.txt
	        *--> man
	        *--> share
	        *    *--> applName
	        *    *--> XX
	        *    *--> YY
	        *--> sources
	"""
	def make_package_binary(self, pkg_name, pkg_properties, base_pkg_path, heritage_list, static):
		#debug.debug("------------------------------------------------------------------------")
		#debug.debug("-- Generate generic '" + pkg_name + "' v" + tools.version_to_string(pkg_properties["VERSION"]))
		#debug.debug("------------------------------------------------------------------------")
		#output path
		target_outpath = os.path.join(self.get_staging_path(pkg_name, tmp=True), pkg_name + ".app")
		tools.create_directory_of_file(target_outpath)
		
		## Create share datas:
		ret_share = self.make_package_binary_data(target_outpath, "zz_generic_zz", base_pkg_path, heritage_list, static)
		
		## copy binary files:
		ret_bin = self.make_package_binary_bin(target_outpath, pkg_name, base_pkg_path, heritage_list, static)
		
		## Create libraries:
		ret_lib = self.make_package_binary_lib(target_outpath, pkg_name, base_pkg_path, heritage_list, static)
		
		## Create generic files:
		ret_file = self.make_package_generic_files(target_outpath, pkg_properties, pkg_name, base_pkg_path, heritage_list, static)
		
		## end of the package generation
		build_package_path_done = os.path.join(self.get_build_path(pkg_name), "generatePackageDone.txt")
		#Check date between the current file "list of action to generate package and the end of package generation
		need_generate_package = depend.need_re_package(build_package_path_done, [__file__], True)
		
		## create the package:
		if    ret_share \
		   or ret_bin \
		   or ret_lib \
		   or ret_file \
		   or need_generate_package or True:
			# Zip the data
			debug.print_element("zip", "data.zip", "<==", os.path.join(self.get_staging_path(pkg_name, tmp=True), pkg_name + ".app/share/*"))
			zip_path = os.path.join(self.get_staging_path(pkg_name), pkg_name + ".app", pkg_name + ".data")
			zip.create_zip([
			    self.get_staging_path(pkg_name, tmp=True) + "/" + pkg_name + ".app/share/",
			    target_outpath + "/pkg"
			    ], zip_path)
			# copy if needed the binary:
			tools.copy_file(
			    os.path.join(self.get_staging_path(pkg_name, tmp=True), pkg_name + ".app", pkg_name + self.suffix_binary),
			    os.path.join(self.get_staging_path(pkg_name), pkg_name + ".app", pkg_name + self.suffix_binary),
			    force_identical=True)
			
			# patch the .js file to update the new real data ...
			js_file_data = tools.file_read_data(os.path.join(self.get_staging_path(pkg_name, tmp=True), pkg_name + ".app", pkg_name + self.suffix_binary2))
			data_to_replace = '"end": 6, "filename": "/' + self._file_data_tmp + '"}], "remote_package_size": 6'
			data_size = str(tools.file_size(zip_path))
			replace_with = '"end": ' + data_size + ', "filename": "/data.zip"}], "remote_package_size": ' + data_size
			debug.print_element("js", pkg_name + ".data", "<==", "correct zip name and data")
			tools.file_write_data(os.path.join(self.get_staging_path(pkg_name), pkg_name + ".app", pkg_name + self.suffix_binary2),
			                      js_file_data.replace(data_to_replace, replace_with),
			                      only_if_new = True)
			
			zip_path_final = os.path.join(self.get_final_path(), pkg_name + ".data")
			# generate deployed zip (for user)
			debug.print_element("zip", pkg_name + ".zip", "<==", self.get_staging_path(pkg_name), pkg_name + ".zip")
			zip.create_zip_file([
			    zip_path,
			    os.path.join(self.get_staging_path(pkg_name), pkg_name + ".app", pkg_name + self.suffix_binary)
			    ],
			    pkg_name + ".app",
			    zip_path_final)
			
			tools.file_write_data(build_package_path_done, "done...")
		## create the package:
		"""
		if    ret_share \
		   or ret_bin \
		   or ret_lib \
		   or ret_file \
		   or need_generate_package:
			#debug.debug("package : " + os.path.join(self.get_staging_path(pkg_name), pkg_name + ".app.pkg"))
			os.system("cd " + self.get_staging_path(pkg_name) + " ; tar -czf " + pkg_name + ".app.tar.gz " + pkg_name + ".app")
			#multiprocess.run_command("cd " + self.get_staging_path(pkg_name) + " ; tar -czf " + pkg_name + ".app.tar.gz " + pkg_name + ".app")
			tools.create_directory_of_file(self.get_final_path())
			tools.copy_file(os.path.join(self.get_staging_path(pkg_name), pkg_name + ".app.tar.gz"), os.path.join(self.get_final_path(), pkg_name + ".app.gpkg"))
			# package is done corectly ...
			tools.file_write_data(build_package_path_done, "done...")
		"""
	
	def install_package(self, pkg_name):
		#debug.debug("------------------------------------------------------------------------")
		debug.info("-- Install package '" + pkg_name + "'")
		#debug.debug("------------------------------------------------------------------------")
		# this is temporary ... Will call:
		if False:
			os.system("lutin-pkg -i " + os.path.join(self.get_final_path(), + pkg_name + ".app.gpkg"))
		else:
			#Copy directly from staging path:
			appl_path = os.path.join(self.get_staging_path(pkg_name), pkg_name + ".app")
			target_path = os.path.join(os.path.expanduser("~"), ".local", "application", pkg_name + ".app")
			target_bin_path = os.path.join(os.path.expanduser("~"), ".local", "application", pkg_name + ".app", "bin", pkg_name)
			target_bin_link = os.path.join(os.path.expanduser("~"), ".local", "application", pkg_name)
			# remove output path:
			tools.remove_path_and_sub_path(target_path)
			# remove executable link version:
			tools.remove_file(target_bin_link)
			# copy result:
			tools.copy_anything(appl_path, target_path, recursive=True)
			# create synbolic link:
			debug.info("kkk " + "ln -s " + target_bin_path + " " + target_bin_link)
			os.symlink(target_bin_path, target_bin_link)
	
	def un_install_package(self, pkg_name):
		#debug.debug("------------------------------------------------------------------------")
		debug.info("-- Un-Install package '" + pkg_name + "'")
		#debug.debug("------------------------------------------------------------------------")
		# this is temporary ... Will call:
		if False:
			os.system("lutin-pkg -r " + pkg_name)
		else:
			#Copy directly from staging path:
			target_path = os.path.join(os.path.expanduser("~"), ".local", "application", pkg_name + ".app")
			target_bin_link = os.path.join(os.path.expanduser("~"), ".local", "application", pkg_name)
			# remove output path:
			tools.remove_path_and_sub_path(target_path)
			# remove executable link version:
			tools.remove_file(target_bin_link)
	
	def run(self, pkg_name, option_list, binary_name = None):
		#debug.debug("------------------------------------------------------------------------")
		debug.info("-- Run package '" + pkg_name + "' + option: " + str(option_list))
		#debug.debug("------------------------------------------------------------------------")
		appl_path = os.path.join(self.get_staging_path(pkg_name), pkg_name + ".app", pkg_name + ".html")
		cmd = "firefox " + appl_path + " "
		for elem in option_list:
			cmd += elem + " "
		multiprocess.run_command_no_lock_out(cmd)
		#debug.debug("------------------------------------------------------------------------")
		debug.info("-- Run package '" + pkg_name + "' Finished")
		#debug.debug("------------------------------------------------------------------------")


