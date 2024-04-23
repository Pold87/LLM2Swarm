#ifndef PY_ACTUSENSOR_WRAPPER_EPUCK_H
#define PY_ACTUSENSOR_WRAPPER_EPUCK_H

#include <boost/python.hpp>
#include <boost/variant.hpp>
#include <boost/python/suite/indexing/map_indexing_suite.hpp>

#include <argos3/core/control_interface/ci_controller.h>

#include <argos3/plugins/robots/e-puck/control_interface/ci_epuck_ground_sensor.h>
#include <argos3/plugins/robots/e-puck/control_interface/ci_epuck_proximity_sensor.h>
#include <argos3/plugins/robots/e-puck/control_interface/ci_epuck_range_and_bearing_actuator.h>
#include <argos3/plugins/robots/e-puck/control_interface/ci_epuck_range_and_bearing_sensor.h>
#include <argos3/plugins/robots/e-puck/control_interface/ci_epuck_rgb_leds_actuator.h>
#include <argos3/plugins/robots/e-puck/control_interface/ci_epuck_wheels_actuator.h>

#include <argos3/core/utility/logging/argos_log.h>
#include <argos3/core/utility/math/general.h>

#include <argos3/plugins/simulator/visualizations/qt-opengl/qtopengl_user_functions.h>

#include <iostream>
#include <string>
#include <map>

namespace argos {

/****************************************/
/****************************************/

// Wrapper for getting the values of a robot's variables
class CVariableWrapper {
  public:
    CVariableWrapper();
    ~CVariableWrapper(){};

  void SetId(const std::string id);
  const std::string GetId();
  std::string m_cId;

  void SetAttribute(const std::string& key, const std::string& value);
  const std::string GetAttribute(const std::string& key);
  const std::string GetAllAttributes();
  std::map<std::string, std::string> m_cAttributes;

  // void SetAttribute(const std::string& key, const bool& value);
  // const boost::variant<std::string, bool> GetAttribute(const std::string& key);
  // std::map<std::string, boost::variant<std::string, bool>> m_cAttributes;


};

/****************************************/
/****************************************/

// Wrapper for the Differential Steering Actuator.
class CEPuckWheelsWrapper {
  public:
    CEPuckWheelsWrapper();
    ~CEPuckWheelsWrapper(){};
    argos::CCI_EPuckWheelsActuator* m_pcEPuckWheels;
    // Set the speed of the two wheels.
    void SetSpeed(const Real f_left_wheel_speed, const Real f_right_wheel_speed);
};

/****************************************/
/****************************************/

// Wrapper for the Proximity Sensor.
class CEPuckProximitySensorWrapper {
  public:
    CEPuckProximitySensorWrapper();
    ~CEPuckProximitySensorWrapper(){};
    argos::CCI_EPuckProximitySensor* m_pcEPuckProximity;
    // Obtain the proximity readings at this control step.
    // The readings are exposed as a python list.
    // Each reading is exposed as a "proximity_reading", from which it is possible to obtain value
    // and angle.
    boost::python::list GetReadings() const;
};

/****************************************/
/****************************************/
// Wrapper for the Ground Motor Sensor.
// Allows to get a list of readings from the ground.
class CEPuckGroundSensorWrapper {
  public:
    CEPuckGroundSensorWrapper();
    ~CEPuckGroundSensorWrapper(){};
    argos::CCI_EPuckGroundSensor* m_pcEPuckGround;

    argos::CCI_EPuckGroundSensor::SReadings GetReadings() const;
};

/****************************************/
/****************************************/
// Wrapper for the EPuck Range and Bearing Sensor and Actuator.
// Both of them are exposed as a single property of the robot, for simplicity.
class CEPuckRangeAndBearingWrapper {
  public:
    CEPuckRangeAndBearingWrapper();
    ~CEPuckRangeAndBearingWrapper(){};

    argos::CCI_EPuckRangeAndBearingActuator* m_pcEPuckRABA;
    argos::CCI_EPuckRangeAndBearingSensor* m_pcEPuckRABS;
    // Erase the readings.
    void ClearPackets();
    // Send a buffer to all the emitters.
    // void SetData(const UInt8 un_data[argos::CCI_EPuckRangeAndBearingActuator::MAX_BYTES_SENT]);
    void SetData(const boost::python::list un_data);
    boost::python::list GetData() const;

    // TODO: Set all bits at once
    // Return the readings obtained at this control step.
    // Each reading contains the range, the horizontal bearing, the vertical bearing and the data
    // table. The data table is exposed as a c_byte_array.
    boost::python::list GetReadings() const;
    boost::python::list GetPackets() const;
};

// Wrapper for the EPuck Leds Actuator.
class CEPuckLedsActuatorWrapper {
  public:
    CEPuckLedsActuatorWrapper();
    ~CEPuckLedsActuatorWrapper(){};

    argos::CCI_EPuckRGBLEDsActuator* m_pcEPuckLeds;

    // Set the color of a given led, given its name.
    void SetSingleColorString(const UInt8 un_led_id, const std::string str_color_name);

    // Set the color of a given led, given its RGB values.
    void SetSingleColorRGB(const UInt8 un_led_id, const UInt8 un_red, const UInt8 un_green,
                           const UInt8 un_blue);

    // Set the color of every led, given its name.
    void SetAllColorsString(const std::string str_color_name);

    // Set the color of every led, given its RGB values.
    void SetAllColorsRGB(const UInt8 un_red, const UInt8 un_green, const UInt8 un_blue);
};

} // namespace argos
#endif
