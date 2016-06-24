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

## Manual

If you want the latest and greatest development code, go ahead and
clone this repo:

```
git clone https://github.com/jackstanek/BotBot.git
cd BotBot
python setup.py install
```

then run

```
./install.sh
```

to install.

# Configuration

BotBot uses 2 primary configuration files: `~/.botbotignore` and
`~/.botbot/botbot.conf`.

## `.botbotignore`

This is a list of files that BotBot won't check. It is similar in
structure to a `.gitignore` file, but it's a bit simpler. Instead of
git's structure, each line is a string which can be handled by the
Python built-in [`glob`](https://docs.python.org/3/library/glob.html)
module. Anything after a `#` character will be ignored, so these can
be used to add comments.

## `.botbot/botbot.conf`

Configuration variables are stored here. The file is an .ini-style
configuration formatted file. The variables are stored in sections as
follows:

- `[checks]`
    - `oldage`: defines how many days old a file must be to be
      considered "old".

    - `largesize`: defines how many bytes large a file must be to be
      considered "large".

- `[fileinfo]`
    - `important`: defines which file extensions are considered
      "important." By default, *.sam and *.bam files are denoted as
      important.

# Testing

BotBot uses pytest as its test suite. To run the tests, run
```py.test``` in the project root directory.
