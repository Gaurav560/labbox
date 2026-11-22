:::step{type=story title="It said Deployed. It was not."}
The observatory's website is deployed with a small script: build the pages, copy them into the live folder. Last week
the build failed, and the script did not care: it carried on, copied the half-built site, and printed **Deployed**.
For a day, schools saw a broken page about tonight's sky.

Look at what it does today, with a build that fails:

```text
$ cd /workspace/10-scripts
$ BUILD_FAILS=1 TARGET=live bash deploy.sh; echo "exit $?"
build: error: tonight.html is not valid
Deployed to live
exit 0
```

An error, then "Deployed", then exit code 0, which means success. Every tool that runs this script believes it. And it
gets worse: run it without the `TARGET` setting, and it tries to delete `/site`, at the very root of the disk.

This chapter is about writing scripts that **check** things and **stop** when something is wrong. A space launch
works the same way: before lift-off, every station answers "go" or "no go", and a single "no go" holds the countdown.

:::photo{src="/lesson-images/linux/launch-control.webp" alt="Rows of engineers at consoles in a large launch control room during a countdown test" credit="NASA" license="Public domain" source="https://commons.wikimedia.org/wiki/File:Firing_Room_3_of_Launch_Control_Center,_Launch_Complex_39_countdown_test_(S69-34332).jpg"}
A launch control room: one "no go" stops the countdown.
:::

:::mission
Write a script that checks a file and reports with the right exit code, and make the deploy script stop at the first
failure.
:::
:::

:::step{type=concept title="Variables, quotes and arguments"}
A script is commands in a file, plus a few things that make it a program. First, **variables**: a name, `=`, a value,
with **no spaces** around the `=`. Read it back with `$`:

```text
$ target=Jupiter; echo "Tonight: $target"; echo 'Tonight: $target'
Tonight: Jupiter
Tonight: $target
```

**Double quotes** keep the text together but still fill in variables. **Single quotes** take everything literally.

Quotes matter most for values with spaces. Without them, the shell splits the value into separate words:

```text
$ file="star list.txt"; touch "$file"; ls -l $file; ls -l "$file"; rm "$file"
ls: cannot access 'star': No such file or directory
ls: cannot access 'list.txt': No such file or directory
-rw-r--r-- 1 learner learner 0 Nov 22 18:24 'star list.txt'
```

The rule professionals follow: **always write `"$variable"`, in double quotes**, unless you have a reason not to.

**Arguments** are the words after the script's name. Inside the script they are `$1`, `$2` and so on; `$#` is how many
there are, `"$@"` is all of them, and `$0` is the script's own name:

```text
$ bash /tmp/args.sh Jupiter "Crab Nebula"
name of script: /tmp/args.sh
first: Jupiter, second: Crab Nebula
how many: 2
all: Jupiter Crab Nebula
```

Two more ways to make a value: `$(command)` puts in what a command prints, and `$(( ))` does arithmetic:

```text
$ today=$(date +%Y-%m-%d); echo "Report for $today"
Report for 2026-11-22
$ n=3; echo $((n * 15)) minutes
45 minutes
```
:::

:::step{type=concept title="Exit codes, tests and if"}
Every command ends with an **exit code** (chapter 4): `0` for success, anything else for failure. Scripts decide what
to do next by looking at it. **`[ ... ]`** is a command whose whole job is to test something and set the exit code:

```text
$ [ -e build.sh ]; echo $?; [ -e nothere ]; echo $?
0
1
```

| Test | True when |
|---|---|
| `[ -e FILE ]` | the file exists |
| `[ -f FILE ]` / `[ -d FILE ]` | it is a plain file / a folder |
| `[ -s FILE ]` | it exists and is not empty |
| `[ "$a" = "$b" ]` | two texts are equal (`!=` for not equal) |
| `[ "$n" -gt 5 ]` | a number is greater than 5 (`-lt`, `-eq`, `-ge`, `-le`) |
| `[ ! -e FILE ]` | `!` turns any test around |

