:::step{type=story title="The change that sent brown water to the wrong team"}
A new developer at the board tidies up the desk graph. `TEAMS` looks redundant to them, so they shorten it, and every
example they try by hand still works: leaks go to the repair crew, bills to the billing office. They try no
brown-water complaint. Two days later a complaint about brown water near the district hospital sits with a repair crew
for 72 hours, when it needed a health team within 4.

Graphs are programs, and programs need **tests**: small pieces of code that run the graph on known inputs and check the
results, every time anything changes. The good news is that most of a graph is plain Python. Routers, reducers and
Python nodes are tested like any function; a model node is tested with a **fake model** that answers from a list; and a
pause for approval is tested with a checkpointer, like the real thing.

In this chapter you write the tests. The checks then do to your tests what the new developer did to the desk: they
plant a bug, and see whether your test notices.

:::mission
Write a test that proves dirty water goes to the health team, and a test that proves a big repair waits for the
engineer and a refusal ends the run, both strong enough to fail when the bug is planted.
:::
:::

:::step{type=history title="Bugs, tests and planted mistakes"}
:::before{title="Testing by trying things"}
Programmers checked their work by running it on a few inputs by hand, and stopped when the results looked right.
:::

On **9 September 1947** the operators of the Harvard Mark II found a moth trapped in a relay and taped it into the log
book: "first actual case of bug being found". The word was older, but the page became famous. Testing became a
discipline with Glenford Myers's **"The Art of Software Testing"** (**1979**), and everyday practice with Kent Beck's
**SUnit** (**1994**) and **JUnit** (**1997**): tests written as code, run in a second. In **1971** Richard Lipton
proposed **mutation testing**: change the program on purpose and see whether the tests notice. A test that still
passes after a planted bug is not testing that behaviour, which is exactly how this chapter's checks judge your tests.

:::solved
**Changes without fear.** Every rule of the desk is written down as a test, and a change that breaks one is caught in
seconds, not in a hospital ward.
:::

:::timeline
- **1947** The moth in the Mark II.
- **1971** Mutation testing proposed.
- **1979** "The Art of Software Testing".
- **1994 to 1997** SUnit and JUnit.
:::

The page from the Mark II log book, 9 September 1947, with the moth still taped to it.

:::photo{src="/lesson-images/langgraph/moth.webp" alt="A page of a squared log book with handwritten times and notes, a moth taped to it, and the line: First actual case of bug being found" credit="Naval Surface Warfare Center, Dahlgren" license="Public domain" source="https://commons.wikimedia.org/wiki/File:H96566k.jpg"}
The Harvard Mark II log, 9 September 1947.
:::
:::

:::step{type=concept title="A fake model, and a worked example" file="20-testing/test_desk.py" line="1-19"}
The desk takes its chat model as an argument (`build_graph(llm=None, ...)`), so a test can pass a fake one:

```python
def fake_llm():
    return GenericFakeChatModel(messages=iter([AIMessage("We have your complaint and will reply soon.")] * 5))

def test_small_repair_is_scheduled():          # given to you, as a worked example
    state = build_graph(fake_llm()).invoke({"text": "Pipe leaking near the gate", "estimate": 1200})
    assert state["team"] == "repair crew"
    assert state["reply"] == "We have your complaint and will reply soon."
```

`GenericFakeChatModel` answers each call with the next message from its list: no network, no cost, the same answer
every time. The test runs the **whole graph**, and asserts on the final state.

