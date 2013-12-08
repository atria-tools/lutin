#!/usr/bin/python
import lutinDebug as debug
import sys
import lutinTools
import re


##
## @brief Transcode balise :
##   [code language=cpp]
##   int main(void) {
##   	return 0;
##   }
##   [/code]
## @param[in] value String to transform.
## @return Transformed string.
##
def transcode(value):
	
	value = re.sub(r'\[code=(\#[0-9A-F]{6}|[a-z\-]+)\](.*?)\[/color\]',
	               r'<span style="color: \1;">\2</span>',
	               value)
	
	return value


