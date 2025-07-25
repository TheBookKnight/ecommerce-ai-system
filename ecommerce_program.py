import asyncio
import weave
import sys
import config

from agents import Runner
from ecommerce_agents import triage_agent

weave.init(project_name=config.WEAVE_PROJECT)

@weave.op()
async def run_agent(prompt: str):
    response = await Runner.run(triage_agent, prompt)
    return response.final_output

@weave.op()
async def ecommerce_ai():
    print("Starting E-Commerce program...")
    await asyncio.sleep(1.5)  # Give Weave a moment to finish printing (TODO: need a more graceful way to wait)
    sys.stdout.flush()  # Ensure all prints are flushed before user input
    print("Welcome to the E-Commerce AI System! How can I assist you today?")
    print("Type 'exit' or 'quit' to leave at any time.")
    previous_response_id = None
    cur_agent = triage_agent
    while True:
        user_in = input("> ")
        if user_in.strip().lower() in {"exit", "quit", "q"}:
            print("Thank you for using the E-Commerce AI System. Goodbye!")
            break
        response = await Runner.run(
            cur_agent, user_in, previous_response_id=previous_response_id
        )
        previous_response_id = response.last_response_id
        cur_agent = response.last_agent
        print(f"[{cur_agent.name}] {response.final_output}")

if __name__ == "__main__":
    asyncio.run(ecommerce_ai())