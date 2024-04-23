/*
 * AUTHOR: Ken Hasselmann <arg AT kenh DOT fr>
 *
 * Connects ARGoS to python
 *
 */
#include "py_controller.h"

using namespace argos;
using namespace boost::python;

#define INIT_MODULE_CONTROLLER PyInit_libpy_controller_interface
extern "C" PyObject* INIT_MODULE_CONTROLLER();

CPyController::CPyController() {
    // init python
    PyImport_AppendInittab("libpy_controller_interface", INIT_MODULE_CONTROLLER);
    
    Py_Initialize();

    m_interpreter = Py_NewInterpreter();
    // init main module and namespace
    m_main = import("__main__");
    m_namesp = m_main.attr("__dict__");
}

void CPyController::Destroy() {
    // launch python destroy function
    try {
        object destroy = m_main.attr("destroy");
        destroy();
    } catch (error_already_set) {
        PyErr_Print();
    }
    // Py_EndInterpreter(m_interpreter);
    // Py_Finalize(); //the documentation of boost says we should NOT use this ..
}

void CPyController::Reset() {
    // launch python reset function
    try {
        object reset_f = m_main.attr("reset");
        reset_f();
    } catch (error_already_set) {
        PyErr_Print();
    }
}

void CPyController::InitSensorsActuators(TConfigurationNode& t_node) {
    for (CCI_Actuator::TMap::iterator it = m_mapActuators.begin(); it != m_mapActuators.end();
     ++it) {
        m_actusensors->CreateActu(it->first, it->second, t_node); // this);
}

for (CCI_Sensor::TMap::iterator it = m_mapSensors.begin(); it != m_mapSensors.end(); ++it) {
    m_actusensors->CreateSensor(it->first, it->second, t_node);
}

m_actusensors->SetId(GetId());

}

void CPyController::Init(TConfigurationNode& t_node) {

    robotId = stoi(GetId().substr(2));
    timeStep = 0;

    // get instances of actuators and sensors and pass them to the wrapper
    m_actusensors = boost::make_shared<ActusensorsWrapper>();

    InitSensorsActuators(t_node);
    // printf("%s\n", this);

    /* Load script */
    std::string strScriptFileName;
    GetNodeAttributeOrDefault(t_node, "script", strScriptFileName, strScriptFileName);
    GetNodeAttributeOrDefault(t_node, "timeRate", timeRate, timeRate);
    if (strScriptFileName == "") {
        THROW_ARGOSEXCEPTION("Error loading python script \"" << strScriptFileName << "\""
          << std::endl);
    }
    // exec user script
    try {
        m_script = exec_file(strScriptFileName.c_str(), m_namesp, m_namesp);

        std::cout << "Controller strScript:" << strScriptFileName << std::endl;
        std::cout << GetId().c_str() << std::endl;
    } catch (error_already_set) {
      std::cout << "ERROR: Could not execute user script" << std::endl;
      PyErr_Print();
  }

  try {
        // import the wrappers's lib
    PyRun_SimpleString("import libpy_controller_interface as lib");
    object lib = import("libpy_controller_interface");
    m_namesp["robot"] = m_actusensors;

        // launch python init function
    object init_f = m_main.attr("init");
    init_f();

} catch (error_already_set) {
    PyErr_Print();
}
}

void CPyController::ControlStep() {

    timeStep++;

    // launch controlstep python function*

    if ((robotId + timeStep) % timeRate == 0) {

        try {

        object controlstep = m_main.attr("controlstep");
        controlstep();

        } catch (error_already_set) {
            PyErr_Print();
        }
    }
}


boost::shared_ptr<ActusensorsWrapper>  CPyController::getActusensors() {
    return m_actusensors;
}

REGISTER_CONTROLLER(CPyController, "python_controller");
