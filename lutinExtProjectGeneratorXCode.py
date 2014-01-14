#!/usr/bin/python
import lutinDebug as debug
import datetime
import lutinTools
import lutinModule
import lutinExtProjectGenerator

# id example : FFBA2F79187F44AE0034CC66
genericID    =                   100000

def convert_name_in_base_id(name,fill=True):
	out = ""
	for element in name.lower():
		if   element == "a": out += "01"
		elif element == "b": out += "02"
		elif element == "c": out += "03"
		elif element == "d": out += "04"
		elif element == "e": out += "05"
		elif element == "f": out += "06"
		elif element == "g": out += "07"
		elif element == "h": out += "08"
		elif element == "i": out += "09"
		elif element == "j": out += "10"
		elif element == "k": out += "11"
		elif element == "l": out += "12"
		elif element == "m": out += "13"
		elif element == "n": out += "14"
		elif element == "o": out += "15"
		elif element == "p": out += "16"
		elif element == "q": out += "17"
		elif element == "r": out += "18"
		elif element == "s": out += "19"
		elif element == "t": out += "20"
		elif element == "u": out += "21"
		elif element == "v": out += "22"
		elif element == "w": out += "23"
		elif element == "x": out += "24"
		elif element == "y": out += "25"
		elif element == "z": out += "27"
		else:                out += "FF"
		if len(out) >= 18:
			return out
	if fill == True:
		for iii in range(0,256):
			out += "A"
			if len(out) >= 18:
				return out
	return out
	

dictId = {}

def convert_folder_in_base_id(name, package):
	global dictId
	debug.info(" generate Id for : " + package + ":" + name);
	if package not in dictId.keys():
		dictId[package] = {"lastID": 100000, "sub":{}}
	if name not in dictId[package]["sub"].keys():
		generatedID = convert_name_in_base_id(package) + str(dictId[package]["lastID"])
		dictId[package]["lastID"] = dictId[package]["lastID"] + 1
		dictId[package]["sub"][name] = {"id":generatedID}
	return dictId[package]["sub"][name]["id"]

def create_tree(fileList):
	tree = {}
	##"declare-name"

from collections import defaultdict

FILE_MARKER = '<files>'

##
## @brief generate a tree from the specific file
##
def attach(branch, trunk):
	parts = branch.split('/', 1)
	if len(parts) == 1:  # branch is a file
		trunk[FILE_MARKER].append(parts[0])
	else:
		node, others = parts
		if node not in trunk:
			trunk[node] = defaultdict(dict, ((FILE_MARKER, []),))
		attach(others, trunk[node])

##
## @brief display a specific path tree field
##
def prettify(d, indent=0):
	for key, value in d.iteritems():
		if key == FILE_MARKER:
			if value:
				debug.debug('  ' * indent + str(value))
		else:
			debug.debug('  ' * indent + str(key))
			if isinstance(value, dict):
				prettify(value, indent+1)
			else:
				debug.debug('  ' * (indent+1) + str(value))


def generate_tree(treedata, package, tree = []):
	data = ""
	tmpPath = "?tree?"
	if len(tree) != 0:
		tmpPath = ""
		for elem in tree:
			if tmpPath != "":
				tmpPath += '/'
			tmpPath += elem
	if len(tree) == 0:
		data +='		' + convert_folder_in_base_id(tmpPath, package) + ' /* ' + package + ' */ = {\n'
	else:
		data +='		' + convert_folder_in_base_id(tmpPath, package) + ' /* ' + tree[-1] + ' */ = {\n'
	data +='			isa = PBXGroup;\n'
	data +='			children = (\n'
	"""
	data +='				FFBA2F8B187F44AE0034CC66 /* AppDelegate.h */,\n'
	data +='				FFBA2F8C187F44AE0034CC66 /* AppDelegate.m */,\n'
	data +='				FFBA2F8E187F44AE0034CC66 /* Main_iPhone.storyboard */,\n'
	data +='				FFBA2F91187F44AE0034CC66 /* Main_iPad.storyboard */,\n'
	data +='				FFBA2F94187F44AE0034CC66 /* Shader.fsh */,\n'
	data +='				FFBA2F96187F44AE0034CC66 /* Shader.vsh */,\n'
	data +='				FFBA2F98187F44AE0034CC66 /* ViewController.h */,\n'
	data +='				FFBA2F99187F44AE0034CC66 /* ViewController.m */,\n'
	data +='				FFBA2F9B187F44AE0034CC66 /* Images.xcassets */,\n'
	data +='				FFBA2F83187F44AE0034CC66 /* Supporting Files */,\n'
	"""
	for key, value in treedata.iteritems():
		if key == FILE_MARKER:
			for file in value:
				data +='				' + convert_folder_in_base_id(tmpPath + '/' + file, package) + ' /* ' + file + ' */,\n'
		else:
			# TODO : Check if folder is empty ...
			data +='				' + convert_folder_in_base_id(tmpPath + '/' + key, package) + ' /* ' + key + ' */,\n'
			"""
			debug.debug('  ' * indent + str(key))
			if isinstance(value, dict):
				prettify(value, indent+1)
			else:
				debug.debug('  ' * (indent+1) + str(value))
			"""
	data +='			);\n'
	if len(tree) == 0:
		data +='			path = ' + package + ';\n'
	else:
		data +='			path = ' + tree[-1] + ';\n'
	data +='			sourceTree = "<group>";\n'
	data +='		};\n'
	# generate all subFolder : 
	for key, value in treedata.iteritems():
		if key == FILE_MARKER:
			continue
		tree.append(key)
		data += generate_tree(value, package, tree)
		tree.pop()
		
	return data


