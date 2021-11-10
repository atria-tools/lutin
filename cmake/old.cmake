

function(GLD_import_old FOLDER LIBRARY_NAME)
	# add the executable
	# add_executable(Tutorial tutorial.cxx)
	
	set(LIBRARY_NAME "etk-core")
	set_property(
	            DIRECTORY
	            APPEND
	            PROPERTY CMAKE_CONFIGURE_DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/GLD_${LIBRARY_NAME}.json
	    )
	# Read the JSON file.
	file(READ ${CMAKE_CURRENT_SOURCE_DIR}/GLD_${LIBRARY_NAME}.json MY_JSON_STRING)
	
	# Loop through each element of the JSON array (indices 0 though 1).
	
	json_get_element(LIBRARY_TYPE ${MY_JSON_STRING} "type")
	json_get_element(LIBRARY_GROUP_ID ${MY_JSON_STRING} "group-id")
	json_get_element(LIBRARY_DECRIPTION ${MY_JSON_STRING} "description")
	json_get_element(LIBRARY_LICENCE ${MY_JSON_STRING} "licence")
	json_get_element(LIBRARY_LICENCE_FILE ${MY_JSON_STRING} "licence-file")
	json_get_element(LIBRARY_MAINTAINER ${MY_JSON_STRING} "maintainer")
	json_get_element(LIBRARY_AUTHORS ${MY_JSON_STRING} "authors")
	json_get_element(LIBRARY_VERSION ${MY_JSON_STRING} "version")
	json_get_element(LIBRARY_SOURCES ${MY_JSON_STRING} "sources")
	json_get_element(LIBRARY_HEADERS ${MY_JSON_STRING} "headers")
	json_get_list(LIBRARY_PATH ${MY_JSON_STRING} "path")
	json_get_element(LIBRARY_COMPILATION_VERSION ${MY_JSON_STRING} "compilation-version")
	json_get_list(LIBRARY_DEPENDENCY ${MY_JSON_STRING} "dependency")
	json_get_element(LIBRARY_TARGET ${MY_JSON_STRING} "target")
	
	json_get_element(LIBRARY_COMPILATION_VERSION_LANGUAGE ${MY_JSON_STRING} "language")
	json_get_element(LIBRARY_COMPILATION_VERSION_VALUE ${MY_JSON_STRING} "version")
	
	message("LIBRARY_NAME         : ${LIBRARY_NAME}")
	message("LIBRARY_TYPE         : ${LIBRARY_TYPE}")
	message("LIBRARY_GROUP_ID     : ${LIBRARY_GROUP_ID}")
	message("LIBRARY_DECRIPTION   : ${LIBRARY_DECRIPTION}")
	message("LIBRARY_LICENCE      : ${LIBRARY_LICENCE}")
	message("LIBRARY_LICENCE_FILE : ${LIBRARY_LICENCE_FILE}")
	message("LIBRARY_MAINTAINER   : ${LIBRARY_MAINTAINER}")
	message("LIBRARY_AUTHORS      : ${LIBRARY_AUTHORS}")
	message("LIBRARY_VERSION      : ${LIBRARY_VERSION}")
	message("LIBRARY_COMPILATION_VERSION      : ${LIBRARY_COMPILATION_VERSION_LANGUAGE} : ${LIBRARY_COMPILATION_VERSION_VALUE}")
	
	#message("LIBRARY_SOURCES: ${LIBRARY_SOURCES}")
	#message("LIBRARY_HEADERS: ${LIBRARY_HEADERS}")
	message("LIBRARY_PATH: ${LIBRARY_PATH}")
	#message("LIBRARY_COMPILATION_VERSION: ${LIBRARY_COMPILATION_VERSION}")
	message("LIBRARY_DEPENDENCY: ${LIBRARY_DEPENDENCY}")
	#message("LIBRARY_TARGET: ${LIBRARY_TARGET}")
	
	
	json_get_list(SOURCES_LIST ${LIBRARY_SOURCES} "list")
	message("SOURCES_LIST: ${SOURCES_LIST}")
	
	json_get_list(EXPORT_HEADER_LIST ${LIBRARY_HEADERS} "list")
	json_get_element(EXPORT_HEADER_LIST_PATH ${LIBRARY_HEADERS} "destination-path")
	message("EXPORT_HEADER_LIST: ${EXPORT_HEADER_LIST}")
	message("EXPORT_HEADER_LIST_PATH: ${EXPORT_HEADER_LIST_PATH}")
	
	
	
	string(JSON LIBRARY_PLOP ERROR_VARIABLE "qsdfqsdfqsdf" GET ${MY_JSON_STRING} "qsdfqsdfqsdf")
	#string(JSON LIBRARY_MEMBERS MEMBER ${MY_JSON_STRING} )
	#message("LIBRARY_MEMBERS      : ${LIBRARY_MEMBERS}")
	message("LIBRARY_PLOP         : ${LIBRARY_PLOP}")
	
	string(REPLACE "-" "_" LIBRARY_NAME222 ${LIBRARY_NAME})
	set(LIBRARY_NAME222 ${LIBRARY_NAME})
	project(${LIBRARY_NAME222} VERSION ${LIBRARY_VERSION})
	set(${LIBRARY_NAME222} PROPERTIES CPACK_PACKAGE_VERSION ${LIBRARY_VERSION})
	add_library(${LIBRARY_NAME222}_OBJ OBJECT ${SOURCES_LIST})
	# shared libraries need PIC
	set_property(TARGET ${LIBRARY_NAME222}_OBJ PROPERTY POSITION_INDEPENDENT_CODE 1)
	
	
	#set_target_properties(${LIBRARY_NAME222} PROPERTIES PUBLIC_HEADER ${EXPORT_HEADER_LIST})
	target_include_directories(${LIBRARY_NAME222}_OBJ PUBLIC
	                           ${LIBRARY_PATH}
	                           )
	
	
	
	
	add_library(${LIBRARY_NAME222}_dynamic SHARED $<TARGET_OBJECTS:${LIBRARY_NAME222}_OBJ>)
	add_library(${LIBRARY_NAME222}_static STATIC $<TARGET_OBJECTS:${LIBRARY_NAME222}_OBJ>)
	
	set_target_properties(${LIBRARY_NAME222}_dynamic PROPERTIES OUTPUT_NAME ${LIBRARY_NAME222})
	if (NOT WIN32)
		set_target_properties(${LIBRARY_NAME222}_static PROPERTIES OUTPUT_NAME ${LIBRARY_NAME222})
	endif()
	
	
	
	set_target_properties(${LIBRARY_NAME222}_dynamic PROPERTIES VERSION ${LIBRARY_VERSION})
	set_target_properties(${LIBRARY_NAME222}_dynamic PROPERTIES SOVERSION ${LIBRARY_VERSION})
	set_target_properties(${LIBRARY_NAME222}_dynamic PROPERTIES DESCRIPTION ${LIBRARY_DECRIPTION})
	
	# install dynamic & static library
	install(TARGETS ${LIBRARY_NAME222}_dynamic EXPORT ${LIBRARY_NAME222}Targets
	        RUNTIME DESTINATION lib
	         )
	install(TARGETS ${LIBRARY_NAME222}_static
	        RUNTIME DESTINATION lib)
	
	
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






