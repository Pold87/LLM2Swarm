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
export NUMROBOTS=3
export CON1="${EXPERIMENTFOLDER}/controllers/main_ood.py"

export RABRANGE="0.3"
export WHEELNOISE="0"
export TPS=10
export DENSITY="1"
export ARENADIM="0.8"
export ARENADIMH="0.4"
export STARTDIM="0.35"


# [BEHAVIOR]

export NUMBYZANTINE=1
export BYZANTINESWARMSTYLE=1

# [LLM]
export SYSTEMMESSAGETEMPLATE='system_content.txt'
export USERMESSAGETEMPLATE='oodmsg.txt'
export DISCUSSIONPERIOD='inf'
export HUMANINTERACTIONPERIOD='inf'

# [OTHER]
export SEED=122
export TIMELIMIT=100
export LENGTH=5000
export SLEEPTIME=5
export REPS=1
export NOTES="debug logs"
