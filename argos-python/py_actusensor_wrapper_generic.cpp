#include "py_actusensor_wrapper_generic.h"
#include "py_wrapper.h"

using namespace argos;


/****************************************/
/****************************************/

CWheelsWrapper::CWheelsWrapper() {}

void CWheelsWrapper::SetSpeed(const Real f_left_wheel_speed, const Real f_right_wheel_speed) {
    if (m_pcWheels == nullptr) {
        ActusensorsWrapper::Logprint(
            "Differential Steering Actuator not implemented or not stated in XML config.");
        return;
    }
    m_pcWheels->SetLinearVelocity(f_left_wheel_speed, f_right_wheel_speed);
}

/****************************************/
/****************************************/

CDifferentialSteeringSensorWrapper::CDifferentialSteeringSensorWrapper() {}

boost::python::list CDifferentialSteeringSensorWrapper::GetReading() const {
    if (m_pcDifferentialSteeringSensor == nullptr) {
        ActusensorsWrapper::Logprint(
            "Differential Steering Sensor not implemented or not stated in XML config.");
        return {};
    }
    // Probably there is an better way to convert SReadings to boost::python::list
    boost::python::list readings;
    readings.append((Real) m_pcDifferentialSteeringSensor->GetReading().CoveredDistanceLeftWheel);
    readings.append((Real) m_pcDifferentialSteeringSensor->GetReading().CoveredDistanceRightWheel);
    readings.append((Real) m_pcDifferentialSteeringSensor->GetReading().VelocityLeftWheel);
    readings.append((Real) m_pcDifferentialSteeringSensor->GetReading().VelocityRightWheel);
    readings.append((Real) m_pcDifferentialSteeringSensor->GetReading().WheelAxisLength);

    return readings;

}

boost::python::list CDifferentialSteeringSensorWrapper::GetDistances() const {
    if (m_pcDifferentialSteeringSensor == nullptr) {
        ActusensorsWrapper::Logprint(
            "Differential Steering Sensor not implemented or not stated in XML config.");
        return {};
    }
    // Probably there is an better way to convert SReadings to boost::python::list
    boost::python::list readings;
    readings.append((Real) m_pcDifferentialSteeringSensor->GetReading().CoveredDistanceLeftWheel);
    readings.append((Real) m_pcDifferentialSteeringSensor->GetReading().CoveredDistanceRightWheel);

    return readings;
}

/****************************************/
/****************************************/

CPositioningSensorWrapper::CPositioningSensorWrapper() {}

boost::python::list CPositioningSensorWrapper::GetPosition() const {
    if (m_pcPositioning == nullptr) {
        ActusensorsWrapper::Logprint("Positioning Sensor not implemented or not stated in XML config.");
        return {};
    }

    // Probably there is an better way to convert CVector3 to boost::python::list
    boost::python::list position;
    position.append((float) m_pcPositioning->GetReading().Position[0]);
    position.append((float) m_pcPositioning->GetReading().Position[1]);
    position.append((float) m_pcPositioning->GetReading().Position[2]);

    return position;
}

Real CPositioningSensorWrapper::GetOrientation() const {
    if (m_pcPositioning == nullptr) {
        ActusensorsWrapper::Logprint("Positioning Sensor not implemented or not stated in XML config.");
        return {};
    }

    // Currently only returns rotation along Z and ignores other axis
    CRadians cZAngle, cYAngle, cXAngle; 
    m_pcPositioning->GetReading().Orientation.ToEulerAngles(cZAngle, cYAngle, cXAngle);

    return cZAngle.GetValue();
}

/****************************************/
/****************************************/
COmnidirectionalCameraWrapper::COmnidirectionalCameraWrapper()
    : m_maxAngle(3.14) {}

void COmnidirectionalCameraWrapper::setFOV(double max_angle) {
    m_maxAngle = max_angle;
}

boost::python::list COmnidirectionalCameraWrapper::GetReadings() const {
    if (m_pcOmniCam == nullptr) {
        ActusensorsWrapper::Logprint(
            "Omnidirectional Camera Sensor not implemented or not stated in XML config.");
        return {};
    }

    boost::python::list readings;

    for (size_t i = 0; i < m_pcOmniCam->GetReadings().BlobList.size(); ++i) {
        double angle = m_pcOmniCam->GetReadings().BlobList[i]->Angle.GetValue();
        if (angle < m_maxAngle && angle > -m_maxAngle) {
            boost::python::list color;
            boost::python::list reading;

            color.append(m_pcOmniCam->GetReadings().BlobList[i]->Color.GetRed());
            color.append(m_pcOmniCam->GetReadings().BlobList[i]->Color.GetGreen());
            color.append(m_pcOmniCam->GetReadings().BlobList[i]->Color.GetBlue());

            reading.append(color);
            reading.append(angle);
            reading.append(m_pcOmniCam->GetReadings().BlobList[i]->Distance);

            readings.append(reading);
        }
    }

    return readings;
}

// Enable the camera.
void COmnidirectionalCameraWrapper::Enable() {
    if (m_pcOmniCam == nullptr) {
        ActusensorsWrapper::Logprint(
            "Omnidirectional Camera Sensor not implemented or not stated in XML config.");
        return;
    }
    m_pcOmniCam->Enable();
}
// Disable the camera.
void COmnidirectionalCameraWrapper::Disable() {
    if (m_pcOmniCam == nullptr) {
        ActusensorsWrapper::Logprint(
            "Omnidirectional Camera Sensor not implemented or not stated in XML config.");
        return;
    }
    m_pcOmniCam->Disable();
}
// Return the number of readings obtained so far, i.e. the number of control steps from which the
// recording started.
const int COmnidirectionalCameraWrapper::GetCounter() const {
    if (m_pcOmniCam == nullptr) {
        ActusensorsWrapper::Logprint(
            "Omnidirectional Camera Sensor not implemented or not stated in XML config.");
        return {};
    }
    return m_pcOmniCam->GetReadings().Counter;
}

