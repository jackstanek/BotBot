#!/bin/bash

SOURCE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

function install-inotify-wrapper {
    pip install git+git://github.com/jackstanek/PyInotify#egg=inotify-0.2.7
}

function install-botbot {
    pip install -e $SOURCE_DIR
}

install-inotify-wrapper && install-botbot
