"""A citizen's conversation and the engineer's decision, both through the server (run langgraph dev first)."""
from langgraph_sdk import get_sync_client


def say(client, thread_id: str, text: str) -> dict:
    """Send a citizen's message; return the run's final state (with __interrupt__ if it paused)."""
    return client.runs.wait(thread_id, "harsh", input={"messages": [{"role": "user", "content": text}]})


def decide(client, thread_id: str, approve: bool, note: str = "") -> dict:
    """The engineer's answer to a paused repair: resume the thread's run with it."""
    return client.runs.wait(thread_id, "harsh", command={"resume": {"approve": approve, "note": note}})


def show(state: dict) -> None:
    if state.get("__interrupt__"):
        asked = state["__interrupt__"][0]["value"]
        print(f"  (waiting for the engineer: {asked['problem']} at {asked['street']}, Rs {asked['estimate']:,})")
    else:
        print(f"  Harsh: {state['messages'][-1]['content']}")


if __name__ == "__main__":
    client = get_sync_client(url="http://127.0.0.1:2024")
    thread = client.threads.create(metadata={"phone": "98220"})["thread_id"]
    for text in ["Any update on my complaints? My number is 98220.",
                 "Do we have to pay for the tanker? Water has been off since Monday because of the burst.",
                 "The main on Station Road has burst, water is flooding the road!"]:
        print(f"> {text}")
        show(say(client, thread, text))
    print("[engineer] approve, note: before the evening rush")
    show(decide(client, thread, True, "before the evening rush"))
