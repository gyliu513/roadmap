#!/bin/bash
# THIS SCRIPT ONLY WORKS FOR UBUNTU LINUX and assumes arch amd64
c_echo(){
    RED="\033[0;31m"
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    NC='\033[0m' # No Color

    printf "${!1}${2} ${NC}\n"
}

c_echo "RED" "I'm RED"
c_echo "YELLOW" "I'm YELLOW"
c_echo "GREEN" "I'm GREEN"
