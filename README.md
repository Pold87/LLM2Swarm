# LLM2Swarm
## Robot Swarms that Responsively Communicate, Plan, and Collaborate Through LLMs

[NeurIPS 2024 - Workshop on Open-World Agents (OWA-2024)](https://sites.google.com/view/open-world-agents/home)


## Abstract

Robot swarms are composed of many simple robots that communicate and collaborate in order to fulfill complex tasks. Robot controllers usually need to be specified by experts on a case-by-case basis via programming code. This process can be time-consuming, prone to errors, and unable to take into account all situations that may be encountered during deployment. On the other hand, recent Large Language Models (LLMs) have been shown to provide reasoning and planning capabilities, new ways to interact and program machines, and represent domain and common sense knowledge. Hence, we propose to address the aforementioned challenges by integrating LLMs with robot swarms and show the potential in preliminary proofs-of-concept (showcases). For this integration, we explore two approaches. The first approach is 'indirect use,' where LLMs are used to generate and validate the robot controllers. This approach may reduce development time and human error before deployment. Moreover, during deployment, it could be used for the on-the-fly creation of new robot behaviors. The second approach is 'direct use,' where each robot locally executes a separate LLM instance during deployment for robot-to-robot and human-swarm interaction. These local LLM instances enable each robot to reason, plan, and collaborate using natural language. Both approaches have the potential to enhance the capabilities of robot swarms, but they also pose challenges, such as executing LLMs on limited robot hardware and ensuring safe and reliable robot behavior during deployment.

## Prerequisites

- [OpenAI API key](https://platform.openai.com/docs/overview)
- [ARGoS robot swarm simulator](https://github.com/ilpincy/argos3)
- [ARGoS-Python wrapper](https://zenodo.org/records/13765570)
- Python 3.9 (later versions are not compatible with the ARGoS-Python wrapper)

## Setup

1. Clone the repository.
2. Install all prerequistes.
3. Update the variables in the `[PATHS]` section of the `LLM2Swarm/experimentconfig.sh` file to reflect the installation directories on your system.


## Description of the repository

- `LLM2Swarm/controllers/main.py` is the main robot controller file
- `LLM2Swarm/controllers/movement_generated.py` is the default file for storing generated controllers
- `LLM2Swarm/experimentconfig.sh` specifies the experiment configuration; in also, it specifies which LLM prompt templates (stored in the folder `LLM2Swarm/controllers/prompt_templates/`) should be used.

The following variables in the `LLM2Swarm/experimentconfig.sh` file are related to the LLM interactions:

For robot-to-robot interaction:
- `DISCUSSIONPERIOD`: Time period between robot-to-robot interactions. For example, a value of 100 specifies that the robots interact with each after every 100 timesteps. Setting this variable to `'inf'` disables robot-robot interaction.
- `SYSTEMMESSAGETEMPLATE`: Template for the system prompt for robot-to-robot interaction.
- `USERMESSAGETEMPLATE`: Template for the user prompt for robot-to-robot interaction.


For human-to-robot interaction:
- `HUMANINTERACTIONPERIOD`: Time period between human-to-robot interaction. For example, a value of 500 specifies that the robots interact with each after every 500 timesteps. Setting this variable to `'inf'` disables human-robot interaction. 
- `SYSTEMHUMAN': Template for the system prompt for human-to-robot interaction.
- `USERHUMAN`: Template for the user prompt for human-to-robot interaction.


## Showcase Execution
 
For all showcases:
1. First, modify the necessary variables in the `LLM2Swarm/experimentconfig.sh` file. The configurations that we used are in the folder `LLM2Swarm/example_configurations/`.
2. Then, run `./starter.sh -s` to start the simulation.

In the following, we detail the configurations for each showcase.

### Controller Generation

```
# [ARGOS]
export FLOOR="3.png" # 3x3 floor with black and white tiles (floor images are stored in the folder experiments/floors/)

# [LLM]
export DISCUSSIONPERIOD='inf' # Disable robot-robot interaction
export HUMANINTERACTIONPERIOD='inf' # Disable human-swarm interaction
```

### Robot-Robot Interaction

#### No anomaly

```
# [ARGOS]
export FLOOR="3.png" # 3x3 floor with black and white tiles (floor images are stored in the folder experiments/floors/)

# [BEHAVIOR]

export NUMBYZANTINE=0 # Set the number of Byzantine robots to 0

# [LLM]
export DISCUSSIONPERIOD='200' # Set the robot-robot interaction period (200 means every 200 timesteps)
```

#### Self diagnosis

```
# [ARGOS]
export FLOOR="3.png" # 3x3 floor with black and white tiles (floor images are stored in the folder experiments/floors/)

# [BEHAVIOR]

export NUMBYZANTINE=3 # Set the number of Byzantine robots to 0
export BYZANTINESWARMSTYLE=1 # Byzantine style 1 means that a robot is not moving

# [LLM]
export DISCUSSIONPERIOD='200' # Set the robot-robot interaction period (200 means every 200 timesteps)
export HUMANINTERACTIONPERIOD='inf' # Set the time period for human-robot interaction to infinity (to disable HRI)

```

#### Peer diagnosis

```
# [ARGOS]
export FLOOR="3.png" # 3x3 floor with black and white tiles (floor images are stored in the folder experiments/floors/)

# [BEHAVIOR]

export NUMBYZANTINE=1
export BYZANTINESWARMSTYLE=2 # Byzantine style 2 means that a robot is always sending 'crops' instead of its actuals sensor readings

# [LLM]
export DISCUSSIONPERIOD='200' # Set the robot-robot interaction period (200 means every 200 timesteps)
export HUMANINTERACTIONPERIOD='inf' # Set the time period for human-robot interaction to infinity (to disable HRI)
```

#### Environmental diagnosis

```
# [ARGOS]
export FLOOR="3_person.png" # 3x3 floor with injured person

# [BEHAVIOR]

export NUMBYZANTINE=0 # Set the number of Byzantine robots to 0

# [LLM]
export DISCUSSIONPERIOD='200' # Set the interaction period (200 means every 200 timesteps)
export HUMANINTERACTIONPERIOD='inf' # Set the time period for human-robot interaction to infinity (to disable HRI)
```

### Human-Swarm Interaction

#### Inform

```
# [ARGOS]
export FLOOR="3_person.png" # 3x3 floor with injured person

# [BEHAVIOR]

export NUMBYZANTINE=0 # Set the number of Byzantine robots to 0

# [LLM]
export DISCUSSIONPERIOD='200' # Set the interaction period (200 means every 200 timesteps)
export HUMANINTERACTIONPERIOD='500' # Set the time period for human-robot interaction to 500

# Use the prompts for 'Inform' human-swarm interaction
#export SYSTEMHUMAN='system_human_inform.txt'
#export USERHUMAN='human_inform_template.txt'
```

#### Instruct

```
# [ARGOS]
export FLOOR="3_person.png" # 3x3 floor with injured person

# [BEHAVIOR]

export NUMBYZANTINE=0 # Set the number of Byzantine robots to 0

# [LLM]
export DISCUSSIONPERIOD='200' # Set the interaction period (200 means every 200 timesteps)
export HUMANINTERACTIONPERIOD='500' # Set the time period for human-robot interaction to 500

# Use the prompts for 'Instruct' human-swarm interaction
export SYSTEMHUMAN='system_human_instruct.txt'
export USERHUMAN='human_concrete_instruct.txt'
```