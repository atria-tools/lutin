#!/usr/bin/python
# -*- coding: utf-8 -*-
##
## @author Edouard DUPIN
##
## @copyright 2012, Edouard DUPIN, all right reserved
##
## @license MPL v2.0 (see license file)
##

import sys
import os
import copy
import inspect
import fnmatch
import json
# Local import
from . import host
from . import tools
from realog import debug
from . import heritage
from . import builder
from . import multiprocess
from . import image
from . import module
from . import license
from . import env
from warnings import catch_warnings
from xmlrpc.client import boolean


def get_module_type_availlable():
    return [
        'BINARY',
        'BINARY_SHARED',
        'BINARY_STAND_ALONE',
        'LIBRARY',
        'LIBRARY_DYNAMIC',
        'LIBRARY_STATIC',
        'PACKAGE',
        'PREBUILD',
        'DATA'
    ]


list_of_property_module=[
        "type",
        "sub-type",
        "group-id",
        "description",
        "license",
        "license-file",
        "author",
        "maintainer",
        "version",
        "version-id",
        "code-quality"
    ];

list_of_element_ignored=[
        "comment", # just to post a comment in the configuration files
        "todo", # just to post a todo in the configuration files
    ];
list_of_element_availlable=[
        "source",
        "header",
        "path",
        "compilation-version",
        "dependency",
        "copy",
        "flag",
        "compilator", # todo
        "mode",
        "target",
        "arch",
        "bus-size", # todo
        "sanity-compilation" # todo "isolate", "intricate", "*" permit to specify element to copy for the isolation mode. intricate is for current mode where everything is mixed together ...
    ];

"""
{
    "type":"LIBRARY",
    "group-id":"com.atria-soft",
    "description":"Ewol tool kit (base: container)",
    "licence":"MPL-2",
    "licence-file":"file://LICENCE.txt",
    "maintainer":"Edouard DUPIN <yui.heero@gmail.com>",
    "author":"file://../authors.txt",
    "version":"1.5.3",
    "__version":"file://../version.txt",
    "code-quality":"MEDIUM",
    "mode": {
        "*": {
            "target": {
                "*": {
                    "arch": {
                        "*": {},
                    }
                },
            },
            "arch": {}
        },
        "release": {
            
        },
        "debug": {
        }
    },
    "source": [
            {
                "source":"xxx/plop.cpp",
                "flag":[
                    ...
                ]
            },
            "xxx/Yyy.cpp",
            "xxx/YuyTer.cpp"
            "xxx/plouf.java"
    ],
    "source": {
        "*": [
            ...
        ],
        "c": [
            ...
        ],
        "c++": [
            ...
        ],
        "nasm": [
            ...
        ] ...
    },
    "header": [
            "xxx/Yyy.hpp",
            "xxx/YuyTer.hpp"
    ],
    "header": {
        "c": [
            "xxx/Yyy.hpp",
            "xxx/YuyTer.hpp"
        ]
    },
    ############## TODO: rename "include"
    "path":[
        "."
    ],
    "compilation-version": { ## old ==> to remove
        "language": "c++",
        "version": 2017
    },
    "compilation-version": {
        "c++": 2017,
        "java": 16
    },
    "dependency": [
        "c",
        "m",
        "pthread"
    ],
    "copy":[
        ...
    ];
    "mode": {
        "*": {
        
        },
        "debug": {
            
        },
        "release": {
            
        },
        "coverage": {
            
        }
    },
    "target": {
        "*": {
        
        },
        "Android": {
            "dependency": [
                "SDK"
            ]
        },
        "MacOs": {
            "dependency": [
                "cxx"
            ]
        },
        "Windows": {
        
        },
        "Linux": {
            "dependency": [
                {
                    "name": "X11",
                    "optional": true,
                    "export": false,
                    "source": [
                        "gale/context/X11/Context.cpp"
                    ],
                    "flag": {
                        "language": "c++",
                        "value": "-DGALE_BUILD_X11"
                    },
                    "missing-flag": {
                        "language": "c++",
                        "value": "-DGALE_DOES_NOT_BUILD_X11"
                    }
                },
        },
        "Debian": { ## Debian/Ubuntu/Suze/RedHat/ArchLinux/Gento ... heritate from linux ...
        
        },
        "IOs": {
        
        },
        "Web": {
        
        },
        "MacOs|IOs": {
        
        },
        "comment": "For all element expect IOS and Android",
        "!Android&!IOs": {
        
        },
    }
    "arch": {
        "x86": {
            
        },
        "arm": {
            
        },
        "ppc": {
            
        }
        "misc": {
            
        }
    },
    "bus-size": {
        "*": {
        
        },
        "8": {
        
        },
        "16": {
        
        },
        "32": {
        
        },
        "64": {
        
        },
        "128": {
        
        }
    },
    "compilator": {
        "*": {
        
        },
        "gcc": {
        
        },
        "clang": {
        
        },
        "mingw": {
        
        },
        "msvc": {
        
        },
        "intel": {
        
        }
    },
    "sanity-compilation": {
        "*": {
        
        },
        "isolate": {
        
        },
        "intricate": {
         
        }
    },
    "instruction-set":{
        not present right now... :the instruction mode available...:
    }
    #### TODO: later
    "import": [ 
        "GDSFGH.json" ## import an other file to have generic definitions ...
    ]
}

get_compilator
get_mode
get_arch
"""


