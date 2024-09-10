# LLM-enhanced robot swarms

### [LLM-enhanced Robot Swarms that Responsively Communicate, Plan, and Collaborate](https://arxiv.org/pdf/2004.03355.pdf)
[Volker Strobel](https://iridia.ulb.ac.be/~vstrobel/), [Marco Dorigo](https://iridia.ulb.ac.be/~mdorigo/), [Mario Fritz](https://cispa.saarland/group/fritz/)<br>
[NeurIPS 2024 - Workshop on Open-World Agents (OWA-2024)](https://sites.google.com/view/open-world-agents/home)


# Large Language Model Swarm

This repository contains the code for letting a robot swarm negotiate
using Large Language Models (LLMs). For this purpose, the robots use OpenAI's API and GPT-4o.

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





