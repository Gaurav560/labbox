:::step{type=story title="Something is eating the processor"}
At two in the morning the dishes started missing their targets: the program that steers them reacts late, as if the
server were too busy to answer. It is. A test program someone left running is spinning in a loop, doing nothing useful,
and using a whole processor core while it does.

Every running program on Linux is a **process**. This chapter teaches you to see them, find the one that misbehaves,
and stop it, **politely first**, because a program stopped in the middle of writing a file can leave that file broken.
And you will learn the other side: starting a long job in the background, so it keeps working after you log out.

Railways solved "please stop" long before computers: a signal on a post, which the driver obeys. Linux talks to
processes the same way, with **signals**: short messages like "please finish up", "stop now", "your terminal has gone".

:::photo{src="/lesson-images/linux/railway-signals.webp" alt="Semaphore railway signals on a tall post beside a single railway line running along a sea wall" credit="Alan Hughes" license="CC BY-SA 2.0" source="https://commons.wikimedia.org/wiki/File:Railway_semaphore_signals_-_geograph.org.uk_-_6994272.jpg"}
Semaphore railway signals: one message, obeyed by the driver.
:::

:::mission
Write a script that stops a runaway program properly, and start the night report in the background.
:::
:::

:::step{type=concept title="Processes, PIDs and ps"}
When you run a program, the kernel makes a **process**: the running program, with its own memory and its own number,
the **PID** (process id). The process that started it is its **parent** (PPID). Your shell is a process; every command
you type becomes a child of it.

`ps` lists processes. With `-o` you choose the columns, and with `-C` you pick by name:

```text
$ cd /workspace/08-processes
$ ./hogger > /dev/null & sleep 2; ps -o pid,ppid,%cpu,%mem,etime,comm -C hogger; pgrep -x hogger; pkill -x hogger; sleep 0.3; pgrep -x hogger || echo "no hogger left"
[1] 2302
    PID    PPID %CPU %MEM     ELAPSED COMMAND
   2302    2289  100  0.0       00:02 hogger
2302
[1]+  Terminated              ./hogger > /dev/null
no hogger left
```

That one line did a lot, so here it is in order:

1. `./hogger > /dev/null &` started the runaway program **in the background** (the `&`); the shell printed its job
   number `[1]` and PID `2302`.
2. `ps` showed it: PID 2302, **100 percent** of one processor core, running for 2 seconds.
3. `pgrep -x hogger` printed the PIDs of every process named exactly `hogger`.
4. `pkill -x hogger` sent it a signal, and the shell reported it `Terminated`.

Other views you will use: `ps aux` (every process on the machine, with users), and **`top`**, a live screen sorted
by CPU, refreshed every few seconds (`q` quits; `htop` is a friendlier version):

```text
$ ./hogger & sleep 1; top -b -n 1 | head -9 | tail -3; kill %1
[1] 2337
    PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND
   2337 learner   20   0    4764   3540   3276 R 100.0   0.0   0:01.20 hogger
      1 learner   20   0    1108    764    720 S   0.0   0.0   0:00.02 docker-init
```

The runaway always floats to the top of `top`. On a real incident, that is where you look first.
:::

:::step{type=concept title="Signals: asking a process to stop"}
`kill` sends a **signal** to a process. Despite the name, most signals are requests:

| Signal | Number | Means | The process can |
|---|---|---|---|
| `TERM` | 15 | please finish and exit (what `kill` sends by default) | clean up first, or even ignore it |
| `INT` | 2 | interrupt (what **Ctrl+C** sends) | clean up first, or ignore it |
| `HUP` | 1 | hang-up: your terminal has closed | many servers reload their settings |
| `KILL` | 9 | stop now | **nothing**: the kernel ends it on the spot |
| `STOP` / `CONT` | 19 / 18 | pause / carry on (**Ctrl+Z** sends `TSTP`, a pause the program may catch) | nothing for STOP |

