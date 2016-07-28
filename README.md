# BotBot
[![Build Status](https://travis-ci.org/jackstanek/BotBot.svg?branch=master)](https://travis-ci.org/jackstanek/BotBot)
[![Coverage Status](https://coveralls.io/repos/github/jackstanek/BotBot/badge.svg?branch=master)](https://coveralls.io/github/jackstanek/BotBot?branch=master)

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
```

then run

```
./install.sh
```

If you want to run the test suite as well, you'll need to run

```
./install.sh -t
```

instead.

To run the test suite just run `py.test` in the project directory.

# Usage

If you want to use BotBot to check files and directories on demand,
use the command:

`botbot file [options] PATH`

There a handful of options you can use:

- `-c, --cached`: generate a report based on the results of the most
  recent check.
- `-k, --force-recheck`: clears the cached version of the last check
  and rechecks the file or directory.
- `-s, --shared`: use a set of checks intended for files and
  directories in the shared folder.
- `-l, --follow-symlinks`: force BotBot to follow symbolic links.
- `-m, --me`: only check files that belong to you.

You can also use BotBot to check if your environment variables are
set up correctly. However, this feature needs a little
configuration to work properly. You must first configure the
`[important]` section in [`botbot.conf`](#botbotbotbotconf).

After that, you can use the command:

`botbot env`

to check that the environment variables are properly configured.

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

- `[email]` (REQUIRED for email mode)
    - `domain`: the domain that the users' email accounts are on
    - `email`: your email address (which emails are sent from)
    - `password`: your email password
    - `smtp_server`: the SMTP server you will send from
    - `smtp_port`: the port the SMTP server uses (probably 587, check
      with your server administrator or documentation)
    - `grace_period`: amount of time, in minutes, after changing a
      file that a user can fix potential issues before receiving an
      email about said changes

- `[important]`
    - `fileinfo`: defines which file extensions are considered
    "important." By default, *.sam and *.bam files are denoted as
    important.
    - `pathitems`: defines which paths (separated by colons) should be
      present in the PATH environment variable.
    - `ldlibpath`: defines which paths (separated by colons) should be
      present in the LD_LIBRARY_PATH environment variable.

# Testing

BotBot uses pytest as its test suite. To run the tests, run
```py.test``` in the project root directory.