function(kjhghkjgkhjgkjhgkjhgkj LIBRARY_NAME)
	
	json_get_element(LIBRARY_SOURCES ${MY_JSON_STRING} "source")
	json_get_element(LIBRARY_HEADERS ${MY_JSON_STRING} "header")
	json_get_list(LIBRARY_PATH ${MY_JSON_STRING} "path")
	json_get_element(LIBRARY_COMPILATION_VERSION ${MY_JSON_STRING} "compilation-version")
	json_get_list(LIBRARY_DEPENDENCY ${MY_JSON_STRING} "dependency")
	json_get_element(LIBRARY_TARGET ${MY_JSON_STRING} "target")
	
	json_get_element(LIBRARY_COMPILATION_VERSION_LANGUAGE ${MY_JSON_STRING} "language")
	json_get_element(LIBRARY_COMPILATION_VERSION_VALUE ${MY_JSON_STRING} "version")
	
	message("LIBRARY_COMPILATION_VERSION      : ${LIBRARY_COMPILATION_VERSION_LANGUAGE} : ${LIBRARY_COMPILATION_VERSION_VALUE}")
	
	#message("LIBRARY_SOURCES: ${LIBRARY_SOURCES}")
	#message("LIBRARY_HEADERS: ${LIBRARY_HEADERS}")
	message("LIBRARY_PATH: ${LIBRARY_PATH}")
	#message("LIBRARY_COMPILATION_VERSION: ${LIBRARY_COMPILATION_VERSION}")
	message("LIBRARY_DEPENDENCY: ${LIBRARY_DEPENDENCY}")
	#message("LIBRARY_TARGET: ${LIBRARY_TARGET}")
	
	
	json_get_list(SOURCES_LIST ${LIBRARY_SOURCES} "list")
	message("SOURCES_LIST: ${SOURCES_LIST}")
	
	json_get_list(EXPORT_HEADER_LIST ${LIBRARY_HEADERS} "list")
	json_get_element(EXPORT_HEADER_LIST_PATH ${LIBRARY_HEADERS} "destination-path")
	message("EXPORT_HEADER_LIST: ${EXPORT_HEADER_LIST}")
	message("EXPORT_HEADER_LIST_PATH: ${EXPORT_HEADER_LIST_PATH}")
	
	
	
	string(JSON LIBRARY_PLOP ERROR_VARIABLE "qsdfqsdfqsdf" GET ${MY_JSON_STRING} "qsdfqsdfqsdf")
	#string(JSON LIBRARY_MEMBERS MEMBER ${MY_JSON_STRING} )
	#message("LIBRARY_MEMBERS      : ${LIBRARY_MEMBERS}")
	message("LIBRARY_PLOP         : ${LIBRARY_PLOP}")
	
	string(REPLACE "-" "_" LIBRARY_NAME222 ${LIBRARY_NAME})
	set(LIBRARY_NAME222 ${LIBRARY_NAME})
	project(${LIBRARY_NAME222} VERSION ${LIBRARY_VERSION})
	set(${LIBRARY_NAME222} PROPERTIES CPACK_PACKAGE_VERSION ${LIBRARY_VERSION})
	add_library(${LIBRARY_NAME222}_OBJ OBJECT ${SOURCES_LIST})
	# shared libraries need PIC
	set_property(TARGET ${LIBRARY_NAME222}_OBJ PROPERTY POSITION_INDEPENDENT_CODE 1)
	
	
	#set_target_properties(${LIBRARY_NAME222} PROPERTIES PUBLIC_HEADER ${EXPORT_HEADER_LIST})
	target_include_directories(${LIBRARY_NAME222}_OBJ PUBLIC
	                           ${LIBRARY_PATH}
	                           )
	
	
	
	
	add_library(${LIBRARY_NAME222}_dynamic SHARED $<TARGET_OBJECTS:${LIBRARY_NAME222}_OBJ>)
	add_library(${LIBRARY_NAME222}_static STATIC $<TARGET_OBJECTS:${LIBRARY_NAME222}_OBJ>)
	
	set_target_properties(${LIBRARY_NAME222}_dynamic PROPERTIES OUTPUT_NAME ${LIBRARY_NAME222})
	if (NOT WIN32)
		set_target_properties(${LIBRARY_NAME222}_static PROPERTIES OUTPUT_NAME ${LIBRARY_NAME222})
	endif()
	
	
	
	set_target_properties(${LIBRARY_NAME222}_dynamic PROPERTIES VERSION ${LIBRARY_VERSION})
	set_target_properties(${LIBRARY_NAME222}_dynamic PROPERTIES SOVERSION ${LIBRARY_VERSION})
	set_target_properties(${LIBRARY_NAME222}_dynamic PROPERTIES DESCRIPTION ${LIBRARY_DECRIPTION})
	
	# install dynamic & static library
	install(TARGETS ${LIBRARY_NAME222}_dynamic EXPORT ${LIBRARY_NAME222}Targets
	        RUNTIME DESTINATION lib
	         )
	install(TARGETS ${LIBRARY_NAME222}_static
	        RUNTIME DESTINATION lib)
	
	
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









