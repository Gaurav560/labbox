:::step{type=story title="A telescope that never sleeps"}
In the hills near Pune there is a small radio telescope called **Tara**: three big metal dishes that listen to the
sky. Not with light, like a camera, but with radio waves, the faint hiss that stars, gas clouds and dead stars send
across space. Every night the dishes turn towards a list of targets, and a computer records what they hear, hour after
hour, until morning.

That computer is a **server**: a machine with no screen and no mouse, sitting in a cupboard, which people control from
far away by typing commands. Like almost every server on Earth, it runs **Linux**.

Anjali, the astronomer who runs Tara, has just given you an account on it. You have never typed a command in your life?
Perfect. By the end of this course you will read its logs, find anything in its folders, fix its permissions, stop a
runaway program, write scripts that work while you sleep, and bring the whole observatory back to life on a bad night.

Tara is a small cousin of the telescope in this photo: the Giant Metrewave Radio Telescope near Narayangaon, north of
Pune, thirty dishes like this one, each 45 metres across, all listening together. Its computers run Linux too.

:::photo{src="/lesson-images/linux/gmrt-dishes.webp" alt="A huge radio telescope dish made of white metal mesh on a concrete tower, standing in dry fields under a blue sky" credit="DesiBoy101" license="CC BY 4.0" source="https://commons.wikimedia.org/wiki/File:Closeup_of_one_GMRT_antenna.jpg"}
One dish of the Giant Metrewave Radio Telescope, near Pune.
:::

:::mission
Find your way around Tara's server: read its files, find a hidden one, and walk down to tonight's observing plan.
:::
:::

:::step{type=concept title="What Linux is, and why servers love it"}
A computer needs an **operating system**: the software that starts first and shares out the processor, the memory,
the disks and the network between all the programs. On a laptop that is usually Windows or macOS. On servers it is
almost always **Linux**.

Linux has two layers you should know by name:

1. The **kernel**: the heart, which talks to the hardware. "Linux" is, strictly, the name of the kernel.
2. The **tools** around it: hundreds of small programs (`ls`, `cp`, `grep`, and many more you will meet), plus the
   **shell**, the program that reads the commands you type and runs them. The shell in this course is **bash**.

Why do servers use Linux, and not the system on your laptop?

| Reason | What it means in practice |
|---|---|
| **It costs nothing** | No licence fee per machine. A company with 1,000 servers pays nothing for the operating system, where a paid server system costs hundreds to thousands of dollars per machine. |
| **It is light** | No desktop, no animations: a server spends its memory and processor on the real work. A small Linux server runs happily in 512 MB of memory. |
| **It is controlled by text** | Every task can be typed, so it can be done from far away over a slow link, and written into a script that does it again tomorrow, by itself. |
| **It is open** | Anyone can read the code, fix it and share the fix. Problems are found and solved by thousands of people. |
| **It runs everywhere** | The same commands work on a Raspberry Pi, a cloud server and a supercomputer. |

The numbers are striking. Since November 2017, **every one** of the 500 fastest supercomputers in the world runs
Linux. Most of the cloud runs on it, and so does every Android phone. Learn its commands once, and you can work on
almost any server you will ever meet.

**Check yourself:** what is the shell? (The program that reads the commands you type, runs them and shows you the
answer. Here it is bash.)
:::

:::step{type=history title="The story of Linux"}
Linux was started by a 21-year-old student who wanted a better system for his own computer, and gave it away.

:::before{title="Before Linux"}
In **1969**, at Bell Labs in the United States, **Ken Thompson** and **Dennis Ritchie** wrote an operating system
called **Unix**. Its ideas were simple and powerful: everything is a file, small tools each do one job, and tools can be
joined together. In 1973 they rewrote it in their new language, C, so it could move to other computers. Universities
and companies loved Unix, but it belonged to AT&T, and licences became expensive. In 1983 **Richard Stallman** began
**GNU**, a free replacement for Unix's tools, but its kernel was not ready. In 1987 a professor, Andrew Tanenbaum, wrote
**MINIX**, a small Unix for teaching, which students could study but not freely change and share.
:::

