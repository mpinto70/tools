cmake_minimum_required (VERSION 3.20)
project (tools VERSION 0.11.0 LANGUAGES CXX)

# add support for CTest
include(FetchContent)

set(UPDATE_DISCONNECTED_IF_AVAILABLE "UPDATE_DISCONNECTED 1")

find_program(CCACHE_FOUND ccache)
if(CCACHE_FOUND)
    set_property(GLOBAL PROPERTY RULE_LAUNCH_COMPILE ccache)
    set_property(GLOBAL PROPERTY RULE_LAUNCH_LINK ccache)
endif(CCACHE_FOUND)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

set(CMAKE_CXX_FLAGS " \
    -Wno-parentheses \
    -Werror \
    -Wall \
    -Wextra \
    -pedantic-errors \
    -O3 \
    -finline-functions")

# set (CMAKE_VERBOSE_MAKEFILE on)

install(
        DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/src
        DESTINATION ${CMAKE_INSTALL_PREFIX}/include
        FILES_MATCHING PATTERN "*.hpp"
)

add_compile_definitions(-DPROJECT_DIR="${CMAKE_SOURCE_DIR}")
add_compile_definitions(-DMHPA_DEBUG_MIN_SPACING=80)

include_directories(
    "${CMAKE_CURRENT_SOURCE_DIR}/src"
)

# Recurse subdirectories
add_subdirectory (src)

include(${CMAKE_SOURCE_DIR}/cmake/UnitTest.cmake)
add_subdirectory (test)
