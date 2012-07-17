#!/bin/bash

if [ "$#" != "2" ]; then
	echo "Usage : $0 <input> <output>"
	exit 1
fi

# Remove CONFIG_ prefix
# Put lines beginig with '#' between '/*' '*/'
# Replace 'key=value' by '#define key value'
# Replace leading ' y' by ' 1'
# Remove leading and trailing quotes from string
# Replace '\"' by '"'
sed \
	-e 's/^CONFIG_//' \
	-e 's/^# CONFIG_/# /' \
	-e "s/^#\(.*\)/\/*\1 *\//" \
	-e 's/\(.*\)=\(.*\)/#define \1 \2 /' \
	-e 's/ y$/ 1/' \
	-e 's/\"\(.*\)\"/\1/' \
	-e 's/\\\"/\"/g' \
	$1 > $2