The spaces inside the brackets are required: `[` is a command, and its parts are its arguments.

`if` runs a block when a command succeeds:

```bash
if [ -s report.txt ]; then
  echo "report ready"
elif [ -e report.txt ]; then
  echo "report is empty" >&2
  exit 2
else
  echo "no report" >&2
  exit 1
fi
```

Inside a script, `exit N` ends it with exit code N, and `>&2` sends a message to standard error, where problems belong.
For one-line decisions, `&&` runs the next command only on success, and `||` only on failure:

```text
$ test -s site/index.html && echo "not empty"
not empty
$ ls nothere 2>/dev/null || echo "no such file, carrying on"
no such file, carrying on
```

**Check yourself:** what exit code does `[ -e /etc/passwd ]` give? (0: the file exists, so the test succeeds.)
:::

:::step{type=task task=check_file title="Your turn: check_file.sh"}
Finish `check_file.sh` in `/workspace/10-scripts`. Given a file name as `"$1"`:

| The file | Print | Where | Exit code |
|---|---|---|---|
| exists and is not empty | `OK: NAME` | standard output | 0 |
| does not exist | `MISSING: NAME` | standard error | 1 |
| exists but is empty | `EMPTY: NAME` | standard error | 2 |

(NAME is the name as given.) Names may contain spaces. Try `bash check_file.sh deploy.sh; echo $?`, then a name that
does not exist, then `touch "empty one.txt"` and that. Press **Check**.
:::

:::step{type=history title="One missing variable"}
In January 2015 a Linux user reported that running Steam, the popular games app, had **deleted every file he owned**,
including his backups on an external disk. The cause was one line in its shell script:

```bash
rm -rf "$STEAMROOT/"*
```

The script set `STEAMROOT` by working out where it lived. When that went wrong, `STEAMROOT` was **empty**, the line
became `rm -rf "/"*`, and it started deleting everything the user was allowed to delete. One comment in the script, just
above it, read: "Scary!"

:::solved
**Make the shell refuse.** Two lines at the top of a script prevent this whole class of accident: `set -u` turns the
use of an unset variable into an error that stops the script, and `${VAR:?message}` stops with a message when a
variable is empty. Careful scripts also check a path before they delete anything under it.
:::

Bash has been the default shell of Linux since the early 1990s. Its name is a pun: the "Bourne Again SHell", a free
rewrite of Stephen Bourne's 1979 Unix shell, written by Brian Fox for GNU in 1989.
:::

:::step{type=example title="Worked example: strict mode"}
By default, bash carries on after a failing command. Three options change that, and most professional scripts start
with all of them:

| Option | Means |
|---|---|
| `set -e` | stop the script when a command fails |
| `set -u` | an unset variable is an error (no silent empty values) |
| `set -o pipefail` | a pipeline fails if **any** command in it fails, not just the last |

Written together: `set -euo pipefail`. Here each one at work:

```text
$ bash /tmp/e.sh; echo "exit $?"
step 1
exit 1
```

(`/tmp/e.sh` turns on all three, prints `step 1`, runs `false`, a command that always fails, then would print
`step 2`.) It stopped at the failure and passed the failure on: exit code 1.

```text
$ bash -c "set -u; echo \"target: \$TARGET\""; echo "exit $?"
bash: line 1: TARGET: unbound variable
exit 127
$ bash -c "set -o pipefail; false | true; echo \"pipe exit \$?\""; bash -c "false | true; echo \"pipe exit \$?\""
pipe exit 1
pipe exit 0
```

With `-u`, an unset `TARGET` stops the script instead of becoming an empty string. And without `pipefail`, a pipeline
whose first command failed still "succeeds", because only the last command's exit code counts.

Now look at the deploy script once more. Without `TARGET`, today, it does this:

```text
$ bash deploy.sh; echo "exit $?"
build: 2 pages built
cp: cannot create directory '/site': Permission denied
Deployed to 
exit 0
```

