# LLM-enhanced robot swarms

### [LLM-enhanced Robot Swarms that Responsively Communicate, Plan, and Collaborate](TODO)
[Volker Strobel](https://iridia.ulb.ac.be/~vstrobel/), [Marco Dorigo](https://iridia.ulb.ac.be/~mdorigo/), [Mario Fritz](https://cispa.saarland/group/fritz/)<br>
[NeurIPS 2024 - Workshop on Open-World Agents (OWA-2024)](https://sites.google.com/view/open-world-agents/home)


## Description of the repository

The main conroller file is specified in `LLM-Swarm/controllers/main.py`. The file `LLM-Swarm/experimentconfig.sh` specifies the experiment configuration; in particular, it specifies which prompt templates (stored in the folder `LLM-Swarm/controllers/prompt_templates`) should be used. The following variables in this file are related to the LLM interactions:

For robot-to-robot interaction:
- `DISCUSSIONPERIOD`: Time period between robot-to-robot interactions. For example, a value of 100 specifies that the robots interact with each after every 100 timesteps. Setting this variable to `'inf'` disables robot-robot interaction.
- `SYSTEMMESSAGETEMPLATE`: Template for the system prompt for robot-to-robot interaction.
- `USERMESSAGETEMPLATE`: Template for the user prompt for robot-to-robot interaction.


For human-to-robot interaction:
- `HUMANINTERACTIONPERIOD`: Time period between human-to-robot interaction. For example, a value of 500 specifies that the robots interact with each after every 500 timesteps. Setting this variable to `'inf'` disables human-robot interaction. 
- `SYSTEMHUMAN': Template for the system prompt for human-to-robot interaction.
- `USERHUMAN`: Template for the user prompt for human-to-robot interaction.



## Abstract
Robot swarms are composed of many simple robots that communicate and collaborate in order to fulfill complex tasks. Robot controllers usually need to be specified by experts on a case-by-case basis via programming code. This process can be time-consuming, prone to errors, and unable to take into account all situations that may be encountered during deployment. To address these challenges, we propose to connect Large Language Models (LLMs) with robot swarms. For this connection, we present two approaches. The first approach is indirect use, where LLMs are used to generate and validate the robot controllers. This approach may reduce development time and human error before deployment. Moreover, during deployment, it could the used for the on-the-fly creation of new robot behaviors. The second approach is direct use, where each robot locally executes a separate LLM instance during deployment for robot-to-robot and human-swarm interaction. These local LLM instances enable each robot to reason, plan, and collaborate using natural language. Both approaches have the potential to enhance the capabilities of robot swarms, but they also pose challenges, such as executing LLMs on limited robot hardware and ensuring safe and reliable robot behavior during deployment.

## Prerequisites
- TODO


# Code Structure

TODO


## Citation
  ```
TODO
  ```

## Acknowledgements
- Volker Strobel and Marco Dorigo acknowledge support from the Belgian F.R.S.-FNRS.
- Volker Strobel acknowledges the Helmholtz Information & Data Science Academy (HIDA) for providing financial support enabling a short-term research stay at CISPA Helmholtz Center for Information Security.





