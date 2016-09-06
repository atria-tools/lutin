#!/usr/bin/python
import os
import doxy.module as module
import doxy.debug as debug
import doxy.tools as tools

def create(target, module_name):
	my_module = module.Module(__file__, module_name)
	my_module.set_version([1,2,6])
	my_module.set_title("lutin: build system and packager")
	my_module.set_website("http://HeeroYui.github.io/" + module_name)
	my_module.set_website_sources("http://github.com/HeeroYui/" + module_name)
	my_module.add_path([
	    module_name,
	    "doc"
	    ])
	my_module.add_exclude_symbols([
	    '_*',
	    'lutinTarget_*',
	    'lutinSystem_*',
	    'lutinBuilder_*',
	    ])
	my_module.add_file_patterns([
	    #'*.py',
	    'builder.py',
	    'debug.py',
	    'env.py',
	    'host.py',
	    'module.py',
	    'system.py',
	    'target.py',
	    '*.md',
	    ])
	
	return my_module