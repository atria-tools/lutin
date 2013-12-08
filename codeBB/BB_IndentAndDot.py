#!/usr/bin/python
import lutinDebug as debug
import sys
import lutinTools
import re


##
## @brief Transcode 
## commencez les ligne par ":" comme:
## : 1
## : 2
## ::2.1
## ::2.2
## :::2.2.1
## ::::2.2.1.1
## :::::2.2.1.1.1
## ::2.3
## :3
## resultat:
## 
##  	1
##  	2
##  		2.1
##  		2.2
##  			2.2.1
##  				2.2.1.1
##  		2.3
##  	3
## 
## note: lorsque vous sautez une ligne, la liste sarraite et en recommence une autre...
## 
## Il est possible de mettre des ":" sans ligne appres ce qui genere une ligne vide..
## 
## AND DOT
## **Ma ligne2 star consecutives engendrent des points quelque soit la position dans la ligne...
## 
## Resultat:
## 
## * premiere ligne
## * deusieme ligne
## @param[in] value String to transform.
## @return Transformed string.
##
def transcode(value):
	
	value = re.sub(r'\n:',
	               r'\n:INDENT:',
	               value)
	p = re.compile('((\:INDENT\:(.*?)\n)*)')
	value = p.sub(replace_wiki_identation,
	              value)
	
	value = re.sub(r'\*\*(.*?)\n',
	               r'<li>\1</li>',
	               value)
	
	return value


def replace_wiki_identation(match):
	if match.group() == "":
		return ""
	debug.info("plop: " + str(match.group()))
	value  = "<ul>"
	value += re.sub(r':INDENT:',
	               r'',
	               match.group())
	value += "</ul>"
	return transcode(value)
