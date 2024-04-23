/*
 * AUTHOR: Ken Hasselmann <arg AT kenh DOT fr>
 *
 * Connects ARGoS to python
 *
 */

#ifndef PY_CONTROLLER_H
#define PY_CONTROLLER_H

#include "py_wrapper.h"
#include <boost/make_shared.hpp>

namespace argos {

class CPyController : public CCI_Controller {

  public:
    CPyController();
    virtual ~CPyController() {}

    /*
     * This function initializes the controller.
     * The 't_node' variable points to the <parameters> section in the XML
     * file in the <controllers><footbot_ccw_wander_controller> section.
     */
    virtual void Init(TConfigurationNode& t_node);

    /*
     * This function is called once every time step.
     * The length of the time step is set in the XML file.
     */
    virtual void ControlStep();

    /*
     * This function resets the controller to its state right after the
     * Init().
     * It is called when you press the reset button in the GUI.
     * In this example controller there is no need for resetting anything,
     * so the function could have been omitted. It's here just for
     * completeness.
     */
    virtual void Reset();

    /*
     * Called to cleanup what done by Init() when the experiment finishes.
     * In this example controller there is no need for clean anything up,
     * so the function could have been omitted. It's here just for
     * completeness.
     */
    virtual void Destroy();

    virtual boost::shared_ptr<ActusensorsWrapper> getActusensors();

    void InitSensorsActuators(TConfigurationNode& t_node);

  private:
    boost::python::object m_main;
    boost::python::object m_namesp;
    boost::python::object m_script;
    PyThreadState* m_interpreter;
    // Get the default thread state  
    //PyThreadState* state;
    PyInterpreterState* interpreterState;


    boost::shared_ptr<ActusensorsWrapper> m_actusensors;
    
    int m_state;
    int m_id;

    int timeStep;
    int timeRate;

    int robotId;

};

} // namespace argos

#endif
