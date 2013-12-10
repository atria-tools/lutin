#!/usr/bin/python
import lutinDebug as debug
import sys
import lutinTools
import re

listRegExp = [
	[ r'#(.*?)\n', r'<span class="code-preproc">#\1</span>\n']
]

def transcode(value):
	for reg1, reg2 in listRegExp:
		value = re.sub(reg1, reg2, value, flags=re.DOTALL)
	return value