| What you test | How |
|---|---|
| a router or reducer | call the function with a small dict |
| a node | call it, or `app.nodes["route"].invoke(state)` on the compiled graph (we tried it: `{'team': 'health team'}`) |
| a model node | inject a fake model (`GenericFakeChatModel`, or a fake server like this course's checks) |
| a path through the graph | `invoke` on a known input, assert on the final state |
| a pause | a checkpointer, a thread id, then `Command(resume=...)` |
:::

:::step{type=task task=test_routes title="Your turn: a test for routing" file="20-testing/test_desk.py" line="21-24"}
Finish `test_dirty_water_goes_to_health`:

1. `state = build_graph(fake_llm()).invoke({"text": "Brown water from the tap", "estimate": 0})`;
2. `assert state["kind"] == "dirty_water"`;
3. `assert state["team"] == "health team"`.

The usual slip: stopping after step 2. That test passes on the broken desk too; the guess-first question below shows
it.

```bash run
cd /workspace/20-testing && python -m pytest -v
```

Press **Check**: it runs your test on the correct desk (it must pass) and on a desk where dirty water goes to the repair
crew (it must fail).
:::

:::step{type=concept title="Testing a pause" file="20-testing/test_desk.py" line="27-32"}
A test for an interrupt does what the engineer's app does:

```python
app = build_graph(fake_llm(), checkpointer=InMemorySaver())
config = {"configurable": {"thread_id": "J-1"}}
state = app.invoke({"text": "Pipe burst on Station Road", "estimate": 65000}, config)
assert state["__interrupt__"][0].value["estimate"] == 65000      # it asked
assert app.get_state(config).next == ("approval",)                 # it is waiting at the right node
state = app.invoke(Command(resume={"approve": False, "note": "no budget"}), config)
```

Then assert what a refusal must mean: the status says so, and **no reply** was written. Asserting what must **not**
happen is as important as asserting what must.

:::diagram{name="lg-mutation"}
The real pytest results (26 November): four tests, on the correct desk and with the planted bug.
:::
:::

:::step{type=task task=test_interrupts title="Your turn: a test for the pause" file="20-testing/test_desk.py" line="27-32"}
Finish `test_big_repair_waits_for_engineer` as above:

1. build the graph **with** `checkpointer=InMemorySaver()` and a thread id;
2. invoke it, and assert the interrupt's estimate and `app.get_state(config).next == ("approval",)`;
3. resume with `Command(resume={"approve": False, "note": "no budget"})`;
4. `assert state["status"] == "refused: no budget"` and `assert "reply" not in state`.

The usual slip: leaving out the checkpointer in step 1. The pause still happens, but the resume cannot find the
thread: chapter 10 showed the error, `RuntimeError: Cannot use Command(resume=...) without checkpointer`.

```bash run
cd /workspace/20-testing && python -m pytest -v
```

Press **Check**: the planted bug this time lets repairs up to Rs 5 lakh skip the engineer.
:::

:::step{type=try title="Three green tests, then one red"}
With both tests written:

```text
$ python -m pytest -v
...
test_desk.py::test_small_repair_is_scheduled PASSED                      [ 33%]
test_desk.py::test_dirty_water_goes_to_health PASSED                     [ 66%]
test_desk.py::test_big_repair_waits_for_engineer PASSED                  [100%]

============================== 3 passed in 0.19s ===============================
```

(We ran it again on 26 November: 3 passed in 0.19 s, and with the planted `TEAMS` change, the same single failure.)
Three tests in a fifth of a second: no model, no network. Now the new developer's change, `TEAMS = {"billing":
"billing office"}`, made by hand in `desk.py`:

```text
$ python -m pytest -q
...
    def test_dirty_water_goes_to_health():
        state = build_graph(fake_llm()).invoke({"text": "Brown water from the tap", "estimate": 0})
        assert state["kind"] == "dirty_water"
>       assert state["team"] == "health team"
E       AssertionError: assert 'repair crew' == 'health team'
E         
E         - health team
E         + repair crew

test_desk.py:24: AssertionError
=========================== short test summary info ============================
FAILED test_desk.py::test_dirty_water_goes_to_health - AssertionError: assert...
1 failed, 2 passed in 0.22s
```

(Both outputs are shortened with "...".) The change is caught before it reaches anyone, with the exact line and the
exact difference. Notice what did **not** catch it: the worked example and the pause test still passed, because they
never send brown water. Each rule needs its own test.
:::

:::step{type=predict title="Guess first"}
:::question
Your routing test asserts only `state["kind"] == "dirty_water"`. The bug is planted. What happens?
:::
- [ ] The test fails
- [x] The test passes: kind is still right; the bug is in the team, which nothing asserts
- [ ] pytest refuses to run
:::explain
We tried it: with the bug planted, that test passed ("1 passed in 0.17s"). A test only checks what it asserts. The check calls such a test too weak, because it passes with the bug.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why use a fake model in tests?
:::
- [x] Fast, free and the same every time, so a failure means the code changed, not the model's mood
- [ ] Real models cannot be tested
- [ ] Fakes are more accurate
:::explain
Test your graph's logic with fakes; judge the model's answers separately, with evaluations.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What does a planted bug (a mutation) tell you about a test?
:::
- [ ] Whether the code is fast
- [x] Whether the test would notice that kind of mistake
- [ ] Whether the model is good
:::explain
A test that passes on both the right and the wrong code protects nothing.
:::
:::

:::step{type=deep-dive title="Go deeper: testing graphs in production"}
**Run part of a graph.** `app.update_state(config, values, as_node="route")` followed by `invoke(None, config)` starts a
test from the middle; `interrupt_after=["triage"]` stops one after a node.

**Evaluations.** Tests check your code; evaluations check the model's behaviour on many real examples (the LangChain
course, chapter 26). LangSmith can run both on every change.

**Record real failures.** Every hand-over from chapter 14 and every wrong team is a test case waiting to be written.
:::

:::step{type=recap}
You can now:

- test routers, nodes and whole paths of a graph with pytest;
- replace the model with a fake one to keep tests fast and repeatable;
- test a pause and its resume with a checkpointer;
- judge a test by planting a bug and seeing whether it fails.

Next, chapter 21: running Harsh as a server.

:::photo{src="/lesson-images/langgraph/lg-20-notes.webp" alt="Handwritten notes titled Testing graphs, graphs are programs, test them: routers, reducers and Python nodes are tested like any function, a fake model answers model nodes from a list, and a pause is tested with a checkpointer and Command resume; fake model, invoke a known input, assert the final state, plant a bug, the right test fails; 3 tests in 0.19 seconds with no model and no network; with the planted bug only the routing test failed; a test of kind only passed with the bug; assert what must not happen too, no reply" ai="true"}
One page of notes for this chapter.
:::
:::
