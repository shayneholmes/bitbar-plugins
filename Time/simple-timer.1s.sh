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

STATUS_LOG=$TMPDIR/status.tmp

WORK_TIME_IN_SECONDS=$((WORK_TIME * 60))
BREAK_TIME_IN_SECONDS=$((BREAK_TIME * 60))

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
}

function writeCompletion {
  echo "$STATUS" >> "$STATUS_LOG"
  osascript -e "display notification \"Finished $(printTimerName)\" with title \"Timer\" sound name \"$(printTimerCompletionSound)\"" &> /dev/null
}

function breakMode {
  changeStatus "2" "Break Mode" "Glass"
}

function workMode {
  changeStatus "1" "Work Mode" "Blow"
}

function disable {
  changeStatus "0" "Disabled"
}

# Support changing from menu items
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
    disable
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

function printBars {
  local TOTAL="$(getCurrentTotal)"
  local ELAPSED="$(secondsElapsed)"
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
  echo "$OUTPUT"
}

function printTimerCompletionSound {
  case "$STATUS" in
    "1")
      # work
      echo "Glass"
      ;;
    "2")
      # break
      echo "Glass"
      ;;
  esac
}

function printTimerName {
  case "$STATUS" in
    "0")
      echo ""
      ;;
    "1")
      echo "work: "
      ;;
    "2")
      echo "break: "
      ;;
  esac
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

function secondsElapsed {
  local ELAPSED=$((CURRENT_TIME - TIME))
  echo "$ELAPSED";
}

function secondsRemaining {
  local TOTAL="$(getCurrentTotal)"
  local ELAPSED="$(secondsElapsed)"
  local REMAINING=$((TOTAL - ELAPSED))
  echo "$REMAINING";
}

function getSeconds {
  echo $(($1 % 60))
}

function getMinutes {
  echo $(($1 / 60))
}

function printTime {
  SECONDS=$(getSeconds "$1")
  MINUTES=$(getMinutes "$1")
  printf "%02d:%02d" $MINUTES $SECONDS
}

function printTimeRemaining {
  if [ $STATUS -eq 0 ]; then
    echo " --:--"
  else
    echo "$(printTime "$(secondsRemaining)")"
  fi
}

# Check for timeouts
if [ $STATUS -ne 0 ]; then
  TIME_LEFT=$(secondsRemaining)
  if (( "$TIME_LEFT" < 0 )); then
    writeCompletion
    disable
  fi
fi

echo "$(printTimerName) $(printBars)"
echo "---";
echo "$(printTimeRemaining)"
echo "👔 Work | bash=\"$0\" param1=work terminal=false refresh=true"
echo "☕ Break | bash=\"$0\" param1=break terminal=false refresh=true"
echo "🔌 Disable | bash=\"$0\" param1=disable terminal=false refresh=true"
