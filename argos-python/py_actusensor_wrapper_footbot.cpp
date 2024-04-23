#include "py_actusensor_wrapper_footbot.h"
#include "py_wrapper.h"

using namespace argos;

/****************************************/
/****************************************/

CGripperWrapper::CGripperWrapper() {}

void CGripperWrapper::Lock() {
    if (m_pcGripper == nullptr) {
        ActusensorsWrapper::Logprint(
            "Gripper Actuator not implemented or not stated in XML config.");
        return;
    }
    m_pcGripper->LockPositive();
}

void CGripperWrapper::Unlock() {
    if (m_pcGripper == nullptr) {
        ActusensorsWrapper::Logprint(
            "Gripper Actuator not implemented or not stated in XML config.");
        return;
    }
    m_pcGripper->Unlock();
}

/****************************************/
/****************************************/

CFootBotProximitySensorWrapper::CFootBotProximitySensorWrapper() {}

boost::python::list CFootBotProximitySensorWrapper::GetReadings() const {
    if (m_pcProximity == nullptr) {
        ActusensorsWrapper::Logprint(
            "Proximity sensor not implemented or not stated in XML config.");
        // TODO: add exception?
        return {};
    }
    return ActusensorsWrapper::ToPythonList(m_pcProximity->GetReadings());
}

/****************************************/
/****************************************/
CGroundSensorWrapper::CGroundSensorWrapper() {}

boost::python::list CGroundSensorWrapper::GetReadings() const {
    if (m_pcGround == nullptr) {
        ActusensorsWrapper::Logprint(
            "Motor Ground Sensor not implemented or not stated in XML config.");
        // TODO: add exception?
        return {};
    }
    return ActusensorsWrapper::ToPythonList(m_pcGround->GetReadings());
}

/****************************************/
/****************************************/

CBaseGroundSensorWrapper::CBaseGroundSensorWrapper() {}

boost::python::list CBaseGroundSensorWrapper::GetReadings() const {
    if (m_pcBaseGround == nullptr) {
        ActusensorsWrapper::Logprint(
            "Base Ground Sensor not implemented or not stated in XML config.");
        // TODO: add exception?
        return {};
    }
    return ActusensorsWrapper::ToPythonList(m_pcBaseGround->GetReadings());
}

/****************************************/
/****************************************/

CLightSensorWrapper::CLightSensorWrapper() {}

boost::python::list CLightSensorWrapper::GetReadings() const {
    if (m_pcLight == nullptr) {
        ActusensorsWrapper::Logprint("Light Sensor not implemented or not stated in XML config.");
        // TODO: add exception?
        return {};
    }
    return ActusensorsWrapper::ToPythonList(m_pcLight->GetReadings());
}

/****************************************/
/****************************************/

CDistanceScannerWrapper::CDistanceScannerWrapper() {}

void CDistanceScannerWrapper::Enable() {
    if (m_pcScannerActuator == nullptr) {
        ActusensorsWrapper::Logprint(
            "Distance Scanner Actuator not implemented or not stated in XML config.");
        return;
    }
    m_pcScannerActuator->Enable();
}

void CDistanceScannerWrapper::Disable() {
    if (m_pcScannerActuator == nullptr) {
        ActusensorsWrapper::Logprint(
            "Distance Scanner Actuator not implemented or not stated in XML config.");
        return;
    }
    m_pcScannerActuator->Disable();
}

void CDistanceScannerWrapper::SetRPM(const Real f_rpm) {
    if (m_pcScannerActuator == nullptr) {
        ActusensorsWrapper::Logprint(
            "Distance Scanner Actuator not implemented or not stated in XML config.");
        return;
    }
    if (f_rpm < 0)
        m_pcScannerActuator->SetRPM(0);
    m_pcScannerActuator->SetRPM(f_rpm);
}

void CDistanceScannerWrapper::SetAngle(const Real f_angle) {
    if (m_pcScannerActuator == nullptr) {
        ActusensorsWrapper::Logprint(
            "Distance Scanner Actuator not implemented or not stated in XML config.");
        return;
    }
    m_pcScannerActuator->SetAngle(CRadians(f_angle));
}

