#ifndef PY_ACTUSENSOR_WRAPPER_FOOTBOT_H
#define PY_ACTUSENSOR_WRAPPER_FOOTBOT_H

#include <boost/python.hpp>
#include <boost/python/suite/indexing/map_indexing_suite.hpp>

#include <argos3/core/control_interface/ci_controller.h>

#include <argos3/plugins/robots/foot-bot/control_interface/ci_footbot_gripper_actuator.h>
#include <argos3/plugins/robots/foot-bot/control_interface/ci_footbot_proximity_sensor.h>
/* Definition of the foot-bot motor ground sensor */
#include <argos3/plugins/robots/foot-bot/control_interface/ci_footbot_motor_ground_sensor.h>
/* Definition of the foot-bot gripper actuator */
#include <argos3/plugins/robots/foot-bot/control_interface/ci_footbot_gripper_actuator.h>
/* Definition of the foot-bot light sensor */
#include <argos3/plugins/robots/foot-bot/control_interface/ci_footbot_base_ground_sensor.h>
#include <argos3/plugins/robots/foot-bot/control_interface/ci_footbot_distance_scanner_actuator.h>
#include <argos3/plugins/robots/foot-bot/control_interface/ci_footbot_distance_scanner_sensor.h>
#include <argos3/plugins/robots/foot-bot/control_interface/ci_footbot_light_sensor.h>
#include <argos3/plugins/robots/foot-bot/control_interface/ci_footbot_turret_actuator.h>
#include <argos3/plugins/robots/foot-bot/control_interface/ci_footbot_turret_encoder_sensor.h>

#include <argos3/core/utility/logging/argos_log.h>
#include <argos3/core/utility/math/general.h>

#include <iostream>
#include <string>

namespace argos {

// Wrapper for the Gripper Actuator
class CGripperWrapper {
  public:
    CGripperWrapper();
    ~CGripperWrapper(){};
    argos::CCI_FootBotGripperActuator* m_pcGripper;

    void Lock();

    void Unlock();
};

// Wrapper for the Proximity Sensor.
class CFootBotProximitySensorWrapper {
  public:
    CFootBotProximitySensorWrapper();
    ~CFootBotProximitySensorWrapper(){};
    argos::CCI_FootBotProximitySensor* m_pcProximity;

    // Obtain the proximity readings at this control step.
    // The readings are exposed as a python list.
    // Each reading is exposed as a "proximity_reading", from which it is possible to obtain value
    // and angle.
    boost::python::list GetReadings() const;
};

// Wrapper for the Ground Motor Sensor.
// Allows to get a list of readings from the ground.
class CGroundSensorWrapper {
  public:
    CGroundSensorWrapper();
    ~CGroundSensorWrapper(){};
    argos::CCI_FootBotMotorGroundSensor* m_pcGround;

    boost::python::list GetReadings() const;
};

/****************************************/
/****************************************/

// Wrapper for the Base Ground Sensor.
// Allows to get a list of readings from the ground.
class CBaseGroundSensorWrapper {
  public:
    CBaseGroundSensorWrapper();
    ~CBaseGroundSensorWrapper(){};
    argos::CCI_FootBotBaseGroundSensor* m_pcBaseGround;

    boost::python::list GetReadings() const;
};

/****************************************/
/****************************************/

// Wrapper for the Light Sensor
class CLightSensorWrapper {
  public:
    CLightSensorWrapper();
    ~CLightSensorWrapper(){};
    argos::CCI_FootBotLightSensor* m_pcLight;

    boost::python::list GetReadings() const;
};

// Wrapper for the Distance Scanner Sensor and Actuator
class CDistanceScannerWrapper {

  public:
    CDistanceScannerWrapper();
    ~CDistanceScannerWrapper(){};
    argos::CCI_FootBotDistanceScannerActuator* m_pcScannerActuator;
    argos::CCI_FootBotDistanceScannerSensor* m_pcScannerSensor;

    void Enable();

    void Disable();

    void SetRPM(const Real f_rpm);

    void SetAngle(const Real f_angle);

    std::map<CRadians, Real> GetReadings() const;

    std::map<CRadians, Real> GetShortReadings() const;

    std::map<CRadians, Real> GetLongReadings() const;
};

/****************************************/
/****************************************/

// Wrapper for the Turret Actuator and Sensor
class CTurretWrapper {
  public:
    CTurretWrapper();
    ~CTurretWrapper(){};
    CCI_FootBotTurretEncoderSensor* m_pcTurretSensor;
    CCI_FootBotTurretActuator* m_pcTurretActuator;

    CRadians GetRotation() const;

    void SetRotation(const Real f_angle);

    void SetRotationSpeed(const UInt32 n_speed_pulses);

    void SetMode(const std::string str_mode_name);

    void SetActiveWithRotation(const Real f_angle);

    void SetSpeedControlMode();

    void SetPositionControlMode();

    void SetPassiveMode();
};

} // namespace argos
#endif
