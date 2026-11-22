:::step{type=story title="The eclipse night"}
Tonight there is a total eclipse of the Moon, and half of Maharashtra wants to watch it with Tara. Schools have
projectors ready, and a news channel has put the observatory's live status on its website. At 21:40, thirty minutes
before the eclipse begins, Anjali calls you: "The status app is down. Nothing answers. Someone redeployed it this
afternoon, from a copy on a laptop. Please, tonight of all nights."

```text
$ cd /workspace/15-capstone
$ curl -s http://localhost:8090/health; echo "exit $?"
exit 7
```

Exit code 7: nothing is listening on port 8090. The app is not running at all.

This capstone has no worked example and no recipe. You have every tool you need: reading files (3), permissions (7),
processes (8), scripts (10), the environment (12), networking (13) and cron (14). The job is the one every on-call
engineer does: **look, read every error, fix one thing at a time, and check after each fix.** Then make sure it can
never stay down this long again.

:::photo{src="/lesson-images/linux/lunar-eclipse.webp" alt="The full Moon glowing red and orange during a total lunar eclipse, against a black sky" credit="Scott Taylor, U.S. Navy" license="Public domain" source="https://commons.wikimedia.org/wiki/File:US_Navy_041027-N-9500T-001_The_moon_turns_red_and_orange_during_a_total_lunar_eclipse.jpg"}
A total eclipse of the Moon: the Moon turns red.
:::

:::mission
Bring the observatory's app back on port 8090, then write a watchdog that restarts it whenever it falls over.
:::
:::

:::step{type=try title="Look before you touch"}
Start, as always, by looking. Here is everything the app needs, in one folder:

```text
$ ls
app  watchdog.sh
$ ls -l app
total 16
-rw-r--r-- 1 learner learner   70 Nov 22 18:29 app.env
-rw-r--r-- 1 learner learner 1225 Nov 22 18:29 server.py
-rw-r--r-- 1 learner learner  320 Nov 22 18:29 start.sh
---------- 1 learner learner  247 Nov 22 18:29 tonight.json
$ cat app/start.sh
#!/usr/bin/env bash
# start.sh: start the Tara observatory app in the background.
# Its output goes to logs/app.log and its process id to app.pid.
cd "$(dirname "$0")"
set -a; . ./app.env; set +a
nohup python3 server.py >> logs/app.log 2>&1 &
echo $! > app.pid
echo "Tara app started (PID $(cat app.pid)) on port $PORT"
$ cat app/app.env
# Settings for the Tara observatory app.
PORT=8090
APP_ENV=production
```

Read every line, slowly. Something in `ls -l` should already worry you, and `start.sh` names a file in a folder that
is not in the listing. (`set -a` exports every variable that `app.env` sets, so the app sees them: chapter 12.)
:::

:::step{type=concept title="How on-call engineers work"}
A calm, repeatable method beats cleverness at 21:40:

1. **Reproduce.** Run exactly what fails: here, `./start.sh` inside `app`, the way the deploy runs it.
2. **Read the error, all of it.** The first error is usually the real one; read Python errors from the bottom line up.
3. **Fix one thing.** Then run the same command again. One change at a time, so you always know what helped.
4. **Do not trust "started".** A script can print a cheerful message while the program behind it dies a second later.
   Check for real: `ps`, `ss -ltnp`, `curl`, and the app's own log.
5. **Write down what you found**, for the people who come after you.

Where to look, layer by layer:

| Question | Command |
|---|---|
| Can I even run it? | `ls -l`, then `./start.sh` |
| Did it start, and is it still running? | `cat app.pid`, `ps -p $(cat app.pid)` |
| What did it say before it died? | `tail logs/app.log` |
| Is it listening? | `ss -ltnp` |
| Does it answer correctly? | `curl -s localhost:8090/health`, `curl -s localhost:8090/tonight` |

There are **three** separate problems. Each one hides the next.
:::

:::step{type=predict title="Guess first"}
:::question
`start.sh` prints "Tara app started (PID 1367) on port 8090", but `curl` still gets no answer. What does that tell you?
:::
- [ ] curl is broken
- [x] The script started the app, but the app died right after; its log will say why
- [ ] The app needs a minute to warm up
:::explain
`start.sh` only launches the app in the background and prints a message; it never checks that the app stayed up. The
app's own errors go to `logs/app.log`. "Started" is a promise, not a fact.
:::
:::

:::step{type=task task=capstone_fix title="Your turn: bring Tara back"}
In `/workspace/15-capstone/app`, find and fix every problem, until:

- `./start.sh` runs without errors;
- `curl -s localhost:8090/health` answers `ok`;
- `curl -s localhost:8090/tonight` shows tonight's plan, with the Crab Nebula in it.