The order matters. **TERM first**: a well-written program closes its files, finishes the record it was writing, and
exits cleanly. **KILL only if it will not go**: KILL cannot be caught, so the program gets no chance to clean up, and
whatever it was half-way through writing stays half-written.

:::diagram{name="linux-signals"}
TERM asks; a good program cleans up and exits. Only a program that ignores TERM gets KILL a few seconds later.
:::

You can send a signal by PID (`kill 2302`, `kill -KILL 2302`), by name (`pkill -x hogger`), or to a background job by
its number (`kill %1`).

**Check yourself:** you press Ctrl+C in front of a running command. Which signal does it get? (INT, number 2.)
:::

:::step{type=example title="Worked example: a process that will not listen"}
`./hogger stubborn` is the same runaway, written to **ignore** TERM. Here is what an engineer sees:

```text
$ ./hogger stubborn & sleep 0.5; pid=$!; kill $pid; sleep 0.5; ps -o pid,comm -p $pid; kill -KILL $pid; sleep 0.3; ps -o pid,comm -p $pid || echo "gone"
[1] 2355
hogger: I ignore TERM
    PID COMMAND
   2355 hogger
[1]+  Killed                  ./hogger stubborn
    PID COMMAND
gone
```

1. `$!` is the PID of the last background command; the line saved it in a variable, `pid`.
2. `kill $pid` sent TERM. The program printed that it ignores it, and half a second later `ps` still showed it.
3. `kill -KILL $pid` did not ask. The shell reports `Killed`, and `ps` finds nothing.

That is the whole recipe every service manager follows: **TERM, wait a few seconds, then KILL what is left.** systemd
(chapter 14) waits 90 seconds by default; Docker waits 10.

One trap before you write it as a script. `pkill -f` and `pgrep -f` match the **whole command line**. A script called
`stop.sh` run as `bash stop.sh hogger` has `hogger` in its own command line, so `pkill -f hogger` would stop the script
itself. `-x` matches the exact **process name**, which is `bash` for your script and `hogger` for the runaway.
:::

:::step{type=predict title="Guess first"}
:::question
A program ignores TERM. You send KILL. Can it ignore that too?
:::
- [ ] Yes, if it is written to
- [x] No: KILL is handled by the kernel, and the program never sees it
- [ ] Only if it runs as root
:::explain
KILL and STOP are the two signals a process cannot catch or ignore. That is what makes KILL the last resort: it always
works, but the program gets no chance to save anything.
:::
:::

:::step{type=task task=stop_hog title="Your turn: stop.sh"}
Finish `stop.sh` in `/workspace/08-processes`. Given a process name as `"$1"`, it:

1. sends **TERM** to every process with exactly that name;
2. waits up to **3 seconds**, checking whether they are gone (`pgrep -x` succeeds while any are left; `sleep 0.5`
   waits half a second);
3. sends **KILL** to any that are still running.

It must never stop itself, or a process with another name. Try it: `./hogger &`, `./hogger stubborn &`, then
`bash stop.sh hogger`, then `pgrep -x hogger`. The check runs it on processes it starts itself. Press **Check**.
:::

:::step{type=concept title="Background jobs, and surviving a closed terminal"}
A command with `&` at the end runs in the **background**: the shell gives you the prompt back at once.

```text
$ sleep 300 & sleep 0.2; jobs; ps -o pid,stat,etime,cmd
[1] 2287
[1]+  Running                 sleep 300 &
    PID STAT     ELAPSED CMD
   2274 Rs+        00:00 ps -o pid,stat,etime,cmd
   2287 S          00:00 sleep 300
```

`jobs` lists this shell's background jobs. `fg` brings one back to the front; **Ctrl+Z** pauses the job in front, and
`bg` lets it carry on in the background.

There is a catch. When you close the terminal (or your connection to a server drops), the shell sends **HUP** to its
jobs, and by default HUP ends a process. Your two-hour job dies with your Wi-Fi. Two ways around it:

