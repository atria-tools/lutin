#!/usr/bin/python
from setuptools import setup

def readme():
	with open('README.rst') as f:
		return f.read()

# https://pypi.python.org/pypi?%3Aaction=list_classifiers
setup(name='lutin',
      version='0.5.3',
      description='Lutin generic builder',
      long_description=readme(),
      url='http://github.com/HeeroYui/lutin',
      author='Edouard DUPIN',
      author_email='yui.heero@gmail.com',
      license='APACHE-2',
      packages=['lutin',
                'lutin/builder',
                'lutin/system',
                'lutin/target'
               ],
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Compilers',
      ],
      keywords='builder c++ c android ios macos makefile cmake',
      scripts=['bin/lutin'],
      include_package_data = True,
      zip_safe=False)

#To developp: ./setup.py install/develop
#TO register all in pip: ./setup.py register sdist upload

