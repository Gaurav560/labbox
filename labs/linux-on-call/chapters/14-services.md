:::step{type=story title="It should run without you"}
So far, every program on Tara's server ran because you started it. That cannot last. The status app must start by
itself when the server boots, come back by itself if it crashes at 3 a.m., and keep its logs somewhere you can read
them later. The nightly backup must run at 02:30 whether anyone is awake or not. A weekly report must go out every
Monday morning.

Linux has two tools for this, on almost every server you will ever touch. **systemd** starts and looks after
long-running programs, called **services**. **cron** runs commands on a **schedule**. You describe what you want in a
small text file, and they do it, every day, for years.

Railways run on the same idea: a timetable, written once, and trains that leave at the minute it says, every day,
whoever is on duty.

:::photo{src="/lesson-images/linux/station-clock.webp" alt="The clock tower of Mysore Junction railway station, with its round clock above the station's name" credit="Christopher J. Fynn" license="CC BY-SA 4.0" source="https://commons.wikimedia.org/wiki/File:Mysore_Junction_railway_station_clocktower.jpg"}
The clock tower of Mysore Junction railway station.
:::

:::mission
Write the systemd unit that runs the observatory's app as a service, and the crontab with its three scheduled jobs.
:::
:::

:::step{type=concept title="Services and systemd"}
When a Linux server boots, the kernel starts one program first, with PID 1, and that program starts everything else.
On almost every modern distribution, PID 1 is **systemd**. It starts services in the right order, restarts them when
they crash, collects their output in a journal, and stops them cleanly (TERM, a pause, then KILL, from chapter 8).

You control it with `systemctl`:

| Command | Does |
|---|---|
| `systemctl status tara` | is it running? since when? its last log lines |
| `systemctl start tara` / `stop` / `restart` | start, stop or restart it now |
| `systemctl enable tara` | start it at every boot (`disable` undoes it) |
| `systemctl daemon-reload` | read changed unit files again |
| `journalctl -u tara` | its logs (`-f` to follow, `--since "1 hour ago"`) |

On a real Ubuntu server, a healthy service looks like this:

```text
$ systemctl status cron --no-pager
● cron.service - Regular background program processing daemon
     Loaded: loaded (/usr/lib/systemd/system/cron.service; enabled; preset: enabled)
     Active: active (running) since Sat 2026-11-21 10:22:07 IST; 1 day 13h ago
 Invocation: cbbb8ac93ab64f2190a407d110b5cf16
       Docs: man:cron(8)
   Main PID: 1946 (cron)
      Tasks: 1 (limit: 18183)
     Memory: 2M (peak: 6.2M, swap: 152K, swap peak: 156K)
        CPU: 489ms
     CGroup: /system.slice/cron.service
             └─1946 /usr/sbin/cron -f -P
```

`enabled` (starts at boot), `active (running)` for 1 day 13 hours, its main PID, and how much memory it uses.

This lab's machine is a **container**, a lightweight box inside a bigger server, and containers usually run without
systemd:

```text
$ ps -o pid,comm -p 1
    PID COMMAND
      1 docker-init
```

So in this chapter you write the files exactly as on a real server, and the check reads them the way systemd and cron
would.
:::

:::step{type=example title="Worked example: reading a real unit file"}
A service is described by a **unit file**, a small text file with sections in square brackets and `Key=value` lines.
This is the real unit of the cron service on Ubuntu:

```text
$ cat /usr/lib/systemd/system/cron.service
[Unit]
Description=Regular background program processing daemon
Documentation=man:cron(8)
After=remote-fs.target nss-user-lookup.target

[Service]
EnvironmentFile=-/etc/default/cron
ExecStart=/usr/sbin/cron -f -P $EXTRA_OPTS
IgnoreSIGPIPE=false
KillMode=process
Restart=on-failure
SyslogFacility=cron

[Install]
WantedBy=multi-user.target
```

1. **[Unit]**: what it is (`Description`), and what must start before it (`After`).
2. **[Service]**: how to run it. `ExecStart` is the command, always with **full paths**, because systemd does not use
   your PATH. `Restart=on-failure` brings it back if it crashes.
3. **[Install]**: when to start it if it is enabled. `multi-user.target` is the normal running state of a server,
   reached at the end of every boot.

Two keys this one does not need but an app does: `User=` (which user it runs as: never root for an app) and
`WorkingDirectory=` (the folder it starts in). And `Environment=NAME=value` sets an environment variable (chapter 12)
for it. Your own units go in `/etc/systemd/system/`.
:::

:::step{type=task task=unit_file title="Your turn: tara.service"}
Write `tara.service` in `/workspace/14-services`, for the observatory's app on the real server:

| Section | Setting |
|---|---|
| [Unit] | `Description` of your choice; start after `network.target` |
| [Service] | run as the user `tara`, in the folder `/srv/tara` |
| [Service] | the environment variable `APP_ENV` set to `production` |
| [Service] | the command `/usr/bin/python3 /srv/tara/server.py 8080` |
| [Service] | restart it when it fails |
| [Install] | wanted by `multi-user.target` |

Press **Check**.
:::

:::step{type=concept title="cron: commands on a timetable"}
`cron` reads **crontabs**, tables of jobs, and runs each job when its time comes. Every line is five time fields, then the
command:

```text
# minute  hour  day-of-month  month  day-of-week  command
  30      2     *             *      *            /srv/tara/backup.sh
```

| Field | Values | Notes |
|---|---|---|
| minute | 0 to 59 | |
| hour | 0 to 23 | 24-hour clock |
| day of month | 1 to 31 | |
| month | 1 to 12 | or `jan` to `dec` |
| day of week | 0 to 7 | 0 and 7 are Sunday, 1 is Monday; or `mon` to `sun` |

