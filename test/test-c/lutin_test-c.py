#!/usr/bin/python
import lutin.tools as tools
import lutin.debug as debug
import os

def get_type():
	return "BINARY"

def get_desc():
	return "Test C compilation"

def configure(target, my_module):
	my_module.add_extra_compile_flags()
	my_module.add_src_file([
		'test.c'
		])
	if target.name=="Android":
		my_module.compile_version("c", 1999)
	return my_module

