#ifndef PY_QTUSER_FUNCTION_H
#define PY_QTUSER_FUNCTION_H

#include <boost/make_shared.hpp>
#include <boost/python.hpp>

#include <argos3/plugins/simulator/visualizations/qt-opengl/qtopengl_user_functions.h>
#include <argos3/plugins/robots/e-puck/simulator/epuck_entity.h>
#include <argos3/core/simulator/loop_functions.h>

#include <py_controller.h>
#include "py_wrapper.h"



using namespace argos;


class CPyQTUserFunction : public CQTOpenGLUserFunctions {

 public:

   CPyQTUserFunction();

   virtual ~CPyQTUserFunction () {}

   virtual void Init(TConfigurationNode& t_node);
   void DrawInWorld();
   void Destroy();
   void Draw(CEPuckEntity& c_entity);
   virtual boost::shared_ptr<EnvironmentWrapper> getEnvironment();

 private:
  
    boost::python::object m_qtuser_main;
    boost::python::object m_qtuser_namesp;
    boost::python::object m_qtuser_script;
    PyThreadState* m_qtuser_interpreter;
    boost::shared_ptr<EnvironmentWrapper> m_environment;

  };
  #endif