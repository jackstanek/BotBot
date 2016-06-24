#!/bin/bash

function install-inotify-wrapper {
    pip install git+git://github.com/jackstanek/PyInotify#egg=inotify-0.2.7
}

install-inotify-wrapper
