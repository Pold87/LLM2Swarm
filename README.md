# LLM2Swarm
## Robot Swarms that Responsively Communicate, Plan, and Collaborate Through LLMs

## Videos

For the showcase videos, please see folder `videos/`.

## Abstract

Robot swarms are composed of many simple robots that communicate and collaborate to fulfill complex tasks. Robot controllers usually need to be specified by experts on a case-by-case basis via programming code. This process is time-consuming, prone to errors, and unable to take into account all situations that may be encountered during deployment. On the other hand, recent Large Language Models (LLMs) have demonstrated reasoning and planning capabilities, introduced new ways to interact with and program machines, and incorporate both domain-specific and commonsense knowledge. Hence, we propose to address the aforementioned challenges by integrating LLMs with robot swarms and show the potential in proofs of concept (showcases). For this integration, we explore two approaches. The first approach is 'indirect integration,' where LLMs are used to synthesize and validate the robot controllers. This approach may reduce development time and human error before deployment. Moreover, during deployment, it could be used for on-the-fly creation of new robot behaviors. The second approach is 'direct integration,' where each robot locally executes a separate LLM instance during deployment for robot-robot collaboration and human-swarm interaction. These local LLM instances enable each robot to reason, plan, and collaborate using natural language, as demonstrated in our showcases where the robots are able to detect a variety of anomalies, without prior information about the nature of these anomalies.


## Prerequisites

- [OpenAI API key](https://platform.openai.com/docs/overview) as environment variable
- [ARGoS robot swarm simulator](https://github.com/ilpincy/argos3)
- [ARGoS-Epuck](https://github.com/demiurge-project/argos3-epuck)
- Python 3.9 (later versions are not compatible with the ARGoS-Python wrapper)

## Setup

1. Clone the repository.
2. Set up and install all prerequistes.
4. Build `argos-python` as follows:
	```
	sudo apt install libboost-python-dev
	
	python3 -m venv venv
	source venv/bin/activate
	
	pip install -r requirements.txt

	cd argos3-python
	mkdir build
	cd build
	cmake ..
	make -j4
 	```
3. Update the variables in the `[PATHS]` section of the `DirectIntegration/experimentconfig.sh` file to reflect the installation directories on your system.


## Description of the repository


### Indirect integration

- `IndirectIntegration/syntax-generation.py` contains the controller synthesis script.
- `IndirectIntegration/logic-validation.py` contains the preliminary logic validation.
- `IndirectIntegration/security-checking.py` contains the preliminary security checking.


### Direct integration
- `DirectIntegration/controllers/main.py` is the main robot controller file.
- `DirectIntegration/controllers/movement_generated.py` is the default file for storing generated controllers.
- `DirectIntegration/experimentconfig.sh` specifies the experiment configuration; in also, it specifies which LLM prompt templates (stored in the folder `DirectUse/controllers/prompt_templates/`) should be used.

The following variables in the `DirectIntegration/experimentconfig.sh` file are related to the LLM interactions:

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
1. First, modify the necessary variables in the `DirectIntegration/experimentconfig.sh` file. The configurations that were used for the showcases are stored in the folder `DirectIntegration/example_configurations/`. To use one of these examples, modify the script `starter`, to source the desired configuration (e.g. `source example_configurations/experimentconfig_noanomaly.sh`) and modify the section `[PATHS]` to reflect your installation directories.
2. Then, run `./starter.sh -s` to start the simulation.

In the following, we detail the configurations for each showcase.

### Indirect Integration: Controller Synthesis

1. Change directory to `LLM2Swarm/IndirectIntegration/`.
2. Modify the `ARGOSPATH` variable in `syntax-generator.py` to reflect your installation directory.
3. Set export `USEGENERATEDMOVEMENT="1"` in `DirectIntegration/experimentconfig.sh`   
4. Execute `python3 syntax-generator.py`


### Direct Integration: Robot-Robot Interaction

#### No anomaly

```
# [ARGOS]
export FLOOR="3.png" # 3x3 floor with black and white tiles (floor images are stored in the folder experiments/floors/)

# [BEHAVIOR]

export NUMBYZANTINE=0 # Set the number of Byzantine robots to 0

# [LLM]
export DISCUSSIONPERIOD='100' # Set the robot-robot interaction period (200 means every 200 timesteps)
```

#### Self diagnosis

```
# [ARGOS]
export FLOOR="3.png" # 3x3 floor with black and white tiles (floor images are stored in the folder experiments/floors/)

# [BEHAVIOR]

export NUMBYZANTINE=3 # Set the number of Byzantine robots to 0
export BYZANTINESWARMSTYLE=1 # Byzantine style 1 means that a robot is not moving

# [LLM]
export DISCUSSIONPERIOD='100' # Set the robot-robot interaction period (200 means every 200 timesteps)
export HUMANINTERACTIONPERIOD='inf' # Set the time period for human-swarm interaction to infinity (to disable it)

```

#### Peer diagnosis

```
# [ARGOS]
export FLOOR="3.png" # 3x3 floor with black and white tiles (floor images are stored in the folder experiments/floors/)

# [BEHAVIOR]

export NUMBYZANTINE=1
export BYZANTINESWARMSTYLE=2 # Byzantine style 2 means that a robot is always sending 'crops' instead of its actuals sensor readings

# [LLM]
export DISCUSSIONPERIOD='100' # Set the robot-robot interaction period (200 means every 200 timesteps)
export HUMANINTERACTIONPERIOD='inf' # Set the time period for human-swarm interaction to infinity (to disable it)
```

#### Environmental diagnosis

```
# [ARGOS]
export FLOOR="3_new_person.png" # 3x3 floor with injured person

# [BEHAVIOR]

export NUMBYZANTINE=0 # Set the number of Byzantine robots to 0

# [LLM]
export DISCUSSIONPERIOD='200' # Set the interaction period (200 means every 200 timesteps)
export HUMANINTERACTIONPERIOD='inf' # Set the time period for human-swarm interaction to infinity (to disable it)
```

### Direct Integration: Human-Swarm Interaction

#### Inform

```
# [ARGOS]
export FLOOR="3_new_person.png" # 3x3 floor with injured person

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
export FLOOR="3_new_person.png" # 3x3 floor with injured person

# [BEHAVIOR]

export NUMBYZANTINE=0 # Set the number of Byzantine robots to 0

# [LLM]
export DISCUSSIONPERIOD='100' # Set the interaction period (100 means every 100 timesteps)
export HUMANINTERACTIONPERIOD='250' # Set the time period for human-robot interaction to 250

# Use the prompts for 'Instruct' human-swarm interaction
export SYSTEMHUMAN='system_human_instruct.txt'
export USERHUMAN='human_concrete_instruct.txt'
```
