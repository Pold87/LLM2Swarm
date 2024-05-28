#ifndef PY_LOOP_FUNCTION_H
#define PY_LOOP_FUNCTION_H

#include <boost/make_shared.hpp>
#include <boost/python.hpp>

#include <argos3/plugins/robots/e-puck/simulator/epuck_entity.h>
#include <argos3/core/simulator/loop_functions.h>

#include <py_controller.h>
#include <py_qtuser_function.h>



using namespace argos;

class CPyLoopFunction : public CLoopFunctions {

 public:
  CPyLoopFunction();
  virtual ~CPyLoopFunction(){};
  //boost::python::list allRobots;
  virtual void Init(TConfigurationNode& t_node);
  
  //void AddEPuckEntity(const CVector3& position, const CQuaternion& orientation);
//  void AddEPuckEntityFromPython(const boost::python::tuple& position, const boost::python::tuple& orientation);
  CEPuckEntity* GetEPUCKWithID(UInt32 id);
  virtual void Reset();

  virtual void Destroy ();

  virtual void PreStep();

  virtual void PostStep();
  void AddRobotEntity(const CVector3& position, const CQuaternion& orientation);
  void AddNewRobot(const boost::python::tuple& position, const boost::python::tuple& orientation);
  virtual void AddRobotArena(float x, float y, int num);

  virtual bool IsExperimentFinished();

  virtual CColor GetFloorColor();

  virtual void PostExperiment();
  boost::python::list GetAllRobots() const;

 private:

    //size_t m_nextRobotID;
    boost::python::object m_loop_main;
    boost::python::object m_loop_namesp;
    boost::python::object m_loop_script;
    PyThreadState* m_loop_interpreter;
    boost::shared_ptr<EnvironmentWrapper> m_environment;
};

#endif