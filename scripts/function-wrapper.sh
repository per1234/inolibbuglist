#!/bin/bash
# I can't find any way to run a bash script function directly from Windows so I need to use this wrapper script to call the function

scriptPath="$1"
# shift out the first argument to the script (the second now becomes $1)
shift
arduinoCIscriptPath="$1"
shift
arduinoCIscriptApplicationFolder="$1"
shift
# strip the trailing ; from this argument (the ; is needed for the Linux command, which does not use this script)
arduinoCIscriptArduinoIDEversion="${1%;}"
shift
function="$1"
shift

source "$scriptPath" "$arduinoCIscriptPath" "$arduinoCIscriptApplicationFolder" "$arduinoCIscriptArduinoIDEversion"

# due to the shifts, $@ contains any remaining arguments, which will be passed as arguments to $function
$function "$@"
