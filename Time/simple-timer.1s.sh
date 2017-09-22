#!/bin/bash
#
# <bitbar.title>Simple Timer</bitbar.title>
# <bitbar.version>v0.1</bitbar.version>
# <bitbar.author>Shayne Holmes</bitbar.author>
# <bitbar.author.github>shayneholmes</bitbar.author.github>
# <bitbar.desc>Simple timer with state representation</bitbar.desc>
# <bitbar.image>None yet (imgur link pending)</bitbar.image>

WORK_TIME=10
BREAK_TIME=10

SAVE_LOCATION=$TMPDIR/simple-timer
TOMATO='🍅'

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
# [OOO---]
OPENING_CHAR='['
CLOSING_CHAR=']'
ELAPSED_CHAR='O'
REMAINING_CHAR='-'
SUMMARY_LENGTH=6

function printState {
  local REMAINING="$(timeLeft $WORK_TIME_IN_SECONDS)"
  local TOTAL="$WORK_TIME_IN_SECONDS"
  local ELAPSED="$((TOTAL - REMAINING))"
  local COMPLETED_BARS="$((ELAPSED * (SUMMARY_LENGTH + 1) / TOTAL))"
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

function printTime {
    SECONDS=$(getSeconds "$1")
    MINUTES=$(getMinutes "$1")
    printf "%s %02d:%02d| color=%s\n" "$TOMATO" "$MINUTES" "$SECONDS"  "$2"
}

case "$STATUS" in
# STOP MODE
"0")
    echo "$TOMATO"
  ;;
"1")
    TIME_LEFT=$(timeLeft $WORK_TIME_IN_SECONDS)
    if (( "$TIME_LEFT" < 0 )); then
        breakMode
    fi
    printState "$TIME_LEFT" "red"
  ;;
"2")
    TIME_LEFT=$(timeLeft $BREAK_TIME_IN_SECONDS)
    if (("$TIME_LEFT" < 0)); then
        workMode
    fi
    printState "$TIME_LEFT" "green"
  ;;
esac

echo "---";
echo "👔 Work | bash=\"$0\" param1=work terminal=false"
echo "☕ Break | bash=\"$0\" param1=break terminal=false"
echo "🔌 Disable | bash=\"$0\" param1=disable terminal=false"
