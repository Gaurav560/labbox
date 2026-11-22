:::step{type=story title="Is it up?"}
Tara has a small app that tells the world what the dishes are doing: ask it for `/tonight` and it answers with tonight's
plan; ask it for `/health` and it answers `ok` if all is well. The website and the schools' science displays ask it
every minute.

Most questions on call are network questions in disguise. "The site is down": is the app running? Is it **listening**?
On which **port**? Does it answer, and with what? Engineers answer these in seconds with four tools: `ss`, `curl`, `nc`
and a little knowledge of how computers find each other.

A hundred years ago, telephone calls were connected by hand. An operator took your call and plugged a cable into the
socket of the person you wanted: one switchboard, hundreds of sockets, each leading to someone. A server works much the
same: one address, and many numbered **ports**, each with a program listening behind it.

:::photo{src="/lesson-images/linux/switchboard.webp" alt="A long row of telephone operators in the 1940s, sitting at a switchboard full of sockets and cables" credit="U.S. National Archives" license="Public domain" source="https://commons.wikimedia.org/wiki/File:Photograph_of_Women_Working_at_a_Bell_System_Telephone_Switchboard_(3660047829).jpg"}
Telephone operators at a switchboard.
:::

:::mission
Start the observatory's app, fetch tonight's plan from it over HTTP, and write a health check script that answers UP or
DOWN.
:::
:::

:::step{type=concept title="Addresses, ports and localhost"}
Three ideas carry all of server networking:

1. An **IP address** names a machine on a network, like `10.0.0.12` or `142.250.183.46`. Names like `example.com` are
   turned into addresses by **DNS**, the internet's phone book.
2. A **port** is a number from 1 to 65535 that picks one program on that machine. Well-known ones: **22** for SSH,
   **80** for HTTP, **443** for HTTPS, **5432** for PostgreSQL. Apps often use **8080** or **8000** while developing.
3. **localhost**, address `127.0.0.1`, means "this machine itself". Traffic to it never leaves the computer.

A program that waits for connections is **listening** on a port; a program that connects is a **client**. Only one
program can listen on a given port at a time.

:::diagram{name="linux-ports"}
One address, many ports. Each port leads to one listening program; a client names both: address and port.
:::

`ip -brief address` lists this machine's network cards and their addresses:

```text
$ ip -brief address
lo               UNKNOWN        127.0.0.1/8 ::1/128 
eth0@if16271     UP             10.88.255.242/28 
$ curl -s https://example.com; echo "exit $?"
exit 6
```

`lo` is the loopback, localhost. `eth0` is a network card on a small private network of your own (your address will be
different). That network has no way out to the internet, on purpose, so your work stays private: exit code 6 from
curl means "could not resolve the host". A real server's `eth0` would lead to the internet through a router.

**Check yourself:** an app listens on port 5432. What is it, most likely? (PostgreSQL.)
:::

:::step{type=try title="Start the app, and see it listen"}
`ss` (socket statistics) lists listening ports: `-l` listening, `-t` TCP, `-n` numbers instead of names, `-p` which
process. First with nothing running, then with the app started in the background:

```text
$ cd /workspace/13-networking
$ ss -ltn
State     Recv-Q     Send-Q          Local Address:Port           Peer Address:Port     Process     
$ python3 server.py 8080 > /tmp/server.log 2>&1 & sleep 1; ss -ltnp
[1] 866
State      Recv-Q     Send-Q         Local Address:Port           Peer Address:Port     Process     
LISTEN     0          5                    0.0.0.0:8080                0.0.0.0:*         users:(("python3",pid=866,fd=3))
```

The app (`python3`, PID 866) is **LISTEN**ing on port **8080**. `0.0.0.0` means "on every address of this machine".
On a real incident this one command answers "is anything listening on the port, and which program is it?".

Try to start a second copy, and Linux refuses:

