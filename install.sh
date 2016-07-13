#!/bin/bash
# Script to set up botbot.
# Written by Jack Stanek and Rob Schaefer.

NAME='BotBot'
BASE="$HOME/.botbot"
CWD=`pwd`
INSTALL_TEST_SUITE=0

function usage()
{
    cat <<EOF
Usage: $0 [flags]

Flags
-----
-b | Set the base install directory for botbot.
-h | Print this help message.
-t | Install test suite as well.
EOF
    exit 0
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
            "-t"|"--tests")
                INSTALL_TEST_SUITE=1
                shift
                ;;
            *)
                usage
                exit 1
                ;;
        esac
    done
}

function install-conda-by-hand()
{
    CONDA_INSTALL_LOCAL=1

    cd $BASE
    mkdir conda

    wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh &&
    bash miniconda.sh -b -f -p $BASE/conda &&
    rm -f miniconda.sh

    green "Installed conda at $BASE..."

    cd $CWD

    echo 'PATH=$PATH:$BASE/conda/bin' > setenv.sh
    source setenv.sh

}

function check-conda-install()
{
    CONDA=`command -v conda`

    if [[ -z $CONDA ]]; then
        red "conda is not installed. Attempting to install..."
        echo "Note: if you do not have sudo privileges, conda will be installed locally."
        sudo pip install conda
        local _conda_install_result=$?

        if [[ $_conda_install_result -ne 0 ]]; then
            red "Could not install conda using pip. Attempting to install in $BASE..."

            install-conda-by-hand
        else
            green "Successfully installed conda..."
        fi
    else
        green "Using conda install found at $CONDA..."
    fi
}

function make-conda-env()
{
    echo "Making conda environment with name $NAME..."
    conda remove -y --name $NAME --all ||
        (red "An environment named $NAME already exists, but could not be removed..." &&
                exit 1)

    conda create -y -n $NAME python==3.5 pip setuptools ||
        (red "Could not create environment $NAME..."
         exit 1)

    green "Created conda environment $NAME..."
}

function setup-conda-env()
{
    green "Configuring conda environment $NAME..."
    source activate $NAME ||
        (red "Could not activate environment $NAME..."
         exit 1)

    pip install -r requirements.txt ||
        (red "Could not install botbot or its dependencies..."
         red "Try running ./install.sh from the directory it's in."
         exit 1)

    if [ $INSTALL_TEST_SUITE -eq 1 ]; then
        pip install -r test_requirements.txt ||
            (red "Could not install test suite..."
             exit 1)
    fi

    source deactivate
    green "Successfully set up environment $NAME..."
}

function create-dot-botbot-directory()
{
    green "Configuring base directory $BASE..."
    if [ ! -d $BASE ]; then
        echo "Creating $BASE..."
        mkdir $BASE
    fi

    echo "Creating default configuration..."
    cp ./botbot/resources/botbot.conf $BASE

    echo "Creating or updating file database..."
    touch $BASE/filecache.sqlite
}

function on-success()
{
    green "Successfully installed in virtual environment $NAME!"

    if [[ $CONDA_INSTALL_LOCAL -eq 1 ]]; then
        red "However, it appears that conda needed to be installed locally."
        echo "This means you will need to adjust your environment variables."
        echo "To do this, run 'source setenv.sh' in this directory."
        echo "Or, run '< setenv.sh >> ~/.bashrc && source ~/.bashrc' to set permanently."
    fi

    echo -n ""

    echo "To use botbot, run 'source activate BotBot'."
    echo "Check out the functionality with 'botbot -h'."
    echo "When you're finished with BotBot, run 'source deactivate'."
    green "Have fun!"
}

function do-everything()
{
    parse-args $@ &&
        create-dot-botbot-directory &&
        check-conda-install &&
        make-conda-env &&
        setup-conda-env &&
        on-success &&
        exit
}

do-everything $@