- `nohup command > file 2>&1 &`: **no hang-up**, the command ignores HUP, and its output goes to a file because there
  will be no terminal to show it on;
- `tmux` or `screen`: a terminal that keeps running on the server, which you can leave and come back to later.

And to wait for a background job inside a script, `wait $pid` waits until it ends and gives you its exit code:

```text
$ sleep 1 & wait $!; echo "exit $?"; sleep 30 & pid=$!; kill $pid; wait $pid; echo "exit $?"
[1] 2389
[1]+  Done                    sleep 1
exit 0
[1] 2390
[1]+  Terminated              sleep 30
exit 143
```

A process ended by a signal exits with 128 plus the signal's number: 143 is 128 + 15, TERM.
:::

:::step{type=task task=run_background title="Your turn: the night report in the background"}
`slow-report.sh` takes a few seconds, and on a real night it would take an hour. Finish `start-report.sh` so that it:

1. starts `./slow-report.sh` in the background, protected from a closed terminal;
2. sends **everything** it prints (both streams) into `report.log`;
3. writes its PID into `report.pid`;
4. comes back at once.

Try it: `bash start-report.sh`, then `cat report.pid`, `ps -p $(cat report.pid)`, and a few seconds later
`cat report.log`. Press **Check**.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why send TERM before KILL?
:::
- [ ] TERM is faster
- [x] TERM lets the program finish what it was writing and exit cleanly; KILL stops it mid-step
- [ ] KILL only works after TERM
:::explain
A database killed in the middle of a write may need a long recovery when it starts again, or lose the last changes.
Asking first costs a few seconds and saves hours.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
You start a long job with `./backup.sh &` and close your laptop. What happens to the job?
:::
- [ ] It keeps running: it was in the background
- [x] It most likely ends: the shell sends it HUP when the terminal closes
- [ ] It pauses until you come back
:::explain
`&` only frees the prompt. To survive a closed terminal, use `nohup` (or run it inside tmux, or as a service).
:::
:::

:::step{type=deep-dive title="Go deeper: /proc, load average, and money"}
**Every process is a folder.** The kernel shows each process as a folder in `/proc`, named by its PID:
`/proc/2302/cmdline` is its command line, `/proc/2302/status` its state and memory. `ps` and `top` simply read these
files. `pstree` draws the parent and child tree.

**Load average.** `uptime` and `top` show three numbers, like `load average: 1.64, 2.04, 2.70`: the average number of
processes running or waiting for the processor over the last 1, 5 and 15 minutes. Compare them with the number of cores
(`nproc`). On a 4-core machine, a load of 4 is fully busy; 8 means processes are queuing.

**Zombies.** A process that has ended but whose parent has not yet collected its exit code shows as `Z` (zombie) in
`ps`. It uses no CPU or memory, only a line in the table; it goes when the parent collects it or ends.

**Why it matters for money.** A runaway process at 100 percent of a core is not just slow for everyone else. On a cloud
server billed by the hour, or with automatic scaling that adds servers when CPU is high, a forgotten loop can quietly
cost more than the work the server was bought for. Teams set alerts on CPU and on processes that run too long for
exactly this reason.
:::

:::step{type=recap}
You can now:

- explain processes, PIDs and parents, and look at them with `ps`, `pgrep -x`, `top` and `htop`;
- send signals with `kill`, `pkill -x` and `kill %1`, and choose between TERM, INT, HUP and KILL;
- stop a program properly: TERM, wait, then KILL what is left, without matching your own script;
- run jobs in the background with `&`, `jobs`, `fg`, `bg`, keep them alive with `nohup`, and get a PID from `$!`.

Next, chapter 9: the disk is full at night, and permissions are wrong again.

:::photo{src="/lesson-images/linux/linux-08-notes.webp" alt="Handwritten notes about processes and signals: ps, top, pgrep -x name; TERM first, KILL last; Ctrl+C = INT; cmd & runs in the background; nohup survives a closed terminal" ai="true"}
One page of notes for this chapter.
:::
:::
