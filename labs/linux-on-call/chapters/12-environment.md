:::step{type=story title="command not found"}
The previous engineer left Tara a handy little command, `tara-status`, which prints the state of the dishes in one line.
Anjali types it every morning on her laptop. You type it on the server:

```text
$ cd /workspace/12-environment
$ tara-status
bash: tara-status: command not found
```

The program is right there, in `bin/`. So why can the shell not find it? And a second puzzle: the observatory's app
should listen on port 8080 on the server, but on 9000 on Anjali's laptop, where 8080 is busy. Changing the code for
each machine would be silly.

Both answers live in the **environment**: a set of named values that every process carries with it, and passes on to
the programs it starts. One of them, **PATH**, decides where the shell looks for commands. Others carry settings, like
which port to use.

Before search engines, finding a number meant a telephone directory, and a city had several: you looked in one, then
the next, in a fixed order, until the name turned up. The shell finds commands the same way, through a list of
folders, in order.

:::photo{src="/lesson-images/linux/telephone-directories.webp" alt="An open telephone directory lying on a carpet, its pages full of names and numbers in small print" credit="Tomasz Sienicki" license="CC BY 3.0" source="https://commons.wikimedia.org/wiki/File:Telefonbog_ubt-1.JPG"}
A telephone directory: thousands of names, searched in order.
:::

:::mission
Make the start script read its settings from the environment, and make tara-status work as a command from any folder.
:::
:::

:::step{type=concept title="Environment variables"}
An **environment variable** is a name with a value, carried by a process. Some are set for you:

```text
$ echo $HOME; echo $USER; echo $SHELL
/home/learner
learner
/bin/bash
$ printenv | sort | head -8
COLUMNS=100
DEBIAN_FRONTEND=noninteractive
HOME=/home/learner
HOSTNAME=e36f5c554a0e
LANG=C.UTF-8
LESSCLOSE=/usr/bin/lesspipe %s %s
LESSOPEN=| /usr/bin/lesspipe %s
LS_COLORS=
```

`printenv` (or `env`) lists them all. By habit their names are in capitals.

The important rule: a variable you set in the shell stays **in the shell**, until you **export** it. Exported variables
are copied into every program the shell starts:

```text
$ colour=blue; bash -c "echo child sees: [\$colour]"; export colour; bash -c "echo child sees: [\$colour]"
child sees: []
child sees: [blue]
```

(`bash -c "..."` starts a new, child bash that runs one command.) Before `export`, the child saw nothing; after it, it
saw `blue`. Copies only travel **down**, to children: a child can never change its parent's variables.

For one command only, put the setting in front of it. It is exported to that command, and the shell itself is
unchanged:

```text
$ PORT=9000 bash -c "echo port is \$PORT"; echo "here PORT is [${PORT:-}]"
port is 9000
here PORT is []
```

:::diagram{name="linux-env"}
Exported variables are copied from parent to child. The child gets its own copy; changes never travel back up.
:::

**Check yourself:** you set `NAME=tara` and run a script that prints `$NAME`. It prints nothing. Why? (`NAME` was not
exported, so the script, a child process, never got a copy.)
:::

:::step{type=example title="Worked example: defaults"}
A program that reads its settings from the environment needs a sensible value when a setting is missing.
`${NAME:-default}` gives the variable's value, or the default when it is unset or empty:

```text
$ unset PORT; echo "${PORT:-8080}"; PORT=9000; echo "${PORT:-8080}"
8080
9000
```

1. `unset PORT` removed the variable, so `${PORT:-8080}` gave the default.
2. With `PORT=9000`, the real value won.

This is how almost every modern app is configured. The same code runs everywhere; each machine just sets different
variables: `PORT=8080 APP_ENV=production` on the server, nothing at all on a laptop, where the defaults apply.
Passwords travel the same way, so they never have to be written into the code.

This chapter's `start.sh` only prints what it would do:

```text
$ cat start.sh
#!/usr/bin/env bash
# start.sh: print how the app would start, from two environment variables:
#   PORT     (when it is not set: 8080)
#   APP_ENV  (when it is not set: development)
# Exactly this line: Starting Tara on port PORT in APP_ENV mode
# TODO (task env_defaults): your line here.
```
:::

:::step{type=task task=env_defaults title="Your turn: settings with defaults"}
Finish `start.sh` in `/workspace/12-environment` so that it prints exactly:

```text
Starting Tara on port PORT in APP_ENV mode
```

with the values of `PORT` (default `8080`) and `APP_ENV` (default `development`). Try `bash start.sh`,
`PORT=9000 bash start.sh` and `APP_ENV=production bash start.sh`. Press **Check**.
:::

:::step{type=concept title="PATH: where commands come from"}
When you type a command without a `/` in it, the shell looks for a program with that name in a list of folders, in
order, and runs the first one it finds. The list is the variable **PATH**, folders separated by colons:

