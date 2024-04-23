# ARGoS-Blockchain Interface in Python

AUTHOR: 

Alexandre Pacheco  <alexandre.melo.pacheco@gmail.com>

CREDITS:

Ken Hasselmann for argos-python wrapper <https://github.com/KenN7/argos-python>

Ulysse Denis for implementing a mockup blockchain in python <https://github.com/uldenis/PROJH402>

DATE: 20/02/2023


# Installation guide
This guide assumes a previously clean installation of Ubuntu20.04

## ARGoS

Step 1: Download and compile ARGoS version 59 
(instructions at https://github.com/ilpincy/argos3)

Step 2: Download and compile E-puck plugin 
(instructions at https://github.com/demiurge-project/argos3-epuck)

## Put it all together

Step 1: Clone the repo

```git clone --recurse-submodules git@github.com:teksander/toychain-argos.git```

Step 2: Compile ARGoS-Python

```
cd toychain-argos/argos-python
mkdir build
cd build
cmake ..
make
```

Step 3: Configuration and Run

Edit ```experimentconfig.sh``` file to match your paths\
Then run an experiment

```
cd toychain-argos/HelloNeighbor
./starter -s
```
