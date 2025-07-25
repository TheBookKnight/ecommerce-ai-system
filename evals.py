import asyncio
import weave
from agents import Runner


import config
weave.init(project_name=config.TEST_WEAVE_PROJECT)

from ecommerce_agents import (
    triage_agent,
    shopping_agent,
    order_agent,
    refund_agent,
    faq_agent,
)

# Define test cases for each agent
AGENT_TESTS = {
    "shopping_agent": [
        {
            "prompt": "I want to buy a Pikachu plush.",
            "expected_output": "Sure! I can help you find a Pikachu plush",
        },
        {
            "prompt": "Show me Nintendo Switch games.",
            "expected_output": "Here are some Nintendo Switch games",
        },
    ],
    "order_agent": [
        {
            "prompt": "Where is my order #12345?",
            "expected_output": "Let me check the status of order #12345",
        },
    ],
    "refund_agent": [
        {
            "prompt": "I want a refund for my last purchase.",
            "expected_output": "I can help you with your refund",
        },
    ],
    "faq_agent": [
        {
            "prompt": "What is your return policy?",
            "expected_output": "Our return policy is",
        },
    ],
    "triage_agent": [
        {
            "prompt": "I want to buy a Pikachu plush.",
            "expected_output": "Sure! I can help you find a Pikachu plush",
        },
        {
            "prompt": "How do I return my order?",
            "expected_output": "Our return policy is",
        },
        {
            "prompt": "Where is my order #12345?",
            "expected_output": "Let me check the status of order #12345",
        },
        {
            "prompt": "I want a refund for my last purchase.",
            "expected_output": "I can help you with your refund",
        },
    ],
}

AGENT_OBJECTS = {
    "shopping_agent": shopping_agent,
    "order_agent": order_agent,
    "refund_agent": refund_agent,
    "faq_agent": faq_agent,
    "triage_agent": triage_agent,
}

@weave.op()
def evaluate_output(expected: str, model_output: str) -> dict:
    """Simple evaluator: checks if expected text is in model output."""
    is_correct = expected.lower() in model_output.lower()
    return {"correct": is_correct, "score": float(is_correct)}

@weave.op()
async def eval_all_agents():
    all_results = {}
    for agent_name, tests in AGENT_TESTS.items():
        agent = AGENT_OBJECTS[agent_name]
        agent_results = []
        print(f"\n=== Evaluating {agent_name} ===")
        for test in tests:
            result = await Runner.run(agent, test["prompt"])
            eval_result = evaluate_output(test["expected_output"], result.final_output)
            agent_results.append({
                "prompt": test["prompt"],
                "output": result.final_output,
                "evaluation": eval_result,
            })
            print(f"Prompt: {test['prompt']}")
            print(f"Output: {result.final_output}")
            print(f"Expected: {test['expected_output']}")
            print(f"Correct: {eval_result['correct']}\n")
        all_results[agent_name] = agent_results
    return all_results

if __name__ == "__main__":
    asyncio.run(eval_all_agents())