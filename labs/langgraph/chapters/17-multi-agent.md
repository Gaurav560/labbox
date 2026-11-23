:::step{type=story title="Two problems in one message"}
"My number is 98220. My August bill is Rs 2,400 instead of about Rs 600, and the meter outside is dripping."

That is two problems for two offices. Billing should check the meter readings and hold the bill; repairs should send a
crew for the dripping meter. One agent with every tool of every office could do both, but its prompt would grow with
every office's rules, and it would mix them up: a model with fifteen tools picks the wrong one more often than a model
with three.

The board works the other way: a **supervisor** reads the case and hands it to the right specialist, gets the report
back, and decides what is still missing. Each specialist is an agent with its own short prompt and its own few tools.
This is a **multi-agent** system, and in LangGraph it is a graph whose nodes are agents.

:::mission
Write the supervisor's routing with `Command`, then make each specialist report back to the supervisor under its own
name.
:::
:::

:::step{type=history title="A society of agents"}
:::before{title="One program that knows everything"}
Expert systems of the 1970s and 1980s put all their knowledge in one big set of rules, which became harder to change
with every rule added.
:::

In the **1970s** the **Hearsay-II** speech recogniser at Carnegie Mellon used a **blackboard**: separate specialist
programs (sounds, words, grammar) read and wrote one shared board, each adding what it knew. In **1986** Marvin Minsky's
book **"The Society of Mind"** argued that intelligence itself is many simple agents working together. Language-model
systems rediscovered the idea in **2023** (Microsoft's AutoGen, CrewAI, and others); in LangGraph, the shared state is
the blackboard, and `Command` is how one agent hands over to the next.

:::solved
**Small specialists, each easy to change**, and a supervisor that decides who acts next.
:::

:::timeline
- **1970s** Hearsay-II: specialists around a blackboard.
- **1986** "The Society of Mind".
- **2023** Multi-agent frameworks for language models.
:::

Marvin Minsky, who argued in 1986 that a mind is a society of many simple agents, each doing one small job.

:::photo{src="/lesson-images/langgraph/minsky.webp" alt="Marvin Minsky, an older man with glasses, seen in profile, looking down" credit="Joi Ito" license="CC BY 2.0" source="https://commons.wikimedia.org/wiki/File:Marvin_Minsky_(1).jpg"}
Marvin Minsky.
:::
:::

:::step{type=concept title="The supervisor routes with Command" file="17-multi-agent/team.py" line="37-42"}
The supervisor is one model call with structured output: who acts next, and why.

```python
class Route(BaseModel):
    next: Literal["billing", "repairs", "FINISH"]
    reason: str
```

The node turns that into a `Command`: go to the chosen specialist (and count the turn), or end the run on `FINISH`. A
turn limit (`MAX_TURNS`) ends it too, in case the supervisor never says FINISH. The graph has only one edge,
`START -> supervisor`; every other move is a `Command`, so the return types (`Command[Literal[...]]`) are what tell
LangGraph, and its diagram, where each node can go.
:::

:::step{type=task task=supervisor_route title="Your turn: the supervisor decides" file="17-multi-agent/team.py" line="37-42"}
Finish `supervisor`: return `Command(goto=END)` when `route.next == "FINISH"` or `state.get("turns", 0) >= MAX_TURNS`;
otherwise `Command(goto=route.next, update={"turns": state.get("turns", 0) + 1})`.

Press **Check**.
:::

:::step{type=concept title="Specialists report back" file="17-multi-agent/team.py" line="45-54"}
Each specialist is a `create_agent` agent (the LangChain course) with its own prompt and tools, wrapped in a node:

```python
def node(state):
    result = agent.invoke({"messages": state["messages"]})           # the agent's own loop, its own tools
    report = AIMessage(result["messages"][-1].content, name=name)     # only its final answer, signed
    return Command(goto="supervisor", update={"messages": [report]})
```

The specialist's tool calls stay inside its own run; the shared conversation gets one signed report. That keeps the
supervisor's context short, and the `name` tells it who said what.

:::diagram{name="lg-supervisor"}
The supervisor hands the case out and reads each report; the run ends when it says FINISH.
:::
:::

:::step{type=task task=specialist_report title="Your turn: report back" file="17-multi-agent/team.py" line="48-53"}
In `node`, return `Command(goto="supervisor", update={"messages": [report]})`.

```bash run
cd /workspace/17-multi-agent && python main.py
```

Press **Check**.
:::

:::step{type=try title="Two problems handled, and one handled twice"}
```text
$ python main.py
> My number is 98220. My August bill is Rs 2,400 instead of about Rs 600, and the meter outside is dripping.
  supervisor -> billing: The citizen's bill is significantly higher than expected, indicating a potential billing error that needs to be addressed first.
  supervisor -> repairs: The citizen reported a dripping meter, which indicates a potential leak that needs to be addressed by the repairs team.
  supervisor -> FINISH: All issues raised by the citizen have been addressed: the high bill is under review, and the dripping meter is scheduled for repair.
  [billing] I found that your August bill is Rs 2400, which is significantly higher than your previous bills averaging around Rs 600. I have held the bill until a meter inspector can check the meter, as it appears to be incorrect.
  [repairs] I have booked two visits for you: one for the dripping meter and another for the meter inspection due to the high bill. Both visits are scheduled for Thursday between 9:00 and 12:00.
```

The supervisor did its job: billing first, then repairs, then FINISH with a correct summary. Billing checked the bills
and readings with its tools and held the bill.

Now read the repairs report. It booked **two** visits: one for the dripping meter, and "another for the meter
inspection due to the high bill". That was billing's problem, already handled: billing had held the bill for a meter
inspector. Repairs read the **whole conversation**, including billing's report, and acted on everything it saw. Its
prompt even says "handle only repairs".

The fix is in what each specialist sees. Instead of the full conversation, the supervisor can send each specialist a
**task**: "Book a visit for the dripping meter at 98220's address." Shared context is convenient, and it is also how
one agent ends up doing another's work.
:::

:::step{type=predict title="Guess first"}
:::question
The supervisor's model keeps choosing "billing" and never says FINISH. What ends the run?
:::
- [ ] The billing agent
- [x] The `MAX_TURNS` check in the supervisor
- [ ] Nothing: it runs until the budget is gone
:::explain
Every loop that a model controls needs a limit in code, here 4 turns (and LangGraph's recursion limit behind it).
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why does a specialist add only its final answer to the shared messages?
:::
- [x] Its tool calls are its own business; the supervisor needs the result, and a short context
- [ ] Tool messages cannot be shared
- [ ] To save the specialist's memory
:::explain
Each agent keeps its working notes; the team shares conclusions.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why did repairs book a meter inspection?
:::
- [ ] Its tools were wrong
- [x] It saw the whole conversation, including billing's problem, and acted on it
- [ ] The supervisor told it to
:::explain
Give a specialist the task it should do, not everything the team knows.
:::
:::

:::step{type=deep-dive title="Go deeper: shapes of multi-agent systems"}
**Supervisor** (this chapter): one agent decides who acts. Easy to follow and to limit.

**Handoffs** (also called a swarm): each agent can pass control directly to another with a tool that returns
`Command(goto=..., graph=Command.PARENT)`, without a supervisor. Fewer calls, harder to follow.

**Hierarchies:** a supervisor of supervisors, each a subgraph (chapter 16), for large teams.

**Start with one agent.** Split into specialists when one prompt has grown too long or too many tools confuse it; every
extra agent is extra calls and extra places for work to be done twice.
:::

:::step{type=recap}
You can now:

- route between agents with a supervisor and `Command`;
- wrap an agent as a node that reports back under its own name;
- end a model-driven loop with a turn limit;
- keep specialists to their own task by choosing what they see.

Next, chapter 18: streaming progress and tokens to the citizen's screen.

:::photo{src="/lesson-images/langgraph/lg-17-notes.webp" alt="Handwritten notes about multi-agent systems: supervisor picks who acts; Command(goto=specialist); report back, signed; MAX_TURNS ends it; send a task, not everything" ai="true"}
One page of notes for this chapter.
:::
:::
