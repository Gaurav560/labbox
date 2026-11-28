:::step{type=story title="Whose key is it, anyway?"}
Since chapter 10, staff prove they are staff with a desk key in a header. It works, but think about what it really
says. Everyone at Riverside shares one key; when a clerk leaves, the key must change for everyone; and the logs can
never say **who** deleted an item, only "someone at Riverside".

Real services give each person their own account: a username and a password, checked once, and then a **token**
that the app sends with every request. Today Lostdesk stores passwords the right way (so that even Lostdesk cannot
read them) and hands out tokens.

:::mission
Make `hash_password`, `verify_password` and `authenticate` work with real password hashes, then add `POST /token`,
which checks a username and password and gives back a signed token.
:::
:::

:::step{type=history title="Why nobody stores passwords"}
In December 2009, attackers broke into RockYou, a company that made apps for social networks, and found 32 million
passwords stored as plain text. Every one of them could be read, and tried on other sites, since many people use one
password everywhere. The list still circulates.

The lesson every service learned: store a **hash**, never the password. A hash function turns a password into a fixed
string from which the password cannot be worked back. To check a login, hash what was typed and compare the hashes.

Hashing for passwords must also be **slow**, so that an attacker who steals the hashes cannot try billions of
guesses a second. In 2015 an open contest, the Password Hashing Competition, chose **Argon2** as its winner; it is
what `pwdlib`'s `PasswordHash.recommended()` uses, and what FastAPI's security tutorial uses.
:::

:::step{type=concept title="A hash, a salt, and a deliberate delay" file="16-security/main.py" line="16-28"}
We hashed Meera's password twice in the course image:

```text
$argon2id$v=19$m=65536,t=3,p=4$FO3xdmuoWFB2tCkFVz4h6w$rQ09aUESg4sHsAWkISJm/rCYry2s14w9QWlIZNRYlkw
$argon2id$v=19$m=65536,t=3,p=4$/+Mzs5CQC4H/KOFh4KN9AQ$foCIE0LSCB2vX04YpRuBVtGqI6qANxEFzEpCQ0bRKNI
```

Read one from the left: the algorithm (`argon2id`), its version, its cost settings (`m=65536` means 64 MB of memory,
`t=3` three passes, `p=4` four lanes), then a random **salt**, then the hash itself. Same password, two different
results, because each hash gets its own salt. That stops an attacker from building one big table of hashes of
common passwords and looking them all up at once.

```python
password_hash = PasswordHash.recommended()

password_hash.hash("riverside-umbrella-42")              # a new hash, with a new salt
password_hash.verify("riverside-umbrella-42", stored)    # True or False
```

`verify` reads the salt and settings out of the stored hash, hashes the typed password the same way, and compares.
Each hash took about 46 ms on the lab machine: nothing for one login, a wall for an attacker trying billions.
:::

:::step{type=concept title="Unknown users take as long" file="16-security/main.py" line="44-48"}
`authenticate` has one subtle line in the solution:

```python
user = STAFF.get(username)
if user is None:
    verify_password(password, DUMMY_HASH)   # take as long as a real check
    return None
```

Without it, a login for a username that does not exist would answer at once, while a real username with a wrong
password would take 46 ms to verify. An attacker could time the answers and learn which usernames exist. Checking
against a dummy hash makes both cases take as long. FastAPI's tutorial does exactly this.
:::

:::step{type=task task=hash_passwords title="Your turn: real hashes" file="16-security/main.py" line="19-27"}
Make `hash_password` and `verify_password` use `password_hash`, and make `authenticate` give back the staff member
when the password matches their `hashed_password`, and `None` otherwise (checking `DUMMY_HASH` for unknown usernames).
`STAFF` hashes its passwords with your `hash_password` when the file loads, so they become real hashes too.

Meera's password is `riverside-umbrella-42`; Arjun's is `airport-keys-77`. (They are written in this lesson so you
can try them; in a real service no one would ever see them.) Then press **Check**.
:::

:::step{type=concept title="A token is a ticket"}
Checking a password costs 46 ms, and sending it with every request would expose it every time. So Lostdesk checks it
**once** and gives back a **token**: proof that the check happened.

Railways solved the same problem in the 1840s with the Edmondson ticket: a small printed card with a serial number.
The gate does not phone the booking office to ask whether you paid; it trusts the ticket, because only the railway
could print one.

:::photo{src="/lesson-images/fastapi/edmondson-tickets.webp" alt="A dozen small card railway tickets in cream, orange and yellow, laid out in rows; each has station names printed on it and a serial number on both ends" credit="Roberto Fiadone" license="CC BY-SA 3.0" source="https://commons.wikimedia.org/wiki/File:Boletos_Edmondson_Tren_Mitre.jpg"}
Edmondson-type tickets of the Mitre railway in Argentina, each with its serial number.
:::

Lostdesk's tokens are **JWTs** (JSON Web Tokens, a standard since 2015, RFC 7519). We logged Meera in and took her
token apart. It has three parts separated by dots; the first two are just JSON, encoded:

```text
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJtZWVyYSIsImV4cCI6MTc5NTg0OTQ4NH0.5eVL8yL0_uVl1amcMZUDkz_ji10IjTui7yFF7FVEilo

{"alg":"HS256","typ":"JWT"}        the header: how it is signed
{"sub":"meera","exp":1795849484}   the payload: who it is about, and when it expires (seconds since 1970)
```

