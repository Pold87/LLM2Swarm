/*
 * AUTHOR: Ken Hasselmann <arg AT kenh DOT fr>
 *
 * Connects ARGoS to python
 *
 */

#ifndef PY_WRAPPER_H
#define PY_WRAPPER_H

#include <boost/python.hpp>
#include <boost/python/suite/indexing/map_indexing_suite.hpp>

#include <argos3/core/control_interface/ci_controller.h>
#include <argos3/plugins/simulator/visualizations/qt-opengl/qtopengl_user_functions.h>

#include "py_actusensor_wrapper_epuck.h"
#include "py_actusensor_wrapper_footbot.h"
#include "py_actusensor_wrapper_generic.h"
#include "py_environment_wrapper.h"

#include <argos3/core/utility/logging/argos_log.h>
#include <argos3/core/utility/math/general.h>

#include <iostream>
#include <string>

namespace argos {

class EnvironmentWrapper {
  public:
    EnvironmentWrapper();
    ~EnvironmentWrapper(){};

    static void Logprint(const std::string& str_message);
    /****************************************/
    /****************************************/

    // Define a wrapper for the QTOpenGL functions
    CQTOpenGLUserFunctionsWrapper m_cCQTOpenGLUserFunctionsWrapper;

    // Define a wrapper for the variables
    CVariableWrapper m_cVariableWrapper;

    /****************************************/
    /****************************************/

    // Define functions to access the elements the argos::CByteArray class.
    // Original source: https://mail.python.org/pipermail/cplusplus-sig/2003-June/004024.html
    static void CByteArraySetItem(argos::CByteArray& c_vec, const UInt32 un_index,
                                  const UInt8 un_value);

    static UInt8 CByteArrayGetItem(const argos::CByteArray& c_vec, const UInt32 un_index);

    /****************************************/
    /****************************************/

    // Used to convert vectors to python lists.
    // Original source: http://www.boost.org/doc/libs/1_62_0/libs/python/pyste/doc/wrappers.html
    template <class T> static boost::python::list ToPythonList(std::vector<T> c_vec) {
        typename std::vector<T>::iterator iter;
        boost::python::list list;
        for (iter = c_vec.begin(); iter != c_vec.end(); ++iter) {
            list.append(*iter);
        }
        return list;
    }
};

class ActusensorsWrapper {
  public:
    ActusensorsWrapper();
    ~ActusensorsWrapper(){};

    static void Logprint(const std::string& str_message);

  void SetId(const std::string id);

  bool GetConsensus();

    // Sensors
    void CreateSensor(const std::string str_name, CCI_Sensor* pc_sensor,
                      TConfigurationNode& t_node);

    // Actuators
    void CreateActu(const std::string str_name, CCI_Actuator* pc_actu, TConfigurationNode& t_node);

    // Wrapper for the CColor class.
    class CColorWrapper {
      public:
        argos::CColor m_cColor;
        // Create a color by providing its name.
        CColorWrapper(const std::string str_color_name);
        // Create a color by providing its RGB values.
        CColorWrapper(const UInt8 un_red, const UInt8 un_green, const UInt8 un_blue);
        ~CColorWrapper(){};
    };

    /****************************************/
    /****************************************/

    // Define a wrapper for each actuator and sensor

    // Generic actusensors
    CWheelsWrapper m_cWheelsWrapper;
    CDifferentialSteeringSensorWrapper m_cDifferentialSteeringSensor;
    CVariableWrapper m_cVariableWrapper;
    CPositioningSensorWrapper m_cPositioningWrapper;


    // CLoopFunctionsWrapper m_cCLoopFunctionsWrapper;

    COmnidirectionalCameraWrapper m_cOmnidirectionalCameraWrapper;
    CPerspectiveCameraWrapper m_cPerspectiveCameraWrapper;
    CLedsActuatorWrapper m_cLedsWrapper;
    CRangeAndBearingWrapper m_cRangeAndBearingWrapper;

    // Footbot Actusensors
    CGripperWrapper m_cGripperWrapper;
    CFootBotProximitySensorWrapper m_cProximitySensorWrapper;
    CTurretWrapper m_cTurretWrapper;
    CDistanceScannerWrapper m_cDistanceScannerWrapper;
    CLightSensorWrapper m_cLightSensorWrapper;
    CGroundSensorWrapper m_cGroundSensorWrapper;
    CBaseGroundSensorWrapper m_cBaseGroundSensorWrapper;

    // E-Puck actusensors
    CEPuckWheelsWrapper m_cEPuckWheelsWrapper;
    CEPuckProximitySensorWrapper m_cEPuckProximitySensorWrapper;
    CEPuckGroundSensorWrapper m_cEPuckGroundSensorWrapper;
    CEPuckRangeAndBearingWrapper m_cEPuckRangeAndBearingWrapper;
    CEPuckLedsActuatorWrapper m_cEPuckLedsWrapper;

    CQTOpenGLUserFunctionsWrapper m_cCQTOpenGLUserFunctionsWrapper;
    
    /****************************************/
    /****************************************/

    // Define functions to access the elements the argos::CByteArray class.
    // Original source: https://mail.python.org/pipermail/cplusplus-sig/2003-June/004024.html
    static void CByteArraySetItem(argos::CByteArray& c_vec, const UInt32 un_index,
                                  const UInt8 un_value);

    static UInt8 CByteArrayGetItem(const argos::CByteArray& c_vec, const UInt32 un_index);

    // Define getter for the EPuck ground sensor readings.
    static Real
    EPuckGroundReadingsGetItem(const argos::CCI_EPuckGroundSensor::SReadings& c_readings,
                               const UInt32 un_index);

    /****************************************/
    /****************************************/

    // Used to convert vectors to python lists.
    // Original source: http://www.boost.org/doc/libs/1_62_0/libs/python/pyste/doc/wrappers.html
    template <class T> static boost::python::list ToPythonList(std::vector<T> c_vec) {
        typename std::vector<T>::iterator iter;
        boost::python::list list;
        for (iter = c_vec.begin(); iter != c_vec.end(); ++iter) {
            list.append(*iter);
        }
        return list;
    }
};

} // namespace argos

#endif
