#include "py_environment_wrapper.h"
#include "py_wrapper.h"
#include <string>

using namespace argos;

/****************************************/
/****************************************/

CQTOpenGLUserFunctionsWrapper::CQTOpenGLUserFunctionsWrapper() {}

void CQTOpenGLUserFunctionsWrapper::SetDrawList(const std::string& key, const std::string& value) {
  m_cAttributes[key] = value;
}

const std::string CQTOpenGLUserFunctionsWrapper::GetDrawList(const std::string& key) {
  return m_cAttributes[key];
}

// Add bool fill, color, number of vertices inputs
// const boost::python::list c_position_list, const boost::python::list c_orientation_list, const Real f_radius
void CQTOpenGLUserFunctionsWrapper::DrawCircle(const boost::python::list c_position_list, 
                                               const boost::python::list c_orientation_list, 
                                               const Real f_radius, 
                                               const boost::python::object color_str_list,
                                               const bool  b_fill) {

    CVector3 c_position;

    c_position = CVector3(boost::python::extract<Real>(boost::python::object(c_position_list[0])), 
                          boost::python::extract<Real>(boost::python::object(c_position_list[1])), 
                          boost::python::extract<Real>(boost::python::object(c_position_list[2])));

    if (boost::python::extract<std::string>(color_str_list).check()) {
        // Handle string color name
        std::string color_str = boost::python::extract<std::string>(color_str_list);

        m_pcCQTOpenGLUserFunctions->DrawCircle(
                    c_position,
                    CQuaternion(), // Implement orientation
                    f_radius, 
                    ActusensorsWrapper::CColorWrapper(color_str).m_cColor,
                    b_fill);

    } else if (boost::python::extract<boost::python::list>(color_str_list).check()) {
        // Handle RGB array
        boost::python::list rgb_list = boost::python::extract<boost::python::list>(color_str_list);
        Real r = boost::python::extract<Real>(rgb_list[0]);
        Real g = boost::python::extract<Real>(rgb_list[1]);
        Real b = boost::python::extract<Real>(rgb_list[2]);

           m_pcCQTOpenGLUserFunctions->DrawCircle(
                c_position,
                CQuaternion(), // Implement orientation
                f_radius, 
                ActusensorsWrapper::CColorWrapper(r,g,b).m_cColor,
                b_fill);
                                            
    } else {
        // Invalid argument type for color
        // Handle the error accordingly
    }



}

void CQTOpenGLUserFunctionsWrapper::DrawPolygon(const boost::python::list c_position_list, 
                                                const boost::python::list c_orientation_list, 
                                                const boost::python::list vec_points_list, 
                                                const std::string str_color_name,
                                                const bool  b_fill) {
  
    std::vector<CVector2> vec_point_vector;
    boost::python::list vec_point;

    for (size_t i = 0; i < boost::python::len(vec_points_list); ++i) {

            vec_point = boost::python::extract<boost::python::list>(boost::python::object(vec_points_list[i]));

            vec_point_vector.push_back(CVector2(boost::python::extract<Real>(boost::python::object(vec_point[0])),
                                                boost::python::extract<Real>(boost::python::object(vec_point[1]))));
        }

    m_pcCQTOpenGLUserFunctions->DrawPolygon(
        CVector3(boost::python::extract<Real>(boost::python::object(c_position_list[0])), 
                 boost::python::extract<Real>(boost::python::object(c_position_list[1])), 
                 boost::python::extract<Real>(boost::python::object(c_position_list[2]))),
        CQuaternion(), // Implement orientation
        vec_point_vector, 
        ActusensorsWrapper::CColorWrapper(str_color_name).m_cColor,
        b_fill);
}

// void CQTOpenGLUserFunctionsWrapper::DrawRay(const boost::python::list c_start,
//                                             const boost::python::list c_end,
//                                             const std::string str_color_name,
//                                             const Real f_width) {
//     CVector3 c_stt_vec;
//     CVector3 c_end_vec;

//     c_stt_vec = CVector3(boost::python::extract<Real>(boost::python::object(c_start[0])), 
//                          boost::python::extract<Real>(boost::python::object(c_start[1])), 
//                          boost::python::extract<Real>(boost::python::object(c_start[2])));

//     c_end_vec = CVector3(boost::python::extract<Real>(boost::python::object(c_end[0])), 
//                          boost::python::extract<Real>(boost::python::object(c_end[1])), 
//                          boost::python::extract<Real>(boost::python::object(c_end[2])));

//     m_pcCQTOpenGLUserFunctions->DrawRay(CRay3(c_stt_vec, c_end_vec), 
//                                         ActusensorsWrapper::CColorWrapper(str_color_name).m_cColor,
//                                         f_width);
// }

