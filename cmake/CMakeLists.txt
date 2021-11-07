cmake_minimum_required(VERSION 3.20)
project(GlobalSearch)


message("List of modules: ${CMAKE_MODULE_PATH}")

#LIST(APPEND CMAKE_MODULE_PATH "cmake")

#find_package(GLDBuilder REQUIRED)

include("cmake/GLDBuilder.cmake")

#GLD_import("./" "etk-core")

get_filename_component(LOCAL_FILE_PATH "." ABSOLUTE)
GLD_auto_prebuild_load_all("${LOCAL_FILE_PATH}")
GLD_auto_load_all("${LOCAL_FILE_PATH}")

GLD_instanciate()

