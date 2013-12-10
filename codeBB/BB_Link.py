#!/usr/bin/python
import lutinDebug as debug
import sys
import lutinTools
import re


##
## @brief Transcode:
## [http://votre_site.con] => http://votre_site.con
## [http://votre_site.con | text displayed] => text displayed
## [http://votre_site.con text displayed] => text displayed.
## 
## @param[in] value String to transform.
## @return Transformed string.
##
def transcode(value):
	
	
	# named link : [[http://plop.html | link name]]
	value = re.sub(r'\[\[http://(.*?) \| (.*?)\]\]',
	               r'<a href="http://\1">\2</a>',
	               value)
	
	# direct link : [[http://plop.html]]
	value = re.sub(r'\[\[http://(.*?)\]\]',
	               r'<a href="http://\1">http://\1</a>',
	               value)
	
	# direct lib link : [lib[libname]]
	value = re.sub(r'\[lib\[(.*?) \| (.*?)\]\]',
	               r'<a href="../\1">\2</a>',
	               value)
	
	value = re.sub(r'\[doc\[(.*?) \| (.*?)\]\]',
	               r'<a href="\1.html">\2</a>',
	               value)
	
	value = re.sub(r'\[tutorial\[(.*?) \| (.*?)\]\]',
	               r'<a href="tutorial_\1.html">\2</a>',
	               value)
	
	value = re.sub(r'\[class\[(.*?)\]\]',
	               replace_link_class,
	               value)
	
	"""
	p = re.compile('\[\[(.*?)(|(.*?))\]\])',
	               flags=re.DOTALL)
	value = p.sub(replace_link,
	              value)
	"""
	return value

"""
def replace_link(match):
	if match.group() == "":
		return ""
	#debug.verbose("plop: " + str(match.group()))
	value  = "<ul>"
	value += re.sub(r':INDENT:',
	               r'',
	               match.group())
	value += "</ul>"
	return transcode(value)
"""

def replace_link_class(match):
	if match.group() == "":
		return ""
	#debug.info("plop: " + str(match.group()))
	className = match.groups()[0]
	value = re.sub(':', '_', className)
	return '<a href="' + value + '.html">' + className + '</a>'