def check_compatible(mode, value, list_to_check, json_path):
    if value == "":
        debug.debug("the <" + mode + ">: condition '" + str(value) + "' empty element >> " + json_path);
        return False;
    if value == "*":
        return True;
    find_a_valid_key = False;
    debug.verbose("Depact: " + value);
    # fist step ==> split in the | value ==> multiple check cases
    for elemOR in value.split("|"):
        debug.verbose("    |: " + elemOR);
        # check the condition is True:
        condition = True;
        if elemOR == "" or elemOR == " " or elemOR == "\t":
            debug.warning("the <" + mode + ">: condition '" + str(value) + "' is not supported must not have ' ' or '\\t' or empty element >> " + json_path);
            return False;
        for elemAND in elemOR.split("&"):
            debug.verbose("        &: " + elemAND);
            if elemAND == "" or elemAND == " " or elemAND == "\t":
                debug.warning("the <" + mode + ">: condition '" + str(value) + "' is not supported must not have ' ' or '\\t' or empty element >> " + json_path);
                return False;
            invert_condition = False;
            if elemAND[0] == "!":
                debug.verbose("            ==> invert condition");
                invert_condition = True;
                elemAND = elemAND[1:]
            if elemAND in list_to_check:
                debug.verbose("            ==> detect condition OK");
                if invert_condition:
                    condition = False;
                    debug.verbose("          FALSE");
                    break;
                else:
                    debug.verbose("          TRUE");
                    continue;
            if invert_condition:
                debug.verbose("          TRUE");
                continue;
            else:
                condition = False;
                debug.verbose("          FALSE");
                break;
        if condition:
            debug.verbose("       Detect OR condition at TRUE !!!!");
            find_a_valid_key = True;
            break;
    if find_a_valid_key:
        return True;
    """
    if "|" in value:
        debug.warning("in <" + mode + ">: '" + str(value) + " not managed '|' >> " + json_path);
        return False;
    if "&" in value:
        debug.warning("in <" + mode + ">: '" + str(value) + " not managed '&' >> " + json_path);
        return False;
    if "!" in value:
        debug.warning("in <" + mode + ">: '" + str(value) + " not managed '!' >> " + json_path);
        return False;
    if value in list_to_check or value == "*":
        return True;
    """
    debug.debug("the <" + mode + ">: '" + str(value) + "' is not compatible with '" + str(list_to_check) + "' >> " + json_path);
    return False;
    


def parse_node_arch(target, path, json_path, my_module, data):
    for elem in data.keys():
        if check_compatible("arch", elem, target.get_arch(), json_path):
            parse_node_generic(target, path, json_path, my_module, data[elem]);

def parse_node_mode(target, path, json_path, my_module, data):
    for elem in data.keys():
        if check_compatible("mode", elem, target.get_mode(), json_path):
            parse_node_generic(target, path, json_path, my_module, data[elem]);

def parse_node_platform(target, path, json_path, my_module, data):
    for elem in data.keys():
        if check_compatible("target", elem, target.get_type(), json_path):
            parse_node_generic(target, path, json_path, my_module, data[elem]);