```text
$ python3 server.py 8080
Traceback (most recent call last):
  File "/workspace/13-networking/server.py", line 31, in <module>
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/socketserver.py", line 457, in __init__
    self.server_bind()
  File "/usr/lib/python3.12/http/server.py", line 136, in server_bind
    socketserver.TCPServer.server_bind(self)
  File "/usr/lib/python3.12/socketserver.py", line 473, in server_bind
    self.socket.bind(self.server_address)
OSError: [Errno 98] Address already in use
```

Read a Python error from the **bottom**: the last line is what went wrong. **Address already in use** means another
program holds the port: `ss -ltnp` tells you which one.
:::

:::step{type=concept title="HTTP with curl"}
**HTTP** is how browsers and apps talk to web servers: the client sends a request ("GET /tonight"), the server sends
back a **status code** (chapter 5's 200, 404, 500) and a **body**. `curl` is HTTP from the terminal:

```text
$ curl http://localhost:8080/health
ok
$ curl -i http://localhost:8080/health
HTTP/1.0 200 OK
Server: BaseHTTP/0.6 Python/3.12.3
Date: Sun, 22 Nov 2026 18:27:00 GMT
Content-Type: text/plain
Content-Length: 3

ok
```

With `-i`, curl shows the **headers** too: the status line `200 OK`, then facts about the answer, then an empty line,
then the body. For scripts, the status code alone is what matters:

```text
$ curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8080/health
200
$ curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8080/nothing
404
$ curl -s -o /dev/null -w "%{http_code}\n" http://localhost:9999/health; echo "exit $?"
000
exit 7
```

| Option | Does |
|---|---|
| `-s` | silent: no progress bar |
| `-o FILE` | write the body to FILE (`/dev/null` throws it away) |
| `-w "%{http_code}"` | print the status code at the end |
| `-f` | fail (exit code 22) on an error status like 404 or 500 |
| `--max-time 3` | give up after 3 seconds |

Nothing listening on port 9999: curl got no answer at all, prints `000` as the code, and exits with 7, "could not
connect".

**Check yourself:** what does `curl -s -o /dev/null -w "%{http_code}"` print for a server that answers "500 Internal
Server Error"? (`500`.)
:::

:::step{type=task task=fetch_tonight title="Your turn: fetch tonight's plan"}
In `/workspace/13-networking`:

1. Start the app in the background, listening on port **8080** (if one is already running, `ss -ltnp` shows it).
2. Fetch `http://localhost:8080/tonight` with curl, and save the answer's **body** into `tonight-fetched.json`.

`head -3 tonight-fetched.json` should show the start of a JSON object. Press **Check**.
:::

:::step{type=example title="Worked example: reading JSON answers"}
Most APIs answer in **JSON**, text that holds structured data. `jq` picks values out of it:

```text
$ curl -s http://localhost:8080/tonight | jq -r ".targets[].name"
Crab Nebula
Orion Nebula
Jupiter
```

1. `.targets` is the list of targets; `[]` goes through each one; `.name` takes its name.
2. `-r` prints plain text, without JSON's quotes.

And the app keeps its own access log, like chapter 5's, one line per request:

```text
$ head -7 /tmp/server.log
Tara observatory app listening on port 8080
127.0.0.1 "GET /health HTTP/1.1" 200 -
127.0.0.1 "GET /health HTTP/1.1" 200 -
127.0.0.1 "GET /tonight HTTP/1.1" 200 -
127.0.0.1 "GET /health HTTP/1.1" 200 -
127.0.0.1 code 404, message No such page
127.0.0.1 "GET /nothing HTTP/1.1" 404 -
```

Three ways to ask "is it up?", each a step deeper: `ss -ltn` (is something listening?), `nc -zv localhost 8080` (can I
connect to the port?), and `curl` (does it answer correctly?). A health check needs the last one: an app can be
listening and still answering 500 to everyone.
:::

:::step{type=predict title="Guess first"}
:::question
The app is running but every request gets status 500. What does plain `curl -s http://localhost:8080/health` do?
:::
- [x] Prints the error body and exits with 0: to curl, any answer is a success
- [ ] Exits with an error code
- [ ] Prints nothing
:::explain
curl's exit code says whether the conversation worked, not whether the answer was good. Check the status code with
`-w "%{http_code}"`, or use `-f` to make error statuses fail.
:::
:::

:::step{type=task task=health_check title="Your turn: health.sh"}
Finish `health.sh` in `/workspace/13-networking`. Given an address as `"$1"`:

- if it answers with status **200** within **3 seconds**, print `UP` and exit with 0;
- otherwise (nothing listening, an error status, too slow), print `DOWN` and exit with 1.

Try it with the app running and stopped: `bash health.sh http://localhost:8080/health`,
`bash health.sh http://localhost:8080/nothing`. The check also tests a slow server. Press **Check**.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
`curl` says "Failed to connect to localhost port 8080: Connection refused" (exit code 7). What does that tell you?
:::
- [ ] The app is answering with an error
- [x] Nothing is listening on port 8080: the app is not running, or listens on another port
- [ ] The internet is down
:::explain
"Connection refused" comes from the machine itself: there is no program behind that port. `ss -ltnp` shows what is
listening and where.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why does a health check need a time limit like `--max-time 3`?
:::
- [ ] curl is slow without it
- [x] A server that hangs would make the check hang too, and a stuck check reports nothing at all
- [ ] HTTP needs it
:::explain
Slow is a kind of down. A check that gives up after a few seconds turns "hanging" into a clear DOWN that can raise an
alarm.
:::
:::

:::step{type=deep-dive title="Go deeper: DNS, firewalls and the internet's plumbing"}
**DNS.** `example.com` becomes an address by asking DNS servers. `dig example.com` or `getent hosts example.com` shows
the answer; `/etc/hosts` can override names on one machine. Many mysterious outages are DNS problems.

**TCP and the handshake.** HTTP travels over **TCP**, which first sets up a connection with three small messages, then
delivers every byte in order, resending what gets lost. Since 1 January 1983, when the ARPANET switched to TCP/IP, it
has been the base of the internet.

**Firewalls.** A server usually allows only a few ports from outside (22, 80, 443) and blocks the rest, with `ufw`,
`nftables` or the cloud provider's security groups. An app listening on `0.0.0.0` is reachable from outside only if the
firewall lets that port through; one listening on `127.0.0.1` is reachable only from the machine itself.

**Ports below 1024** have traditionally needed root to listen on. That is one reason apps listen on 8080 and a web
server like nginx, started as root and then dropping its rights, sits on 80 and 443 in front of them.

**Speed.** A request to localhost takes well under a millisecond:

```text
$ curl -s -o /dev/null -w "%{time_total}\n" http://localhost:8080/health
0.000564
```

Across a city it takes a few milliseconds, between continents a hundred or more. Each extra round trip is felt by users,
which is why big sites put copies of their pages close to people (a CDN).
:::

:::step{type=recap}
You can now:

- explain IP addresses, DNS, ports, localhost and listening, and name the well-known ports;
- see what listens where with `ss -ltnp`, and recognise "Address already in use" and "Connection refused";
- talk HTTP with `curl` (`-i`, `-s`, `-o`, `-w "%{http_code}"`, `-f`, `--max-time`) and read JSON with `jq`;
- write a health check that turns any failure, including a slow answer, into DOWN.

Next, chapter 14: running the app as a proper service, its logs with journalctl, and jobs on a schedule with cron.

:::photo{src="/lesson-images/linux/linux-13-notes.webp" alt="Handwritten notes about networking: address picks the machine; port picks the program; ss -ltnp: who listens?; curl -w '%(http_code)'; refused = nothing listening" ai="true"}
One page of notes for this chapter.
:::
:::