These are the two who started it all: Ken Thompson (left) and Dennis Ritchie, years after they wrote Unix.

:::photo{src="/lesson-images/linux/thompson-ritchie.webp" alt="Ken Thompson, with a long beard and glasses, and Dennis Ritchie, with a grey beard, smiling side by side" credit="Unknown photographer" license="Public domain" source="https://commons.wikimedia.org/wiki/File:Ken_Thompson_and_Dennis_Ritchie--1973.jpg"}
Ken Thompson and Dennis Ritchie, the creators of Unix.
:::

On **25 August 1991**, **Linus Torvalds**, a computer science student in Helsinki, posted a message: he was making
"a (free) operating system (just a hobby, won't be big and professional like gnu)" for his PC. He released the code,
people sent improvements, and in 1992 he chose the GNU licence, which keeps the code free for everyone forever.

:::solved
**A free Unix-like system for everyone.** Linus's kernel joined GNU's tools, and together they made a complete, free
system that anyone could use, study, change and share. Thousands of people worked on it over the internet. Companies
built products on it, and today Linux runs most of the world's servers, every Android phone, cars, televisions, routers
and all of the fastest supercomputers.
:::

Linus Torvalds in 2003, at a Linux conference in Australia. He still leads the kernel today.

:::photo{src="/lesson-images/linux/linus-torvalds.webp" alt="A young Linus Torvalds, smiling broadly, in a white polo shirt under a gum tree" credit="Alex Dawson (photo), Bff (crop)" license="CC BY-SA 2.0" source="https://commons.wikimedia.org/wiki/File:Linus_Torvalds,_2002,_Australian_Linux_conference2.jpg"}
Linus Torvalds in 2003, aged 33.
:::

:::timeline
- **1969** Ken Thompson and Dennis Ritchie write Unix at Bell Labs.
- **1983** Richard Stallman starts GNU, free versions of Unix's tools.
- **1991** Linus Torvalds releases the first Linux kernel.
- **1993** Debian, one of the first big Linux distributions, begins. Ubuntu, built on it, follows in 2004.
- **2008** The first Android phone: Linux in billions of pockets.
- **2017** All 500 of the world's fastest supercomputers run Linux.
:::

A **distribution** is Linux packaged with tools and an installer: Ubuntu, Debian, Fedora, Red Hat Enterprise Linux,
Alpine. Tara's server runs **Ubuntu 24.04**. The commands you learn here work on all of them.

:::usedby{title="Used for"}
- Web and app servers
- The cloud (AWS, Google Cloud, Azure)
- Phones (Android)
- Supercomputers and telescopes
- Routers, cars and televisions
:::

:::usedby{title="Used by"}
- Google, Amazon, Meta
- Netflix and Wikipedia
- NASA (even its Ingenuity helicopter on Mars)
- Stock exchanges
- Almost every startup
:::

:::funfact
Linux's mascot is a penguin called **Tux**. Linus once said he chose a penguin after a small one at a zoo in
Australia bit him, and he felt it should be a happy, well-fed one.
:::
:::

:::step{type=try title="Your first three commands"}
Open the terminal. You will see a line like this, waiting for you:

```text
learner@linux-on-call:/workspace$
```

That is the **prompt**. It tells you who you are (`learner`), which machine you are on (`linux-on-call`), and which
folder you are in (`/workspace`). The `$` means "type here". In this course, a line starting with `$ ` is a command for
you to type (without the `$`), and the lines after it are the answer.

Three commands to start. `pwd` (print working directory) says where you are. `ls` (list) shows what is in the folder.
`cat` shows what is inside a file:

```text
$ cd /workspace/01-why-linux
$ pwd
/workspace/01-why-linux
$ ls
tara
$ ls tara
README.txt  dishes  observations
$ cat tara/README.txt
Welcome to the Tara Observatory server.
Tara is a small radio telescope in the hills near Pune: three dishes that listen to the sky every night.
Each dish has a folder in dishes/, and every night's observing plan is in observations/.
```