void CQTOpenGLUserFunctionsWrapper::DrawRay(const boost::python::list c_start,
                                            const boost::python::list c_end,
                                            const boost::python::object str_color_name,
                                            const Real f_width) {
    CVector3 c_stt_vec;
    CVector3 c_end_vec;

    c_stt_vec = CVector3(boost::python::extract<Real>(boost::python::object(c_start[0])), 
                         boost::python::extract<Real>(boost::python::object(c_start[1])), 
                         boost::python::extract<Real>(boost::python::object(c_start[2])));

    c_end_vec = CVector3(boost::python::extract<Real>(boost::python::object(c_end[0])), 
                         boost::python::extract<Real>(boost::python::object(c_end[1])), 
                         boost::python::extract<Real>(boost::python::object(c_end[2])));

    if (boost::python::extract<std::string>(str_color_name).check()) {
        // Handle string color name
        std::string color_name = boost::python::extract<std::string>(str_color_name);
        m_pcCQTOpenGLUserFunctions->DrawRay(CRay3(c_stt_vec, c_end_vec),
                                            ActusensorsWrapper::CColorWrapper(color_name).m_cColor,
                                            f_width);
    } else if (boost::python::extract<boost::python::list>(str_color_name).check()) {
        // Handle RGB array
        boost::python::list rgb_list = boost::python::extract<boost::python::list>(str_color_name);
        Real r = boost::python::extract<Real>(rgb_list[0]);
        Real g = boost::python::extract<Real>(rgb_list[1]);
        Real b = boost::python::extract<Real>(rgb_list[2]);
        m_pcCQTOpenGLUserFunctions->DrawRay(CRay3(c_stt_vec, c_end_vec),
                                            ActusensorsWrapper::CColorWrapper(r,g,b).m_cColor,
                                            f_width);
    } else {
        // Invalid argument type for color
        // Handle the error accordingly
    }
}

void CQTOpenGLUserFunctionsWrapper::DrawBox(const boost::python::list c_position_list, 
                                            const boost::python::list c_orientation_list, 
                                            const boost::python::list c_size_list, 
                                            const boost::python::object color_str_list) {

    CVector3 c_pos_vec;
    CVector3 c_siz_vec;

    c_pos_vec = CVector3(boost::python::extract<Real>(boost::python::object(c_position_list[0])), 
                         boost::python::extract<Real>(boost::python::object(c_position_list[1])), 
                         boost::python::extract<Real>(boost::python::object(c_position_list[2])));

    c_siz_vec = CVector3(boost::python::extract<Real>(boost::python::object(c_size_list[0])), 
                         boost::python::extract<Real>(boost::python::object(c_size_list[1])), 
                         boost::python::extract<Real>(boost::python::object(c_size_list[2])));

    if (boost::python::extract<std::string>(color_str_list).check()) {
        // Handle string color name
        std::string color_str = boost::python::extract<std::string>(color_str_list);

         m_pcCQTOpenGLUserFunctions->DrawBox(c_pos_vec,
                                             CQuaternion(), // To-do: Implement orientation
                                             c_siz_vec, 
                                             ActusensorsWrapper::CColorWrapper(color_str).m_cColor);

    } else if (boost::python::extract<boost::python::list>(color_str_list).check()) {
        // Handle RGB array
        boost::python::list rgb_list = boost::python::extract<boost::python::list>(color_str_list);
        Real r = boost::python::extract<Real>(rgb_list[0]);
        Real g = boost::python::extract<Real>(rgb_list[1]);
        Real b = boost::python::extract<Real>(rgb_list[2]);

         m_pcCQTOpenGLUserFunctions->DrawBox(c_pos_vec,
                                             CQuaternion(), // To-do: Implement orientation
                                             c_siz_vec, 
                                             ActusensorsWrapper::CColorWrapper(r,g,b).m_cColor);
    } else {
        // Invalid argument type for color
        // Handle the error accordingly
    }

    // m_pcCQTOpenGLUserFunctions->DrawBox(
    //     c_pos_vec,
    //     CQuaternion(), // To-do: Implement orientation
    //     c_siz_vec, 
    //     ActusensorsWrapper::CColorWrapper(color_str_list).m_cColor);
}

void CQTOpenGLUserFunctionsWrapper::DrawCylinder(const boost::python::list c_position_list, 
                                                 const boost::python::list c_orientation_list, 
                                                 const Real f_radius, 
                                                 const Real f_height,
                                                 const std::string str_color_name) {
    m_pcCQTOpenGLUserFunctions->DrawCylinder(
        CVector3(boost::python::extract<Real>(boost::python::object(c_position_list[0])), 
                 boost::python::extract<Real>(boost::python::object(c_position_list[1])), 
                 boost::python::extract<Real>(boost::python::object(c_position_list[2]))),
        CQuaternion(), // Implement orientation
        f_radius,
        f_height, 
        ActusensorsWrapper::CColorWrapper(str_color_name).m_cColor);
}


// NOT WORKING DrawText; CORE DUMP
void CQTOpenGLUserFunctionsWrapper::DrawText(const boost::python::list c_position,
                                             const std::string str_text,
                                             const std::string str_color_name) {


    m_pcCQTOpenGLUserFunctions->DrawText(
        CVector3(boost::python::extract<Real>(boost::python::object(c_position[0])), 
                 boost::python::extract<Real>(boost::python::object(c_position[1])), 
                 boost::python::extract<Real>(boost::python::object(c_position[2]))),   
        str_text,   
        ActusensorsWrapper::CColorWrapper(str_color_name).m_cColor); 
}

// NOT WORKING CloseWindow; CORE DUMP
void CQTOpenGLUserFunctionsWrapper::CloseWindow() {
  m_pcCQTOpenGLUserFunctions->GetMainWindow().close();

}
