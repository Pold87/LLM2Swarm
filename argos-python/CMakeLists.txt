project (pythonwrapper CXX)
# cmake_minimum_required (VERSION 2.8)
cmake_minimum_required (VERSION 3.0)

set(BOOST_INCLUDEDIR /usr/include)

# set(Python_ADDITIONAL_VERSIONS 3.5)

find_package(PythonLibs)
include_directories (${PYTHON_INCLUDE_DIRS})
link_directories(${PYTHON_LIBRARIES})

# SET(LUA_CONST "-I/usr/include/lua5.3 -I/usr/include/python3 -I/usr/local/include -lboost_python3  -lpython3.5m -o -shared -fPIC")
# add_definitions(${LUA_CONST})

# find_package(Boost 1.61.0 COMPONENTS python3)
find_package(Boost COMPONENTS python38)


include_directories (${Boost_INCLUDE_DIRS})
link_directories(${Boost_LIBRARY_DIR})

find_package(PkgConfig)
find_package(ARGoS REQUIRED)


set(ARGOS_PREFIX ${ARGOS_PREFIX} CACHE INTERNAL "")
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${ARGOS_PREFIX}/share/argos3/cmake)

link_directories(${ARGOS_LIBRARY_DIR})
link_libraries(${ARGOS_LDFLAGS})

# Set ARGoS include dir
include_directories(${CMAKE_SOURCE_DIR} ${ARGOS_INCLUDE_DIRS} ${GSL_INCLUDE_DIR} ${LUA_INCLUDE_DIR})

# Set ARGoS link dir
link_directories(${ARGOS_LIBRARY_DIRS})

include_directories(${CMAKE_SOURCE_DIR}/controllers)

set(PYCONTROLLER_HEADERS
  py_controller.h
  py_wrapper.h
  py_actusensor_wrapper_generic.h
  py_actusensor_wrapper_footbot.h
  py_actusensor_wrapper_epuck.h
  )

set(PYCONTROLLER_SOURCES
  py_controller.cpp
  py_wrapper.cpp
  py_actusensor_wrapper_generic.cpp
  py_actusensor_wrapper_footbot.cpp
  py_actusensor_wrapper_epuck.cpp
  )

set(PYLOOPFUNCTION_HEADERS
  py_loop_function.h 
  )

set(PYLOOPFUNCTION_SOURCES
  py_loop_function.cpp
  )


set(PYQTUSERFUNCTION_HEADERS
  py_qtuser_function.h 
  py_environment_wrapper.h
  )

set(PYQTUSERFUNCTION_SOURCES
  py_qtuser_function.cpp
  py_environment_wrapper.cpp
  )

add_library (
    py_controller_interface SHARED ${PYCONTROLLER_HEADERS} ${PYCONTROLLER_SOURCES})

add_library (
    py_loop_function_interface SHARED ${PYLOOPFUNCTION_HEADERS} ${PYLOOPFUNCTION_SOURCES})
 
add_library (
    py_qtuser_function_interface SHARED ${PYQTUSERFUNCTION_HEADERS} ${PYQTUSERFUNCTION_SOURCES})

  target_link_libraries (py_controller_interface
    py_loop_function_interface
    py_qtuser_function_interface
    argos3core_simulator
    argos3plugin_simulator_footbot
    argos3plugin_simulator_genericrobot
    ${PYTHON_LIBRARIES}
    ${Boost_LIBRARIES}
)
