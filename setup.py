#!/usr/bin/python
from setuptools import setup

setup(name='lutin',
      version='0.5.0',
      description='Lutin generic builder',
      url='http://github.com/HeeroYui/lutin',
      author='Edouard DUPIN',
      author_email='yui.heero@gmail.com',
      license='APACHE-2',
      packages=['lutin'],
      scripts=['bin/lutin'],
      zip_safe=False)
