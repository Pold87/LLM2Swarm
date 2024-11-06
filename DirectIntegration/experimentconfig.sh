# [PATHS]
export HOMEFOLDER="$HOME/software"
export MAINFOLDER="$HOMEFOLDER/LLM2Swarm"
export ARGOSFOLDER="$MAINFOLDER/argos-python"
export EXPERIMENTFOLDER="$MAINFOLDER/DirectIntegration"

# [FILES]
export ARGOSNAME="llm2swarm"
export ARGOSFILE="${EXPERIMENTFOLDER}/experiments/${ARGOSNAME}.argos"
export ARGOSTEMPLATE="${EXPERIMENTFOLDER}/experiments/${ARGOSNAME}.x.argos"

# [ARGOS]
export FLOOR="aggregation.png"
export NUMROBOTS=10
export CON1="${EXPERIMENTFOLDER}/controllers/main.py"

export RABRANGE="0.3"
export WHEELNOISE="0"
export TPS=10
export DENSITY="1"
export ARENADIM="1.0"
export ARENADIMH="0.5"
export STARTDIM="0.35"


# [BEHAVIOR]

export NUMBYZANTINE=0
export BYZANTINESWARMSTYLE=0

# [LLM]
export SYSTEMMESSAGETEMPLATE='system_content.txt'
export USERMESSAGETEMPLATE='oodmsg.txt'
export DISCUSSIONPERIOD='inf'
export HUMANINTERACTIONPERIOD='inf'
export USEGENERATEDMOVEMENT="1"
export PRINTLLMRESPONSE="1"


# [OTHER]
export SEED=122
export TIMELIMIT=100
export LENGTH=5000
export SLEEPTIME=5
export REPS=1
export NOTES="debug logs"
