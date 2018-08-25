#!/bin/bash
# This script is necessary because arduino-ci-script's check_keywords_txt's reference link check feature requires environment variables set by set_application_folder and install_ide but when those functions are run they are in a separate bash session so those environment variables are lost. Therefore this kludge of hardcoding them in this wrapper script is necessary.
arduinoCIscriptPath="$1"
arduinoCIscriptApplicationFolder="$2"
arduinoCIscriptArduinoIDEversion="$3"
source "$arduinoCIscriptPath"
set_application_folder "$arduinoCIscriptApplicationFolder"
NEWEST_INSTALLED_IDE_VERSION="$arduinoCIscriptArduinoIDEversion"
