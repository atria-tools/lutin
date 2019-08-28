#!/usr/bin/python
# -*- coding: utf-8 -*-
##
## @author Edouard DUPIN
##
## @copyright 2012, Edouard DUPIN, all right reserved
##
## @license MPL v2.0 (see license file)
##

from setuptools import setup
import os

def readme():
	with open('README.rst') as f:
		return f.read()

def read_version_file():
	if not os.path.isfile("version.txt"):
		return ""
	file = open("version.txt", "r")
	data_file = file.read()
	file.close()
	if len(data_file) > 4 and data_file[-4:] == "-dev":
		data_file = data_file[:-4]
	return data_file

# https://pypi.python.org/pypi?%3Aaction=list_classifiers
setup(name='lutin',
      version=read_version_file(),
      description='Lutin generic builder (might replace makefile, CMake ...)',
      long_description=readme(),
      url='http://github.com/HeeroYui/lutin',
      author='Edouard DUPIN',
      author_email='yui.heero@gmail.com',
      license='MPL-2',
      packages=['lutin',
                'lutin/z_builder',
                'lutin/z_system',
                'lutin/z_target',
                ],
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Programming Language :: Python',
        'Topic :: Software Development :: Build Tools',
      ],
      long_description_content_type="text/markdown",
      keywords='builder c++ c android ios macos makefile cmake',
      scripts=['bin/lutin'],
      # Does not work on MacOs
      #data_file=[
      #    ('/etc/bash_completion.d', ['bash-autocompletion/lutin']),
      #],
      install_requires=[
          'realog',
          'death',
      ],
      include_package_data = True,
      zip_safe=False)

#To developp: sudo ./setup.py install
#             sudo ./setup.py develop
#pylint test: pylint2 --rcfile=pylintRcFile.txt lutin/module.py

#TO register all in pip: use external tools:
#  pip install twine
#  # create the archive
#  ./setup.py sdist
#  twine upload dist/*