In any field: `*` means every value, `1,15` a list, `1-5` a range (Monday to Friday), and `*/10` every tenth value.

:::diagram{name="linux-cron"}
Five fields, read from left to right: minute, hour, day of the month, month, day of the week. A job runs when all five match.
:::

A few to read: `0 * * * *` is every hour, on the hour. `0 9 * * 1-5` is 09:00 on weekdays. `*/15 * * * *` is every 15
minutes. `0 0 1 * *` is midnight on the first of every month.

`crontab -e` edits your own crontab, and `crontab -l` lists it. A cron job runs with almost no environment: a short
PATH, no `~/.bashrc`, and its starting folder is your home. So in a crontab, **use full paths** for every program and
file. Its output, if any, is mailed to you or lost; redirect it into a log: `... >> /var/log/tara/backup.log 2>&1`.

**Check yourself:** what does `0 18 * * 5` mean? (Every Friday at 18:00.)
:::

:::step{type=predict title="Guess first"}
:::question
Which line runs a job every Monday at 09:00?
:::
- [ ] `9 0 * * 1`
- [x] `0 9 * * 1`
- [ ] `0 9 1 * *`
:::explain
Minute first, then hour: `0 9` is 09:00. The day of the week is the last time field, and Monday is 1. `0 9 1 * *`
would mean 09:00 on the first day of every month.
:::
:::

:::step{type=task task=cron_lines title="Your turn: Tara's crontab"}
Add three jobs to `crontab.txt` in `/workspace/14-services`, one line each, with full paths:

1. `/srv/tara/backup.sh` every day at **02:30**;
2. `/srv/tara/report.sh` every **Monday** at **09:00**;
3. `/srv/tara/health.sh` every **5 minutes**.

Press **Check**.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
A script works when you run it by hand, but fails from cron with "command not found". What is the most likely cause?
:::
- [ ] cron cannot run bash scripts
- [x] cron's PATH is much shorter than yours, so the script must use full paths (or set PATH itself)
- [ ] The script needs `sudo`
:::explain
cron starts jobs with a minimal environment. Full paths like `/usr/bin/curl`, or a `PATH=...` line at the top of the
crontab, fix it.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
You changed `ExecStart` in `/etc/systemd/system/tara.service`. What do you run before restarting the service?
:::
- [x] `systemctl daemon-reload`, so systemd reads the changed file
- [ ] Nothing: systemd watches the file
- [ ] `systemctl enable tara`
:::explain
systemd keeps unit files in memory. After editing one, `daemon-reload`, then `systemctl restart tara`. `status` warns you
when a unit changed on disk and was not reloaded.
:::
:::

:::step{type=deep-dive title="Go deeper: timers, backups with tar, and how init came to be"}
**systemd timers** are the modern alternative to cron: a `.timer` unit next to a `.service` unit. Ubuntu itself uses
them, for example to download package updates twice a day:

```text
[Unit]
Description=Daily apt download activities

[Timer]
OnCalendar=*-*-* 6,18:00
RandomizedDelaySec=12h
Persistent=true

[Install]
WantedBy=timers.target
```

`Persistent=true` runs a missed job after the machine was off; `RandomizedDelaySec` spreads millions of machines over
twelve hours, so they do not all hit the download servers at once. `systemctl list-timers` shows them all.

**What a backup job usually does.** `tar` packs a folder into one compressed file:

```text
$ tar czf /tmp/targets.tar.gz -C ../02-files targets && ls -lh /tmp/targets.tar.gz && tar tzf /tmp/targets.tar.gz
-rw-r--r-- 1 learner learner 343 Nov 22 18:28 /tmp/targets.tar.gz
targets/
targets/this-week.txt
targets/tonight.txt
targets/special/
targets/special/eclipse.txt
```

`c` create, `z` compress, `f` the file name; `t` lists what is inside, and `x` unpacks. A real backup job adds the
date to the name (`$(date +%F)`), copies the file to another machine, and deletes copies older than a few weeks. And a
backup nobody has ever restored is only a hope: test restoring it.

**A short history of init.** Unix's first program, `init`, ran a list of shell scripts at boot, one after the other.
As servers grew, booting got slow and services had no one to restart them. **Upstart** (Ubuntu, 2006) and **systemd**
(Lennart Poettering and Kay Sievers, 2010) started services in parallel and watched over them. By 2015 most big
distributions had moved to systemd. `cron` itself dates from Unix in the 1970s; the version most Linux systems use was
written by Paul Vixie in 1987.
:::

:::step{type=recap}
You can now:

- explain what systemd does as PID 1, and use `systemctl` (`status`, `start`, `stop`, `restart`, `enable`,
  `daemon-reload`) and `journalctl -u`;
- read and write a unit file: `[Unit]`, `[Service]` with `ExecStart`, `User`, `WorkingDirectory`, `Environment`,
  `Restart`, and `[Install]`;
- read and write crontab lines, with `*`, lists, ranges and `*/N`, and remember that cron needs full paths;
- know where timers and `tar` backups fit in.

Next, chapter 15, the capstone: the observatory's app is down on the night of an eclipse, and you are on call.

:::photo{src="/lesson-images/linux/linux-14-notes.webp" alt="Handwritten notes about services and cron: systemctl status / restart; journalctl -u name; ExecStart needs full paths; min hour day month weekday; */5 = every 5 minutes" ai="true"}
One page of notes for this chapter.
:::
:::