The first line, `cd`, moved you into this chapter's folder; you will meet it properly in a moment. Notice that a command
can take a **name to work on** (`ls tara`, `cat tara/README.txt`). Notice too that most commands answer with nothing
but the facts: Linux tools are quiet unless they have something to say.
:::

:::step{type=concept title="Paths, folders and hidden files"}
Every file on Linux lives in one big tree of folders, which starts at `/`, called the **root**. There are no drive
letters like `C:`. Here is the top of Tara's tree:

```text
$ ls /
bin                boot  etc   lab  lib64  mnt  proc  run   sbin.usr-is-merged  sys  usr  workspace
bin.usr-is-merged  dev   home  lib  media  opt  root  sbin  srv                 tmp  var
```

A few you will visit in this course: `/etc` (settings), `/var/log` (logs), `/home` (each user's own folder), `/tmp`
(scratch space, emptied at restart), and `/workspace` (your work for this course).

:::diagram{name="linux-tree"}
One tree from the root, /. A path is the list of folders to walk through, joined by slashes.
:::

A **path** names a place in that tree:

| Path | Means |
|---|---|
| `/workspace/01-why-linux/tara` | **absolute**: starts with `/`, so it starts at the root. Works from anywhere. |
| `tara/dishes` | **relative**: starts from the folder you are in now. |
| `.` | this folder |
| `..` | the folder one level up |
| `~` | your home folder (`/home/learner`) |

`cd` (change directory) moves you. Here is a walk down and back up:

```text
$ cd tara; cd dishes; cd dish-1; pwd; cd ..; pwd; cd ../..; pwd; cd ~; pwd; cd -
/workspace/01-why-linux/tara/dishes/dish-1
/workspace/01-why-linux/tara/dishes
/workspace/01-why-linux
/home/learner
/workspace/01-why-linux
```

(The `;` lets you put several commands on one line.) `cd -` jumps back to where you were before.

**Hidden files.** A file whose name starts with a dot is **hidden**: plain `ls` leaves it out, to keep listings tidy.
Settings files are often hidden. `ls -a` (all) shows them:

```text
$ ls -a tara
.  ..  .welcome  README.txt  dishes  observations
```

`-a` is an **option**: a small switch that changes what a command does. `ls -l` (long) is another, which shows details:

```text
$ ls -l tara
total 4
-rw-r--r-- 1 learner learner 234 Nov 22 18:15 README.txt
drwxr-xr-x 5 learner learner 100 Nov 22 18:15 dishes
drwxr-xr-x 3 learner learner  60 Nov 22 18:15 observations
```

A `d` at the very start means a folder (directory); `-` means a plain file. Then come the permissions (chapter 7), the
owner, the size in bytes, and the date it last changed.

**Check yourself:** you are in `/workspace/01-why-linux/tara/dishes`. Where does `cd ..` take you? (To
`/workspace/01-why-linux/tara`.)
:::

:::step{type=task task=hidden_file title="Your turn: the hidden welcome note"}
Anjali left a hidden welcome note somewhere in the `tara` folder, with a secret word in it.

1. Find it and read it.
2. Save just the secret word into a file called `answer-hidden.txt` in `/workspace/01-why-linux`:

```bash
echo WORD > /workspace/01-why-linux/answer-hidden.txt
```

with the real word instead of WORD. (`echo` prints what you give it, and `>` sends that into a file instead of the
screen. Chapter 4 explains `>` properly.) Press **Check**.
:::

:::step{type=example title="Worked example: reading a dish's status"}
Here is how an operator finds out what dish 3 is doing, one step at a time:

```text
$ cd /workspace/01-why-linux
$ cd tara/dishes && pwd && ls
/workspace/01-why-linux/tara/dishes
dish-1  dish-2  dish-3
$ cat tara/dishes/dish-3/status.txt
Dish 3: under repair, back on Friday
```

1. `cd tara/dishes` used a relative path: from here, into `tara`, then into `dishes`. (`&&` runs the next command
   only if the one before it worked.)
2. `ls` showed three folders, one per dish.
3. `cat` with a longer path read the file directly, without moving there first. You can always give the whole path.

And when you mistype? Linux tells you, plainly:

```text
$ cd tara/Dishes
bash: cd: tara/Dishes: No such file or directory
```

Names on Linux are **case sensitive**: `Dishes` and `dishes` are two different names. Two habits save a lot of typing
and mistakes: press **Tab** to complete a name (type `cd ta`, press Tab, and it becomes `cd tara/`), and press the
**up arrow** to bring back the last command.
:::

:::step{type=predict title="Guess first"}
:::question
You are in `/workspace/01-why-linux/tara/dishes`. You type `cd ../observations`. Where are you now?
:::
- [ ] `/workspace/01-why-linux/tara/dishes/observations`
- [x] `/workspace/01-why-linux/tara/observations`
- [ ] Nowhere: the command fails, because you can only go up or down, not both
:::explain
`..` goes up to `tara`, then `observations` goes down into it. A path can go up and down in one go; `pwd` would confirm
it.
:::
:::

:::step{type=task task=deep_file title="Your turn: tonight's first target"}
Every night's observing plan is in a file called `plan.txt`, several folders deep inside `tara/observations`, in a
folder for each year, month and day.

1. Find tonight's plan (23 November 2026) and read it.
2. Save the name of the **first** target into `answer-target.txt` in `/workspace/01-why-linux` (a name with a space
   needs quotes: `echo 'Two Words' > ...`).

Press **Check**.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Which command shows the files whose names start with a dot?
:::
- [ ] `ls`
- [x] `ls -a`
- [ ] `cat -a`
:::explain
`-a` means all. Plain `ls` hides dot files to keep listings short; nothing on Linux is truly hidden from someone who
looks.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What is the difference between `/workspace/01-why-linux` and `01-why-linux`?
:::
- [x] The first starts at the root and works from anywhere; the second starts from the folder you are in
- [ ] None: Linux treats them the same
- [ ] The first is a file, the second a folder
:::explain
A path starting with `/` is absolute. Without the `/`, it is relative to where you are now, so it only works from
`/workspace`.
:::
:::

:::step{type=deep-dive title="Go deeper: terminal, shell, kernel, and asking for help"}
**Terminal, shell, kernel.** The **terminal** is the window that shows text. The **shell** (bash) reads what you type
and runs programs. The **kernel** actually runs them on the hardware. When you type `ls`, the shell finds the program
`/usr/bin/ls`, asks the kernel to run it, and shows you what it prints.

**Built into the shell.** A few commands are part of bash itself, not separate programs:

```text
$ type cd ls
cd is a shell builtin
ls is /usr/bin/ls
```

`cd` has to be built in: a separate program could not change the folder of the shell that started it.

**Asking for help.** Every command has a manual page: `man ls` (press `q` to leave it, space for the next page).
Most also print a short summary with `--help`:

```text
$ ls --help | head -3
Usage: ls [OPTION]... [FILE]...
List information about the FILEs (the current directory by default).
Sort entries alphabetically if none of -cftuvSUX nor --sort is specified.
```

Chapter 3 shows how to read man pages quickly.

**About this machine.** `uname -a` prints the kernel's version, and `cat /etc/os-release` names the distribution:

```text
$ cat /etc/os-release | head -2
PRETTY_NAME="Ubuntu 24.04.5 LTS"
NAME="Ubuntu"
```
:::

:::step{type=recap}
You can now:

- explain what Linux is (a kernel plus tools) and why servers use it: free, light, controlled by text, open;
- tell its story: Unix in 1969, GNU in 1983, Linus Torvalds in 1991, and Linux everywhere today;
- read the prompt, and use `pwd`, `ls`, `ls -a`, `ls -l`, `cd` and `cat`;
- use absolute and relative paths, `.`, `..`, `~` and `cd -`, and find hidden files.

Next, chapter 2: making, copying, moving and deleting files and folders.

:::photo{src="/lesson-images/linux/linux-01-notes.webp" alt="Handwritten notes about why Linux?: kernel + tools + the shell (bash); free, light, controlled by text; Unix 1969, Linus 1991; pwd, ls -a, cd .., cat; / is the root of one tree" ai="true"}
One page of notes for this chapter.
:::
:::
