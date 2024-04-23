#ifndef PY_ENVIRONMENT_WRAPPER_H
#define PY_ENVIRONMENT_WRAPPER_H

#include <boost/python.hpp>
#include <boost/python/suite/indexing/map_indexing_suite.hpp>

// #include <argos3/core/control_interface/ci_controller.h>

// /* Definition of the differential steering actuator */
// #include <argos3/plugins/robots/generic/control_interface/ci_differential_steering_actuator.h>
// /* Definition of the leds actuator */
// #include <argos3/plugins/robots/generic/control_interface/ci_leds_actuator.h>
// /* Definition of the range and bearing actuator */
// #include <argos3/plugins/robots/generic/control_interface/ci_range_and_bearing_actuator.h>


// /* Definition of the differential steering sensor */
// #include <argos3/plugins/robots/generic/control_interface/ci_differential_steering_sensor.h>
// /* Definition of the range and bearing sensor */
// #include <argos3/plugins/robots/generic/control_interface/ci_range_and_bearing_sensor.h>
// /* Definition of the positioning sensor */
// #include <argos3/plugins/robots/generic/control_interface/ci_positioning_sensor.h>
// /* Definition of the omni camera sensor */
// #include <argos3/plugins/robots/generic/control_interface/ci_colored_blob_omnidirectional_camera_sensor.h>
// /* Definition of the perspective camera sensor */
// #include <argos3/plugins/robots/generic/control_interface/ci_colored_blob_perspective_camera_sensor.h>

#include <argos3/plugins/simulator/visualizations/qt-opengl/qtopengl_user_functions.h>

#include <argos3/core/utility/logging/argos_log.h>
#include <argos3/core/utility/math/general.h>

#include <iostream>
#include <string>

namespace argos {

	class CQTOpenGLUserFunctionsWrapper {
	  public:
	    CQTOpenGLUserFunctionsWrapper();
	    ~CQTOpenGLUserFunctionsWrapper(){};

	    argos::CQTOpenGLUserFunctions* m_pcCQTOpenGLUserFunctions;

	    void SetDrawList(const std::string& key, const std::string& value);

	    const std::string GetDrawList(const std::string& key);

	    std::map<std::string, std::string> m_cAttributes;

	    void DrawCircle(
	      const boost::python::list c_position_list, 
	      const boost::python::list c_orientation_list, 
	      const Real f_radius, 
	      const boost::python::object color_str_list,
	      const bool  b_fill=true);

	    void DrawPolygon(
	      const boost::python::list c_position_list, 
	      const boost::python::list c_orientation_list, 
	      const boost::python::list vec_points, 
	      const std::string str_color_name,
	      const bool  b_fill);
	    
	    void DrawRay(
	      const boost::python::list c_start,
	      const boost::python::list c_end,
	      const boost::python::object str_color_name,
	      const Real f_width);

	    void DrawCylinder(
	      const boost::python::list c_position_list, 
	      const boost::python::list c_orientation_list, 
	      const Real f_radius,
	      const Real f_height,  
	      const std::string str_color_name);

	    void DrawBox(
	      const boost::python::list c_position_list, 
	      const boost::python::list c_orientation_list, 
	      const boost::python::list c_size_list, 
	      const boost::python::object str_color_name);

	    void DrawText(
	      const boost::python::list c_position,
	      const std::string str_text,
	      const std::string str_color_name); 

	    void CloseWindow();
	};
};

#endif
