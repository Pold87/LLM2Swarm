/*
 * AUTHOR: Ken Hasselmann <arg AT kenh DOT fr>
 *
 * Connects ARGoS to python
 *
 */
#include "py_wrapper.h"

using namespace argos;
using namespace boost::python;

/****************************************/
/****************************************/

EnvironmentWrapper::EnvironmentWrapper() {}

void EnvironmentWrapper::Logprint(const std::string& str_message) {
    std::cout << str_message << std::endl;
}



/****************************************/
/****************************************/

ActusensorsWrapper::ActusensorsWrapper() {}

void ActusensorsWrapper::SetId(const std::string id) {
    m_cVariableWrapper.m_cId = id;
}

void ActusensorsWrapper::Logprint(const std::string& str_message) {
    std::cout << str_message << std::endl;
}


/****************************************/
/****************************************/

// Initialize the actuator specified by the provided name.

// NOTE: the Init function gives problems for all the sensors/actuators that use the "media"
// parameter. When the argos file is loaded, the following error is given:
//    [FATAL] Error parsing attribute "medium"
//    Attribute does not exist <ticpp.h@1791>
// The sensors/actuators seem to work even without it, so for now it has been disabled.
void ActusensorsWrapper::CreateActu(const std::string str_name, CCI_Actuator* pc_actu,
                                    TConfigurationNode& t_node) {
    if (str_name == "differential_steering") {
        m_cWheelsWrapper.m_pcWheels = dynamic_cast<CCI_DifferentialSteeringActuator*>(pc_actu);
        m_cWheelsWrapper.m_pcWheels->Init(t_node);
    } else if (str_name == "footbot_gripper") {
        m_cGripperWrapper.m_pcGripper = dynamic_cast<CCI_FootBotGripperActuator*>(pc_actu);
        m_cGripperWrapper.m_pcGripper->Init(t_node);
    } else if (str_name == "leds") {
        m_cLedsWrapper.m_pcLeds = (CCI_LEDsActuator*)pc_actu;
        // m_cLedsWrapper.m_pcLeds->Init(t_node);
    } else if (str_name == "range_and_bearing") {
        m_cRangeAndBearingWrapper.m_pcRABA = (CCI_RangeAndBearingActuator*)pc_actu;
        // m_cRangeAndBearingWrapper.m_pcRABA->Init(t_node);
    } else if (str_name == "footbot_distance_scanner") {
        m_cDistanceScannerWrapper.m_pcScannerActuator =
            dynamic_cast<CCI_FootBotDistanceScannerActuator*>(pc_actu);
        m_cDistanceScannerWrapper.m_pcScannerActuator->Init(t_node);
    } else if (str_name == "footbot_turret") {
        m_cTurretWrapper.m_pcTurretActuator = dynamic_cast<CCI_FootBotTurretActuator*>(pc_actu);
        m_cTurretWrapper.m_pcTurretActuator->Init(t_node);
    }

    // E-Puck actuators.
    else if (str_name == "epuck_wheels") {
        m_cEPuckWheelsWrapper.m_pcEPuckWheels = dynamic_cast<CCI_EPuckWheelsActuator*>(pc_actu);
        m_cEPuckWheelsWrapper.m_pcEPuckWheels->Init(t_node);
    } else if (str_name == "epuck_range_and_bearing") {
        m_cEPuckRangeAndBearingWrapper.m_pcEPuckRABA =
            dynamic_cast<CCI_EPuckRangeAndBearingActuator*>(pc_actu);
        /* m_cEPuckRangeAndBearingWrapper.m_pcEPuckRABA->Init(t_node); */
    } else if (str_name == "epuck_rgb_leds") {
        m_cEPuckLedsWrapper.m_pcEPuckLeds = (CCI_EPuckRGBLEDsActuator*)pc_actu;
        // m_cLedsWrapper.m_pcLeds->Init(t_node);
    }
}

/****************************************/
/****************************************/

