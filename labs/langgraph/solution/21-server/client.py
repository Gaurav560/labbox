"""Talk to Harsh through the local server, the way a WhatsApp bridge or a web page would."""
import sys

from langgraph_sdk import get_sync_client


def ask(client, thread_id: str, text: str) -> str:
    """Send one message on a thread, wait for the run to finish, and return Harsh's answer."""
    state = client.runs.wait(thread_id, "harsh", input={"messages": [{"role": "user", "content": text}]})
    return state["messages"][-1]["content"]


if __name__ == "__main__":
    client = get_sync_client(url="http://127.0.0.1:2024")
    thread = client.threads.create(metadata={"phone": "98220"})
    for text in sys.argv[1:]:
        print(f"> {text}")
        print(f"  {ask(client, thread['thread_id'], text)}")
    saved = client.threads.get_state(thread["thread_id"])["values"]["messages"]
    print(f"(thread {thread['thread_id'][:8]}: {len(saved)} messages saved by the server)")
