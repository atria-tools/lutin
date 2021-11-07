cmake_minimum_required(VERSION 3.20)

if (WIN32)
	set(CPACK_GENERATOR "ZIP")
else()
	set(CPACK_GENERATOR "TGZ")
endif()
set(CPACK_VERBATIM_VARIABLES YES)
include(CPack)


## fist step is determining the target:
if (WIN32)
	set(GLD_TARGET "Windows" CACHE INTERNAL "")
elseif(APPLE)
	set(GLD_TARGET "MacOs" CACHE INTERNAL "")
elseif(LINUX)
	set(GLD_TARGET "Linux" CACHE INTERNAL "")
elseif(UNIX AND NOT APPLE)
	set(GLD_TARGET "Linux" CACHE INTERNAL "")
else()
	message("GLD Can not determine the target !!!")
	exit(-1)
endif()

if (CMAKE_CXX_COMPILER_ID STREQUAL "Clang")
	set(GLD_COMPILATOR "clang" CACHE INTERNAL "")
elseif (CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
	set(GLD_COMPILATOR "gcc" CACHE INTERNAL "")
elseif (CMAKE_CXX_COMPILER_ID STREQUAL "Intel")
	set(GLD_COMPILATOR "intel" CACHE INTERNAL "")
elseif (CMAKE_CXX_COMPILER_ID STREQUAL "MSVC")
	set(GLD_COMPILATOR "msvc" CACHE INTERNAL "")
else()
	message("GLD Can not determine the compilator !!!")
	exit(-1)
endif()

if(CMAKE_BUILD_TYPE STREQUAL "Debug")
	set(GLD_MODE "debug" CACHE INTERNAL "")
elseif(CMAKE_BUILD_TYPE STREQUAL "debug")
	set(GLD_MODE "debug" CACHE INTERNAL "")
else()
	set(GLD_MODE "release" CACHE INTERNAL "")
endif()
            
            
if(CMAKE_SYSTEM_PROCESSOR STREQUAL "x86_64"
   OR CMAKE_SYSTEM_PROCESSOR STREQUAL amd64)
	set(GLD_ARCH "x86" CACHE INTERNAL "")
	set(GLD_BUS_SIZE "64" CACHE INTERNAL "")
elseif(CMAKE_SYSTEM_PROCESSOR STREQUAL "x86"
       OR CMAKE_SYSTEM_PROCESSOR STREQUAL "i686")
	set(GLD_ARCH "x86" CACHE INTERNAL "")
	set(GLD_BUS_SIZE "32" CACHE INTERNAL "")
elseif(CMAKE_SYSTEM_PROCESSOR STREQUAL "ppc64")
	set(GLD_ARCH "ppc" CACHE INTERNAL "")
	set(GLD_BUS_SIZE "64" CACHE INTERNAL "")
elseif(CMAKE_SYSTEM_PROCESSOR STREQUAL "ppc")
	set(GLD_ARCH "ppc" CACHE INTERNAL "")
	set(GLD_BUS_SIZE "32" CACHE INTERNAL "")
elseif(CMAKE_SYSTEM_PROCESSOR STREQUAL "arm64"
       OR CMAKE_SYSTEM_PROCESSOR STREQUAL "aarch64")
	set(GLD_ARCH "arm" CACHE INTERNAL "")
	set(GLD_BUS_SIZE "64" CACHE INTERNAL "")
elseif(CMAKE_SYSTEM_PROCESSOR STREQUAL "arm"
       OR CMAKE_SYSTEM_PROCESSOR STREQUAL "armv7l"
       OR CMAKE_SYSTEM_PROCESSOR STREQUAL "armv9")
	set(GLD_ARCH "arm" CACHE INTERNAL "")
	set(GLD_BUS_SIZE "32" CACHE INTERNAL "")
else()
	message("GLD Can not determine the architecture and bus-size !!!")
	exit(-1)
endif()

# cmake does not support other mode than "intricate" the "isolate" mode is too much complicated to do. 
set(GLD_SANITY_MODE "intricate" CACHE INTERNAL "")
# list of current supported language:
#     - 'c': C language
#     - 'c++': C++ language
#     - 'asm': asembler language
#     - 'm': Objective-C language
#     - 'mm': Objective-C++ language
#     - 'java': Java language
#     - 'javah': generated c header with Java description (for JNI)
# TODO: maybe permit user to add some other... like "in", "masm", or other pre-step generation code??? 
set(GLD_SUPPORT_LANGUAGE "c;asm;c++;m;mm;java;javah" CACHE INTERNAL "")
set(GLD_SUPPORT_LANGUAGE_VARIABLE "C;ASM;CXX;M;MM;JAVA;JAVAH" CACHE INTERNAL "")
set(GLD_LANGUAGE_EXTENTION_C     "c;C" CACHE INTERNAL "")
set(GLD_LANGUAGE_EXTENTION_CXX   "cpp;CPP;cxx;CXX" CACHE INTERNAL "")
set(GLD_LANGUAGE_EXTENTION_ASM   "s;S" CACHE INTERNAL "")
set(GLD_LANGUAGE_EXTENTION_M     "m;M" CACHE INTERNAL "")
set(GLD_LANGUAGE_EXTENTION_MM    "mm;MM" CACHE INTERNAL "")
set(GLD_LANGUAGE_EXTENTION_JAVA  "java" CACHE INTERNAL "")
set(GLD_LANGUAGE_EXTENTION_JAVAH "javah" CACHE INTERNAL "")

# where is build the module
set(GLD_GLOBAL_BUILD_FOLDER "${CMAKE_CURRENT_BINARY_DIR}/${GLD_TARGET}_${GLD_ARCH}_${GLD_BUS_SIZE}/${GLD_MODE}/build/${GLD_COMPILATOR}/" CACHE INTERNAL "")
# where the package is prepared
set(GLD_GLOBAL_STAGING_FOLDER "${CMAKE_CURRENT_BINARY_DIR}/${GLD_TARGET}_${GLD_ARCH}_${GLD_BUS_SIZE}/${GLD_MODE}/staging/${GLD_COMPILATOR}/" CACHE INTERNAL "")
# whe the bundle (tar, jar ...) is set
set(GLD_GLOBAL_FINAL_FOLDER "${CMAKE_CURRENT_BINARY_DIR}/${GLD_TARGET}_${GLD_ARCH}_${GLD_BUS_SIZE}/${GLD_MODE}/final/${GLD_COMPILATOR}/" CACHE INTERNAL "")
	
message("Global GLD properties:")
message("	GLD_MODE :        ${GLD_MODE}")
message("	GLD_COMPILATOR :  ${GLD_COMPILATOR}")
message("	GLD_TARGET :      ${GLD_TARGET}")
message("	GLD_ARCH :        ${GLD_ARCH}")
message("	GLD_BUS_SIZE :    ${GLD_BUS_SIZE}")
message("	GLD_SANITY_MODE : ${GLD_SANITY_MODE}")
message("	GLD_GLOBAL_BUILD_FOLDER :   ${GLD_GLOBAL_BUILD_FOLDER}")
message("	GLD_GLOBAL_STAGING_FOLDER : ${GLD_GLOBAL_STAGING_FOLDER}")
message("	GLD_GLOBAL_FINAL_FOLDER :   ${GLD_GLOBAL_FINAL_FOLDER}")

##
## @brief get the type of a variable
## @param[in] INPUT_JSON Json data.
## @param[in] VARIABLE Name of the variable.
## @param[out] OUT_VAR Retrun type of the node: NULL, NUMBER, STRING, BOOLEAN, ARRAY, OBJECT or NOTFOUND (if does not exist)
##
function(json_get_type OUT_VAR INPUT_JSON VARIABLE)
	string(JSON VALUE ERROR_VARIABLE ${VARIABLE} TYPE ${INPUT_JSON} ${VARIABLE})
	if (${VALUE} STREQUAL ${VARIABLE}-NOTFOUND)
		set(${OUT_VAR} "NOTFOUND" PARENT_SCOPE)
	else()
		set(${OUT_VAR} "${VALUE}" PARENT_SCOPE)
	endif()
endfunction()


function(json_size OUT_VAR INPUT_JSON VARIABLE)
	string(JSON VALUE ERROR_VARIABLE ${VARIABLE} LENGTH ${INPUT_JSON} ${VARIABLE})
	if (${VALUE} STREQUAL ${VARIABLE}-NOTFOUND)
		set("${OUT_VAR}" 0 PARENT_SCOPE)
	else ()
		set("${OUT_VAR}" ${VALUE} PARENT_SCOPE)
	endif()
endfunction()

function(json_get_data OUT_VAR INPUT_JSON VARIABLE)
	string(JSON VALUE GET ${INPUT_JSON} ${VARIABLE})
	set("${OUT_VAR}" ${VALUE} PARENT_SCOPE)
endfunction()

function(json_object_key OUT_VAR INPUT_JSON IDX)
	string(JSON VALUE MEMBER ${INPUT_JSON} ${IDX})
	set("${OUT_VAR}" ${VALUE} PARENT_SCOPE)
endfunction()

function(json_object_keys OUT_VAR MY_JSON_STRING VARIABLE)
	json_size(SIZE ${MY_JSON_STRING} ${VARIABLE})
	#message("target SIZE = ${SIZE}")
	json_get_data(OBJECT_DATA ${MY_JSON_STRING} ${VARIABLE})
	MATH(EXPR SIZE "${SIZE}-1")
	set(OUT "")
	foreach(IDX RANGE ${SIZE})
		json_object_key(ELEMENT ${OBJECT_DATA} ${IDX})
		#message("   - : ${ELEMENT}")
		list(APPEND OUT ${ELEMENT})
	endforeach()
	set("${OUT_VAR}" ${OUT} PARENT_SCOPE)
endfunction()

function(json_object_values OUT_VAR INPUT_JSON VARIABLE KEYS)
	string(JSON VALUE GET ${INPUT_JSON} ${VARIABLE} ${KEYS})
	set("${OUT_VAR}" ${VALUE} PARENT_SCOPE)
endfunction()

function(json_get_list OUT_VAR INPUT_JSON VARIABLE)
	string(JSON LIST_JSON_ELEMENTS ERROR_VARIABLE ${VARIABLE} GET ${INPUT_JSON} ${VARIABLE})
	if (${LIST_JSON_ELEMENTS} STREQUAL ${VARIABLE}-NOTFOUND)
		set("${OUT_VAR}" PARENT_SCOPE)
		retrun()
	endif()
	#message("LIST_JSON_ELEMENTS      : ${LIST_JSON_ELEMENTS}")
	
	string(JSON LENGTH_VALUE LENGTH ${LIST_JSON_ELEMENTS})
	#message("LENGTH_VALUE      : ${LENGTH_VALUE}")
	if (${LENGTH_VALUE} EQUAL 0)
		set("${OUT_VAR}" PARENT_SCOPE)
		retrun()
	endif()
	set(OUT_LIST)
	MATH(EXPR LENGTH_VALUE "${LENGTH_VALUE}-1")
	foreach(IDX RANGE ${LENGTH_VALUE})
		string(JSON ELEM GET ${LIST_JSON_ELEMENTS} ${IDX})
		#message("   - : ${ELEM}")
		list(APPEND OUT_LIST ${ELEM})
	endforeach()
	#message("OUT_LIST : ${OUT_LIST}")
	set("${OUT_VAR}" ${OUT_LIST} PARENT_SCOPE)
endfunction()



function(json_get_element OUT_VAR INPUT_JSON VARIABLE)
	string(JSON ELEMENT ERROR_VARIABLE ${VARIABLE} GET ${INPUT_JSON} ${VARIABLE})
	if ("${ELEMENT}" STREQUAL "${VARIABLE}-NOTFOUND")
		set("${OUT_VAR}" "" PARENT_SCOPE)
	elseif ("${ELEMENT}" STREQUAL "NOTFOUND")
		set("${OUT_VAR}" "" PARENT_SCOPE)
	else()
		set("${OUT_VAR}" ${ELEMENT} PARENT_SCOPE)
	endif()
endfunction()



function(GLD_import_full_group NAME_GLD_MODULE MY_JSON_STRING ELEMENT_TO_CHECK TYPE_VARIABLE)
	json_get_type(TYPE ${MY_JSON_STRING} ${ELEMENT_TO_CHECK})
	#message("target type = ${TYPE}")
	if (${TYPE} STREQUAL "OBJECT")
		json_object_keys(LIST_KEY ${MY_JSON_STRING} ${ELEMENT_TO_CHECK})
		foreach (III ${LIST_KEY})
			# check the target, no need to had unknown target ...
			if (${III} STREQUAL "*")
				json_object_values(DATA_TARGET ${MY_JSON_STRING} ${ELEMENT_TO_CHECK} "*")
				#message("target(*) data: ${DATA_TARGET}")
				GLD_import_full(NAME_GLD_MODULE DATA_TARGET)
			elseif (${III} STREQUAL ${TYPE_VARIABLE})
				json_object_values(DATA_TARGET ${MY_JSON_STRING} ${ELEMENT_TO_CHECK} "${III}")
				GLD_import_full(NAME_GLD_MODULE DATA_TARGET)
				#message("target(${III}) data: ${DATA_TARGET}")
			else()
				message("TODO: get dependency manage '${ELEMENT_TO_CHECK}' : ${III}") 
			endif()
		endforeach()
	elseif(${TYPE} STREQUAL "NOTFOUND" OR ${TYPE} STREQUAL "NULL")
		# nothing to do ..
	else()
		message("ERROR : '${ELEMENT_TO_CHECK}' can not be other than an json object : ${TYPE}")
	endif()
endfunction()
	

function(GLD_import_element_dependency NAME_GLD_MODULE MY_JSON_STRING)
	GLD_get_module_name(LOCAL_MODULE_NAME ${NAME_GLD_MODULE})
	##########################################################
	## DEPENDENCY:
	##########################################################
	json_get_type(TYPE ${MY_JSON_STRING} "dependency")
	set(LIST_VALUE "")
	set(LIST_OPTIONAL_VALUE "")
	#message("Dependency type = ${TYPE}")
	if (${TYPE} STREQUAL "ARRAY")
		json_size(SIZE ${MY_JSON_STRING} "dependency")
		#message("Dependency SIZE = ${SIZE}")
		json_get_data(OBJECT_DATA ${MY_JSON_STRING} "dependency")
		MATH(EXPR SIZE "${SIZE}-1")
		set(VAR_OUT_TMP "")
		foreach(IDX RANGE ${SIZE})
			json_get_data(ELEMENT ${OBJECT_DATA} ${IDX})
			json_get_type(TYPE ${OBJECT_DATA} ${IDX})
			if (${TYPE} STREQUAL "STRING")
				message("   - <dep> : ${ELEMENT}")
				list(APPEND VAR_OUT_TMP ${ELEMENT})
			elseif (${TYPE} STREQUAL "OBJECT")
				json_get_type(TYPE ${ELEMENT} "name")
				if (${TYPE} STREQUAL "STRING")
					json_get_data(DEPENDENCY_NAME ${ELEMENT} "name")
					json_get_type(TYPE ${ELEMENT} "optional")
					#message("optional type = ${TYPE} <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< ${DEPENDENCY_NAME}")
					if (${TYPE} STREQUAL "BOOLEAN")
						json_get_data(DEPENDENCY_OPTIONAL ${ELEMENT} "optional")
						if (${DEPENDENCY_OPTIONAL})
							message("   - <dep> : ${DEPENDENCY_NAME} (optional) ==> not managed now ...")
							#message("optional value ==========================> '${DEPENDENCY_OPTIONAL}' ==> MAYBE")
							list(APPEND LIST_OPTIONAL_VALUE ${DEPENDENCY_NAME})
						else()
							message("   - <dep> : ${DEPENDENCY_NAME}")
							#message("optional value ==========================> '${DEPENDENCY_OPTIONAL}' ==> MUST")
							list(APPEND VAR_OUT_TMP ${DEPENDENCY_NAME})
						endif()
					else()
						message("   - <dep> : ${DEPENDENCY_NAME}")
						list(APPEND VAR_OUT_TMP ${DEPENDENCY_NAME})
					endif()
					#message("optional type = ${TYPE} <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< ${DEPENDENCY_NAME}")
				else()
					message("Dependency 'name' is not a string or is missing type: ${TYPE}")
				endif()
			else()
				message("dependency element not manage data : ${ELEMENT}")
				## TODO add in dependency if optional : check if the element exit in the current module list ...
				
			endif()
		endforeach()
		list(APPEND LIST_VALUE ${VAR_OUT_TMP})
	elseif(${TYPE} STREQUAL "NOTFOUND")
		return()
	endif()
	set(MODULE_MAP_${LOCAL_MODULE_NAME}_DEPENDENCY ${MODULE_MAP_${LOCAL_MODULE_NAME}_DEPENDENCY} ${LIST_VALUE} CACHE INTERNAL "")

endfunction()

function(GLD_import_element_source NAME_GLD_MODULE MY_JSON_STRING)
	GLD_get_module_name(LOCAL_MODULE_NAME ${NAME_GLD_MODULE})
	##########################################################
	## SOURCE:
	##########################################################
	set(LIST_VALUE "")
	json_get_type(TYPE ${MY_JSON_STRING} "source")
	if (${TYPE} STREQUAL "STRING")
		json_get_data(OBJECT_DATA ${MY_JSON_STRING} "source")
		message("   - <src> : ${OBJECT_DATA}")
		list(APPEND LIST_VALUE ${OBJECT_DATA})
	elseif (${TYPE} STREQUAL "ARRAY")
		json_get_data(OBJECT_DATA ${MY_JSON_STRING} "source")
		json_size(SIZE ${MY_JSON_STRING} "source")
		#message("Dependency SIZE = ${SIZE}")
		MATH(EXPR SIZE "${SIZE}-1")
		set(VAR_OUT_TMP "")
		foreach(IDX RANGE ${SIZE})
			json_get_data(ELEMENT ${OBJECT_DATA} ${IDX})
			json_get_type(TYPE ${OBJECT_DATA} ${IDX})
			if (${TYPE} STREQUAL "STRING")
				message("   - <src> : ${ELEMENT}")
				list(APPEND LIST_VALUE ${ELEMENT})
			elseif (${TYPE} STREQUAL "OBJECT")
				json_get_type(TYPE ${ELEMENT} "source")
				json_get_data(ELEMENT_SOURCE ${ELEMENT} "source")
				if (${TYPE} STREQUAL "STRING")
					message("   - <src> : ${ELEMENT_SOURCE}")
					list(APPEND LIST_VALUE ${ELEMENT_SOURCE})
					#message("optional type = ${TYPE} <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< ${DEPENDENCY_NAME}")
				elseif (${TYPE} STREQUAL "ARRAY")
					message("   - <src> : ${ELEMENT_SOURCE}")
					list(APPEND LIST_VALUE ${ELEMENT_SOURCE})
				else()
					message("Dependency 'name' is not a string or is missing type: ${TYPE}")
				endif()
				# TODO: add the source specific flags or other things ... 
			else()
				message("'source' element not manage data : ${ELEMENT}")
				## TODO add in dependency if optional : check if the element exit in the current module list ...
			endif()
		endforeach()
	elseif (${TYPE} STREQUAL "OBJECT")
		# todo: manage object with source like { "c++":[...]...}
	elseif(${TYPE} STREQUAL "NOTFOUND")
		return()
	else()
		message(WARNING "Unmanaged type='${TYPE}' for 'source' node")
	endif()
	set(MODULE_MAP_${LOCAL_MODULE_NAME}_SOURCE ${MODULE_MAP_${LOCAL_MODULE_NAME}_SOURCE} ${LIST_VALUE} CACHE INTERNAL "")
endfunction()

function(GLD_import_element_header NAME_GLD_MODULE MY_JSON_STRING)
	GLD_get_module_name(LOCAL_MODULE_NAME ${NAME_GLD_MODULE})
	##########################################################
	## HEADER:
	##########################################################
	set(LIST_VALUE "")
	json_get_type(TYPE ${MY_JSON_STRING} "header")
	if (${TYPE} STREQUAL "STRING")
		json_get_data(OBJECT_DATA ${MY_JSON_STRING} "header")
		message("   - <header> : ${OBJECT_DATA}")
		list(APPEND LIST_VALUE ${OBJECT_DATA})
	elseif (${TYPE} STREQUAL "ARRAY")
		json_get_data(OBJECT_DATA ${MY_JSON_STRING} "header")
		json_size(SIZE ${MY_JSON_STRING} "header")
		#message("Dependency SIZE = ${SIZE}")
		MATH(EXPR SIZE "${SIZE}-1")
		set(VAR_OUT_TMP "")
		foreach(IDX RANGE ${SIZE})
			json_get_data(ELEMENT ${OBJECT_DATA} ${IDX})
			json_get_type(TYPE ${OBJECT_DATA} ${IDX})
			if (${TYPE} STREQUAL "STRING")
				message("   - <header> : ${ELEMENT}")
				list(APPEND LIST_VALUE ${ELEMENT})
			elseif (${TYPE} STREQUAL "OBJECT")
				json_get_type(TYPE ${ELEMENT} "source")
				json_get_data(ELEMENT_SOURCE ${ELEMENT} "source")
				if (${TYPE} STREQUAL "STRING")
					message("   - <header> : ${ELEMENT_SOURCE}")
					list(APPEND LIST_VALUE ${ELEMENT_SOURCE})
					#message("optional type = ${TYPE} <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< ${DEPENDENCY_NAME}")
				elseif (${TYPE} STREQUAL "ARRAY")
					message("   - <header> : ${ELEMENT_SOURCE}")
					list(APPEND LIST_VALUE ${ELEMENT_SOURCE})
				else()
					message("Dependency 'name' is not a string or is missing type: ${TYPE}")
				endif()
				# TODO: add the source specific flags or other things ... 
			else()
				message("'header' element not manage data : ${ELEMENT}")
				## TODO add in dependency if optional : check if the element exit in the current module list ...
			endif()
		endforeach()
	elseif (${TYPE} STREQUAL "OBJECT")
		json_get_data(OBJECT_DATA ${MY_JSON_STRING} "header")
		# todo: manage object with source like { "c++":[...]...}
	elseif(${TYPE} STREQUAL "NOTFOUND")
		return()
	else()
		message(WARNING "Unmanaged type='${TYPE}' for 'header' node")
	endif()
	set(MODULE_MAP_${LOCAL_MODULE_NAME}_HEADER ${MODULE_MAP_${LOCAL_MODULE_NAME}_HEADER} ${LIST_VALUE} CACHE INTERNAL "")
endfunction()

function(GLD_import_element_path NAME_GLD_MODULE MY_JSON_STRING)
	GLD_get_module_name(LOCAL_MODULE_NAME ${NAME_GLD_MODULE})
	##########################################################
	## PATH:
	##########################################################
	set(LIST_VALUE "")
	json_get_type(TYPE ${MY_JSON_STRING} "path")
	if (${TYPE} STREQUAL "STRING")
		json_get_data(OBJECT_DATA ${MY_JSON_STRING} "path")
		message("   - <header> : ${OBJECT_DATA}")
		list(APPEND LIST_VALUE ${OBJECT_DATA})
	elseif (${TYPE} STREQUAL "ARRAY")
		json_get_data(OBJECT_DATA ${MY_JSON_STRING} "path")
		json_size(SIZE ${MY_JSON_STRING} "path")
		#message("Dependency SIZE = ${SIZE}")
		MATH(EXPR SIZE "${SIZE}-1")
		set(VAR_OUT_TMP "")
		foreach(IDX RANGE ${SIZE})
			json_get_data(ELEMENT ${OBJECT_DATA} ${IDX})
			json_get_type(TYPE ${OBJECT_DATA} ${IDX})
			if (${TYPE} STREQUAL "STRING")
				message("   - <header> : ${ELEMENT}")
				list(APPEND LIST_VALUE ${ELEMENT})
			else()
				message("'path' element not manage data : ${ELEMENT}")
				## TODO add in dependency if optional : check if the element exit in the current module list ...
			endif()
		endforeach()
	elseif (${TYPE} STREQUAL "OBJECT")
		json_get_data(OBJECT_DATA ${MY_JSON_STRING} "path")
		# todo: manage object with source like { "c++":[...]...}
	elseif(${TYPE} STREQUAL "NOTFOUND")
		return()
	else()
		message(WARNING "Unmanaged type='${TYPE}' for 'path' node")
	endif()
	set(MODULE_MAP_${LOCAL_MODULE_NAME}_INCLUDE_LOCAL ${MODULE_MAP_${LOCAL_MODULE_NAME}_INCLUDE_LOCAL} ${LIST_VALUE} CACHE INTERNAL "")
endfunction()

function(GLD_import_element_compilation_version NAME_GLD_MODULE MY_JSON_STRING)
	GLD_get_module_name(LOCAL_MODULE_NAME ${NAME_GLD_MODULE})
	##########################################################
	## COMPILATION-VERSION:
	##########################################################

endfunction()

function(GLD_import_element_copy NAME_GLD_MODULE MY_JSON_STRING)
	GLD_get_module_name(LOCAL_MODULE_NAME ${NAME_GLD_MODULE})
	##########################################################
	## COPY:
	##########################################################

endfunction()

##
## @brief Get the list of all dependency even if they are optional.
## @param[out] VAR_OUT list of dependency library
## @param[out] VAR_OPTIONAL_OUT list of optional dependency library
## @param[in] MY_JSON_STRING Json string
## @note This function is dependent of the target  
##
function(GLD_import_full NAME_GLD_MODULE MY_JSON_STRING)
	GLD_import_element_dependency(${NAME_GLD_MODULE} ${MY_JSON_STRING})
	GLD_import_element_source(${NAME_GLD_MODULE} ${MY_JSON_STRING})
	GLD_import_element_header(${NAME_GLD_MODULE} ${MY_JSON_STRING})
	GLD_import_element_path(${NAME_GLD_MODULE} ${MY_JSON_STRING})
	GLD_import_element_compilation_version(${NAME_GLD_MODULE} ${MY_JSON_STRING})
	GLD_import_element_copy(${NAME_GLD_MODULE} ${MY_JSON_STRING})
	
	GLD_import_full_group(${NAME_GLD_MODULE} ${MY_JSON_STRING} "target" ${GLD_TARGET})
	
	GLD_import_full_group(${NAME_GLD_MODULE} ${MY_JSON_STRING} "mode" ${GLD_MODE})
	
	GLD_import_full_group(${NAME_GLD_MODULE} ${MY_JSON_STRING} "arch" ${GLD_ARCH})
	
	GLD_import_full_group(${NAME_GLD_MODULE} ${MY_JSON_STRING} "bus-size" ${GLD_BUS_SIZE})
	
	GLD_import_full_group(${NAME_GLD_MODULE} ${MY_JSON_STRING} "compilator" ${GLD_COMPILATOR})
	
	GLD_import_full_group(${NAME_GLD_MODULE} ${MY_JSON_STRING} "sanity-compilation" ${GLD_SANITY_MODE})
	
endfunction()


function(GLD_load_from_file_if_needed VAR_OUT LIBRARY_PATH ELEMENT)
	#message("Check element: ${ELEMENT}")
	if("${ELEMENT}" MATCHES "file://*")
		#message("match file://")
		string(REPLACE "file://" "" FILENAME ${ELEMENT})
		#message("   ==> ${FILENAME}")
		file (STRINGS "${LIBRARY_PATH}/${FILENAME}" DATA_READ)
		set(${VAR_OUT} "${DATA_READ}" PARENT_SCOPE)
	else()
		set(${VAR_OUT} "${ELEMENT}" PARENT_SCOPE)
	endif()
endfunction()

function(GLD_import NAME_GLD_MODULE)
	GLD_get_module_name(LOCAL_MODULE_NAME ${NAME_GLD_MODULE})


	#	set(MODULE_MAP_${LOCAL_MODULE_NAME}_FOLDER ${FOLDER} CACHE INTERNAL "")
	#	set(MODULE_MAP_${LOCAL_MODULE_NAME}_FILENAME ${FILENAME} CACHE INTERNAL "")
	#	set(MODULE_MAP_${LOCAL_MODULE_NAME}_NAME ${NAME_GLD_MODULE} CACHE INTERNAL "")
	#	set(MODULE_MAP_LIST ${MODULE_MAP_LIST} ${NAME_GLD_MODULE} CACHE INTERNAL "")
	# Read the JSON file.
	set(MY_JSON_STRING ${MODULE_MAP_${LOCAL_MODULE_NAME}_JSON})
	
	# Loop through each element of the JSON array (indices 0 though 1).
	
	json_get_element(LIBRARY_TYPE         ${MY_JSON_STRING} "type")
	json_get_element(LIBRARY_SUB_TYPE     ${MY_JSON_STRING} "sub-type")
	json_get_element(LIBRARY_GROUP_ID     ${MY_JSON_STRING} "group-id")
	json_get_element(LIBRARY_DECRIPTION   ${MY_JSON_STRING} "description")
	json_get_element(LIBRARY_LICENCE      ${MY_JSON_STRING} "license")
	json_get_element(LIBRARY_LICENCE_FILE ${MY_JSON_STRING} "license-file")
	json_get_element(LIBRARY_MAINTAINER   ${MY_JSON_STRING} "maintainer")
	json_get_element(LIBRARY_AUTHORS      ${MY_JSON_STRING} "author")
	json_get_element(LIBRARY_VERSION      ${MY_JSON_STRING} "version")
	json_get_element(CODE_QUALITY         ${MY_JSON_STRING} "code-quality")
	
	message("LIBRARY              : ${LIBRARY_GROUP_ID}:${NAME_GLD_MODULE}")
	message("LIBRARY_TYPE         : ${LIBRARY_TYPE} / ${LIBRARY_SUB_TYPE}")
	message("LIBRARY_DECRIPTION   : ${LIBRARY_DECRIPTION}")
	message("LIBRARY_LICENCE      : ${LIBRARY_LICENCE}")
	if (LIBRARY_LICENCE_FILE)
		message("LIBRARY_LICENCE_FILE : ${LIBRARY_LICENCE_FILE}")
		#GLD_load_from_file_if_needed(LIBRARY_LICENCE_FILE "${MODULE_MAP_${LOCAL_MODULE_NAME}_FOLDER}" "${LIBRARY_LICENCE_FILE}")
		#message("                 ==> : ${LIBRARY_LICENCE_FILE}")
	endif()
	if (LIBRARY_MAINTAINER)
		message("LIBRARY_MAINTAINER   : ${LIBRARY_MAINTAINER}")
		GLD_load_from_file_if_needed(LIBRARY_MAINTAINER "${MODULE_MAP_${LOCAL_MODULE_NAME}_FOLDER}" "${LIBRARY_MAINTAINER}")
		message("                 ==> : ${LIBRARY_MAINTAINER}")
	endif()
	if (LIBRARY_AUTHORS)
		message("LIBRARY_AUTHORS      : ${LIBRARY_AUTHORS}")
		GLD_load_from_file_if_needed(LIBRARY_AUTHORS "${MODULE_MAP_${LOCAL_MODULE_NAME}_FOLDER}" "${LIBRARY_AUTHORS}")
		message("                 ==> : ${LIBRARY_AUTHORS}")
	endif()
	if (LIBRARY_VERSION)
		message("LIBRARY_VERSION      : ${LIBRARY_VERSION}")
		GLD_load_from_file_if_needed(LIBRARY_VERSION "${MODULE_MAP_${LOCAL_MODULE_NAME}_FOLDER}" "${LIBRARY_VERSION}")
		message("                 ==> : ${LIBRARY_VERSION}")
		# NOTE CMAKE does not support DEV_MODEL, then we use the lact ELEMENT for dev version (666)
		string(REPLACE "-dev" ".666" LIBRARY_VERSION ${LIBRARY_VERSION}) 
	endif()
	
	#string(REPLACE "-" "_" LIBRARY_NAME222 ${NAME_GLD_MODULE})
	set(LIBRARY_NAME222 ${NAME_GLD_MODULE})
	if (LIBRARY_VERSION)
		project(${LIBRARY_NAME222} VERSION ${LIBRARY_VERSION})
		set(${LIBRARY_NAME222} PROPERTIES CPACK_PACKAGE_VERSION ${LIBRARY_VERSION})
	else()
		project(${LIBRARY_NAME222})
	endif()
	
	set(MODULE_MAP_${LOCAL_MODULE_NAME}_INCLUDE_LOCAL "" CACHE INTERNAL "")
	
	# TODO : Remove if no element in header...
	if (MODULE_MAP_${LOCAL_MODULE_NAME}_HEADER)
		set(MODULE_MAP_${LOCAL_MODULE_NAME}_INCLUDE_PUBLIC "${GLD_GLOBAL_BUILD_FOLDER}${NAME_GLD_MODULE}/include/" CACHE INTERNAL "")
	endif()
	# remove if no library generated
	set(MODULE_MAP_${LOCAL_MODULE_NAME}_LIB_PATH "${GLD_GLOBAL_STAGING_FOLDER}${NAME_GLD_MODULE}/lib/" CACHE INTERNAL "")
	# remove if no doc ...
	set(MODULE_MAP_${LOCAL_MODULE_NAME}_DOC_PATH "${GLD_GLOBAL_STAGING_FOLDER}${NAME_GLD_MODULE}/doc/" CACHE INTERNAL "")
	
	set(MODULE_MAP_${LOCAL_MODULE_NAME}_DEPENDENCY "" CACHE INTERNAL "")
	set(MODULE_MAP_${LOCAL_MODULE_NAME}_SOURCE "" CACHE INTERNAL "")
	set(MODULE_MAP_${LOCAL_MODULE_NAME}_HEADER "" CACHE INTERNAL "")
	
	GLD_import_full(${NAME_GLD_MODULE} ${MY_JSON_STRING})
	set(TMP_LIST "")
	foreach(III ${MODULE_MAP_${LOCAL_MODULE_NAME}_INCLUDE_LOCAL})
		get_filename_component(BASE_FOLDER ${MODULE_MAP_${LOCAL_MODULE_NAME}_FOLDER}/${III} ABSOLUTE)
		list(APPEND TMP_LIST "${BASE_FOLDER}")
	endforeach()
	set(MODULE_MAP_${LOCAL_MODULE_NAME}_INCLUDE_LOCAL "${TMP_LIST}" CACHE INTERNAL "")
	
	message("    _INCLUDE_LOCAL : ${MODULE_MAP_${LOCAL_MODULE_NAME}_INCLUDE_LOCAL}")
	message("    _INCLUDE_PUBLIC: ${MODULE_MAP_${LOCAL_MODULE_NAME}_INCLUDE_PUBLIC}")
	message("    _LIB_PATH      : ${MODULE_MAP_${LOCAL_MODULE_NAME}_LIB_PATH}")
	message("    _DOC_PATH      : ${MODULE_MAP_${LOCAL_MODULE_NAME}_DOC_PATH}")
	message("    _DEPENDENCY    : ${MODULE_MAP_${LOCAL_MODULE_NAME}_DEPENDENCY}")
	message("    _SOURCE        : ${MODULE_MAP_${LOCAL_MODULE_NAME}_SOURCE}")
	message("    _HEADER        : ${MODULE_MAP_${LOCAL_MODULE_NAME}_HEADER}")
	
	set(TMP_LIST "")
	foreach(III ${MODULE_MAP_${LOCAL_MODULE_NAME}_SOURCE})
		get_filename_component(BASE_FOLDER ${MODULE_MAP_${LOCAL_MODULE_NAME}_FOLDER}/${III} ABSOLUTE)
		list(APPEND TMP_LIST "${BASE_FOLDER}")
	endforeach()
	add_library(${LIBRARY_NAME222}_OBJ OBJECT ${TMP_LIST})
	# allow relocation code for shared library:
	set_property(TARGET ${LIBRARY_NAME222}_OBJ PROPERTY POSITION_INDEPENDENT_CODE 1)
	
	
	foreach(III ${MODULE_MAP_${LOCAL_MODULE_NAME}_HEADER})
		configure_file(${MODULE_MAP_${LOCAL_MODULE_NAME}_FOLDER}/${III} ${MODULE_MAP_${LOCAL_MODULE_NAME}_INCLUDE_PUBLIC}/${III} COPYONLY)
	endforeach()
	
	set(TMP_LIST ${MODULE_MAP_${LOCAL_MODULE_NAME}_INCLUDE_LOCAL})
	list(APPEND TMP_LIST ${MODULE_MAP_${LOCAL_MODULE_NAME}_INCLUDE_PUBLIC})
	target_include_directories(${LIBRARY_NAME222}_OBJ PUBLIC "${TMP_LIST}")
	add_library(${LIBRARY_NAME222}_dynamic SHARED $<TARGET_OBJECTS:${LIBRARY_NAME222}_OBJ>)
	add_library(${LIBRARY_NAME222}_static STATIC $<TARGET_OBJECTS:${LIBRARY_NAME222}_OBJ>)
	
	if ("${GLD_TARGET}" STREQUAL "Windows")
		set_target_properties(${LIBRARY_NAME222}_dynamic PROPERTIES OUTPUT_NAME ${LIBRARY_NAME222})
		# static will keep the element static at the end (the windows architecture fore shared object need to have a static library to access to the DLL ==> create a conflict!!!
	else()
		set_target_properties(${LIBRARY_NAME222}_dynamic PROPERTIES OUTPUT_NAME ${LIBRARY_NAME222})
		set_target_properties(${LIBRARY_NAME222}_static PROPERTIES OUTPUT_NAME ${LIBRARY_NAME222})
	endif()
	if (LIBRARY_VERSION)
		set_target_properties(${LIBRARY_NAME222}_dynamic PROPERTIES VERSION ${LIBRARY_VERSION})
		set_target_properties(${LIBRARY_NAME222}_dynamic PROPERTIES SOVERSION ${LIBRARY_VERSION})
	endif()
	if (LIBRARY_DECRIPTION)
		set_target_properties(${LIBRARY_NAME222}_dynamic PROPERTIES DESCRIPTION ${LIBRARY_DECRIPTION})
	endif()
	
	# install dynamic & static library
	install(TARGETS ${LIBRARY_NAME222}_dynamic EXPORT ${LIBRARY_NAME222}Targets
	        RUNTIME DESTINATION ${MODULE_MAP_${LOCAL_MODULE_NAME}_LIB_PATH}
	         )
	install(TARGETS ${LIBRARY_NAME222}_static
	        RUNTIME DESTINATION ${MODULE_MAP_${LOCAL_MODULE_NAME}_LIB_PATH})
	
	
	#install(TARGETS ${LIBRARY_NAME222} EXPORT ${LIBRARY_NAME222}Targets
	#  LIBRARY DESTINATION lib
	#  ARCHIVE DESTINATION lib
	#  RUNTIME DESTINATION bin
	#  INCLUDES DESTINATION include
	#)
	# install exported headers
	# this copy all the headers in a single folder:
	#install(FILES ${EXPORT_HEADER_LIST} DESTINATION include)
	# this keep the basic path for each folders:
	set(BASE "${PROJECT_SOURCE_DIR}/install")
	foreach(ITEM ${EXPORT_HEADER_LIST})
	  get_filename_component(ITEM_PATH ${ITEM} PATH)
	  string(REPLACE ${BASE} "" ITEM_PATH ${ITEM_PATH})
	  install(FILES ${ITEM}
	          DESTINATION "include/${ITEM_PATH}"
	          COMPONENT Devel)
	endforeach()
	
	
	
	
	include(CMakePackageConfigHelpers)
	#write_basic_package_version_file(
	#  "${CMAKE_CURRENT_BINARY_DIR}/${LIBRARY_NAME222}/${LIBRARY_NAME222}ConfigVersion.cmake"
	#  VERSION ${LIBRARY_VERSION}
	#  COMPATIBILITY AnyNewerVersion
	#)
	#
	#export(EXPORT ${LIBRARY_NAME222}Targets
	#  FILE "${CMAKE_CURRENT_BINARY_DIR}/${LIBRARY_NAME222}/${LIBRARY_NAME222}Targets.cmake"
	#  NAMESPACE Upstream::
	#)
	##configure_file(cmake/${LIBRARY_NAME222}Config.cmake
	##  "${CMAKE_CURRENT_BINARY_DIR}/${LIBRARY_NAME222}/${LIBRARY_NAME222}Config.cmake"
	##  COPYONLY
	##)
	
	set(CONFIG_PACKAGE_LOCATION cmake/${LIBRARY_NAME222})
	install(EXPORT ${LIBRARY_NAME222}Targets
	  FILE
	    ${LIBRARY_NAME222}Targets.cmake
	  NAMESPACE
	    ${LIBRARY_NAME222}::
	  DESTINATION
	    ${CONFIG_PACKAGE_LOCATION}
	)
	#install(
	#  FILES
	#    cmake/${LIBRARY_NAME222}Config.cmake
	#    "${CMAKE_CURRENT_BINARY_DIR}/${LIBRARY_NAME222}/${LIBRARY_NAME222}ConfigVersion.cmake"
	#  DESTINATION
	#    ${CONFIG_PACKAGE_LOCATION}
	#  COMPONENT
	#    Devel
	#)
	message("CMAKE_INSTALL_LIBDIR===${CMAKE_INSTALL_LIBDIR}")
	
	
endfunction()


function(sdfsqdfqsdfqrezesrdtygfhsg LIST_OF_MODULE_AVAILLABLE)
	include(CMakePackageConfigHelpers)
	configure_package_config_file(cmake/${LIBRARY_NAME222}Config.cmake.in
	  "${PROJECT_BINARY_DIR}/${LIBRARY_NAME222}Config.cmake"
	  INSTALL_DESTINATION ${CONFIG_PACKAGE_LOCATION}
	  NO_SET_AND_CHECK_MACRO
	  NO_CHECK_REQUIRED_COMPONENTS_MACRO)
	write_basic_package_version_file(
	  "${PROJECT_BINARY_DIR}/${LIBRARY_NAME222}ConfigVersion.cmake"
	  VERSION ${LIBRARY_VERSION}
	  COMPATIBILITY SameMajorVersion)
	install(
	  FILES
	  "${PROJECT_BINARY_DIR}/${LIBRARY_NAME222}Config.cmake"
	  "${PROJECT_BINARY_DIR}/${LIBRARY_NAME222}ConfigVersion.cmake"
	  DESTINATION ${CONFIG_PACKAGE_LOCATION}
	  COMPONENT Devel)
	
	
endfunction()


function(GLD_generate_cmake_wrapping LIST_OF_MODULE_AVAILLABLE)
	message("Generate cmake wrapping")
	foreach(NAME_GLD_MODULE ${LIST_OF_MODULE_AVAILLABLE})
		GLD_get_module_name(LOCAL_MODULE_NAME ${NAME_GLD_MODULE})
		message("Import: ${NAME_GLD_MODULE}")
		#MODULE_MAP_LIST_DEPENDENCE_RESOLVED
		GLD_import(${NAME_GLD_MODULE})
	endforeach()
	message("Generate cmake wrapping (DONE)")
endfunction()


##
## @brief List all folder in a specific inout folder.
## @param[out] VAR_OUT Result list of folders.
## @param[in] BASE_FOLDER Basic folder to parse.
##
function(sub_dir_list VAR_OUT BASE_FOLDER)
  #message("                                 Search: ${BASE_FOLDER}" )
  file(GLOB children "${BASE_FOLDER}/*")
  #message("     ==>>>  ${children}" )
  set(dirlist "")
  foreach(child ${children})
    #message("     -  ${child}" )
    if(IS_DIRECTORY ${child})
      #message("         ==> is directory" )
      list(APPEND dirlist ${child})
    endif()
  endforeach()
  set(${VAR_OUT} ${dirlist} PARENT_SCOPE)
endfunction()


##
## @brief Recursive search of a specific patter (stop whan find the pattern in a folder.
##        (have a limit of parsing ==> optimise resarch in a worktree).
## @param[out] VAR_OUT List of all files that corespond of the reg-exp
## @param[in] BASE_FOLDER Basic folder to parse.
## @param[in] REG_EXP Regular expression to search the data.
## @param[in] LIMIT Lismit of folder to recursively parse.
##
function(find_all_files VAR_OUT BASE_FOLDER REG_EXP LIMIT)
	if (${LIMIT} LESS_EQUAL 0)
		set(${VAR_OUT} "" PARENT_SCOPE)
		return()
	endif()
	MATH(EXPR LIMIT "${LIMIT}-1")
	get_filename_component(BASE_FOLDER ${BASE_FOLDER} ABSOLUTE)
	#message("KK Search in subDiratory: ${BASE_FOLDER}/${REG_EXP}" )
	file(GLOB GLD_FILES "${BASE_FOLDER}/${REG_EXP}")
	#message("Find file: '${GLD_FILES}'" )
	if("${GLD_FILES}" STREQUAL "")
		#message("Search in subDiratory: ${BASE_FOLDER}" )
		# no element continue search...
		set(SUBDIRS "")
		sub_dir_list(SUBDIRS "${BASE_FOLDER}")
		#message("            =!=> : ${SUBDIRS}" )
		foreach(ELEM ${SUBDIRS})
			get_filename_component(DIR_NAME_RELATIVE ${ELEM} NAME)
			#message("            =!=> DIR_NAME_RELATIVE = ${DIR_NAME_RELATIVE}" )
			if("${DIR_NAME_RELATIVE}" STREQUAL ".git" OR "${DIR_NAME_RELATIVE}" STREQUAL ".island" OR "${DIR_NAME_RELATIVE}" STREQUAL "archive" OR "${DIR_NAME_RELATIVE}" STREQUAL "out" OR "${DIR_NAME_RELATIVE}" STREQUAL "target")
				continue()
			endif()
			if("${ELEM}" STREQUAL "${BASE_FOLDER}" OR "${ELEM}" STREQUAL "${BASE_FOLDER}/")
				continue()
			endif()
			#message("        element: ${ELEM}" )
			#message("    BASE_FOLDER: ${BASE_FOLDER}" )
			find_all_files(OUT_SUB_LIST "${ELEM}" "${REG_EXP}" ${LIMIT})
			list(APPEND GLD_FILES ${OUT_SUB_LIST})
		endforeach()
	endif()
	set(${VAR_OUT} ${GLD_FILES} PARENT_SCOPE)
endfunction()


function(GLD_get_full_dependency_group VAR_OUT VAR_OPTIONAL_OUT MY_JSON_STRING ELEMENT_TO_CHECK TYPE_VARIABLE)
	set(LIST_VALUE "")
	set(LIST_OPTIONAL_VALUE "")
	json_get_type(TYPE ${MY_JSON_STRING} ${ELEMENT_TO_CHECK})
	#message("target type = ${TYPE}")
	if (${TYPE} STREQUAL "OBJECT")
		json_object_keys(LIST_KEY ${MY_JSON_STRING} ${ELEMENT_TO_CHECK})
		foreach (III ${LIST_KEY})
			# check the target, no need to had unknown target ...
			if (${III} STREQUAL "*")
				json_object_values(DATA_TARGET ${MY_JSON_STRING} ${ELEMENT_TO_CHECK} "*")
				#message("target(*) data: ${DATA_TARGET}")
				GLD_get_full_dependency(VAR_OUT_TMP LIST_OPTIONAL_VALUE_TMP DATA_TARGET)
				list(APPEND LIST_VALUE ${DATA_TARGET})
				list(APPEND LIST_OPTIONAL_VALUE ${LIST_OPTIONAL_VALUE_TMP})
			elseif (${III} STREQUAL ${TYPE_VARIABLE})
				json_object_values(DATA_TARGET ${MY_JSON_STRING} ${ELEMENT_TO_CHECK} "${III}")
				GLD_get_full_dependency(VAR_OUT_TMP LIST_OPTIONAL_VALUE_TMP DATA_TARGET)
				#message("target(${III}) data: ${DATA_TARGET}")
				list(APPEND LIST_VALUE ${VAR_OUT_TMP})
				list(APPEND LIST_OPTIONAL_VALUE ${LIST_OPTIONAL_VALUE_TMP})
			else()
				message("TODO: get dependency manage '${ELEMENT_TO_CHECK}' : ${III}") 
			endif()
		endforeach()
	elseif(${TYPE} STREQUAL "NOTFOUND" OR ${TYPE} STREQUAL "NULL")
		# nothing to do ..
	else()
		message("ERROR : '${ELEMENT_TO_CHECK}' can not be other than an json object : ${TYPE}")
	endif()
	set(${VAR_OUT} ${LIST_VALUE} PARENT_SCOPE)
	set(${VAR_OPTIONAL_OUT} ${LIST_OPTIONAL_VALUE} PARENT_SCOPE)
endfunction()
	

##
## @brief Get the list of all dependency even if they are optional.
## @param[out] VAR_OUT list of dependency library
## @param[out] VAR_OPTIONAL_OUT list of optional dependency library
## @param[in] MY_JSON_STRING Json string
## @note This function is dependent of the target  
##
function(GLD_get_full_dependency VAR_OUT VAR_OPTIONAL_OUT MY_JSON_STRING)
	json_get_type(TYPE ${MY_JSON_STRING} "dependency")
	set(LIST_VALUE "")
	set(LIST_OPTIONAL_VALUE "")
	#message("Dependency type = ${TYPE}")
	if (${TYPE} STREQUAL "ARRAY")
		json_size(SIZE ${MY_JSON_STRING} "dependency")
		#message("Dependency SIZE = ${SIZE}")
		json_get_data(OBJECT_DATA ${MY_JSON_STRING} "dependency")
		MATH(EXPR SIZE "${SIZE}-1")
		set(VAR_OUT_TMP "")
		foreach(IDX RANGE ${SIZE})
			json_get_data(ELEMENT ${OBJECT_DATA} ${IDX})
			json_get_type(TYPE ${OBJECT_DATA} ${IDX})
			if (${TYPE} STREQUAL "STRING")
				message("   - : ${ELEMENT}")
				list(APPEND VAR_OUT_TMP ${ELEMENT})
			elseif (${TYPE} STREQUAL "OBJECT")
				json_get_type(TYPE ${ELEMENT} "name")
				if (${TYPE} STREQUAL "STRING")
					json_get_data(DEPENDENCY_NAME ${ELEMENT} "name")
					json_get_type(TYPE ${ELEMENT} "optional")
					#message("optional type = ${TYPE} <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< ${DEPENDENCY_NAME}")
					if (${TYPE} STREQUAL "BOOLEAN")
						json_get_data(DEPENDENCY_OPTIONAL ${ELEMENT} "optional")
						if (${DEPENDENCY_OPTIONAL})
							message("   - : ${DEPENDENCY_NAME} (optional)")
							#message("optional value ==========================> '${DEPENDENCY_OPTIONAL}' ==> MAYBE")
							list(APPEND LIST_OPTIONAL_VALUE ${DEPENDENCY_NAME})
						else()
							message("   - : ${DEPENDENCY_NAME}")
							#message("optional value ==========================> '${DEPENDENCY_OPTIONAL}' ==> MUST")
							list(APPEND VAR_OUT_TMP ${DEPENDENCY_NAME})
						endif()
					else()
						message("   - : ${DEPENDENCY_NAME}")
						list(APPEND VAR_OUT_TMP ${DEPENDENCY_NAME})
					endif()
					#message("optional type = ${TYPE} <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< ${DEPENDENCY_NAME}")
				else()
					message("Dependency 'name' is not a string or is missing type: ${TYPE}")
				endif()
			else()
				message("dependency element not manage data : ${ELEMENT}")
				## TODO add in dependency if optional : check if the element exit in the current module list ...
				
			endif()
		endforeach()
		list(APPEND LIST_VALUE ${VAR_OUT_TMP})
	endif()
	
	GLD_get_full_dependency_group(VAR_OUT_TMP LIST_OPTIONAL_VALUE_TMP MY_JSON_STRING "target" ${GLD_TARGET})
	list(APPEND LIST_VALUE ${VAR_OUT_TMP})
	list(APPEND LIST_OPTIONAL_VALUE ${LIST_OPTIONAL_VALUE_TMP})
	
	GLD_get_full_dependency_group(VAR_OUT_TMP LIST_OPTIONAL_VALUE_TMP MY_JSON_STRING "mode" ${GLD_MODE})
	list(APPEND LIST_VALUE ${VAR_OUT_TMP})
	list(APPEND LIST_OPTIONAL_VALUE ${LIST_OPTIONAL_VALUE_TMP})
	
	GLD_get_full_dependency_group(VAR_OUT_TMP LIST_OPTIONAL_VALUE_TMP MY_JSON_STRING "arch" ${GLD_ARCH})
	list(APPEND LIST_VALUE ${VAR_OUT_TMP})
	list(APPEND LIST_OPTIONAL_VALUE ${LIST_OPTIONAL_VALUE_TMP})
	
	GLD_get_full_dependency_group(VAR_OUT_TMP LIST_OPTIONAL_VALUE_TMP MY_JSON_STRING "bus-size" ${GLD_BUS_SIZE})
	list(APPEND LIST_VALUE ${VAR_OUT_TMP})
	list(APPEND LIST_OPTIONAL_VALUE ${LIST_OPTIONAL_VALUE_TMP})
	
	GLD_get_full_dependency_group(VAR_OUT_TMP LIST_OPTIONAL_VALUE_TMP MY_JSON_STRING "compilator" ${GLD_COMPILATOR})
	list(APPEND LIST_VALUE ${VAR_OUT_TMP})
	list(APPEND LIST_OPTIONAL_VALUE ${LIST_OPTIONAL_VALUE_TMP})
	
	GLD_get_full_dependency_group(VAR_OUT_TMP LIST_OPTIONAL_VALUE_TMP MY_JSON_STRING "sanity-compilation" ${GLD_SANITY_MODE})
	list(APPEND LIST_VALUE ${VAR_OUT_TMP})
	list(APPEND LIST_OPTIONAL_VALUE ${LIST_OPTIONAL_VALUE_TMP})
	
	set(${VAR_OUT} ${LIST_VALUE} PARENT_SCOPE)
	set(${VAR_OPTIONAL_OUT} ${LIST_OPTIONAL_VALUE} PARENT_SCOPE)
endfunction()


function(GLD_read_json_file VAR_OUT JSON_FILE)
	file(READ ${JSON_FILE} MY_JSON_STRING)
	if("${MY_JSON_STRING}" STREQUAL "")
		message(WARNING "Empty json file : '${JSON_FILE}'") 
	else()
		string(REPLACE "    " "" MY_JSON_STRING ${MY_JSON_STRING})
		string(REPLACE "\t" "" MY_JSON_STRING ${MY_JSON_STRING})
		string(REPLACE "\n" "" MY_JSON_STRING ${MY_JSON_STRING})
	endif()
	set(${VAR_OUT} ${MY_JSON_STRING} PARENT_SCOPE)
endfunction()



set(MODULE_MAP_LIST "" CACHE INTERNAL "")
set(MODULE_MAP_LIST_DEPENDENCE_RESOLVED "" CACHE INTERNAL "")

function(GLD_get_module_name VAR_OUT BASE_NAME)
	string(REPLACE "_" "_U_" TMP ${BASE_NAME})
	string(REPLACE "." "_D_" TMP ${BASE_NAME})
	string(REPLACE "-" "_S_" TMP ${TMP})
	set(${VAR_OUT} ${TMP} PARENT_SCOPE)
endfunction()

function(GLD_add_module NAME_GLD_MODULE FOLDER FILENAME)
	GLD_get_module_name(LOCAL_MODULE_NAME ${NAME_GLD_MODULE})
	message("Add module: ${LOCAL_MODULE_NAME} ==> ${NAME_GLD_MODULE} in ${FILENAME}")
	
	# load all the json data:
	GLD_read_json_file(JSON_DATA "${FOLDER}/${FILENAME}.json")
	if("${JSON_DATA}" STREQUAL "")
		message(WARNING "SKIP library: ${NAME_GLD_MODULE}")
	else()
		set(MODULE_MAP_${LOCAL_MODULE_NAME}_FOLDER ${FOLDER} CACHE INTERNAL "")
		set(MODULE_MAP_${LOCAL_MODULE_NAME}_FILENAME ${FILENAME} CACHE INTERNAL "")
		set(MODULE_MAP_${LOCAL_MODULE_NAME}_NAME ${NAME_GLD_MODULE} CACHE INTERNAL "")
		set(MODULE_MAP_LIST ${MODULE_MAP_LIST} ${NAME_GLD_MODULE} CACHE INTERNAL "")
		
		set(MODULE_MAP_${LOCAL_MODULE_NAME}_JSON "${JSON_DATA}" CACHE INTERNAL "")
	endif()
endfunction()

function(GLD_generate_module_without_optionnal_inexistant NAME_GLD_MODULE)
	GLD_get_module_name(LOCAL_MODULE_NAME ${NAME_GLD_MODULE})
	#message("Call : GLD_get_full_dependency(outA, outB, ${MODULE_MAP_${LOCAL_MODULE_NAME}_JSON}) ${NAME_GLD_MODULE} ==> ${LOCAL_MODULE_NAME}")
	GLD_get_full_dependency(DEPENDENCY DEPENDENCY_OPTIONAL ${MODULE_MAP_${LOCAL_MODULE_NAME}_JSON})
	set(MODULE_MAP_${LOCAL_MODULE_NAME}_DEPENDENCY ${DEPENDENCY} CACHE INTERNAL "")
	set(MODULE_MAP_${LOCAL_MODULE_NAME}_DEPENDENCY_OPTIONAL ${DEPENDENCY_OPTIONAL} CACHE INTERNAL "")
endfunction()



function(GLD_is_in_list VAR_OUT ELEM_TO_CHECK LIST_TO_CHECK)
	set(ELEMENT_FIND "true")
	#message("                    verify '${ELEM_TO_CHECK}' in '${LIST_TO_CHECK}'")
	foreach(ELEM ${LIST_TO_CHECK})
		if ("${ELEM_TO_CHECK}" STREQUAL "${ELEM}")
			set(${VAR_OUT} "true" PARENT_SCOPE)
			#message("                        ==> true")
			return()
		endif()
	endforeach()
	set(${VAR_OUT} "false" PARENT_SCOPE)
	#message("                        ==> false")
endfunction()

function(GLD_are_in_list VAR_OUT LIST_VALUES LIST_TO_CHECK)
	set(ELEMENT_FIND "true")
	#message("            verify '${LIST_VALUES}' are in '${LIST_TO_CHECK}'")
	foreach(ELEM ${LIST_VALUES})
		GLD_is_in_list(EXIST "${ELEM}" "${LIST_TO_CHECK}")
		if (${EXIST} STREQUAL "false")
			set(${VAR_OUT} "false" PARENT_SCOPE)
			#message("                =>> false")
			return()
		endif()
	endforeach()
	set(${VAR_OUT} "true" PARENT_SCOPE)
	#message("                =>> true")
endfunction()

## todo: REMOVE OPTIONNAL DEPENDENCY THAT DOES NOT EXIST IN THE LIST
## TODO: display and does not include element that dependency are not resolved and indicate which dependency is not found ...
function(GLD_order_dependency_list VAR_OUT DEPENDENCY_FAILED)
	set(TMP_ORDERED "")####### crypto;edtaa3;luaWrapper;freetype;")
	set(TMP_UN_ADDED "")
	message("===========================================")
	message("== STEP 1 : Add all module without dependency:")
	message("===========================================")
	# step 1 Add all module without dependency:
	foreach(MODULE_ELEM ${MODULE_MAP_LIST})
		message("check add element : ${MODULE_ELEM}")
		message("    dependency = '${MODULE_ELEM}'")
		GLD_get_module_name(LOCAL_MODULE_NAME ${MODULE_ELEM})
		message("    dependency = '${MODULE_MAP_${LOCAL_MODULE_NAME}_DEPENDENCY}'")
		# todo check dependency here ... ${MODULE_MAP_${LOCAL_MODULE_NAME}_DEPENDENCY}
		list(LENGTH MODULE_MAP_${LOCAL_MODULE_NAME}_DEPENDENCY LIST_LENGTH)
		message("        ==> length'${LIST_LENGTH}'")
		if (LIST_LENGTH EQUAL 0)
			message("Add element ${III} (0 dependency) ******** ")
			list(APPEND TMP_ORDERED ${MODULE_ELEM})
			continue()
		endif()
		list(APPEND TMP_UN_ADDED ${MODULE_ELEM})
	endforeach()
	message("result: ${TMP_ORDERED}")
	message("===========================================")
	message("== STEP 2 : Add all when the dependency are available in the list:")
	message("===========================================")
	# step 2 Add all when the dependency are available in the list:
	list(LENGTH TMP_UN_ADDED LIST_TOTAL_LENGTH)
	message("unadded : ${LIST_TOTAL_LENGTH}")
	# must be resolved in the number of cycle in the list (maximum)
	foreach(III RANGE ${LIST_TOTAL_LENGTH})
		message("cycle : ${III}")
		set(TMP_UN_ADDED_TMP ${TMP_UN_ADDED})
		set(TMP_UN_ADDED "")
		foreach(ELEM_TO_ADD ${TMP_UN_ADDED_TMP})
			message("    check to add : ${ELEM_TO_ADD}")
			GLD_get_module_name(LOCAL_MODULE_NAME ${ELEM_TO_ADD})
			message("        dependency : ${MODULE_MAP_${LOCAL_MODULE_NAME}_DEPENDENCY} in ? ${TMP_ORDERED}")
			GLD_are_in_list(IS_ALL_PRESENT "${MODULE_MAP_${LOCAL_MODULE_NAME}_DEPENDENCY}" "${TMP_ORDERED}")
			if (${IS_ALL_PRESENT} STREQUAL "true")
				message("Add element ${ELEM_TO_ADD} (depend: ${MODULE_MAP_${LOCAL_MODULE_NAME}_DEPENDENCY})")
				list(APPEND TMP_ORDERED ${ELEM_TO_ADD})
			else()
				list(APPEND TMP_UN_ADDED ${ELEM_TO_ADD})
			endif()
	 	endforeach()
	endforeach()
	message("result:")
		foreach(ELEM ${TMP_ORDERED})
			message("    - ${ELEM}")	
		endforeach()
	message("===========================================")
	message("== STEP 3 : All must be added before...")
	message("===========================================")
	# step 3 All must be added before...
	list(LENGTH TMP_UN_ADDED LIST_TOTAL_LENGTH)
	if (${LIST_TOTAL_LENGTH} GREATER_EQUAL 0)
		message(WARNING "Some element are not added: (${LIST_TOTAL_LENGTH})")
		foreach(ELEM ${TMP_UN_ADDED})
			message("    - ${ELEM}")
			GLD_get_module_name(LOCAL_MODULE_NAME ${ELEM})
			message("        dep          : ${MODULE_MAP_${LOCAL_MODULE_NAME}_DEPENDENCY}")
			message("        dep(optional): ${MODULE_MAP_${LOCAL_MODULE_NAME}_DEPENDENCY_OPTIONAL}")
		endforeach()
	endif()
	set(MODULE_MAP_LIST_DEPENDENCE_RESOLVED ${TMP_ORDERED} CACHE INTERNAL "")
	set(${VAR_OUT} ${TMP_ORDERED} PARENT_SCOPE)
	set(${DEPENDENCY_FAILED} ${TMP_UN_ADDED} PARENT_SCOPE)
endfunction()


function(GLD_load_all ROOT_FOLDER BASE_NAME COMMENT_ACTION)
	message("Parse all files ${BASE_NAME}*.json: base: ${ROOT_FOLDER}")
	#file(GLOB_RECURSE GLD_FILES "${ROOT_FOLDER}/GLD_*.json")
	find_all_files(GLD_FILES "${ROOT_FOLDER}" "${BASE_NAME}*.json" 5)
	message("List of GLD files:")
	foreach(III ${GLD_FILES})
		GET_FILENAME_COMPONENT(FILENAME ${III} NAME_WE)
		set(FULL_FILENAME ${FILENAME})
		string(REPLACE "${BASE_NAME}" "" FILENAME ${FILENAME})
		GET_FILENAME_COMPONENT(FOLDER ${III} DIRECTORY)
		message("    - ${COMMENT_ACTION} ${FOLDER} ==> ${FILENAME}")
		GLD_add_module(${FILENAME} ${FOLDER} ${FULL_FILENAME})
	endforeach()
	#GLD_import("./" "etk-core")
endfunction()

function(GLD_auto_prebuild_load_all ROOT_FOLDER)
	GLD_load_all(${ROOT_FOLDER} "GLDPrebuild_${GLD_TARGET}_" "(prebuild)")
endfunction()

function(GLD_auto_load_all ROOT_FOLDER)
	GLD_load_all(${ROOT_FOLDER} "GLD_" "")
endfunction()


function(GLD_instanciate)
	message("List of modules:")
	foreach(III ${MODULE_MAP_LIST})
		GLD_get_module_name(LOCAL_MODULE_NAME ${III})
		message("    - ${III}")
	endforeach()
	foreach(III ${MODULE_MAP_LIST})
		GLD_get_module_name(LOCAL_MODULE_NAME ${III})
		GLD_generate_module_without_optionnal_inexistant(${III})
		message("    - ${III}")
		message("        FOLDER=${MODULE_MAP_${LOCAL_MODULE_NAME}_FOLDER}")
		#message("        JSON=${MODULE_MAP_${LOCAL_MODULE_NAME}_JSON}")
		message("        DEPENDENCY=${MODULE_MAP_${LOCAL_MODULE_NAME}_DEPENDENCY}")
		message("        DEPENDENCY_OPTIONAL=${MODULE_MAP_${LOCAL_MODULE_NAME}_DEPENDENCY_OPTIONAL}")
	endforeach()
	GLD_order_dependency_list(DEPENDENCY_ORDER DEPENDENCY_FAILED)
	
	GLD_generate_cmake_wrapping("${DEPENDENCY_ORDER}")
	
	#message("dependency resolver & ordered:")
	#foreach(III ${DEPENDENCY_ORDER})
	#	message("    - ${III}")
	#endforeach()
	
	#message("dependency fail:")
	#foreach(III ${DEPENDENCY_FAILED})
	#	message("    - ${III}")
	#endforeach()
	
endfunction()
