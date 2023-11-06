cmake_minimum_required( VERSION 3.0 )
project( triangle )

add_library( triangle triangle.cpp )

add_executable( standalone standalone.cpp )
target_link_libraries( standalone triangle )

add_executable( run_triangle run_triangle.cpp )
target_link_libraries( run_triangle triangle )

add_executable( test_triangle test_triangle.cpp )
target_link_libraries( test_triangle triangle )
