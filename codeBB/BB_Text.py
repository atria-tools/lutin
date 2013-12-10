#!/usr/bin/python
import lutinDebug as debug
import sys
import lutinTools
import re


##
## @brief Transcode .
##      [b]texte ici[/b]
##      [i]texte ici[/i]
##      [u]texte ici[/u]
##      [strike]texte ici[/strike]
##      [color=olive]texte ici[/color]
##      [color=#456FF33F]texte ici[/color]
##      Left : [left]texte ici[/left]
##      Center : [center]texte ici[/center]
##      Right : [right]texte ici[/right]
##      [size=22]sdfgsdfgsdgsfd[/size]
##      [cadre]mettre les code ici[/cadre]
## @param[in] string String to transform.
## @return Transformed string.
##
def transcode(value):
	
	value = re.sub(r'\[b\](.*?)\[/b\]',
	               r'<span style="font-weight: bold;">\1</span>',
	               value,
	               flags=re.DOTALL)
	
	value = re.sub(r'\[i\](.*?)\[/i\]',
	               r'<span style="font-style: italic;">\1</span>',
	               value,
	               flags=re.DOTALL)
	
	value = re.sub(r'\[u\](.*?)\[/u\]',
	               r'<span style="text-decoration: underline;">\1</span>',
	               value,
	               flags=re.DOTALL)
	
	value = re.sub(r'\[sup\](.*?)\[/sup\]',
	               r'<sup>\1</sup>',
	               value,
	               flags=re.DOTALL)
	
	value = re.sub(r'\[sub\](.*?)\[/sub\]',
	               r'<sub>\1</sub>',
	               value,
	               flags=re.DOTALL)
	
	value = re.sub(r'\[color=(\#[0-9A-F]{6}|[a-z\-]+)\](.*?)\[/color\]',
	               r'<span style="color: \1;">\2</span>',
	               value,
	               flags=re.DOTALL)
	
	value = re.sub(r'\[center\](.*)\[/center\]',
	               r'<div align="center">\1</div>',
	               value,
	               flags=re.DOTALL)
	
	value = re.sub(r'\[right\](.*?)\[/right\]',
	               r'<div align="right">\1</div>',
	               value,
	               flags=re.DOTALL)
	
	value = re.sub(r'\[left\](.*?)\[/left\]',
	               r'<div align="left">\1</div>',
	               value,
	               flags=re.DOTALL)
	
	value = re.sub(r'\[strike\](.*?)\[/strike\]',
	               r'<span><strike>\1</strike></span>',
	               value,
	               flags=re.DOTALL)
	
	value = re.sub(r'\[size=(.*?)\](.*?)\[/size\]',
	               r'<span style="font-size: \1px; line-height: normal;">\2</span>',
	               value,
	               flags=re.DOTALL)
	
	value = re.sub(r'\[cadre\](.*?)\[/cadre\]',
	               r'<table align="center" border="0" cellpadding="3" cellspacing="1" width="90%"><tbody><tr><td class="quote">\1</td></tr></tbody></table>',
	               value,
	               flags=re.DOTALL)
	
	value = re.sub(r'____(.*?)\n',
	               r'<hr>',
	               value,
	               flags=re.DOTALL)
	
	return value
