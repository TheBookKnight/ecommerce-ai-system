import asyncio

import weave
from agents import Agent, Runner, function_tool

import config

weave.init(project_name=config.WEAVE_PROJECT)

@function_tool
def search_items(query: str):
    return f"Search results for '{query}': Item001 - Pikachu Plush, Item002 - Charmander Figure"

@function_tool
def add_to_cart(item_id: str):
    return f"Item {item_id} added to cart"

@function_tool
def place_order(user: str):
    return f"Order placed for {user}. Ref: ORD-9001"

@function_tool
def get_order_status(order_id: str):
    return f"Order {order_id} is in transit"

@function_tool
def submit_refund(order_id: str, reason: str):
    return f"Refund for {order_id} submitted due to: {reason}. Ref: RFD-102"

@function_tool
def get_store_faq(topic: str):
    return {
        "shipping": "We ship within 3-5 business days.",
        "returns": "You can return items within 30 days of delivery.",
        "gift cards": "Gift cards are valid for 1 year after purchase.",
    }.get(topic.lower(), "Sorry, we don't have info on that topic.")

shopping_agent = Agent(
    name="Shopping Agent",
    instructions=(
        "1. greet user\n"
        "2. use search_items to fetch options\n"
        "3. ask user to choose one\n"
        "4. confirm item and use add_to_cart to add to cart\n"
        "5. offer further help"
    ),
    tools=[search_items, add_to_cart],
    model="gpt-4.1",
)

order_agent = Agent(
    name="Order Agent",
    instructions=(
        "1. greet user\n"
        "2. ask user if they w ant to place order or get order status\n"
        "3. if place order -> use place_order and give answer\n"
        "4. if get order status -> ask user for order id\n"
        "5. call get_order_status with order id and give answer\n"
    ),
    tools=[place_order, get_order_status],
    model="gpt-4.1",
)

refund_agent = Agent(
    name="Refund Agent",
    instructions=(
        "1. greet user\n"
        "2. ask user for order id\n"
        "3. ask user for return reason\n"
        "3. use submit_return\n"
        "4. confirm refund and give ref\n"
    ),
    tools=[submit_refund],
    model="gpt-4.1",
)

faq_agent = Agent(
    name="FAQ Agent",
    instructions=(
        "1. greet user\n"
        "2. ask what info they need\n"
        "3. call get_store_faq\n"
        "4. give answer\n"
        "5. offer further help"
    ),
    tools=[get_store_faq],
    model="gpt-4.1",
)

triage_agent = Agent(
    name="Triage Agent",
    instructions=(
        "1. greet user\n"
        "2. decide: shopping, order, refund or info\n"
        "3. shopping → shopping_agent\n"
        "4. order → order_agent\n"
        "5. refund → refund_agent\n"
        "6. info → faq_agent"
    ),
    handoffs=[shopping_agent, order_agent, refund_agent, faq_agent],
    model="gpt-4.1",
)

@weave.op()
async def run_agent(prompt: str):
    response = await Runner.run(triage_agent, prompt)
    return response.final_output

@weave.op()
async def run_agent(prompt: str):
    response = await Runner.run(triage_agent, prompt)
    return response.final_output

@weave.op()
async def ecommerce_ai():
    print("Starting E-Commerce program...")
    previous_response_id = None
    cur_agent = triage_agent
    while True:
        user_in = input("> ")
        response = await Runner.run(
            cur_agent, user_in, previous_response_id=previous_response_id
        )
        previous_response_id = response.last_response_id
        cur_agent = response.last_agent
        print(f"[{cur_agent.name}] {response.final_output}")

if __name__ == "__main__":
    asyncio.run(ecommerce_ai())