// Initialize the sensor specified by the provided name.
void ActusensorsWrapper::CreateSensor(const std::string str_name, CCI_Sensor* pc_sensor,
                                      TConfigurationNode& t_node) {

    // Generic sensors.
    if (str_name == "colored_blob_omnidirectional_camera") {
        m_cOmnidirectionalCameraWrapper.m_pcOmniCam = (CCI_ColoredBlobOmnidirectionalCameraSensor*)pc_sensor;
        // m_cOmnidirectionalCameraWrapper.m_pcOmniCam->Init(t_node);

    } else if (str_name == "colored_blob_perspective_camera") {
        m_cPerspectiveCameraWrapper.m_pcPerspCam = (CCI_ColoredBlobPerspectiveCameraSensor*)pc_sensor;
        // m_cPerspectiveCameraWrapper.m_pcPerspCam->Init(t_node);

    } else if (str_name == "range_and_bearing") {
        m_cRangeAndBearingWrapper.m_pcRABS = (CCI_RangeAndBearingSensor*)pc_sensor;    
        // m_cRangeAndBearingWrapper.m_pcRABS->Init(t_node);

    } else if (str_name == "differential_steering") {
        m_cDifferentialSteeringSensor.m_pcDifferentialSteeringSensor = (CCI_DifferentialSteeringSensor*)pc_sensor;
    } else if (str_name == "positioning") {
        m_cPositioningWrapper.m_pcPositioning = (CCI_PositioningSensor*)pc_sensor;
    } 

    // Footbot sensors.
    else if (str_name == "footbot_motor_ground") {
        m_cGroundSensorWrapper.m_pcGround = (CCI_FootBotMotorGroundSensor*)pc_sensor;
        m_cGroundSensorWrapper.m_pcGround->Init(t_node);

    } else if (str_name == "footbot_proximity") {
        m_cProximitySensorWrapper.m_pcProximity = (CCI_FootBotProximitySensor*)pc_sensor;
        m_cProximitySensorWrapper.m_pcProximity->Init(t_node);

    } else if (str_name == "footbot_base_ground") {
        m_cBaseGroundSensorWrapper.m_pcBaseGround = dynamic_cast<CCI_FootBotBaseGroundSensor*>(pc_sensor);
        m_cBaseGroundSensorWrapper.m_pcBaseGround->Init(t_node);

    } else if (str_name == "footbot_light") {
        m_cLightSensorWrapper.m_pcLight = (CCI_FootBotLightSensor*)pc_sensor;
        m_cLightSensorWrapper.m_pcLight->Init(t_node);

    } else if (str_name == "footbot_distance_scanner") {
        m_cDistanceScannerWrapper.m_pcScannerSensor = (CCI_FootBotDistanceScannerSensor*)pc_sensor;
        m_cDistanceScannerWrapper.m_pcScannerSensor->Init(t_node);

    } else if (str_name == "footbot_turret_encoder") {
        m_cTurretWrapper.m_pcTurretSensor = dynamic_cast<CCI_FootBotTurretEncoderSensor*>(pc_sensor);
        m_cTurretWrapper.m_pcTurretSensor->Init(t_node);
    }

    // E-Puck sensors.
    else if (str_name == "epuck_proximity") {
        m_cEPuckProximitySensorWrapper.m_pcEPuckProximity = dynamic_cast<CCI_EPuckProximitySensor*>(pc_sensor);
        m_cEPuckProximitySensorWrapper.m_pcEPuckProximity->Init(t_node);

    } else if (str_name == "epuck_ground") {
        m_cEPuckGroundSensorWrapper.m_pcEPuckGround = dynamic_cast<CCI_EPuckGroundSensor*>(pc_sensor);
        m_cEPuckGroundSensorWrapper.m_pcEPuckGround->Init(t_node);

    } else if (str_name == "epuck_range_and_bearing") {
        m_cEPuckRangeAndBearingWrapper.m_pcEPuckRABS = (CCI_EPuckRangeAndBearingSensor*)pc_sensor;
        // m_cRangeAndBearingWrapper.m_pcRABA->Init(t_node);
    }
}

