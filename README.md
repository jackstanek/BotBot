# BotBot
[![Build Status](https://travis-ci.org/jackstanek/BotBot.svg?branch=master)](https://travis-ci.org/jackstanek/BotBot)

A manager for lab computational resources.

# Functionality

- Ensures all files in a shared folder are group readable.
- Encourages users to use symbolic links instead of copying large
  files.
- Suggests file compression when appropriate to save space.
- Modular design allowing for easy extension.

# Installation

## Automatic

Pretty simple:

```pip install botbot```

# Usage

The general usage of BotBot is as follows:

```botbot [-h] [-v] [-p] [-F] [-s] PATH```

```PATH``` specifies the path to check. Typically, this is the current
working directory.

## Command Line Options

* ```-h```, ```--help```: show this help message and exit
* ```-v```, ```--verbose```: Print issues and fixes for all files
* ```-p```: Check for group permissions issues
* ```-F```: Check for raw FASTQ files
* ```-s```: Check for *.sam files

# Testing

BotBot uses pytest as its test suite. To run the tests, run
```py.test``` in the project root directory.
