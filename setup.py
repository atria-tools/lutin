#!/usr/bin/python
from setuptools import setup

def readme():
	with open('README.rst') as f:
		return f.read()

# https://pypi.python.org/pypi?%3Aaction=list_classifiers
setup(name='lutin',
      version='0.7.6',
      description='Lutin generic builder (might replace makefile, CMake ...)',
      long_description=readme(),
      url='http://github.com/HeeroYui/lutin',
      author='Edouard DUPIN',
      author_email='yui.heero@gmail.com',
      license='APACHE-2',
      packages=['lutin',
                'lutin/z_builder',
                'lutin/z_system',
                'lutin/z_target'],
      classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Compilers',
      ],
      keywords='builder c++ c android ios macos makefile cmake',
      scripts=['bin/lutin'],
      # Does not work on MacOs
      #data_file=[
      #    ('/etc/bash_completion.d', ['bash-autocompletion/lutin']),
      #],
      include_package_data = True,
      zip_safe=False)

#To developp: sudo ./setup.py install
#             sudo ./setup.py develop
#TO register all in pip: ./setup.py register sdist upload

