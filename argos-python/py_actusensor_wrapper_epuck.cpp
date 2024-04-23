#include "py_actusensor_wrapper_epuck.h"
#include "py_wrapper.h"

using namespace argos;

/****************************************/
/****************************************/

CVariableWrapper::CVariableWrapper() {}

const std::string CVariableWrapper::GetId() {
  return m_cId;
}

void CVariableWrapper::SetId(const std::string id) {
  m_cId = id;
}

void CVariableWrapper::SetAttribute(const std::string& key, const std::string& value) {
  m_cAttributes[key] = value;
}

const std::string CVariableWrapper::GetAttribute(const std::string& key) {
  return m_cAttributes[key];
}

const std::string CVariableWrapper::GetAllAttributes() {
  std::map<std::string, std::string>::iterator it = m_cAttributes.begin();
  std::string json = "{";

    for (std::pair<std::string, std::string> attr : m_cAttributes) 
    {
        std::string key = attr.first;
        std::string value = attr.second;
        json.append("\"" + key + "\"" + ": " + "\"" + value+ "\"" + ", ");
    }
    if (!json.empty())
        json.pop_back();
        json.pop_back();
    json.append("}");
    return json;
}

// void CVariableWrapper::SetAttribute(const std::string& key, const bool& value) {
//   m_cAttributes[key] = value;
// }
// const boost::variant<std::string, bool> CVariableWrapper::GetAttribute(const std::string& key) {
//   return m_cAttributes[key];
// }


// // Ideally this function gets a atributes dictionary
// void CVariableWrapper::SetAttribute(const boost::python::dict key) {
// }


/****************************************/
/****************************************/

// CLoopFunctionsWrapper::CLoopFunctionsWrapper() {}

// // Add bool fill, color, number of vertices inputs
// void CLoopFunctionsWrapper::DrawCircle(const boost::python::list c_position_list, const boost::python::list c_orientation_list, const Real f_radius) {

// //     extract python list for position

// //     // Create Cvector3 with position
// //     // c_position = convert c_position_list
// //     // Create Cvector3 with orientation
// //     // c_orientation = convert c_orientation_list
// //     // Do arrow thingy
    

//     std::cout << "test:" << CVector3(boost::python::extract<UInt8>(boost::python::object(c_position_list[0])), boost::python::extract<UInt8>(boost::python::object(c_position_list[1])), boost::python::extract<UInt8>(boost::python::object(c_position_list[2]))) << std::endl;
//     std::cout << "test2:" << f_radius << std::endl;
//     m_pcCLoopFunctions->DrawCylinder(CVector3(0.0f, 0.0f, 0.3f), CQuaternion(), 0.1f,  0.05f, CColor::BLACK);
// //     m_pcCLoopFunctions->DrawInWorld() {
// //         DrawCircle(CVector3(0.5, 0.5, 0.5), CQuaternion(), 0.5);
// //         // std::cout << "test2:" << f_radius << std::endl;

// // };
// }

/****************************************/
/****************************************/



/****************************************/
/****************************************/

CEPuckWheelsWrapper::CEPuckWheelsWrapper() {}

void CEPuckWheelsWrapper::SetSpeed(const Real f_left_wheel_speed, const Real f_right_wheel_speed) {
    if (m_pcEPuckWheels == nullptr) {
        ActusensorsWrapper::Logprint(
            "E-puck Wheels not implemented or not stated in XML config.");
        return;
    }
    m_pcEPuckWheels->SetLinearVelocity(f_left_wheel_speed, f_right_wheel_speed);
    
}

/****************************************/
/****************************************/

CEPuckProximitySensorWrapper::CEPuckProximitySensorWrapper() {}

boost::python::list CEPuckProximitySensorWrapper::GetReadings() const {
    if (m_pcEPuckProximity == nullptr) {
        ActusensorsWrapper::Logprint(
            "Proximity sensor not implemented or not stated in XML config.");
        // TODO: add exception?
        return {};
    }
    return ActusensorsWrapper::ToPythonList(m_pcEPuckProximity->GetReadings());
}

/****************************************/
/****************************************/

CEPuckGroundSensorWrapper::CEPuckGroundSensorWrapper() {}

argos::CCI_EPuckGroundSensor::SReadings CEPuckGroundSensorWrapper::GetReadings() const {
    if (m_pcEPuckGround == nullptr) {
        ActusensorsWrapper::Logprint(
            "Motor Ground Sensor not implemented or not stated in XML config.");
        // TODO: add exception?
        return {};
    }
    return m_pcEPuckGround->GetReadings();
}

/****************************************/
/****************************************/

CEPuckRangeAndBearingWrapper::CEPuckRangeAndBearingWrapper() {}