/****************************************/
/****************************************/

// Create a color by providing its name.
ActusensorsWrapper::CColorWrapper::CColorWrapper(const std::string str_color_name) {
    if (str_color_name == "red")
        m_cColor = argos::CColor::RED;
    else if (str_color_name == "black")
        m_cColor = argos::CColor::BLACK;
    else if (str_color_name == "blue")
        m_cColor = argos::CColor::BLUE;
    else if (str_color_name == "green")
        m_cColor = argos::CColor::GREEN;
    else if (str_color_name == "yellow")
        m_cColor = argos::CColor::YELLOW;
    else if (str_color_name == "white")
        m_cColor = argos::CColor::WHITE;
    else if (str_color_name == "gray10")
        m_cColor = argos::CColor::GRAY10;
    else if (str_color_name == "gray20")
        m_cColor = argos::CColor::GRAY20;
    else if (str_color_name == "gray30")
        m_cColor = argos::CColor::GRAY30;
    else if (str_color_name == "gray40")
        m_cColor = argos::CColor::GRAY40;
    else if (str_color_name == "gray50")
        m_cColor = argos::CColor::GRAY50;
    else if (str_color_name == "gray60")
        m_cColor = argos::CColor::GRAY60;
    else if (str_color_name == "gray70")
        m_cColor = argos::CColor::GRAY70;
    else if (str_color_name == "gray80")
        m_cColor = argos::CColor::GRAY80;
    else if (str_color_name == "gray90")
        m_cColor = argos::CColor::GRAY90;
    else if (str_color_name == "magenta")
        m_cColor = argos::CColor::MAGENTA;
    else if (str_color_name == "cyan")
        m_cColor = argos::CColor::CYAN;
    else if (str_color_name == "orange")
        m_cColor = argos::CColor::ORANGE;
    else if (str_color_name == "brown")
        m_cColor = argos::CColor::BROWN;
    else if (str_color_name == "purple")
        m_cColor = argos::CColor::PURPLE;
    else if (str_color_name == "custom")
        m_cColor = argos::CColor(70,160,70,0);
    else if (str_color_name == "custom2")
        m_cColor = argos::CColor(160,110,110,0);
    else
        m_cColor = argos::CColor::WHITE;
}

// Create a color by providing its RGB values.
ActusensorsWrapper::CColorWrapper::CColorWrapper(const UInt8 un_red, const UInt8 un_green,
                                                 const UInt8 un_blue) {
    m_cColor = argos::CColor((const UInt8)un_red, (const UInt8)un_green, (const UInt8)un_blue, 0);
}

/****************************************/
/****************************************/

void ActusensorsWrapper::CByteArraySetItem(argos::CByteArray& c_vec, const UInt32 un_index,
                                           const UInt8 un_value) {
    if (un_index >= 0 && un_index < c_vec.Size()) {
        c_vec[un_index] = un_value;
    } else {
        PyErr_SetString(PyExc_IndexError, "index out of range");
        boost::python::throw_error_already_set();
    }
}

UInt8 ActusensorsWrapper::CByteArrayGetItem(const argos::CByteArray& c_vec, const UInt32 un_index) {
    if (un_index >= 0 && un_index < c_vec.Size()) {
        return c_vec[un_index];
    }
    PyErr_SetString(PyExc_IndexError, "index out of range");
    boost::python::throw_error_already_set();
    return {};
}

Real ActusensorsWrapper::EPuckGroundReadingsGetItem(
    const argos::CCI_EPuckGroundSensor::SReadings& c_readings, const UInt32 un_index) {
    if (un_index >= 0 && un_index < 3) {
        return c_readings[un_index];
    }
    PyErr_SetString(PyExc_IndexError, "index out of range");
    boost::python::throw_error_already_set();
    return {};
}

