#!/usr/bin/python
# -*- coding: utf-8 -*-
##
## @author Edouard DUPIN
##
## @copyright 2012, Edouard DUPIN, all right reserved
##
## @license MPL v2.0 (see license file)
##

license_base = {
	"APACHE-2": {
		"generic":True,
		"contaminate-static":False,
		"contaminate-dynamic":False,
		"redistribute-source":False,
		"title":"MPL v2.0 license",
		"licence-file":"licence/apache-2.txt"
		},
	"GPL-2": {
		"generic":True,
		"contaminate-static":True,
		"contaminate-dynamic":True,
		"redistribute-source":True,
		"title":"GPL: Gnu Public Licence v2.0",
		"licence-file":"licence/GPL-2.txt"
		},
	"GPL-3": {
		"generic":True,
		"contaminate-static":True,
		"contaminate-dynamic":True,
		"redistribute-source":True,
		"title":"GPL: GNU General Public License v3.0",
		"licence-file":"licence/GPL-3.txt"
		},
	"LGPL-2": {
		"generic":True,
		"contaminate-static":False,
		"contaminate-dynamic":False,
		"redistribute-source":True,
		"title":"LGPL: GNU Lesser General Public License v2.0",
		"licence-file":"licence/LGPL-2.txt"
		},
	"LGPL-3": {
		"generic":True,
		"contaminate-static":True,
		"contaminate-dynamic":False,
		"redistribute-source":True,
		"title":"LGPL: GNU Lesser General Public License v3.0",
		"licence-file":"licence/LGPL-3.txt"
		},
	"MIT": {
		"generic":True,
		"contaminate-static":False,
		"contaminate-dynamic":False,
		"redistribute-source":False,
		"title":"MIT: Massachusetts Institute of Technology License",
		"licence-file":"licence/MIT.txt"
		},
	"BSD-2": {
		"generic":True,
		"contaminate-static":False,
		"contaminate-dynamic":False,
		"redistribute-source":False,
		"title":"BSD 2-clauses: Berkeley Software Distribution License",
		"licence-file":"licence/BSD-2.txt"
		},
	"BSD-3": {
		"generic":True,
		"contaminate-static":False,
		"contaminate-dynamic":False,
		"redistribute-source":False,
		"title":"BSD 3-clauses: Berkeley Software Distribution License",
		"licence-file":"licence/BSD-3.txt"
		},
	"BSD-4": {
		"generic":True,
		"contaminate-static":False,
		"contaminate-dynamic":False,
		"redistribute-source":False,
		"title":"BSD 4-clauses: Berkeley Software Distribution License",
		"licence-file":"licence/BSD-4.txt"
		},
	"PNG": {
		"generic":True,
		"contaminate-static":False,
		"contaminate-dynamic":False,
		"redistribute-source":False,
		"title":"PNG License",
		"licence-file":"licence/png.txt"
		},
	"MPL-1": {
		"generic":True,
		"contaminate-static":False,
		"contaminate-dynamic":False,
		"redistribute-source":True,
		"title":"MPL: Mozilla Public Licence v1.0",
		"licence-file":"licence/MPL-1.txt"
		},
	"MPL-1.1": {
		"generic":True,
		"contaminate-static":False,
		"contaminate-dynamic":False,
		"redistribute-source":True,
		"title":"MPL: Mozilla Public Licence v1.1",
		"licence-file":"licence/MPL-1.1.txt"
		},
	"MPL-2": {
		"generic":True,
		"contaminate-static":False,
		"contaminate-dynamic":False,
		"redistribute-source":True,
		"title":"MPL: Mozilla Public Licence v2.0",
		"licence-file":"licence/MPL-2.txt"
		},
}

def get_basic_list():
	global license_base
	out = []
	for name in license_base:
		out.append(name)
	return out


