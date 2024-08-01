# Large Language Model Swarm

This repository contains the code for letting a robot swarm negotiate
using Large Language Models (LLMs). For this purpose, the robots using
together.ai'API.

# Code Structure

In `LLM-Swarm/controllers/`, there are two .txt files that are used to generate prompts:
- byzmsg.txt: the prompt that is used by Byzantine robots 
- nonbyzmsg.txt: the promopt that is used by non-Byzantine robots
These files contains {placeholders} (indicated by the curly brackets in the .txt files) that are filled by the ARGoS controllers. At the end of each prompt, the ARGoS controller also adds a history of the results of the previous queries, 
