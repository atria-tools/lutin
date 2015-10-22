#!/usr/bin/python
import lutin.module as module
import lutin.tools as tools
import lutin.debug as debug
import os

def get_type():
	return "BINARY"

def get_desc():
	return "Text C compilation"

def create(target, module_name):
	my_module = module.Module(__file__, module_name, get_type())
	my_module.add_extra_compile_flags()
	my_module.add_src_file([
		'test.c'
		])
	if target.name=="Android":
		my_module.compile_version("c", 1999)
	return my_module