The third part is the **signature**: a code worked out from the first two parts and Lostdesk's `SECRET_KEY`. Change
one letter of the payload (`"sub":"arjun"`) and the signature no longer matches; nobody without the secret can make
a new one. Note what that does **not** mean: the payload is encoded, not hidden. Anyone holding a token can read it,
so never put a password or a phone number in one.
:::

:::step{type=concept title="The login form" file="16-security/main.py" line="59-61"}
How does the username and password arrive? FastAPI's security tools follow **OAuth2** (RFC 6749, 2012), the standard
behind "sign in" on most of the web. Its simplest form, the "password flow", sends them as **form fields** named
`username` and `password`, which FastAPI reads with one dependency:

```python
@app.post("/token")
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    ...   # form.username, form.password
```

The answer is a `Token`: `{"access_token": "...", "token_type": "bearer"}`. "Bearer" means "whoever bears (holds)
this token is let in", just like a ticket. Press Play:

:::diagram{name="fastapi-login-token"}
The password is checked once against its hash; a signed token with an expiry goes back, and travels with every later request.
:::

A wrong login answers 401 with the header `WWW-Authenticate: Bearer`, which tells a client how it is meant to
authenticate. With the solution:

```text
$ curl -s -X POST localhost:8000/token -d "username=meera&password=riverside-umbrella-42"
{"access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJtZWVyYSIsImV4cCI6MTc5NTg0OTQ4NH0.5eVL8yL0_uVl1amcMZUDkz_ji10IjTui7yFF7FVEilo","token_type":"bearer"}

$ curl -s -i -X POST localhost:8000/token -d "username=meera&password=wrong"
HTTP/1.1 401 Unauthorized
www-authenticate: Bearer
...
{"detail":"Wrong username or password"}
```

The message does not say **which** of the two was wrong, for the same reason as the dummy hash.
:::

:::step{type=predict title="Guess first"}
:::question
Someone reads Meera's token. What can they learn from it, without the secret key?
:::
- [ ] Nothing: it is encrypted
- [x] Her username and when the token expires
- [ ] Her password
:::explain
The payload is only encoded (base64), so anyone can read it. The signature stops them from **changing** it, not from
reading it.
:::
:::

:::step{type=task task=login_token title="Your turn: POST /token" file="16-security/main.py" line="59-61"}
Add `POST /token`: read the form with `OAuth2PasswordRequestForm`, call `authenticate`, and give back a `Token` with
`create_access_token(...)` and `"bearer"`; a wrong username or password gives 401 with `WWW-Authenticate: Bearer`.

Start this chapter's server from `/workspace/16-security` and open `/docs`: a green **Authorize** button has not
appeared yet (that comes with chapter 17's protected routes), but `POST /token` shows its form fields. Try it, then
press **Check**: it decodes your token with `SECRET_KEY` and looks for `sub` and `exp`.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
Why does the same password give a different hash each time?
:::
- [ ] Argon2 is random and cannot be checked
- [x] Each hash has its own random salt, stored inside it
:::explain
The salt is part of the stored string, so `verify` can reuse it. Different salts stop precomputed tables of hashes.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
What stops someone from changing `"sub":"meera"` to `"sub":"arjun"` in a token?
:::
- [ ] The payload is encrypted
- [x] The signature would no longer match, and only the server knows the secret to make a new one
:::explain
Chapter 17's decoding checks the signature first; a changed token is refused.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
A login fails. Why does Lostdesk say "Wrong username or password" instead of "No such user"?
:::
- [ ] It is shorter
- [x] So an attacker cannot learn which usernames exist
:::explain
The same reason `authenticate` checks a dummy hash for unknown users: give nothing away.
:::
:::

:::step{type=deep-dive title="Go deeper: the secret, expiry, and HTTPS"}
**The secret key.** Anyone with `SECRET_KEY` can make tokens for any user. In this chapter it sits in the code so you
can see it; a real service reads it from the environment (chapter 19) and makes it with a command like
`openssl rand -hex 32`. Changing it signs everyone out at once, which is sometimes exactly what you want.

**Expiry.** A stolen token works until its `exp`. Short lives (Lostdesk: 30 minutes) limit the damage; many services
add a longer-lived **refresh token** to get new access tokens without typing the password again.

**HTTPS, always.** Passwords and bearer tokens travel in the request. Without HTTPS, anyone on the same network could
read them. In production, the proxy in front of Lostdesk serves HTTPS.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Explain why services store password hashes, and what Argon2's salt and slowness are for.
- Hash and verify passwords with `pwdlib`, and keep an unknown user's login as slow as a known one's.
- Read a JWT's three parts, and explain what its signature does and does not protect.
- Write an OAuth2 password-flow login, `POST /token`, that gives back a bearer token or a 401.

:::photo{src="/lesson-images/fastapi/fa-16-sketch.webp" alt="Sketchnote: Passwords and tokens. Store a slow, salted hash of each password, never the password. After one check, give back a signed token. Flow: username and password, verify against the hash, sign a token: sub and exp, the app keeps the token, Authorization: Bearer token. Remember: Argon2 adds a random salt to every hash; Unknown users are checked against a dummy hash too; A JWT is signed, not hidden: anyone can read it; Wrong login: 401 with WWW-Authenticate: Bearer." ai="true"}
One page of notes for this chapter.
:::

Next, chapter 17: checking that token on every request, and deciding what each person may do.
:::