XCodeTypeElements = {
	'a':         ('archive.ar',            'PBXFrameworksBuildPhase'),
	'app':       ('wrapper.application',   None),
	's':         ('sourcecode.asm',        'PBXSourcesBuildPhase'),
	'c':         ('sourcecode.c.c',        'PBXSourcesBuildPhase'),
	'cpp':       ('sourcecode.cpp.cpp',    'PBXSourcesBuildPhase'),
	'framework': ('wrapper.framework',     'PBXFrameworksBuildPhase'),
	'h':         ('sourcecode.c.h',        None),
	'hpp':       ('sourcecode.c.h',        None),
	'icns':      ('image.icns',            'PBXResourcesBuildPhase'),
	'm':         ('sourcecode.c.objc',     'PBXSourcesBuildPhase'),
	'j':         ('sourcecode.c.objc',     'PBXSourcesBuildPhase'),
	'mm':        ('sourcecode.cpp.objcpp', 'PBXSourcesBuildPhase'),
	'nib':       ('wrapper.nib',           'PBXResourcesBuildPhase'),
	'plist':     ('text.plist.xml',        'PBXResourcesBuildPhase'),
	'json':      ('text.json',             'PBXResourcesBuildPhase'),
	'png':       ('image.png',             'PBXResourcesBuildPhase'),
	'rtf':       ('text.rtf',              'PBXResourcesBuildPhase'),
	'tiff':      ('image.tiff',            'PBXResourcesBuildPhase'),
	'txt':       ('text',                  'PBXResourcesBuildPhase'),
	'xcodeproj': ('wrapper.pb-project',    None),
	'xib':       ('file.xib',              'PBXResourcesBuildPhase'),
	'strings':   ('text.plist.strings',    'PBXResourcesBuildPhase'),
	'bundle':    ('wrapper.plug-in',       'PBXResourcesBuildPhase'),
	'dylib':     ('compiled.mach-o.dylib', 'PBXFrameworksBuildPhase'),
	'fsh':       ('sourcecode.glsl',       'PBXResourcesBuildPhase'),
	'frag':      ('sourcecode.glsl',       'PBXResourcesBuildPhase'),
	'vsh':       ('sourcecode.glsl',       'PBXResourcesBuildPhase'),
	'vert':      ('sourcecode.glsl',       'PBXResourcesBuildPhase')
}

