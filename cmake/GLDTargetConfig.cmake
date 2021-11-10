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
	set(GLD_COMPILER "clang" CACHE INTERNAL "")
elseif (CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
	set(GLD_COMPILER "gcc" CACHE INTERNAL "")
elseif (CMAKE_CXX_COMPILER_ID STREQUAL "Intel")
	set(GLD_COMPILER "intel" CACHE INTERNAL "")
elseif (CMAKE_CXX_COMPILER_ID STREQUAL "MSVC")
	set(GLD_COMPILER "msvc" CACHE INTERNAL "")
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
set(GLD_GLOBAL_BUILD_FOLDER "${CMAKE_CURRENT_BINARY_DIR}/${GLD_TARGET}_${GLD_ARCH}_${GLD_BUS_SIZE}/${GLD_MODE}/build/${GLD_COMPILER}/" CACHE INTERNAL "")
# where the package is prepared
set(GLD_GLOBAL_STAGING_FOLDER "${CMAKE_CURRENT_BINARY_DIR}/${GLD_TARGET}_${GLD_ARCH}_${GLD_BUS_SIZE}/${GLD_MODE}/staging/${GLD_COMPILER}/" CACHE INTERNAL "")
# whe the bundle (tar, jar ...) is set
set(GLD_GLOBAL_FINAL_FOLDER "${CMAKE_CURRENT_BINARY_DIR}/${GLD_TARGET}_${GLD_ARCH}_${GLD_BUS_SIZE}/${GLD_MODE}/final/${GLD_COMPILER}/" CACHE INTERNAL "")
	
message("Global GLD properties:")
message("	GLD_MODE :        ${GLD_MODE}")
message("	GLD_COMPILER :    ${GLD_COMPILER}")
message("	GLD_TARGET :      ${GLD_TARGET}")
message("	GLD_ARCH :        ${GLD_ARCH}")
message("	GLD_BUS_SIZE :    ${GLD_BUS_SIZE}")
message("	GLD_SANITY_MODE : ${GLD_SANITY_MODE}")
message("	GLD_GLOBAL_BUILD_FOLDER :   ${GLD_GLOBAL_BUILD_FOLDER}")
message("	GLD_GLOBAL_STAGING_FOLDER : ${GLD_GLOBAL_STAGING_FOLDER}")
message("	GLD_GLOBAL_FINAL_FOLDER :   ${GLD_GLOBAL_FINAL_FOLDER}")
