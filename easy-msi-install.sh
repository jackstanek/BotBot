#!/bin/bash
# Script to set up botbot.
# Written by Jack Stanek and Rob Schaefer.

NAME='BotBot'
BASE="/home/mccuem/shared/.local/conda"
CWD=`pwd`

function get-canonical-path() {
    cd -P -- "$(dirname -- "$1")" &&
        printf '%s\n' "$(pwd -P)/$(basename -- "$1")"
}

function usage()
{
    cat <<EOF
Usage: $0 [flags]

Flags
-----
-b | Specify the directory where conda is installed.
     (By default: $)
EOF
    exit 0
}

function vecho()
{
    if [[ $VERBOSE -eq 1 ]]; then
        echo $1
    fi
}

function color()
{
    local RED='\033[1;31m'
    local GREEN='\033[1;32m'
    local NC='\033[0m'

    case "$1" in
        1) echo -e "$RED$2$NC"
           ;;
        2) echo -e "$GREEN$2$NC"
           ;;
    esac
}

function red()
{
    color 1 "$1"
}

function green()
{
    color 2 "$1"
}

function parse-args()
{
    while [[ $# -gt 0 ]]
    do
        local key="$1"
        case $key in
            "-h"|"--help")
                usage
                shift
                exit
                ;;
            "-b"|"--base")
                BASE=$2
                shift
                ;;
            "-v"|"--verbose")
                VERBOSE=1
                shift
                ;;
            *)
                usage
                exit 1
                ;;
        esac
    done

    # This should be in the path
    BIN_BASE="$(get-canonical-path $BASE)/bin"
    vecho "Set BIN_BASE to $BIN_BASE"
}

function separate-path-var()
{
    echo $PATH | tr ":" "\n"
}

function add-conda-to-path()
{
    echo "export PATH=$PATH:$BIN_BASE" >> $HOME/.bash_profile
}

function test-conda-bin-dir-in-path()
{
    PATH_N=$(separate-path-var)

    for path in $PATH_N; do
        if [[ $(get-canonical-path $path) == $BIN_BASE ]]; then
            green "Found $BIN_BASE in PATH..."
        else
            vecho "Checked $path..."
        fi
    done

    red "Could not find conda installation in $BIN_BASE..."
    green "Adding conda to \$PATH bash config..."
    add-conda-to-path

}

function do-everything()
{
    parse-args $@
    test-conda-bin-dir-in-path
}

do-everything $@
