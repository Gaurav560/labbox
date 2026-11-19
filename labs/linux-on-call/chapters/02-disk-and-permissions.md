:::step{type=story title="No space left on device"}
:::character{name="Priya" role="Founder, Dabba Express"}
New alert: "disk 100% full". Orders cannot be saved. Someone left debug logging on last week.
And while you are in there: our deploy script will not run, and I think the secrets file is open
to everyone on the box.
:::

:::mission
Get disk space back without stopping the app, then fix the permissions for good.
:::
:::

:::step{type=concept title="Space and permissions"}
`du -sh *` shows how much space each file or folder in the current folder takes.
`find . -size +100k` lists files bigger than 100 KB.

A program that has a file **open** keeps writing to it. If you `rm` that file, the name disappears
but the space is only freed when the program closes it, often at a restart. `truncate -s 0 file`
empties it in place instead: same file, zero bytes.

`ls -l` shows permissions as three groups, **owner, group, others**:

```text
-rw-r--r--  deploy.sh     owner: read+write, everyone else: read
-rwx------  run.sh        owner: read+write+execute, nobody else anything
```

`chmod +x file` adds execute. `chmod 600 file` means read and write for the owner only.
:::

:::step{type=predict title="Guess first"}
:::question
The app is still running and writing to `debug.log`. You run `rm debug.log`. What happens to the disk space?
:::
- [ ] It is freed right away
- [x] It stays used until the app closes the file
- [ ] The app crashes and the space is freed
:::explain
The name is removed, but the app still holds the file open, so its data stays on disk (and keeps
growing) until the app restarts. That is why on-call engineers empty a live log instead of deleting it.
:::
:::

:::step{type=try title="Find what is big"}
```bash run
du -sh server/var/log/app/*
```

```bash run
ls -l server/bin server/config
```
:::

:::step{type=task task=free_disk title="Free the disk"}
One log in `server/var/log/app` is far bigger than the rest. **Empty it** (zero bytes) without
deleting it, and leave the other logs alone.
:::

:::step{type=task task=fix_perms title="Fix the permissions"}
Make `fix_perms.sh` fix any server folder you give it:

- every `.sh` file in `<folder>/bin` becomes **executable**;
- `<folder>/config/secrets.env` becomes **read and write for its owner only**.

```bash
bash fix_perms.sh server && ls -l server/bin server/config
```

The check runs it on a fresh copy with a script you have not seen, so do not list file names one by one.
:::

:::step{type=recap}
- `du -sh` and `find -size` find what fills a disk.
- Empty a live log with `truncate -s 0`; deleting it frees nothing while the app holds it open.
- Permissions are owner, group, others; `chmod +x` to run, `chmod 600` to keep secrets private.
:::