void CEPuckRangeAndBearingWrapper::ClearPackets() {
    if (m_pcEPuckRABS == nullptr) {
        ActusensorsWrapper::Logprint("RABS not implemented or not stated in XML config.");
        return;
    }
    m_pcEPuckRABS->ClearPackets();
}
// Send a buffer to all the emitters.
void CEPuckRangeAndBearingWrapper::SetData(const boost::python::list un_data) {
    if (m_pcEPuckRABA == nullptr) {
        ActusensorsWrapper::Logprint("RABA not implemented or not stated in XML config.");
        return;
    }
    /* std::cout << "rab da:" << un_data << std::endl; */
    const UInt8 unData[argos::CCI_EPuckRangeAndBearingActuator::MAX_BYTES_SENT] =
         {boost::python::extract<UInt8>(boost::python::object(un_data[0])),
          boost::python::extract<UInt8>(boost::python::object(un_data[1])),
          boost::python::extract<UInt8>(boost::python::object(un_data[2])),
          boost::python::extract<UInt8>(boost::python::object(un_data[3]))};
    //const UInt8 unData[3] = {0, 0, 0};
    // std::cout << m_pcEPuckRABA << "raba" << std::endl;
    m_pcEPuckRABA->SetData(unData);
}
// TODO: Set all bits at once
// Return the readings obtained at this control step.
// Each reading contains the range, the horizontal bearing, the vertical bearing and the data table.
// The data table is exposed as a c_byte_array.


boost::python::list CEPuckRangeAndBearingWrapper::GetPackets() const {
    if (m_pcEPuckRABS == nullptr) {
        ActusensorsWrapper::Logprint("RABS not implemented or not stated in XML config.");
        return {};
    }

    boost::python::list packets_list;

    for (size_t i = 0; i < m_pcEPuckRABS->GetPackets().size(); ++i) {

        packets_list.append(m_pcEPuckRABS->GetPackets()[i]);

    }

    return packets_list;
}



boost::python::list CEPuckRangeAndBearingWrapper::GetReadings() const {
    if (m_pcEPuckRABS == nullptr) {
        ActusensorsWrapper::Logprint("RABS not implemented or not stated in XML config.");
        return {};
    }

    boost::python::list readings_list;
    

    for (size_t i = 0; i < m_pcEPuckRABS->GetPackets().size(); ++i) {
        boost::python::list data_list;    
        boost::python::list reading_list;

        for (size_t j = 0; j < sizeof(m_pcEPuckRABS->GetPackets()[i]->Data)/sizeof(*m_pcEPuckRABS->GetPackets()[i]->Data); ++j) {
            data_list.append((int) m_pcEPuckRABS->GetPackets()[i]->Data[j]);
        }

        reading_list.append(data_list);
        reading_list.append(m_pcEPuckRABS->GetPackets()[i]->Range/100);
        reading_list.append(m_pcEPuckRABS->GetPackets()[i]->Bearing.GetValue());
        //readings_list.append(m_pcEPuckRABS->GetPackets()[i]->VerticalBearing);

        readings_list.append(reading_list);
    }

    return readings_list;
}

boost::python::list CEPuckRangeAndBearingWrapper::GetData() const {
    if (m_pcEPuckRABS == nullptr) {
        ActusensorsWrapper::Logprint("RABS not implemented or not stated in XML config.");
        return {};
    }

    boost::python::list readings_list;

        for (size_t i = 0; i < m_pcEPuckRABS->GetPackets().size(); ++i) {
        boost::python::list data_list;    

            for (size_t j = 0; j < sizeof(m_pcEPuckRABS->GetPackets()[i]->Data)/sizeof(*m_pcEPuckRABS->GetPackets()[i]->Data); ++j) {
                data_list.append((int) m_pcEPuckRABS->GetPackets()[i]->Data[j]);
            }

            readings_list.append(data_list);

    }
        return readings_list;
}


/****************************************/
/****************************************/

CEPuckLedsActuatorWrapper::CEPuckLedsActuatorWrapper() {}

// Set the color of a given led, given its name.
void CEPuckLedsActuatorWrapper::SetSingleColorString(const UInt8 un_led_id,
                                                     const std::string str_color_name) {
    if (m_pcEPuckLeds == nullptr) {
        ActusensorsWrapper::Logprint("Leds not implemented or not stated in XML config.");
        return;
    }
    m_pcEPuckLeds->SetColor(un_led_id, ActusensorsWrapper::CColorWrapper(str_color_name).m_cColor);
}
// Set the color of a given led, given its RGB values.
void CEPuckLedsActuatorWrapper::SetSingleColorRGB(const UInt8 un_led_id, const UInt8 un_red,
                                                  const UInt8 un_green, const UInt8 un_blue) {
    if (m_pcEPuckLeds == nullptr) {
        ActusensorsWrapper::Logprint("Leds not implemented or not stated in XML config.");
        return;
    }
    m_pcEPuckLeds->SetColor(un_led_id,
                            ActusensorsWrapper::CColorWrapper(un_red, un_green, un_blue).m_cColor);
}
// Set the color of every led, given its name.
void CEPuckLedsActuatorWrapper::SetAllColorsString(const std::string str_color_name) {
    if (m_pcEPuckLeds == nullptr) {
        ActusensorsWrapper::Logprint("Leds not implemented or not stated in XML config.");
        return;
    }
    m_pcEPuckLeds->SetColors(ActusensorsWrapper::CColorWrapper(str_color_name).m_cColor);
}
// Set the color of every led, given its RGB values.
void CEPuckLedsActuatorWrapper::SetAllColorsRGB(const UInt8 un_red, const UInt8 un_green,
                                                const UInt8 un_blue) {
    if (m_pcEPuckLeds == nullptr) {
        ActusensorsWrapper::Logprint("Leds not implemented or not stated in XML config.");
        return;
    }
    m_pcEPuckLeds->SetColors(ActusensorsWrapper::CColorWrapper(un_red, un_green, un_blue).m_cColor);
}