It ran `rm -rf /site` (harmless here only because a normal user may not delete at the root), failed to copy, and still
said Deployed. Strict mode turns all of that into one clear stop.
:::

:::step{type=predict title="Guess first"}
:::question
A script starts with `set -euo pipefail`. Its third line, `./build.sh`, fails with exit code 1. What happens to line 4?
:::
- [ ] It runs, and the script exits 1 at the end
- [x] It never runs: the script stops at line 3 and exits with code 1
- [ ] It runs, because set -e only applies to pipelines
:::explain
`set -e` ends the script at the first command that fails (outside an `if`, `&&` or `||`, where failing is expected), and
the script's exit code tells whoever ran it that something went wrong.
:::
:::

:::step{type=task task=safe_deploy title="Your turn: a deploy that stops"}
Fix `deploy.sh` in `/workspace/10-scripts`:

1. When the build fails, it must **stop** before copying anything, and exit with a failure code.
2. When `TARGET` is not set, it must **refuse to run** (and never reach the `rm`).
3. A normal deploy, `TARGET=live bash deploy.sh`, must still work.

Try all three: `BUILD_FAILS=1 TARGET=live bash deploy.sh`, `bash deploy.sh`, and `TARGET=live bash deploy.sh`, with
`echo $?` after each. Press **Check**.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why write `"$1"` instead of `$1`?
:::
- [ ] It is faster
- [x] Without quotes, a name with spaces is split into several words, and each becomes a separate argument
- [ ] `$1` only works for numbers
:::explain
`ls $1` with `star list.txt` becomes `ls star list.txt`: two files, neither of which exists. `"$1"` keeps it one name.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Your script prints an error message but ends with `exit 0`. Why is that a problem?
:::
- [ ] It is not: the message is enough
- [x] Other programs (cron, CI, other scripts) see 0 and believe it succeeded
- [ ] Exit codes only matter on Windows
:::explain
People read messages; programs read exit codes. A failure must be both: a message on standard error, and a non-zero
exit code.
:::
:::

:::step{type=deep-dive title="Go deeper: shebangs, functions and checking your scripts"}
**The shebang.** `#!/usr/bin/env bash` on line one lets you run a script directly (`./deploy.sh`, once it has `x`).
`env` finds bash wherever it is installed. A script written for `sh` (`#!/bin/sh`) must avoid bash-only features: on
Ubuntu `sh` is `dash`, a smaller, faster shell.

**Functions** give a few lines a name, and take arguments like a script does:

```bash
die() { echo "error: $*" >&2; exit 1; }
[ -d "$TARGET" ] || die "no folder $TARGET"
```

**Defaults and required values.** `${PORT:-8080}` means PORT, or 8080 when it is empty or unset (chapter 12).
`${TARGET:?TARGET is not set}` stops the script with that message when TARGET is empty.

**Check your scripts automatically.** `shellcheck` reads a script and points out missing quotes, unset variables and
many classic traps, before they bite. Many teams run it on every change.

**When to stop writing bash.** For more than about a hundred lines, or anything with complex data, a language like
Python is easier to read and test. Bash is perfect for gluing commands together.
:::

:::step{type=recap}
You can now:

- use variables (no spaces around `=`), double quotes, `$1`, `$#`, `"$@"`, `$(command)` and `$(( ))`;
- test files and values with `[ ]`, and branch with `if`, `elif`, `else`, `&&` and `||`;
- report problems properly: a message on standard error with `>&2`, and a non-zero `exit`;
- write in strict mode, `set -euo pipefail`, and know the accident it prevents.

Next, chapter 11: loops, so one script can do the same thing to a thousand files.

:::photo{src="/lesson-images/linux/linux-10-notes.webp" alt="Handwritten notes about shell scripts: name=value (no spaces); always '$quote' variables; [ -e file ] && echo yes; errors: echo ... >&2; exit 1; set -euo pipefail" ai="true"}
One page of notes for this chapter.
:::
:::