Do not change `server.py`: fix the server, not the code. The check copies your `app` folder and runs `./start.sh`
itself, so the fixes must be in the files, not only in your terminal. Press **Check**.
:::

:::step{type=concept title="Never again: a watchdog"}
Fixing it tonight is half the job. Apps crash: a bad request, a full disk, a power cut at the dish. A **watchdog** is a
small script, run every minute by cron, that checks the app and starts it again if it is down. On a real server,
systemd's `Restart=on-failure` (chapter 14) does this for services; a watchdog script is the same idea, and it can also
catch an app that is running but no longer answering.

What it needs, all from earlier chapters:

| Piece | From |
|---|---|
| ask `/health`, with a time limit, and act on the result | chapter 13's `curl` and chapter 10's `if` |
| start the app again | `app/start.sh` |
| a line in a log, with the date and time | `date '+%Y-%m-%d %H:%M:%S'` and `>>` |
| work from any folder, as cron starts it | `cd` to a full path first |
| do **nothing** when all is well | so a healthy night leaves an empty log |

The crontab line that runs it every minute would be:

```text
* * * * * /workspace/15-capstone/watchdog.sh
```
:::

:::step{type=task task=capstone_watch title="Your turn: watchdog.sh"}
Finish `watchdog.sh` in `/workspace/15-capstone`:

- if `http://localhost:8090/health` answers within 3 seconds with status 200, do **nothing** at all;
- otherwise run `app/start.sh` to start the app again, and add one line to `watchdog.log` in this folder:
  `YYYY-MM-DD HH:MM:SS restarted the app`.

It must work when started from any folder. Try it: stop the app (`pkill -f "python3 server.py"`), run
`cd / && bash /workspace/15-capstone/watchdog.sh`, check that the app answers, and run it again: the log should still
have one line. Press **Check**.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why did the app fail even after `start.sh` was executable and the `logs` folder existed?
:::
- [ ] The port was wrong
- [x] The app could not read `tonight.json`: its mode was `000`, so even its owner had no read permission
- [ ] Python was not installed
:::explain
The last line of the traceback in `logs/app.log` said `PermissionError: [Errno 13] Permission denied` on
`tonight.json`. A careless copy had stripped its permissions; `chmod 644` gives them back.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why must the watchdog do nothing at all when the app is healthy?
:::
- [ ] To save electricity
- [x] Run every minute, any extra start would launch a second copy (which fails on the busy port) and fill the log with noise
- [ ] cron requires it
:::explain
A check that runs 1,440 times a day must be quiet when all is well, so that the one line it writes means something:
the app fell over, at this time, and was brought back.
:::
:::

:::step{type=deep-dive title="Go deeper: where to go from here"}
You now know the Linux that most engineers use every day, and the habits that make on-call nights short. Some
directions for later:

**SSH.** Real servers are reached with `ssh user@address`, using a key pair (chapter 7's private key, `600`). `scp` and
`rsync` copy files to and from them.

**Packages.** `apt install nginx` (Ubuntu and Debian) or `dnf install nginx` (Fedora, Red Hat) installs software with all
it needs, and `apt upgrade` keeps it patched. Most break-ins use holes that already had a fix.

**Containers.** Docker and Kubernetes run apps in boxes like this lab's machine: every Linux idea in this course
(processes, signals, ports, environment variables, file permissions) works the same inside them.

**Monitoring.** Instead of a watchdog per app, teams collect numbers and logs from every server (Prometheus, Grafana,
Loki) and get an alert before users notice. The questions are still the ones you learned: is it up, is it slow, what
does the log say.

**Automation.** Tools like Ansible write down a server's whole setup (users, packages, permissions, services, cron jobs)
as files, so a new server is built in minutes and every server is the same.

**Your own server.** The best way to keep this knowledge is to use it: a cheap cloud server, or an old laptop with
Ubuntu Server, and something of your own to run on it.
:::

:::step{type=recap}
You can now:

- work an incident with a method: reproduce, read every error, fix one thing, verify for real, write it down;
- find problems layer by layer: permissions, missing folders, the app's own log, listening ports, HTTP answers;
- see that "started" is not "running", and check with `ps`, `ss -ltnp` and `curl`;
- keep an app alive with a quiet watchdog run by cron.

You have finished Linux on call: from your first `ls` to bringing an observatory back on the air on the night of an
eclipse. Well done.

:::photo{src="/lesson-images/linux/linux-15-notes.webp" alt="Handwritten notes about on call: 1. reproduce; 2. read every error; 3. fix one thing, check again; started is not running; a quiet watchdog" ai="true"}
One page of notes for this chapter.
:::
:::