def parse_node_generic(target, path, json_path, my_module, data, first = False ):
    for elem in data.keys():
        if elem in list_of_property_module:
            if first == True:
                continue;
            else:
                debug.error("key: '" + elem + "' is NOT allowed at expect in the root node: " + json_path);
            continue;
        if elem in list_of_element_ignored:
            continue;
        if elem not in list_of_element_availlable:
            debug.warning("key: '" + elem + "' is unknown: " + json_path);
            debug.warning("Available List: " + str(list_of_element_ignored) + " or: " + str(list_of_element_availlable));
    
    if "source" in data.keys():
        if type(data["source"]) == list:
            my_module.add_src_file(data["source"]);
        elif type(data["source"]) == dict:
            if "list" in data["source"].keys():
                my_module.add_src_file(data["source"]["list"]);
            else:
                debug.error("missing 'list' in node 'source:{}'");
        else:
            debug.error("Wrong type for node 'source' [] or {}");
    
    if "header" in data.keys():
        if type(data["header"]) == list:
            my_module.add_header_file(data["header"]);
        elif type(data["header"]) == dict:
            if "list" in data["header"].keys():
                my_module.add_header_file(data["header"]["list"]);
            else:
                debug.error("missing 'list' in node 'header:{}'");
        else:
            debug.error("Wrong type for node 'headers' [] or {}");
    
    if "path" in data.keys():
        if type(data["path"]) == list:
            my_module.add_path(data["path"]);
        else:
            debug.error("Wrong type for node 'path' []");
    
    
    if "dependency" in data.keys():
        if type(data["dependency"]) == list:
            for elem in data["dependency"]:
                GLD_add_depend(my_module, elem);
        else:
            debug.error("Wrong type for node 'dependency' []");
    
    if "compilation-version" in data.keys():
        if type(data["compilation-version"]) == list:
            for elem in data["compilation-version"]:
                GLD_compile_version(my_module, elem);
        elif type(data["compilation-version"]) == dict:
            GLD_compile_version(my_module, data["compilation-version"]);
        else:
            debug.error("Wrong type for node 'compilation-version' [] or {}");
    
    if "copy" in data.keys():
        if type(data["copy"]) == list:
            for elem in data["copy"]:
                GLD_copy(my_module, elem);
        elif type(data["copy"]) == dict:
            GLD_copy(my_module, data["copy"]);
        else:
            debug.error("Wrong type for node 'dependency' []");

    if "arch" in data.keys():
        parse_node_arch(target, path, json_path, my_module, data["arch"]);
        
    if "target" in data.keys():
        parse_node_platform(target, path, json_path, my_module, data["target"]);
        
    if "mode" in data.keys():
        parse_node_mode(target, path, json_path, my_module, data["mode"]);

def load_module_from_GLD(target, name, path, json_path):
    debug.debug("Parse file: "+ json_path + "'");
    try:
        data = json.load(open(json_path,))
    except json.decoder.JSONDecodeError as ex:
        debug.error("Can not parse the file : "+ json_path + " Detect error as : " + str(ex));
    
    property = get_module_option_GLD(path, data, name)
    # create the module:
    my_module = module.Module(json_path, name, property["type"])
    # debug.warning("plopppp " + json.dumps(property, sort_keys=True, indent=4))
    # overwrite some package default property (if not set by user)
    if property["compagny-type"] != None:
        my_module._pkg_set_if_default("COMPAGNY_TYPE", property["compagny-type"])
    if property["compagny-name"] != None:
        my_module._pkg_set_if_default("COMPAGNY_NAME", property["compagny-name"])
    if property["maintainer"] != None:
        my_module._pkg_set_if_default("MAINTAINER", property["maintainer"])
    if property["name"] != None:
        my_module._pkg_set_if_default("NAME", property["name"])
    if property["description"] != None:
        my_module._pkg_set_if_default("DESCRIPTION", property["description"])
    if property["license"] != None:
        my_module._pkg_set_if_default("LICENSE", property["license"])
    if property["version"] != None:
        my_module._pkg_set_if_default("VERSION", property["version"])
    # parsing all the file to configure:
    parse_node_generic(target, path, json_path, my_module, data, True);
    
        
    return my_module

