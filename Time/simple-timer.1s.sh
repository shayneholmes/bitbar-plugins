#!/bin/bash
#
# <bitbar.title>Simple Timer</bitbar.title>
# <bitbar.version>v0.1</bitbar.version>
# <bitbar.author>Shayne Holmes</bitbar.author>
# <bitbar.author.github>shayneholmes</bitbar.author.github>
# <bitbar.desc>Simple timer with state representation</bitbar.desc>
# <bitbar.image>None yet (imgur link pending)</bitbar.image>

WORK_TIME=15
BREAK_TIME=5

SAVE_LOCATION=$TMPDIR/simple-timer

WORK_TIME_IN_SECONDS=$((WORK_TIME * 1))
BREAK_TIME_IN_SECONDS=$((BREAK_TIME * 1))

CURRENT_TIME=$(date +%s)

if [ -f "$SAVE_LOCATION" ];
then
  DATA=$(cat "$SAVE_LOCATION")
else
  DATA="$CURRENT_TIME|0"
fi

TIME=$(echo "$DATA" | cut -d "|" -f1)
STATUS=$(echo "$DATA" | cut -d "|" -f2)

function changeStatus {
  echo "$CURRENT_TIME|$1" > "$SAVE_LOCATION";
  # osascript -e "display notification \"$2\" with title \"$TOMATO Pomodoro\" sound name \"$3\"" &> /dev/null
}

function breakMode {
  changeStatus "2" "Break Mode" "Glass"
}

function workMode {
  changeStatus "1" "Work Mode" "Blow"
}

case "$1" in
  "work")
    workMode
    exit
    ;;
  "break")
    breakMode
    exit
    ;;
  "disable")
    changeStatus "0" "Disabled"
    exit
    ;;
esac

# Should look something like this:
# ■■■□□□
OPENING_CHAR=''
CLOSING_CHAR=''
ELAPSED_CHAR='■'
REMAINING_CHAR='□'
SUMMARY_LENGTH=6

function printState {
  local TOTAL="$(getCurrentTotal)"
  local REMAINING="$(timeLeft $TOTAL)"
  local ELAPSED="$((TOTAL - REMAINING))"
  local COMPLETED_BARS="$((ELAPSED * (SUMMARY_LENGTH + 1) / TOTAL))"
  if [ $STATUS -eq 0 ]; then #DISABLED
    COMPLETED_BARS=0
  fi
  local OUTPUT="$OPENING_CHAR"
  for i in $(seq 1 $SUMMARY_LENGTH); do
    if [ $i -lt $COMPLETED_BARS ]; then
      OUTPUT+="$ELAPSED_CHAR"
    else
      OUTPUT+="$REMAINING_CHAR"
    fi
  done
  OUTPUT+="$CLOSING_CHAR"
  echo "$OUTPUT | $(getColor)"
}

function getCurrentTotal {
  case "$STATUS" in
    "0")
      # STOP MODE
      echo "10000000"
      ;;
    "1")
      # WORK
      echo "$WORK_TIME_IN_SECONDS"
      ;;
    "2")
      # BREAK
      echo "$BREAK_TIME_IN_SECONDS"
      ;;
  esac
}

function timeLeft {
  local FROM=$1
  local TIME_DIFF=$((CURRENT_TIME - TIME))
  local TIME_LEFT=$((FROM - TIME_DIFF))
  echo "$TIME_LEFT";
}

function getSeconds {
  echo $(($1 % 60))
}

function getMinutes {
  echo $(($1 / 60))
}

function getColor {
  echo "color="
  case "$STATUS" in
    "0")
      # STOP MODE
      echo "gray"
      ;;
    "1")
      # WORK
      echo "blue"
      ;;
    "2")
      # BREAK
      echo "green"
      ;;
  esac
}

case "$STATUS" in
  "0")
    # STOP MODE
    ;;
  "1")
    TIME_LEFT=$(timeLeft $WORK_TIME_IN_SECONDS)
    if (( "$TIME_LEFT" < 0 )); then
      breakMode
    fi
    ;;
  "2")
    TIME_LEFT=$(timeLeft $BREAK_TIME_IN_SECONDS)
    if (("$TIME_LEFT" < 0)); then
      workMode
    fi
    ;;
esac
echo $(printState)

echo "---";
echo "👔 Work | bash=\"$0\" param1=work terminal=false refresh=true"
echo "☕ Break | bash=\"$0\" param1=break terminal=false refresh=true"
echo "🔌 Disable | bash=\"$0\" param1=disable terminal=false refresh=true"
