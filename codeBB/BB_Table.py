#!/usr/bin/python
import lutinDebug as debug
import sys
import lutinTools
import re


##
## @brief Transcode table:
## { | tableau_type_1
## | [b]colone 1[/b]
## ligne 1
## | colone 2 ligne 1
## |---
## | colone 1 ligne 1
## | colone 2 ligne 2
## |}
## Avec autant de ligne et de colone que vous voullez..
## Il est possible de faire des retour a la ligne dans une case du tableau...
## En bref sa tend a marcher comme sur un Wiki...
## 
## result:
##      +-------------------------------------+
##      | colone 1                            |
##      +------------------+------------------+
##      | ligne 1          | colone 2 ligne 1 |
##      +------------------+------------------+
##      | colone 1 ligne 1 | colone 2 ligne 2 |
##      +------------------+------------------+
## 
## TODO : Create simple table like :
##      | colone 1 ||
##      | ligne 1 |	colone 2 ligne 1 |
##      | colone 1 ligne 1 | colone 2 ligne 2|
## @param[in] value String to transform.
## @return Transformed string.
##
def transcode(value):
	
	return value