class ExtProjectGeneratorXCode(lutinExtProjectGenerator.ExtProjectGenerator):
	def __init__(self):
		lutinExtProjectGenerator.ExtProjectGenerator.__init__(self, "XCode")
		self.baseId = "FFFFFFFFFFFFFFFFFF"
		
	def set_project_name(self, name):
		self.name = name
		self.baseId = convert_name_in_base_id(name)
	
	def add_files(self, group, basePath, srcList):
		genericID = 100001
		groupBaseID = convert_name_in_base_id(group)
		if group in self.groups.keys() :
			debug.error("use case not manage yet ...")
			return
		reworkedListFile = []
		for element in srcList:
			debug.info("plop : " + str(element))
			debug.info("plop : " + str(basePath))
			path = basePath + "/" + element
			pos = path.rfind('/')
			simpleName = path
			if pos >= 0:
				simpleName = path[pos+1:]
			pos = simpleName.rfind('.')
			extention = "";
			if pos >= 0:
				extention = simpleName[pos+1:]
			
			reworkedListFile.append({ "path" : path,
			                          "name" : simpleName,
			                          "extention":extention,
			                          "declare-name":element,
			                          "id" : groupBaseID + str(genericID)})
			genericID += 1
		self.groups[group] = {
		    "id" : groupBaseID + str(genericID + 100000),
		    "list-files" : reworkedListFile,
		    "extra-flags" : []
		    }
	
	def generate_project_file(self):
		
		
		#debug.error(" list : " + str(self.groups))
		
		data  ='// !$*UTF8*$!\n'
		data +='{\n'
		data +='	archiveVersion = 1;\n'
		data +='	classes = {\n'
		data +='	};\n'
		data +='	objectVersion = 46;\n'
		data +='	objects = {\n'
		data +='\n'
		data +='/* Begin PBXBuildFile section */\n'
		for group in self.groups:
			element = self.groups[group]
			for files in element["list-files"]:
				debug.debug(" PBXBuildFile ?? " + str(files))
				if files["extention"] in XCodeTypeElements.keys():
					if XCodeTypeElements[files["extention"]][1] == "PBXSourcesBuildPhase":
						data +='		/* ' + files["name"] + ' */\n'
						data +='		************************ = { isa = PBXBuildFile; fileRef = ' + files["id"] + '; };\n'
		data +='/* End PBXBuildFile section */\n'
		data +='\n'
		data +='/* Begin PBXContainerItemProxy section */\n'
		
		# I did not understand this section ...
		data +='		' + convert_folder_in_base_id("?PBXContainerItemProxy?", self.name) + ' /* PBXContainerItemProxy */ = {\n'
		data +='			isa = PBXContainerItemProxy;\n'
		data +='			containerPortal = ' + convert_folder_in_base_id("?PBXProject?", self.name) + ' /* Project object */;\n'
		data +='			proxyType = 1;\n'
		data +='			remoteGlobalIDString = ' + convert_folder_in_base_id("?PBXNativeTarget?sectio", self.name) + ';\n'
		data +='			remoteInfo = ' + self.name + ';\n'
		data +='		};\n'
		
		data +='/* End PBXContainerItemProxy section */\n'
		data +='\n'
		data +='/* Begin PBXFileReference section */\n'
		
		data +='		' + convert_folder_in_base_id("?app?", self.name) + ' /* ' + self.name + '.app */ = {\n'
		data +='			isa = PBXFileReference;\n'
		data +='			explicitFileType = wrapper.application;\n'
		data +='			includeInIndex = 0;\n'
		data +='			path = ' + self.name + '.app;\n'
		data +='			sourceTree = BUILT_PRODUCTS_DIR;\n'
		data +='		};\n'
		for group in self.groups:
			element = self.groups[group]
			for files in element["list-files"]:
				debug.debug(" PBXBuildFile ?? " + str(files))
				data +='		/* ' + files["name"] + ' */\n'
				if files["extention"] in XCodeTypeElements.keys():
				
					data +='		' + convert_folder_in_base_id(files["declare-name"], group) + ' = {'
					data +=' isa = PBXBuildFile;'
					data +=' lastKnownFileType = ' + XCodeTypeElements[files["extention"]][0] + ';'
					data +=' path = ' + files["path"] + ';'
					data +=' name = ' + files["name"] + ';'
					data +=' sourceTree = "<group>"; };\n'
				else:
					data +='		' + convert_folder_in_base_id(files["declare-name"], group) + ' = {'
					data +=' isa = PBXBuildFile;'
					data +=' lastKnownFileType = ' + XCodeTypeElements[files["extention"]][0] + ';'
					data +=' path = ' + files["path"] + ';'
					data +=' name = ' + files["name"] + ';'
					data +=' sourceTree = "<group>"; };\n'
		"""
		data +='		FFBA2F78187F44AE0034CC66 /* Foundation.framework */ = {''
		data +='			isa = PBXFileReference; lastKnownFileType = wrapper.framework; name = Foundation.framework; path = System/Library/Frameworks/Foundation.framework; sourceTree = SDKROOT; };\n'
		data +='		FFBA2F7A187F44AE0034CC66 /* CoreGraphics.framework */ = {'
		data +='			isa = PBXFileReference; lastKnownFileType = wrapper.framework; name = CoreGraphics.framework; path = System/Library/Frameworks/CoreGraphics.framework; sourceTree = SDKROOT; };
		data +='		FFBA2F7C187F44AE0034CC66 /* UIKit.framework */ = {
		data +='			isa = PBXFileReference; lastKnownFileType = wrapper.framework; name = UIKit.framework; path = System/Library/Frameworks/UIKit.framework; sourceTree = SDKROOT; };
		data +='		FFBA2F7E187F44AE0034CC66 /* GLKit.framework */ = {
		data +='			isa = PBXFileReference; lastKnownFileType = wrapper.framework; name = GLKit.framework; path = System/Library/Frameworks/GLKit.framework; sourceTree = SDKROOT; };
		data +='		FFBA2F80187F44AE0034CC66 /* OpenGLES.framework */ = {
		data +='			isa = PBXFileReference; lastKnownFileType = wrapper.framework; name = OpenGLES.framework; path = System/Library/Frameworks/OpenGLES.framework; sourceTree = SDKROOT; };
		data +='		FFBA2F84187F44AE0034CC66 /* edn-Info.plist */ = {
		data +='			isa = PBXFileReference; lastKnownFileType = text.plist.xml; path = "edn-Info.plist"; sourceTree = "<group>"; };
		data +='		FFBA2F86187F44AE0034CC66 /* en */ = {
		data +='			isa = PBXFileReference; lastKnownFileType = text.plist.strings; name = en; path = en.lproj/InfoPlist.strings; sourceTree = "<group>"; };
		data +='		FFBA2F88187F44AE0034CC66 /* main.m */ = {
		data +='			isa = PBXFileReference; lastKnownFileType = sourcecode.c.objc; path = main.m; sourceTree = "<group>"; };
		data +='		FFBA2F8A187F44AE0034CC66 /* edn-Prefix.pch */ = {
		data +='			isa = PBXFileReference; lastKnownFileType = sourcecode.c.h; path = "edn-Prefix.pch"; sourceTree = "<group>"; };
		data +='		FFBA2F8B187F44AE0034CC66 /* AppDelegate.h */ = {
		data +='			isa = PBXFileReference; lastKnownFileType = sourcecode.c.h; path = AppDelegate.h; sourceTree = "<group>"; };
		data +='		FFBA2F8C187F44AE0034CC66 /* AppDelegate.m */ = {
		data +='			isa = PBXFileReference; lastKnownFileType = sourcecode.c.objc; path = AppDelegate.m; sourceTree = "<group>"; };
		data +='		FFBA2F8F187F44AE0034CC66 /* Base */ = {
		data +='			isa = PBXFileReference; lastKnownFileType = file.storyboard; name = Base; path = Base.lproj/Main_iPhone.storyboard; sourceTree = "<group>"; };
		data +='		FFBA2F92187F44AE0034CC66 /* Base */ = {
		data +='			isa = PBXFileReference; lastKnownFileType = file.storyboard; name = Base; path = Base.lproj/Main_iPad.storyboard; sourceTree = "<group>"; };
		data +='		FFBA2F94187F44AE0034CC66 /* Shader.fsh */ = {
		data +='			isa = PBXFileReference;
		data +='			lastKnownFileType = sourcecode.glsl;
		data +='			name = Shader.fsh;
		data +='			path = Shaders/Shader.fsh;
		data +='			sourceTree = "<group>";
		data +='		};
		data +='		FFBA2F96187F44AE0034CC66 /* Shader.vsh */ = {
		data +='			isa = PBXFileReference; lastKnownFileType = sourcecode.glsl; name = Shader.vsh; path = Shaders/Shader.vsh; sourceTree = "<group>"; };
		data +='		FFBA2F98187F44AE0034CC66 /* ViewController.h */ = {
		data +='			isa = PBXFileReference; lastKnownFileType = sourcecode.c.h; path = ViewController.h; sourceTree = "<group>"; };
		data +='		FFBA2F99187F44AE0034CC66 /* ViewController.m */ = {
		data +='			isa = PBXFileReference; lastKnownFileType = sourcecode.c.objc; path = ViewController.m; sourceTree = "<group>"; };
		data +='		FFBA2F9B187F44AE0034CC66 /* Images.xcassets */ = {
		data +='			isa = PBXFileReference; lastKnownFileType = folder.assetcatalog; path = Images.xcassets; sourceTree = "<group>"; };
		data +='		FFBA2FA1187F44AE0034CC66 /* ednTests.xctest */ = {
		data +='			isa = PBXFileReference; explicitFileType = wrapper.cfbundle; includeInIndex = 0; path = ednTests.xctest; sourceTree = BUILT_PRODUCTS_DIR; };
		data +='		FFBA2FA2187F44AE0034CC66 /* XCTest.framework */ = {
		data +='			isa = PBXFileReference; lastKnownFileType = wrapper.framework; name = XCTest.framework; path = Library/Frameworks/XCTest.framework; sourceTree = DEVELOPER_DIR; };
		data +='		FFBA2FAA187F44AF0034CC66 /* ednTests-Info.plist */ = {
		data +='			isa = PBXFileReference; lastKnownFileType = text.plist.xml; path = "ednTests-Info.plist"; sourceTree = "<group>"; };
		data +='		FFBA2FAC187F44AF0034CC66 /* en */ = {
		data +='			isa = PBXFileReference;
		data +='			lastKnownFileType = text.plist.strings;
		data +='			name = en;
		data +='			path = en.lproj/InfoPlist.strings;
		data +='			sourceTree = "<group>";
		data +='		};
		data +='		FFBA2FAE187F44AF0034CC66 /* ednTests.m */ = {\n'
		data +='			isa = PBXFileReference;\n'
		data +='			lastKnownFileType = sourcecode.c.objc;\n'
		data +='			path = ednTests.m;\n'
		data +='			sourceTree = "<group>";\n'
		data +='		};\n'
		"""
		
		data +='/* End PBXFileReference section */\n'
		data +='\n'
		data +='/* Begin PBXFrameworksBuildPhase section */\n'
		
		data +='		' + convert_folder_in_base_id("?Frameworks?", self.name) + ' /* Frameworks */ = {\n'
		data +='			isa = PBXFrameworksBuildPhase;\n'
		data +='			buildActionMask = 2147483647;\n'
		data +='			files = (\n'
		data +='				FFBA2F81187F44AE0034CC66 /* OpenGLES.framework in Frameworks */,\n'
		data +='				FFBA2F7B187F44AE0034CC66 /* CoreGraphics.framework in Frameworks */,\n'
		data +='				FFBA2F7D187F44AE0034CC66 /* UIKit.framework in Frameworks */,\n'
		data +='				FFBA2F7F187F44AE0034CC66 /* GLKit.framework in Frameworks */,\n'
		data +='				FFBA2F79187F44AE0034CC66 /* Foundation.framework in Frameworks */,\n'
		data +='			);\n'
		data +='			runOnlyForDeploymentPostprocessing = 0;\n'
		data +='		};\n'
		
		data +='/* End PBXFrameworksBuildPhase section */\n'
		data +='\n'
		data +='/* Begin PBXGroup section */\n'
		
		data +='		' + convert_folder_in_base_id("?mainTreeGroup?", self.name) + ' = {\n'
		data +='			isa = PBXGroup;\n'
		data +='			children = (\n'
		for group, element in self.groups:
			data +='				' + convert_folder_in_base_id("?tree?", group) + ' /* ' + group + ' */,\n'
		data +='				' + convert_folder_in_base_id("?tree?", "frameworks") + ' /* Frameworks */,\n'
		data +='				' + convert_folder_in_base_id("?tree?", "Products") + ' /* Products */,\n'
		data +='			);\n'
		data +='			sourceTree = "<group>";\n'
		data +='		};\n'
		data +='		' + convert_folder_in_base_id("?tree?", "Products") + ' /* Products */ = {\n'
		data +='			isa = PBXGroup;\n'
		data +='			children = (\n'
		data +='				' + convert_folder_in_base_id("?app?", self.name) + ' /* ' + self.name + '.app */,\n'
		data +='			);\n'
		data +='			name = Products;\n'
		data +='			sourceTree = "<group>";\n'
		data +='		};\n'
		data +='		' + convert_folder_in_base_id("?tree?", "frameworks") + ' /* Frameworks */ = {\n'
		data +='			isa = PBXGroup;\n'
		data +='			children = (\n'
		data +='				FFBA2F78187F44AE0034CC66 /* Foundation.framework */,\n'
		data +='				FFBA2F7A187F44AE0034CC66 /* CoreGraphics.framework */,\n'
		data +='				FFBA2F7C187F44AE0034CC66 /* UIKit.framework */,\n'
		data +='				FFBA2F7E187F44AE0034CC66 /* GLKit.framework */,\n'
		data +='				FFBA2F80187F44AE0034CC66 /* OpenGLES.framework */,\n'
		data +='				FFBA2FA2187F44AE0034CC66 /* XCTest.framework */,\n'
		data +='			);\n'
		data +='			name = Frameworks;\n'
		data +='			sourceTree = "<group>";\n'
		data +='		};\n'
		# treeview :
		for group, element in self.groups:
			main_dict = defaultdict(dict, ((FILE_MARKER, []),))
			for line in element["list-files"]:
				attach(line["declare-name"], main_dict)
			data += generate_tree(main_dict, group)
		"""
		data +='		FFBA2F82187F44AE0034CC66 /* edn */ = {\n'
		data +='			isa = PBXGroup;\n'
		data +='			children = (\n'
		data +='				FFBA2F8B187F44AE0034CC66 /* AppDelegate.h */,\n'
		data +='				FFBA2F8C187F44AE0034CC66 /* AppDelegate.m */,\n'
		data +='				FFBA2F8E187F44AE0034CC66 /* Main_iPhone.storyboard */,\n'
		data +='				FFBA2F91187F44AE0034CC66 /* Main_iPad.storyboard */,\n'
		data +='				FFBA2F94187F44AE0034CC66 /* Shader.fsh */,\n'
		data +='				FFBA2F96187F44AE0034CC66 /* Shader.vsh */,\n'
		data +='				FFBA2F98187F44AE0034CC66 /* ViewController.h */,\n'
		data +='				FFBA2F99187F44AE0034CC66 /* ViewController.m */,\n'
		data +='				FFBA2F9B187F44AE0034CC66 /* Images.xcassets */,\n'
		data +='				FFBA2F83187F44AE0034CC66 /* Supporting Files */,\n'
		data +='			);\n'
		data +='			path = edn;\n'
		data +='			sourceTree = "<group>";\n'
		data +='		};\n'
		data +='		FFBA2F83187F44AE0034CC66 /* Supporting Files */ = {\n'
		data +='			isa = PBXGroup;\n'
		data +='			children = (\n'
		data +='				FFBA2F84187F44AE0034CC66 /* edn-Info.plist */,\n'
		data +='				FFBA2F85187F44AE0034CC66 /* InfoPlist.strings */,\n'
		data +='				FFBA2F88187F44AE0034CC66 /* main.m */,\n'
		data +='				FFBA2F8A187F44AE0034CC66 /* edn-Prefix.pch */,\n'
		data +='			);\n'
		data +='			name = "Supporting Files";\n'
		data +='			sourceTree = "<group>";\n'
		data +='		};\n'
		"""
		
		data +='/* End PBXGroup section */\n'
		data +='\n'
		data +='/* Begin PBXNativeTarget section */\n'
		
		data +='		' + convert_folder_in_base_id("?PBXNativeTarget?sectio", self.name) + ' /* edn */ = {\n'
		data +='			isa = PBXNativeTarget;\n'
		data +='			buildConfigurationList = ' + convert_folder_in_base_id("?PBXNativeTarget?", self.name) + ' /* Build configuration list for PBXNativeTarget "edn" */;\n'
		data +='			buildPhases = (\n'
		data +='				FFBA2F71187F44AE0034CC66 /* Sources */,\n'
		data +='				' + convert_folder_in_base_id("?Frameworks?", self.name) + ' /* Frameworks */,\n'
		data +='				' + convert_folder_in_base_id("?Resources?", self.name) + ' /* Resources */,\n'
		data +='			);\n'
		data +='			buildRules = (\n'
		data +='			);\n'
		data +='			dependencies = (\n'
		data +='			);\n'
		data +='			name = edn;\n'
		data +='			productName = edn;\n'
		data +='			productReference = ' + convert_folder_in_base_id("?app?", self.name) + ' /* ' + self.name + '.app */;\n'
		data +='			productType = "com.apple.product-type.application";\n'
		data +='		};\n'
		
		data +='/* End PBXNativeTarget section */\n'
		data +='\n'
		data +='/* Begin PBXProject section */\n'
		
		data +='		' + convert_folder_in_base_id("?Project-object?", self.name) + ' /* Project object */ = {\n'
		data +='			isa = PBXProject;\n'
		data +='			attributes = {\n'
		data +='				LastUpgradeCheck = 0500;\n'
		data +='				ORGANIZATIONNAME = "Edouard DUPIN";\n'
		data +='				TargetAttributes = {\n'
		data +='					' + convert_folder_in_base_id("?Project-object?targetAttribute", self.name) + ' = {\n'
		data +='						TestTargetID = ' + convert_folder_in_base_id("?PBXNativeTarget?sectio", self.name) + ';\n'
		data +='					};\n'
		data +='				};\n'
		data +='			};\n'
		data +='			buildConfigurationList = ' + convert_folder_in_base_id("?PBXProject?", self.name) + ' /* Build configuration list for PBXProject "edn" */;\n'
		data +='			compatibilityVersion = "Xcode 3.2";\n'
		data +='			developmentRegion = English;\n'
		data +='			hasScannedForEncodings = 0;\n'
		data +='			knownRegions = (\n'
		data +='				en,\n'
		data +='				Base,\n'
		data +='			);\n'
		data +='			mainGroup = ' + convert_folder_in_base_id("?mainTreeGroup?", self.name) + ';\n'
		data +='			productRefGroup = ' + convert_folder_in_base_id("?tree?", "Products") + ' /* Products */;\n'
		data +='			projectDirPath = "";\n'
		data +='			projectRoot = "";\n'
		data +='			targets = (\n'
		data +='				' + convert_folder_in_base_id("?PBXNativeTarget?sectio", self.name) + ' /* edn */,\n'
		data +='			);\n'
		data +='		};\n'
		data +='/* End PBXProject section */\n'
		data +='\n'
		data +='/* Begin PBXResourcesBuildPhase section */\n'
		
		data +='		' + convert_folder_in_base_id("?Resources?", self.name) + ' /* Resources */ = {\n'
		data +='			isa = PBXResourcesBuildPhase;\n'
		data +='			buildActionMask = 2147483647;\n'
		data +='			files = (\n'
		# list of all resources to copy
		"""
		data +='				FFBA2F95187F44AE0034CC66 /* Shader.fsh in Resources */,\n'
		data +='				FFBA2F93187F44AE0034CC66 /* Main_iPad.storyboard in Resources */,\n'
		data +='				FFBA2F90187F44AE0034CC66 /* Main_iPhone.storyboard in Resources */,\n'
		data +='				FFBA2F9C187F44AE0034CC66 /* Images.xcassets in Resources */,\n'
		data +='				FFBA2F87187F44AE0034CC66 /* InfoPlist.strings in Resources */,\n'
		data +='				FFBA2F97187F44AE0034CC66 /* Shader.vsh in Resources */,\n'
		"""
		data +='			);\n'
		data +='			runOnlyForDeploymentPostprocessing = 0;\n'
		data +='		};\n'
		
		data +='/* End PBXResourcesBuildPhase section */\n'
		data +='\n'
		data +='/* Begin PBXSourcesBuildPhase section */\n'
		
		data +='		FFBA2F71187F44AE0034CC66 /* Sources */ = {\n'
		data +='			isa = PBXSourcesBuildPhase;\n'
		data +='			buildActionMask = 2147483647;\n'
		data +='			files = (\n'
		# list of all file to compile ...
		"""
		data +='				FFBA2F9A187F44AE0034CC66 /* ViewController.m in Sources */,\n'
		data +='				FFBA2F8D187F44AE0034CC66 /* AppDelegate.m in Sources */,\n'
		data +='				FFBA2F89187F44AE0034CC66 /* main.m in Sources */,\n'
		"""
		data +='			);\n'
		data +='			runOnlyForDeploymentPostprocessing = 0;\n'
		data +='		};\n'
		
		data +='/* End PBXSourcesBuildPhase section */\n'
		data +='\n'
		data +='/* Begin PBXTargetDependency section */\n'
		# nothing ...
		data +='/* End PBXTargetDependency section */\n'
		data +='\n'
		data +='/* Begin PBXVariantGroup section */\n'
		"""
		data +='		FFBA2F85187F44AE0034CC66 /* InfoPlist.strings */ = {\n'
		data +='			isa = PBXVariantGroup;\n'
		data +='			children = (\n'
		data +='				FFBA2F86187F44AE0034CC66 /* en */,\n'
		data +='			);\n'
		data +='			name = InfoPlist.strings;\n'
		data +='			sourceTree = "<group>";\n'
		data +='		};\n'
		data +='		FFBA2F8E187F44AE0034CC66 /* Main_iPhone.storyboard */ = {\n'
		data +='			isa = PBXVariantGroup;\n'
		data +='			children = (\n'
		data +='				FFBA2F8F187F44AE0034CC66 /* Base */,\n'
		data +='			);\n'
		data +='			name = Main_iPhone.storyboard;\n'
		data +='			sourceTree = "<group>";\n'
		data +='		};\n'
		data +='		FFBA2F91187F44AE0034CC66 /* Main_iPad.storyboard */ = {\n'
		data +='			isa = PBXVariantGroup;\n'
		data +='			children = (\n'
		data +='				FFBA2F92187F44AE0034CC66 /* Base */,\n'
		data +='			);\n'
		data +='			name = Main_iPad.storyboard;\n'
		data +='			sourceTree = "<group>";\n'
		data +='		};\n'
		data +='		FFBA2FAB187F44AF0034CC66 /* InfoPlist.strings */ = {\n'
		data +='			isa = PBXVariantGroup;\n'
		data +='			children = (\n'
		data +='				FFBA2FAC187F44AF0034CC66 /* en */,\n'
		data +='			);\n'
		data +='			name = InfoPlist.strings;\n'
		data +='			sourceTree = "<group>";\n'
		data +='		};\n'
		"""
		data +='/* End PBXVariantGroup section */\n'
		data +='\n'
		data +='/* Begin XCBuildConfiguration section */\n'
		data +='		' + convert_folder_in_base_id("?PBXProject?Debug", self.name) + ' /* Debug */ = {\n'
		data +='			isa = XCBuildConfiguration;\n'
		data +='			buildSettings = {\n'
		data +='				ALWAYS_SEARCH_USER_PATHS = NO;\n'
		data +='				ARCHS = "$(ARCHS_STANDARD_INCLUDING_64_BIT)";\n'
		data +='				CLANG_CXX_LANGUAGE_STANDARD = "gnu++0x";\n'
		data +='				CLANG_CXX_LIBRARY = "libc++";\n'
		data +='				CLANG_ENABLE_MODULES = YES;\n'
		data +='				CLANG_ENABLE_OBJC_ARC = YES;\n'
		data +='				CLANG_WARN_BOOL_CONVERSION = YES;\n'
		data +='				CLANG_WARN_CONSTANT_CONVERSION = YES;\n'
		data +='				CLANG_WARN_DIRECT_OBJC_ISA_USAGE = YES_ERROR;\n'
		data +='				CLANG_WARN_EMPTY_BODY = YES;\n'
		data +='				CLANG_WARN_ENUM_CONVERSION = YES;\n'
		data +='				CLANG_WARN_INT_CONVERSION = YES;\n'
		data +='				CLANG_WARN_OBJC_ROOT_CLASS = YES_ERROR;\n'
		data +='				CLANG_WARN__DUPLICATE_METHOD_MATCH = YES;\n'
		data +='				"CODE_SIGN_IDENTITY[sdk=iphoneos*]" = "iPhone Developer";\n'
		data +='				COPY_PHASE_STRIP = NO;\n'
		data +='				GCC_C_LANGUAGE_STANDARD = gnu99;\n'
		data +='				GCC_DYNAMIC_NO_PIC = NO;\n'
		data +='				GCC_OPTIMIZATION_LEVEL = 0;\n'
		data +='				GCC_PREPROCESSOR_DEFINITIONS = (\n'
		data +='					"DEBUG=1",\n'
		data +='					"$(inherited)",\n'
		data +='				);\n'
		data +='				GCC_SYMBOLS_PRIVATE_EXTERN = NO;\n'
		data +='				GCC_WARN_64_TO_32_BIT_CONVERSION = YES;\n'
		data +='				GCC_WARN_ABOUT_RETURN_TYPE = YES_ERROR;\n'
		data +='				GCC_WARN_UNDECLARED_SELECTOR = YES;\n'
		data +='				GCC_WARN_UNINITIALIZED_AUTOS = YES;\n'
		data +='				GCC_WARN_UNUSED_FUNCTION = YES;\n'
		data +='				GCC_WARN_UNUSED_VARIABLE = YES;\n'
		data +='				IPHONEOS_DEPLOYMENT_TARGET = 7.0;\n'
		data +='				ONLY_ACTIVE_ARCH = YES;\n'
		data +='				SDKROOT = iphoneos;\n'
		data +='				TARGETED_DEVICE_FAMILY = "1,2";\n'
		data +='			};\n'
		data +='			name = Debug;\n'
		data +='		};\n'
		data +='		' + convert_folder_in_base_id("?PBXProject?Release", self.name) + ' /* Release */ = {\n'
		data +='			isa = XCBuildConfiguration;\n'
		data +='			buildSettings = {\n'
		data +='				ALWAYS_SEARCH_USER_PATHS = NO;\n'
		data +='				ARCHS = "$(ARCHS_STANDARD_INCLUDING_64_BIT)";\n'
		data +='				CLANG_CXX_LANGUAGE_STANDARD = "gnu++0x";\n'
		data +='				CLANG_CXX_LIBRARY = "libc++";\n'
		data +='				CLANG_ENABLE_MODULES = YES;\n'
		data +='				CLANG_ENABLE_OBJC_ARC = YES;\n'
		data +='				CLANG_WARN_BOOL_CONVERSION = YES;\n'
		data +='				CLANG_WARN_CONSTANT_CONVERSION = YES;\n'
		data +='				CLANG_WARN_DIRECT_OBJC_ISA_USAGE = YES_ERROR;\n'
		data +='				CLANG_WARN_EMPTY_BODY = YES;\n'
		data +='				CLANG_WARN_ENUM_CONVERSION = YES;\n'
		data +='				CLANG_WARN_INT_CONVERSION = YES;\n'
		data +='				CLANG_WARN_OBJC_ROOT_CLASS = YES_ERROR;\n'
		data +='				CLANG_WARN__DUPLICATE_METHOD_MATCH = YES;\n'
		data +='				"CODE_SIGN_IDENTITY[sdk=iphoneos*]" = "iPhone Developer";\n'
		data +='				COPY_PHASE_STRIP = YES;\n'
		data +='				ENABLE_NS_ASSERTIONS = NO;\n'
		data +='				GCC_C_LANGUAGE_STANDARD = gnu99;\n'
		data +='				GCC_WARN_64_TO_32_BIT_CONVERSION = YES;\n'
		data +='				GCC_WARN_ABOUT_RETURN_TYPE = YES_ERROR;\n'
		data +='				GCC_WARN_UNDECLARED_SELECTOR = YES;\n'
		data +='				GCC_WARN_UNINITIALIZED_AUTOS = YES;\n'
		data +='				GCC_WARN_UNUSED_FUNCTION = YES;\n'
		data +='				GCC_WARN_UNUSED_VARIABLE = YES;\n'
		data +='				IPHONEOS_DEPLOYMENT_TARGET = 7.0;\n'
		data +='				SDKROOT = iphoneos;\n'
		data +='				TARGETED_DEVICE_FAMILY = "1,2";\n'
		data +='				VALIDATE_PRODUCT = YES;\n'
		data +='			};\n'
		data +='			name = Release;\n'
		data +='		};\n'
		data +='		' + convert_folder_in_base_id("?PBXNativeTarget?Debug", self.name) + ' /* Debug */ = {\n'
		data +='			isa = XCBuildConfiguration;\n'
		data +='			buildSettings = {\n'
		data +='				ASSETCATALOG_COMPILER_APPICON_NAME = AppIcon;\n'
		data +='				ASSETCATALOG_COMPILER_LAUNCHIMAGE_NAME = LaunchImage;\n'
		data +='				GCC_PRECOMPILE_PREFIX_HEADER = YES;\n'
		data +='				GCC_PREFIX_HEADER = "edn/edn-Prefix.pch";\n'
		data +='				INFOPLIST_FILE = "edn/edn-Info.plist";\n'
		data +='				PRODUCT_NAME = "$(TARGET_NAME)";\n'
		data +='				WRAPPER_EXTENSION = app;\n'
		data +='			};\n'
		data +='			name = Debug;\n'
		data +='		};\n'
		data +='		' + convert_folder_in_base_id("?PBXNativeTarget?Release", self.name) + ' /* Release */ = {\n'
		data +='			isa = XCBuildConfiguration;\n'
		data +='			buildSettings = {\n'
		data +='				ASSETCATALOG_COMPILER_APPICON_NAME = AppIcon;\n'
		data +='				ASSETCATALOG_COMPILER_LAUNCHIMAGE_NAME = LaunchImage;\n'
		data +='				GCC_PRECOMPILE_PREFIX_HEADER = YES;\n'
		data +='				GCC_PREFIX_HEADER = "edn/edn-Prefix.pch";\n'
		data +='				INFOPLIST_FILE = "edn/edn-Info.plist";\n'
		data +='				PRODUCT_NAME = "$(TARGET_NAME)";\n'
		data +='				WRAPPER_EXTENSION = app;\n'
		data +='			};\n'
		data +='			name = Release;\n'
		data +='		};\n'
		
		data += '/* End XCBuildConfiguration section */\n'
		data += '\n'
		data += '/* Begin XCConfigurationList section */\n'
		
		data +='		' + convert_folder_in_base_id("?PBXProject?", self.name) + ' /* Build configuration list for PBXProject "' + self.name + '" */ = {\n'
		data +='			isa = XCConfigurationList;\n'
		data +='			buildConfigurations = (\n'
		data +='				' + convert_folder_in_base_id("?PBXProject?Debug", self.name) + ' /* Debug */,\n'
		data +='				' + convert_folder_in_base_id("?PBXProject?Release", self.name) + ' /* Release */,\n'
		data +='			);\n'
		data +='			defaultConfigurationIsVisible = 0;\n'
		data +='			defaultConfigurationName = Release;\n'
		data +='		};\n'
		data +='		' + convert_folder_in_base_id("?PBXNativeTarget?", self.name) + ' /* Build configuration list for PBXNativeTarget "PBXNativeTarget" */ = {\n'
		data +='			isa = XCConfigurationList;\n'
		data +='			buildConfigurations = (\n'
		data +='				' + convert_folder_in_base_id("?PBXNativeTarget?Debug", self.name) + ' /* Debug */,\n'
		data +='				' + convert_folder_in_base_id("?PBXNativeTarget?Release", self.name) + ' /* Release */,\n'
		data +='			);\n'
		data +='			defaultConfigurationIsVisible = 0;\n'
		data +='		};\n'
		data +='/* End XCConfigurationList section */\n'
		data +='	};\n'
		data +='	rootObject = ******************* /* Project object */;\n'
		data +='}\n'
		
		debug.info(data)


		