/****************************************/
/****************************************/

CPerspectiveCameraWrapper::CPerspectiveCameraWrapper() {}

boost::python::list CPerspectiveCameraWrapper::GetReadings() const {
    if (m_pcPerspCam == nullptr) {
        ActusensorsWrapper::Logprint(
            "Perspective Camera Sensor not implemented or not stated in XML config.");
        return {};
    }

    // boost::python::list readings;
    // for (size_t i = 0; i < m_pcPerspCam->GetReadings().BlobList.size(); ++i) {
    //     boost::python::list color;
    //     boost::python::list reading;

    //     color.append(m_pcPerspCam->GetReadings().BlobList[i]->Color.GetRed());
    //     color.append(m_pcPerspCam->GetReadings().BlobList[i]->Color.GetGreen());
    //     color.append(m_pcPerspCam->GetReadings().BlobList[i]->Color.GetBlue());

    //     reading.append(color);
    //     reading.append(m_pcPerspCam->GetReadings().BlobList[i]->Angle.GetValue());
    //     reading.append(m_pcPerspCam->GetReadings().BlobList[i]->Distance);

    //     readings.append(reading);
    // }
    // return readings;

    // In the way below I was unable to read color on python. angle.value() and distance are ok
    return ActusensorsWrapper::ToPythonList(m_pcPerspCam->GetReadings().BlobList);
}
// Enable the camera.
void CPerspectiveCameraWrapper::Enable() {
    if (m_pcPerspCam == nullptr) {
        ActusensorsWrapper::Logprint(
            "Perspective Camera Sensor not implemented or not stated in XML config.");
        return;
    }
    m_pcPerspCam->Enable();
}
// Disable the camera.
void CPerspectiveCameraWrapper::Disable() {
    if (m_pcPerspCam == nullptr) {
        ActusensorsWrapper::Logprint(
            "Perspective Camera Sensor not implemented or not stated in XML config.");
        return;
    }
    m_pcPerspCam->Disable();
}


/****************************************/
/****************************************/

CRangeAndBearingWrapper::CRangeAndBearingWrapper() {}

void CRangeAndBearingWrapper::ClearData() {
    if (m_pcRABA == nullptr) {
        ActusensorsWrapper::Logprint("RABA not implemented or not stated in XML config.");
        return;
    }
    m_pcRABA->ClearData();
}
// Set the i-th bit of the data table.
void CRangeAndBearingWrapper::SetData(const size_t un_idx, const UInt8 un_value) {
    if (m_pcRABA == nullptr) {
        ActusensorsWrapper::Logprint("RABA not implemented or not stated in XML config.");
        return;
    }
    m_pcRABA->SetData(un_idx, un_value);
}
// TODO: Set all bits at once
// Return the readings obtained at this control step.
// Each reading contains the range, the horizontal bearing, the vertical bearing and the data table.
// The data table is exposed as a c_byte_array.
boost::python::list CRangeAndBearingWrapper::GetReadings() const {
    if (m_pcRABS == nullptr) {
        ActusensorsWrapper::Logprint("RABA not implemented or not stated in XML config.");
        return {};
    }
    return ActusensorsWrapper::ToPythonList(m_pcRABS->GetReadings());
}

/****************************************/
/****************************************/

CLedsActuatorWrapper::CLedsActuatorWrapper() {}

// Set the color of a given led, given its name.
void CLedsActuatorWrapper::SetSingleColorString(const UInt8 un_led_id,
                                                const std::string str_color_name) {
    if (m_pcLeds == nullptr) {
        ActusensorsWrapper::Logprint("Leds not implemented or not stated in XML config.");
        return;
    }
    m_pcLeds->SetSingleColor(un_led_id, ActusensorsWrapper::CColorWrapper(str_color_name).m_cColor);
}
// Set the color of a given led, given its RGB values.
void CLedsActuatorWrapper::SetSingleColorRGB(const UInt8 un_led_id, const UInt8 un_red,
                                             const UInt8 un_green, const UInt8 un_blue) {
    if (m_pcLeds == nullptr) {
        ActusensorsWrapper::Logprint("Leds not implemented or not stated in XML config.");
        return;
    }
    m_pcLeds->SetSingleColor(un_led_id,
                             ActusensorsWrapper::CColorWrapper(un_red, un_green, un_blue).m_cColor);
}
// Set the color of every led, given its name.
void CLedsActuatorWrapper::SetAllColorsString(const std::string str_color_name) {
    if (m_pcLeds == nullptr) {
        ActusensorsWrapper::Logprint("Leds not implemented or not stated in XML config.");
        return;
    }
    m_pcLeds->SetAllColors(ActusensorsWrapper::CColorWrapper(str_color_name).m_cColor);
}
// Set the color of every led, given its RGB values.
void CLedsActuatorWrapper::SetAllColorsRGB(const UInt8 un_red, const UInt8 un_green,
                                           const UInt8 un_blue) {
    if (m_pcLeds == nullptr) {
        ActusensorsWrapper::Logprint("Leds not implemented or not stated in XML config.");
        return;
    }
    m_pcLeds->SetAllColors(ActusensorsWrapper::CColorWrapper(un_red, un_green, un_blue).m_cColor);
}
