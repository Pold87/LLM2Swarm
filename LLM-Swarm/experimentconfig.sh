# [PATHS]
export HOMEFOLDER="$HOME/software"
export MAINFOLDER="$HOMEFOLDER/chatgpt-swarm"
export ARGOSFOLDER="$MAINFOLDER/argos-python"
export EXPERIMENTFOLDER="$MAINFOLDER/LLM-Swarm"

# [FILES]
export ARGOSNAME="market-foraging"
export ARGOSFILE="${EXPERIMENTFOLDER}/experiments/${ARGOSNAME}.argos"
export ARGOSTEMPLATE="${EXPERIMENTFOLDER}/experiments/${ARGOSNAME}.x.argos"

# [DOCKER]
export SWARMNAME=ethereum
export CONTAINERBASE=${SWARMNAME}_eth

# [ARGOS]
export FLOOR="3.png"
export NUMROBOTS=3
export CON1="${EXPERIMENTFOLDER}/controllers/main.py"

export RABRANGE="0.3"
export WHEELNOISE="0"
export TPS=10
export DENSITY="1"
export ARENADIM="3.0"
export ARENADIMH="1.5"
export STARTDIM="0.35"


# [BEHAVIOR]

export NUMBYZANTINE=1
export BYZANTINESWARMSTYLE=1

# [LLM]
export SYSTEMMESSAGETEMPLATE='system_content.txt'
export USERMESSAGETEMPLATE='oodmsg.txt'
export DISCUSSIONPERIOD='inf'
export HUMANINTERACTIONPERIOD='100'

# For 'Instruct' human-swarm interaction
export SYSTEMHUMAN='system_human_instruct.txt'
export USERHUMAN='human_concrete_instruct.txt'

# For 'Inform' human-swarm interaction
#export SYSTEMHUMAN='system_human_inform.txt'
#export USERHUMAN='human_inform_template.txt'


# [OTHER]
export SEED=122
export TIMELIMIT=100
export LENGTH=5000
export SLEEPTIME=5
export REPS=1
export NOTES="debug logs"
