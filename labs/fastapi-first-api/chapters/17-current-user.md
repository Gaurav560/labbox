:::step{type=story title="Who are you, and may you do that?"}
Meera can now sign in and get a token. But a token is worth nothing until every protected route checks it. And
checking **who** someone is answers only half the question. Meera is a clerk: she logs found items all day. Deleting
an item from the records is a supervisor's decision, Arjun's, because it cannot be undone.

Two separate questions, then, with two separate answers:

| Question | Name | When the answer is no |
|---|---|---|
| Who are you? | **authentication** | `401 Unauthorized`: sign in first |
| May you do this? | **authorisation** | `403 Forbidden`: you are known, and the answer is still no |

(HTTP's names are muddled for historical reasons: "401 Unauthorized" really means "not authenticated".)

:::mission
Make `get_current_user` check the token and find the staff member it names, then let only supervisors delete items.
:::
:::

:::step{type=concept title="Taking the token from the request" file="17-current-user/main.py" line="56"}
The app sends its token in a header, `Authorization: Bearer eyJ...`. FastAPI has a dependency that reads it:

```python
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
```

As a dependency, `oauth2_scheme` gives back the text after `Bearer `. With no `Authorization` header at all, it
answers by itself; we tried `GET /me` without one:

```text
HTTP/1.1 401 Unauthorized
www-authenticate: Bearer
...
{"detail":"Not authenticated"}
```

`tokenUrl="token"` tells `/docs` where to log in. Start this chapter's server from `/workspace/17-current-user` and
open `/docs`: there is now a green **Authorize** button. Type Meera's username and password there, and `/docs` will
send her token with every request you try.
:::

:::step{type=concept title="Checking the token" file="17-current-user/main.py" line="59-66"}
`oauth2_scheme` only finds the token. Checking it is your job, in `get_current_user`:

```python
payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
```

`jwt.decode` does three things at once: it checks the signature with the secret, checks that `exp` has not passed,
and gives back the payload as a dictionary, like `{"sub": "meera", "exp": 1795849484}`. When anything is wrong, it
raises. We tried three bad tokens:

| The token | `jwt.decode` raised |
|---|---|
| expired five minutes ago | `ExpiredSignatureError: Signature has expired` |
| not a token at all, `x.y.z` | `DecodeError: Invalid header padding` |
| payload changed to `"sub":"arjun"` | `InvalidSignatureError: Signature verification failed` |

All three are kinds of `InvalidTokenError`, so one `except InvalidTokenError:` catches them all. Then look up the
`sub`: a valid token for a user who has since been removed must fail too. Every failure becomes the same 401, with
`WWW-Authenticate: Bearer`. Press Play to see the whole chain:

:::diagram{name="fastapi-auth-check"}
Three dependencies in a row: take the token, check it and find the user, check the role; only then the route.
:::
:::

:::step{type=task task=current_user title="Your turn: get_current_user" file="17-current-user/main.py" line="59-62"}
Today `get_current_user` gives back Meera, whatever the token says. Make it decode the token, catch
`InvalidTokenError`, and find the staff member in `sub`; every failure gives 401 with `WWW-Authenticate: Bearer`.

`GET /me` then answers with the person the token names. With Meera's token, the solution answered:

```json
{"username":"meera","full_name":"Meera Joshi","desk":"Riverside","role":"clerk"}
```

(no `hashed_password`: the return type `StaffPublic` filters it, chapter 7's lesson). A token with one character
changed gave `401 {"detail":"Could not check who you are"}`. Then press **Check**: it tries a forged token, an expired
one, one for a user who does not exist, and a broken one.
:::

:::step{type=example title="Worked example: only your own desk"}
This is not in your project. A rule that depends on the user **and** the data: a clerk may change only the items
logged at their own desk.

```python
@app.patch("/items/{item_id}")
def update_item(item_id: int, changes: ItemUpdate, user: CurrentUser):
    item = find(item_id)
    if user["role"] != "supervisor" and item["desk"] != user["desk"]:
        raise HTTPException(status_code=403, detail="That item belongs to another desk")
    ...
```

1. `user: CurrentUser` runs the whole token check; inside the route, `user` is a known staff member.
2. The rule needs the item, so it lives in the route, not in a dependency.
3. 403, not 401: we know who they are, and the answer is still no.
:::

:::step{type=predict title="Guess first"}
:::question
Meera, a clerk with a valid token, sends `DELETE /items/1` once your next task is done. What does she get?
:::
- [ ] 401, because she is not allowed
- [x] 403, because she is known but not a supervisor
- [ ] 204, because her token is valid
:::explain
Her token proves who she is (no 401). Her role says no: 403 Forbidden. We saw exactly that:
`{"detail":"Only a supervisor can do this"}`.
:::
:::

:::step{type=task task=supervisor_only title="Your turn: supervisors only" file="17-current-user/main.py" line="69-72"}
Make `require_supervisor` answer 403 unless the current user's role is `supervisor`, and guard
`DELETE /items/{item_id}` with it (in the decorator's `dependencies`, as in chapter 11). Then:

- no token: 401;
- Meera (clerk): 403;
- Arjun (supervisor, password `airport-keys-77`): 204.

Press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
Which status fits a request whose token expired an hour ago?
:::
- [x] 401
- [ ] 403
- [ ] 404
:::explain
An expired token proves nothing about who is asking: authentication failed, so 401. The client should sign in again.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
Why does `require_supervisor` take `user: CurrentUser` instead of decoding the token itself?
:::
- [ ] It cannot import jwt
- [x] Dependencies can depend on dependencies: the token check is written once and reused
:::explain
FastAPI runs `oauth2_scheme`, then `get_current_user`, then `require_supervisor`, in that order, for one request.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
Arjun is removed from `STAFF`, but still holds a token that expires in 20 minutes. What should `GET /me` give?
:::
- [ ] His details, because the token is valid
- [x] 401, because the user it names no longer exists
:::explain
That is why `get_current_user` looks the user up after decoding: a valid signature is not enough.
:::
:::

:::step{type=deep-dive title="Go deeper: scopes, and signing out"}
**Scopes.** OAuth2 lets a token carry a list of permissions, its **scopes**, like `items:write`. FastAPI's "OAuth2
scopes" page shows `Security(...)` dependencies that demand a scope per route; useful when other companies' apps act
on your users' behalf.

**Signing out with JWTs.** The server keeps no list of tokens, so it cannot simply forget one. Ways out: keep tokens
short-lived; keep a small "denylist" of revoked token ids (a `jti` claim) until they expire; or change the secret to
sign everyone out.

**Disabled accounts.** Add a `disabled` field and refuse those users in `get_current_user`, so suspending someone
takes effect on their very next request.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Read a bearer token with `OAuth2PasswordBearer`, and use the **Authorize** button in `/docs`.
- Write `get_current_user`: decode with `jwt.decode`, catch `InvalidTokenError`, look the user up, or answer 401.
- Tell authentication (401) from authorisation (403), and write a role check as a dependency.
- Chain dependencies: the scheme, the current user, the role, then the route.

:::photo{src="/lesson-images/fastapi/fa-17-sketch.webp" alt="Sketchnote: Protecting routes. Authentication asks who you are; authorisation asks what you may do. Dependencies check both before the route. Flow: take the token from the header, decode: signature and expiry, find the user, check the role, the route runs. Remember: 401: we do not know who you are; 403: we know you, and the answer is no; Catch InvalidTokenError for every bad token; Look the user up after decoding." ai="true"}
One page of notes for this chapter.
:::

Next, chapter 18: `async`, `await`, and work that carries on after the answer has gone.
:::