/****************************************/
/****************************************/

// BOOST_PYTHON_MODULE(libpy_qtuser_function_interface) {


// }

BOOST_PYTHON_MODULE(libpy_controller_interface) {

    // Export the main "environment" class with the draw functions and variables
     class_<EnvironmentWrapper, boost::shared_ptr<EnvironmentWrapper>, boost::noncopyable>("environment", no_init)
        .def("logprint", &EnvironmentWrapper::Logprint)
        .staticmethod("logprint")
        .add_property("qt_draw", &EnvironmentWrapper::m_cCQTOpenGLUserFunctionsWrapper)
        .add_property("variables", &EnvironmentWrapper::m_cVariableWrapper);

    // Export the main "robot" class with the sensors, actuators and variables
    class_<ActusensorsWrapper, boost::shared_ptr<ActusensorsWrapper>, boost::noncopyable>("robot", no_init)
        .def("logprint", &ActusensorsWrapper::Logprint)
        .staticmethod("logprint")
        .add_property("variables", &ActusensorsWrapper::m_cVariableWrapper)
        .add_property("wheels", &ActusensorsWrapper::m_cWheelsWrapper)
        .add_property("differential_steering", &ActusensorsWrapper::m_cDifferentialSteeringSensor)
        .add_property("colored_blob_omnidirectional_camera", &ActusensorsWrapper::m_cOmnidirectionalCameraWrapper)
        .add_property("colored_blob_perspective_camera", &ActusensorsWrapper::m_cPerspectiveCameraWrapper)
        .add_property("proximity", &ActusensorsWrapper::m_cProximitySensorWrapper)
        .add_property("position", &ActusensorsWrapper::m_cPositioningWrapper)
        .add_property("leds", &ActusensorsWrapper::m_cLedsWrapper)
        .add_property("range_and_bearing", &ActusensorsWrapper::m_cRangeAndBearingWrapper)
        .add_property("motor_ground", &ActusensorsWrapper::m_cGroundSensorWrapper)
        .add_property("base_ground", &ActusensorsWrapper::m_cBaseGroundSensorWrapper)
        .add_property("gripper", &ActusensorsWrapper::m_cGripperWrapper)
        .add_property("light_sensor", &ActusensorsWrapper::m_cLightSensorWrapper)
        .add_property("distance_scanner", &ActusensorsWrapper::m_cDistanceScannerWrapper)
        .add_property("turret", &ActusensorsWrapper::m_cTurretWrapper)
        .add_property("epuck_wheels", &ActusensorsWrapper::m_cEPuckWheelsWrapper)
        .add_property("epuck_proximity", &ActusensorsWrapper::m_cEPuckProximitySensorWrapper)
        .add_property("epuck_ground", &ActusensorsWrapper::m_cEPuckGroundSensorWrapper)
        .add_property("epuck_range_and_bearing", &ActusensorsWrapper::m_cEPuckRangeAndBearingWrapper)
        .add_property("epuck_leds", &ActusensorsWrapper::m_cEPuckLedsWrapper);

    // Export "QTOpenGLUserFunctionsWrapper" that contains qtuser draw functions
    class_<CQTOpenGLUserFunctionsWrapper, boost::noncopyable>("qtuser_wrapper", no_init)
        .def("set_draw_list", &CQTOpenGLUserFunctionsWrapper::SetDrawList)
        .def("get_draw_list", &CQTOpenGLUserFunctionsWrapper::GetDrawList)  
        .def("circle", &CQTOpenGLUserFunctionsWrapper::DrawCircle)
        .def("ray", &CQTOpenGLUserFunctionsWrapper::DrawRay)
        .def("polygon", &CQTOpenGLUserFunctionsWrapper::DrawPolygon)
        .def("cylinder", &CQTOpenGLUserFunctionsWrapper::DrawCylinder)
        .def("box", &CQTOpenGLUserFunctionsWrapper::DrawBox)
        .def("text", &CQTOpenGLUserFunctionsWrapper::DrawText)
        .def("close_window", &CQTOpenGLUserFunctionsWrapper::CloseWindow);

    // Export "VariableWrapper" that contains a robot's variables
    class_<CVariableWrapper, boost::noncopyable>("variable_wrapper", no_init)
        .def("get_id", &CVariableWrapper::GetId)
        .def("set_attribute", &CVariableWrapper::SetAttribute)
        .def("get_attribute", &CVariableWrapper::GetAttribute)  
        .def("get_all_attributes", &CVariableWrapper::GetAllAttributes);
        
    // Export "WheelsWrapper", wrapper of CCI_DifferentialSteeringActuator.
    class_<CWheelsWrapper, boost::noncopyable>("wheels_wrapper", no_init)
        .def("set_speed", &CWheelsWrapper::SetSpeed);

    // Export "DifferentialSteeringSensorWrapper", wrapper of CCI_DifferentialSteeringSensor.
    class_<CDifferentialSteeringSensorWrapper, boost::noncopyable>("differential_steering_sensor_wrapper", no_init)
        .def("get_readings", &CDifferentialSteeringSensorWrapper::GetReading)
        .def("get_distances", &CDifferentialSteeringSensorWrapper::GetDistances);
 
    // Export "EPuckWheelsWrapper", wrapper of CCI_EPuckWheelsActuator.
    class_<CEPuckWheelsWrapper, boost::noncopyable>("epuck_wheels_wrapper", no_init)
        .def("set_speed", &CEPuckWheelsWrapper::SetSpeed);

    // Export "GripperWrapper", wrapper of CFootBotGripping.
    class_<CGripperWrapper, boost::noncopyable>("m_cGripperWrapper", no_init)
        .def("lock", &CGripperWrapper::Lock)
        .def("unlock", &CGripperWrapper::Unlock);

    // Export "OmnidirectionalCameraWrapper" , wrapper of
    // CCI_ColoredBlobOmnidirectionalCameraSensor.
    class_<COmnidirectionalCameraWrapper, boost::noncopyable>("omnidirectional_camera_wrapper",
                                                              no_init)
        .def("enable", &COmnidirectionalCameraWrapper::Enable)
        .def("disable", &COmnidirectionalCameraWrapper::Disable)
        .def("get_readings", &COmnidirectionalCameraWrapper::GetReadings)
        .def("set_fov", &COmnidirectionalCameraWrapper::setFOV)
        .def("get_counter", &COmnidirectionalCameraWrapper::GetCounter);

    class_<CPerspectiveCameraWrapper, boost::noncopyable>("perspective_camera_wrapper",
                                                              no_init)
        .def("enable", &CPerspectiveCameraWrapper::Enable)
        .def("disable", &CPerspectiveCameraWrapper::Disable)
        .def("get_readings", &CPerspectiveCameraWrapper::GetReadings);

    // Export "PositionSensorWrapper", wrapper of CCI_PositionSensor.
    class_<CPositioningSensorWrapper, boost::noncopyable>("positioning_wrapper",
                                                               no_init)
        .def("get_position", &CPositioningSensorWrapper::GetPosition)
        .def("get_orientation", &CPositioningSensorWrapper::GetOrientation);

    // Export "FootBotProximitySensorWrapper", wrapper of CCI_FootBotProximitySensor.
    class_<CFootBotProximitySensorWrapper, boost::noncopyable>("footbot_proximity_sensor_wrapper",
                                                               no_init)
        .def("get_readings", &CFootBotProximitySensorWrapper::GetReadings);

    // Export "CEPuckProximitySensorWrapper", wrapper of CCI_EPuckProximitySensor.
    class_<CEPuckProximitySensorWrapper, boost::noncopyable>("epuck_proximity_sensor_wrapper",
                                                             no_init)
        .def("get_readings", &CEPuckProximitySensorWrapper::GetReadings);

    // Export "LedsActuatorWrapper", wrapper of CCI_LEDsActuator.
    class_<CLedsActuatorWrapper, boost::noncopyable>("leds_actuator_wrapper", no_init)
        .def("set_single_color", &CLedsActuatorWrapper::SetSingleColorString)
        .def("set_single_color", &CLedsActuatorWrapper::SetSingleColorRGB)
        .def("set_all_colors", &CLedsActuatorWrapper::SetAllColorsString)
        .def("set_all_colors", &CLedsActuatorWrapper::SetAllColorsRGB);

    // Export "EPuckLedsActuatorWrapper", wrapper of CCI_EPuckRGBLEDsActuator.
    class_<CEPuckLedsActuatorWrapper, boost::noncopyable>("epuck_leds_actuator_wrapper", no_init)
        .def("set_single_color", &CEPuckLedsActuatorWrapper::SetSingleColorString)
        .def("set_single_color", &CEPuckLedsActuatorWrapper::SetSingleColorRGB)
        .def("set_all_colors", &CEPuckLedsActuatorWrapper::SetAllColorsString)
        .def("set_all_colors", &CEPuckLedsActuatorWrapper::SetAllColorsRGB);

    // Export RangeAndBearingWrapper, wrapper of CCI_RangeAndBearingActuator and
    // CCI_RangeAndBearingSensor.
    class_<CRangeAndBearingWrapper, boost::noncopyable>("m_cRangeAndBearingWrapper", no_init)
        .def("clear_data", &CRangeAndBearingWrapper::ClearData)
        .def("set_data", &CRangeAndBearingWrapper::SetData)
        .def("get_readings", &CRangeAndBearingWrapper::GetReadings);

    // Export RangeAndBearingWrapper, wrapper of CCI_RangeAndBearingActuator and
    // CCI_RangeAndBearingSensor.
    class_<CEPuckRangeAndBearingWrapper, boost::noncopyable>("m_cEPuckRangeAndBearingWrapper",
                                                             no_init)
        .def("clear_data", &CEPuckRangeAndBearingWrapper::ClearPackets)
        .def("set_data", &CEPuckRangeAndBearingWrapper::SetData)
        .def("get_data", &CEPuckRangeAndBearingWrapper::GetData)
        .def("get_readings", &CEPuckRangeAndBearingWrapper::GetReadings)
        .def("get_packets", &CEPuckRangeAndBearingWrapper::GetPackets);


    // Export GroundSensorWrapper, wrapper of CCI_FootBotMotorGroundSensor.
    class_<CGroundSensorWrapper, boost::noncopyable>("m_cGroundSensorWrapper", no_init)
        .def("get_readings", &CGroundSensorWrapper::GetReadings);

    // Export BaseGroundSensorWrapper, wrapper of CCI_FootBotBaseGroundSensor .
    class_<CBaseGroundSensorWrapper, boost::noncopyable>("m_cBaseGroundSensorWrapper", no_init)
        .def("get_readings", &CBaseGroundSensorWrapper::GetReadings);

    // Export EPuckGroundSensorWrapper, wrapper of CCI_EPuckGroundSensor .
    class_<CEPuckGroundSensorWrapper, boost::noncopyable>("m_cEPuckGroundSensorWrapper", no_init)
        .def("get_readings", &CEPuckGroundSensorWrapper::GetReadings);

    // Export LightSensorWrapper, wrapper of CCI_FootBotLightSensor.
    class_<CLightSensorWrapper, boost::noncopyable>("m_cLightSensorWrapper", no_init)
        .def("get_readings", &CLightSensorWrapper::GetReadings);

    // Export DistanceScannerWrapper, wrapper of CCI_FootBotDistanceScannerActuator and
    // CCI_FootBotDistanceScannerSensor.
    class_<CDistanceScannerWrapper, boost::noncopyable>("m_cDistanceScannerWrapper", no_init)
        .def("enable", &CDistanceScannerWrapper::Enable)
        .def("disable", &CDistanceScannerWrapper::Disable)
        .def("set_rpm", &CDistanceScannerWrapper::SetRPM)
        .def("set_angle", &CDistanceScannerWrapper::SetAngle)
        .def("get_readings", &CDistanceScannerWrapper::GetReadings)
        .def("get_short_readings", &CDistanceScannerWrapper::GetShortReadings)
        .def("get_long_readings", &CDistanceScannerWrapper::GetLongReadings);

    // Export TurretWrapper, wrapper of CCI_FootBotTurretEncoderSensor and
    // CCI_FootBotTurretActuator.
    class_<CTurretWrapper, boost::noncopyable>("m_cTurretWrapper", no_init)
        .def("get_rotation", &CTurretWrapper::GetRotation)
        .def("set_rotation", &CTurretWrapper::SetRotation)
        .def("set_rotation_speed", &CTurretWrapper::SetRotationSpeed)
        .def("set_mode", &CTurretWrapper::SetMode)
        .def("set_active_with_rotation", &CTurretWrapper::SetActiveWithRotation)
        .def("set_speed_control_mode", &CTurretWrapper::SetSpeedControlMode)
        .def("set_position_control_mode", &CTurretWrapper::SetPositionControlMode)
        .def("set_passive_mode", &CTurretWrapper::SetPassiveMode);

    // Export a CRadians - float map, used for the readings of the Distance Scanner Sensor.
    // The map can be iterated. For a given map entry, get the key with map_entry.key()
    // (map_entry.key().value() to get the actual angle value),
    // and the value with map_entry.data()
    class_<std::map<argos::CRadians, Real>>("distance_sensor_readings_map")
        .def(boost::python::map_indexing_suite<std::map<argos::CRadians, Real>>());

    // Export the CRadians class, used by the readings of various sensors.
    // TODO: add more properties
    class_<argos::CRadians>("radians", init<>())
        .def(init<Real>())
        .def("value", &argos::CRadians::GetValue);

    // Export the SReading class, used to store the readings of the proximity sensor.
    class_<argos::CCI_FootBotProximitySensor::SReading>("footbot_proximity_reading", no_init)
        .def_readonly("value", &argos::CCI_FootBotProximitySensor::SReading::Value)
        .def_readonly("angle", &argos::CCI_FootBotProximitySensor::SReading::Angle);

    // Export the SReading class, used to store the readings of the proximity sensor.
    class_<argos::CCI_EPuckProximitySensor::SReading>("epuck_proximity_reading", no_init)
        .def_readonly("value", &argos::CCI_EPuckProximitySensor::SReading::Value)
        .def_readonly("angle", &argos::CCI_EPuckProximitySensor::SReading::Angle);

    // Export the SReading class, used to store the readings of the light sensor.
    class_<argos::CCI_FootBotLightSensor::SReading>("footbot_light_reading", no_init)
        .def_readonly("value", &argos::CCI_FootBotLightSensor::SReading::Value)
        .def_readonly("angle", &argos::CCI_FootBotLightSensor::SReading::Angle);

    // Export the SBlob class, used to store the readings of the omnidirectiona camera.
    class_<argos::CCI_ColoredBlobOmnidirectionalCameraSensor::SBlob>(
        "omnidirectional_camera_packet", no_init)
        .def_readonly("distance",
                      &argos::CCI_ColoredBlobOmnidirectionalCameraSensor::SBlob::Distance)
        .def_readonly("angle", &argos::CCI_ColoredBlobOmnidirectionalCameraSensor::SBlob::Angle)
        .def_readonly("color", &argos::CCI_ColoredBlobOmnidirectionalCameraSensor::SBlob::Color);

    // Export the SPacket class, used to store the readings of the range and bearing sensor.
    class_<argos::CCI_RangeAndBearingSensor::SPacket>("range_and_bearing_packet", no_init)
        .add_property("range", &argos::CCI_RangeAndBearingSensor::SPacket::Range)
        .add_property("horizontal_bearing",
                      &argos::CCI_RangeAndBearingSensor::SPacket::HorizontalBearing)
        .add_property("vertical_bearing",
                      &argos::CCI_RangeAndBearingSensor::SPacket::VerticalBearing)
        .add_property("data", &argos::CCI_RangeAndBearingSensor::SPacket::Data);

    // Export the SReceivedPacket class, used to store the readings of the EPuck range and bearing
    // sensor.
    class_<argos::CCI_EPuckRangeAndBearingSensor::SReceivedPacket>("range_and_bearing_packet",
                                                                   no_init)
        .add_property("range", &argos::CCI_EPuckRangeAndBearingSensor::SReceivedPacket::Range)
        .add_property("bearing", &argos::CCI_EPuckRangeAndBearingSensor::SReceivedPacket::Bearing)
        .add_property("data", &argos::CCI_EPuckRangeAndBearingSensor::SReceivedPacket::Data);

    // Export the SReading class, used to store the readings of the motor ground sensor.
    // Each reading contains a value and the offset, expressed in x/y coordinates.
    class_<argos::CCI_FootBotMotorGroundSensor::SReading>("motor_ground_sensor_wrapper_reading",
                                                          no_init)
        .def_readonly("value", &argos::CCI_FootBotMotorGroundSensor::SReading::Value)
        .def_readonly("offset", &argos::CCI_FootBotMotorGroundSensor::SReading::Offset);

    // Export the SReading class, used to store the readings of the base ground sensor.
    // Each reading contains a value and the offset, expressed in x/y coordinates.
    class_<argos::CCI_FootBotBaseGroundSensor::SReading>("base_ground_sensor_wrapper_reading",
                                                         no_init)
        .def_readonly("value", &argos::CCI_FootBotBaseGroundSensor::SReading::Value)
        .def_readonly("offset", &argos::CCI_FootBotBaseGroundSensor::SReading::Offset);

    // Export the SReading class, used to store the readings of the EPuck ground sensor.
    // Each reading has 3 values (left, center, right).
    class_<argos::CCI_EPuckGroundSensor::SReadings>("epuck_ground_sensor_wrapper_reading", no_init)
        .def_readonly("left", &argos::CCI_EPuckGroundSensor::SReadings::Left)
        .def_readonly("center", &argos::CCI_EPuckGroundSensor::SReadings::Center)
        .def_readonly("right", &argos::CCI_EPuckGroundSensor::SReadings::Right)
        .def("__getitem__", &ActusensorsWrapper::EPuckGroundReadingsGetItem);

    class_<argos::CVector2>("vector2", init<>())
        .def(init<Real, Real>())
        .add_property("x", &argos::CVector2::GetX, &argos::CVector2::SetX)
        .add_property("y", &argos::CVector2::GetY, &argos::CVector2::SetY)
        .def_readonly("length", &argos::CVector2::Length)
        .def_readonly("angle", &argos::CVector2::Angle)
        .def_readonly("square_length", &argos::CVector2::SquareLength);

    // Export the ColorWrapper class.
    class_<ActusensorsWrapper::CColorWrapper>("color", init<std::string>())
        .def(init<UInt8, UInt8, UInt8>())
        .add_property("raw_color", &ActusensorsWrapper::CColorWrapper::m_cColor);
    // TODO: add other color stuff

    // Export the CColor class. This class is not directly usable in python,
    // but it is exported to simplify the usage of colors in python.
    class_<argos::CColor>("raw_color", no_init).def("__eq__", &argos::CColor::operator==);

    // Export the CByteArray class, and define new functions on it to access its data.
    class_<argos::CByteArray>("c_byte_array", no_init)
        .def("__getitem__", &ActusensorsWrapper::CByteArrayGetItem)
        .def("__setitem__", &ActusensorsWrapper::CByteArraySetItem);
}