def GLD_add_depend(my_module, data):
    if type(data) == str:
        my_module.add_depend(data);
    elif type(data) == dict:
        if "name" in data.keys():
            name = data["name"];
        else:
            debug.error("Can not have dependency without name ...");
        optional = False;
        if "optional" in data.keys():
            if type(data["optional"]) == boolean:
                optional = data["optional"];
            else:
                debug.error("Can not have dependency 'optional' in an other type than boolean ...");
        export = False;
        if "export" in data.keys():
            if type(data["export"]) == boolean:
                optional = data["export"];
            else:
                debug.error("Can not have dependency 'export' in an other type than boolean ...");
        flags_data = None;
        if "flag" in data.keys():
            if "language" in data["flag"].keys() and "value" in data["flag"].keys():
                flags_data = [data["flag"]["language"], data["flag"]["value"]]
            else:
                debug.error("Can not have dependency 'flag' without value 'language' and 'value' ...");
        missing_flags_data = None;
        if "missing-flag" in data.keys():
            if "language" in data["missing-flag"].keys() and "value" in data["missing-flag"].keys():
                missing_flags_data = [data["missing-flag"]["language"], data["missing-flag"]["value"]]
            else:
                debug.error("Can not have dependency 'missing-flag' without value 'language' and 'value' ...");
        src_file=[]
        if "source" in data.keys():
            if type(data["source"]) == list:
                src_file = data["source"];
            elif type(data["source"]) == str:
                src_file = [ data["source"] ];
            else:
                debug.error("Can not have dependency 'source' in an other type than [] or string: '" + str(data["source"]) + "'");
        header_file=[]
        if "header" in data.keys():
            if type(data["header"]) == list:
                header_file = data["header"];
            elif type(data["header"]) == str:
                header_file = [ data["header"] ];
            else:
                debug.error("Can not have dependency 'header' in an other type than [] or string: '" + str(data["header"]) + "'");
        
        
        if optional == False:
            my_module.add_depend(name);
            my_module.add_header_file(header_file);
            my_module.add_src_file(src_file);
            # TODO: add flags
        else:
            my_module.add_optionnal_depend(name, flags_data, export=export, compilation_flags_not_found = missing_flags_data, src_file=src_file, header_file=header_file)
    else:
        debug.error("dependency only support [ {} or string ]");

def GLD_compile_version(my_module, data):
    if "language" in data.keys() and "version" in data.keys():
        my_module.compile_version(data["language"], data["version"])
    else:
        debug.error("missing 'language' and/or 'version' in node 'compilation-version:{}'");

def GLD_copy(my_module, data):
    path_src = None;
    file_src = None;
    path_to = "";
    recursive = False;
    if "path" in data.keys():
        path_src = data["path"];
    if "file" in data.keys():
        file_src = data["file"];
    if "to" in data.keys():
        path_to = data["to"];
    if "recursive" in data.keys():
        if type(data["recursive"]) == bool:
            recursive = data["recursive"];
        else:
            debug.error("recursive is a boolean !!!");
    if path_src == None and file_src == None:
        debug.error("copy must at least have 'path' or 'file' !!!");
    if path_src != None:
        my_module.copy_path(path_src, path_to);
    if file_src != None:
        my_module.copy_file(file_src, path_to);
        
        

def get_module_option_GLD(path, data, name):
    type = None;
    if "type" in data.keys():
        type = data["type"];
        # TODO: check it is in a list ...
    else:
        debug.error(" the node 'type' must be provided in the module: " + name);
    sub_type = None
    if "sub-type" in data.keys():
        sub_type = data["sub-type"];
    compagny_type = None;
    compagny_name = None;
    group_id = None;
    if "group-id" in data.keys():
        compagny_name = data["group-id"];
        group_id = data["group-id"];
    description = None;
    if "description" in data.keys():
        description = data["description"];
    license = None;
    if "license" in data.keys():
        license = data["license"];
    license_file = None;
    if "license-file" in data.keys():
        license_file = data["license-file"];
    maintainer = None;
    if "author" in data.keys():
        maintainer = tools.get_maintainer_from_file_or_direct(path, data["author"]);
    version = None;
    if "version" in data.keys():
        version = tools.get_version_from_file_or_direct(path, data["version"]);
    version_id = None;
    if "version-id" in data.keys():
        version_id = data["version-id"];
    
    # check type property:
    if type not in get_module_type_availlable():
        debug.error("Does not support module type: '" + str(type) + "' not in " + str(get_module_type_availlable()) + " path: " + str(path));
    
    list_sub_type = ["TEST", "SAMPLE", "TOOL", None];
    if sub_type not in list_sub_type:
        debug.error("Does not support module sub-type: '" + str(sub_type) + "' not in " + str(list_sub_type) + " path: " + str(path));
    
    return {
           "name":name,
           "description":description,
           "type":type,
           "sub-type":sub_type,
           "license":license,
           "license-file":license_file,
           "compagny-type":compagny_type,
           "compagny-name":compagny_name,
           "group-id":group_id,
           "maintainer":maintainer,
           "version":version,
           "version-id":version_id
           }