```text
$ echo "$PATH" | tr : "\n"
/usr/local/sbin
/usr/local/bin
/usr/sbin
/usr/bin
/sbin
/bin
$ which ls python3 bash
/usr/bin/ls
/usr/bin/python3
/usr/bin/bash
```

`which` shows where a command was found. Your `bin` folder is not in the list, so `tara-status` is "not found". And
there is a second problem:

```text
$ bin/tara-status
bash: bin/tara-status: Permission denied
$ ls -l bin
total 4
-rw-r--r-- 1 learner learner 80 Nov 22 18:15 tara-status
```

No `x`. A command must be **on the PATH** and **executable** (chapter 7). To add a folder, put it in front of the
existing PATH, keeping everything else:

```bash
export PATH="/some/folder:$PATH"
```

Never replace PATH completely. This is what happens when you do:

```text
$ PATH=/nothing; ls
bash: ls: command not found
```

Every command is suddenly "not found". (Close the terminal and open a new one, and PATH is back to normal.)

**Making it stick.** A setting typed in the terminal lasts until the terminal closes. Lines in `~/.bashrc` run every
time a new interactive bash starts, so that is where your own `export PATH=...` and aliases go. And to load settings
from a file into **the current shell**, use `source file` (or `. file`): plain `bash file` would run it in a child,
whose changes vanish when it ends.
:::

:::step{type=predict title="Guess first"}
:::question
`env.sh` contains `export PATH="$HOME/tools:$PATH"`. You run `bash env.sh`. Is `~/tools` on your PATH afterwards?
:::
- [ ] Yes
- [x] No: bash env.sh runs in a child process, and the child's PATH disappears when it ends
- [ ] Only for new terminals
:::explain
`source env.sh` runs the lines in your current shell, so the change stays. That is why such files say "source me".
:::
:::

:::step{type=task task=path_tool title="Your turn: tara-status as a command"}
In `/workspace/12-environment`:

1. Make `bin/tara-status` executable.
2. Write one line in `env.sh` that puts this chapter's `bin` folder, by its **full path**, in front of your PATH,
   keeping the rest.

Then `source env.sh`, `cd /`, and `tara-status` should work from anywhere, and `ls` should still work too. Press
**Check**.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What does `${APP_ENV:-development}` give when `APP_ENV=production`?
:::
- [x] `production`
- [ ] `development`
- [ ] `production:-development`
:::explain
The default is used only when the variable is unset or empty. A real value always wins.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Two folders on your PATH both contain a program called `report`. Which one runs?
:::
- [x] The one in the folder that comes first in PATH
- [ ] The newer one
- [ ] Neither: the shell asks you
:::explain
The shell stops at the first match. `which -a report` lists every match, in the order the shell would find them. That
is also why your own folder goes at the **front**: your version wins.
:::
:::

:::step{type=deep-dive title="Go deeper: configuration in the environment"}
**The twelve-factor app.** In 2011 engineers at Heroku wrote down twelve rules for apps that run well in the cloud.
Factor three: **store configuration in the environment**. Code stays the same everywhere; ports, database addresses and
passwords come from environment variables. Docker, Kubernetes and every cloud platform follow it.

**.env files.** Many projects keep variables in a file called `.env`, loaded at start. Never commit it to Git (chapter
13 of the Git course): it is where secrets live.

**Seeing a process's environment.** On Linux, `/proc/PID/environ` holds the environment of a running process, with
names separated by zero bytes. That is also why secrets in environment variables are visible to root, and to the same
user's other processes: environment variables are convenient, not a vault.

**Aliases.** `alias ll='ls -alF'` makes a short name for a longer command; `type ll` shows what it really runs.
Aliases are for typing, in your terminal; scripts should use full commands.

**login and non-login shells.** A shell started at login reads `~/.profile`; a new terminal window reads `~/.bashrc`. On
Ubuntu, `~/.profile` also reads `~/.bashrc`, so putting your settings in `~/.bashrc` covers both.
:::

:::step{type=recap}
You can now:

- list environment variables with `printenv`, and explain `export`, and why copies only travel down to children;
- set a variable for one command (`PORT=9000 cmd`) and give defaults with `${NAME:-default}`;
- explain how PATH finds commands, use `which`, and add a folder to the front of PATH without breaking it;
- tell `source file` from `bash file`, and know where settings that should last belong (`~/.bashrc`).

Next, chapter 13: networking, from IP addresses and ports to talking to the observatory's app over HTTP.

:::photo{src="/lesson-images/linux/linux-12-notes.webp" alt="Handwritten notes about the environment: export: copies go down to children; PORT=9000 cmd; $(PORT:-8080) = default; PATH: folders searched in order; source file, not bash file" ai="true"}
One page of notes for this chapter.
:::
:::