std::map<CRadians, Real> CDistanceScannerWrapper::GetReadings() const {
    if (m_pcScannerSensor == nullptr) {
        ActusensorsWrapper::Logprint(
            "Distance Scanner Sensor not implemented or not stated in XML config.");
        return {};
    }
    return m_pcScannerSensor->GetReadingsMap();
}

std::map<CRadians, Real> CDistanceScannerWrapper::GetShortReadings() const {
    if (m_pcScannerSensor == nullptr) {
        ActusensorsWrapper::Logprint(
            "Distance Scanner Sensor not implemented or not stated in XML config.");
        return {};
    }
    return m_pcScannerSensor->GetShortReadingsMap();
}

std::map<CRadians, Real> CDistanceScannerWrapper::GetLongReadings() const {
    if (m_pcScannerSensor == nullptr) {
        ActusensorsWrapper::Logprint(
            "Distance Scanner Sensor not implemented or not stated in XML config.");
        return {};
    }
    return m_pcScannerSensor->GetLongReadingsMap();
}

/****************************************/
/****************************************/

CTurretWrapper::CTurretWrapper() {}

CRadians CTurretWrapper::GetRotation() const {
    if (m_pcTurretSensor == nullptr) {
        ActusensorsWrapper::Logprint("Turret Sensor not implemented or not stated in XML config.");
        return {};
    }
    return m_pcTurretSensor->GetRotation();
}

void CTurretWrapper::SetRotation(const Real f_angle) {
    if (m_pcTurretActuator == nullptr) {
        ActusensorsWrapper::Logprint(
            "Turret Actuator not implemented or not stated in XML config.");
        return;
    }
    m_pcTurretActuator->SetRotation(argos::CRadians(f_angle));
}

void CTurretWrapper::SetRotationSpeed(const UInt32 n_speed_pulses) {
    if (m_pcTurretActuator == nullptr) {
        ActusensorsWrapper::Logprint(
            "Turret Actuator not implemented or not stated in XML config.");
        return;
    }
    m_pcTurretActuator->SetRotationSpeed(n_speed_pulses);
}

void CTurretWrapper::SetMode(const std::string str_mode_name) {
    if (m_pcTurretActuator == nullptr) {
        ActusensorsWrapper::Logprint(
            "Turret Actuator not implemented or not stated in XML config.");
        return;
    }
    if (str_mode_name == "off") {
        m_pcTurretActuator->SetMode(argos::CCI_FootBotTurretActuator::ETurretModes::MODE_OFF);
    } else if (str_mode_name == "passive") {
        m_pcTurretActuator->SetMode(argos::CCI_FootBotTurretActuator::ETurretModes::MODE_PASSIVE);
    } else if (str_mode_name == "speed_control") {
        m_pcTurretActuator->SetMode(
            argos::CCI_FootBotTurretActuator::ETurretModes::MODE_SPEED_CONTROL);
    } else if (str_mode_name == "position_control") {
        m_pcTurretActuator->SetMode(
            argos::CCI_FootBotTurretActuator::ETurretModes::MODE_POSITION_CONTROL);
    } else {
        ActusensorsWrapper::Logprint("Turret Actuator mode not recognized.");
        return;
    }
}

void CTurretWrapper::SetActiveWithRotation(const Real f_angle) {
    if (m_pcTurretActuator == nullptr) {
        ActusensorsWrapper::Logprint(
            "Turret Actuator not implemented or not stated in XML config.");
        return;
    }
    m_pcTurretActuator->SetActiveWithRotation(argos::CRadians(f_angle));
}

void CTurretWrapper::SetSpeedControlMode() {
    if (m_pcTurretActuator == nullptr) {
        ActusensorsWrapper::Logprint(
            "Turret Actuator not implemented or not stated in XML config.");
        return;
    }
    m_pcTurretActuator->SetSpeedControlMode();
}

void CTurretWrapper::SetPositionControlMode() {
    if (m_pcTurretActuator == nullptr) {
        ActusensorsWrapper::Logprint(
            "Turret Actuator not implemented or not stated in XML config.");
        return;
    }
    m_pcTurretActuator->SetPositionControlMode();
}

void CTurretWrapper::SetPassiveMode() {
    if (m_pcTurretActuator == nullptr) {
        ActusensorsWrapper::Logprint(
            "Turret Actuator not implemented or not stated in XML config.");
        return;
    }
    m_pcTurretActuator->SetPassiveMode();
}
