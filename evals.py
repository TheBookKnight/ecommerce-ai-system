import asyncio
from dataclasses import dataclass
from typing import Any, Callable, List, Optional, Tuple

import weave
from agents import Agent, Runner
from pydantic import Field

import config

weave.init(config.TEST_WEAVE_PROJECT)

@dataclass
class EvalResult:
    """
    Represents the result of an evaluation.
    """
    correct_final_output: bool
    correct_tool_calls: bool
    correct_agent_routing: bool
    appropriate_steps: bool

    def total_score(self) -> float:
        criteria = [
            self.correct_final_output,
            self.correct_tool_calls,
            self.correct_agent_routing,
            self.appropriate_steps,
        ]
        return sum(criteria) / len(criteria) * 100

    def __str__(self) -> str:
        return (
            f"Final Output: {'✅' if self.correct_final_output else '❌'}\n"
            f"Tool Calls: {'✅' if self.correct_tool_calls else '❌'}\n"
            f"Agent Routing: {'✅' if self.correct_agent_routing else '❌'}\n"
            f"Step Count: {'✅' if self.appropriate_steps else '❌'}\n"
            f"Total Score: {self.total_score()}%"
        )
    
@dataclass
class ExpectedBehavior:
    final_output_validator: Callable[[str], bool]
    expected_tool_calls: List[str]
    expected_agent_sequence: List[str]
    min_steps: int
    max_steps: int

# Individual Agent tests
SHOPPING_AGENT_TESTS = [
    (
        "I want to buy a Pikachu plush.",
        ExpectedBehavior(
            final_output_validator=lambda x: all(
                term.lower() in x.lower() for term in ["pikachu plush"]
            ),
            expected_tool_calls=["search_items"],
            expected_agent_sequence=["Shopping Agent"],
            min_steps=2,
            max_steps=4,
        ),
    ),
    (
        "Can you help me find a Charizard figure?",
        ExpectedBehavior(
            final_output_validator=lambda x: all(
                term.lower() in x.lower() for term in ["charizard figure"]
            ),
            expected_tool_calls=["search_items"],
            expected_agent_sequence=["Shopping Agent"],
            min_steps=2,
            max_steps=4,
        ),
    )
]

ORDER_AGENT_TESTS = [
    (
        "Where is my order #12345?",
        ExpectedBehavior(
            final_output_validator=lambda x: all(
                term.lower() in x.lower() for term in ["order", "12345"]
            ),
            expected_tool_calls=["get_order_status"],
            expected_agent_sequence=["Order Agent"],
            min_steps=2,
            max_steps=4,
        ),
    ),
]

REFUND_AGENT_TESTS = [
    (
        "I want a refund for my last purchase. Its order number is ORD-9001 and the reason is it's a defective item.",
        ExpectedBehavior(
            final_output_validator=lambda x: all(
                term.lower() in x.lower() for term in ["refund"]
            ),
            expected_tool_calls=["submit_refund"],
            expected_agent_sequence=["Refund Agent"],
            min_steps=2,
            max_steps=4,
        ),
    ),
]

FAQ_AGENT_TESTS = [
    (
        "What is your return policy?",
        ExpectedBehavior(
            final_output_validator=lambda x: all(
                term.lower() in x.lower() for term in ["return policy"]
            ),
            expected_tool_calls=["get_store_faq"],
            expected_agent_sequence=["FAQ Agent"],
            min_steps=2,
            max_steps=4,
        ),
    )
]

# Multi-Agent tests
## TODO: For multi-agent system, need to update the agents (or even create a routing agent) to handle these more complex scenarios
MULTI_AGENT_TESTS = {
    "Shopping Agent": [
        (
            "I am Ash Ketchum. If you find a Charmander figure, then add it to the cart, place the order now (no confirmation needed), and finally tell me the return policy for it. That's the only item I want.",
            ExpectedBehavior(
                final_output_validator=lambda x: all(
                    term.lower() in x.lower() for term in ["charmander figure", "cart", "return", "ord"]
                ),
                expected_tool_calls=["search_items", "add_to_cart", "place_order", "get_store_faq"],
                expected_agent_sequence=[
                    "Triage Agent",
                    "Shopping Agent",
                    "Flight Booking Agent",
                ],
                min_steps=3,
                max_steps=6,
            ),
        ),
    ]
}

"""
Inherits from weave.Model to define the structure of the agent model.
https://weave-docs.wandb.ai/reference/python-sdk/weave/#class-model
"""
class AgentModel(weave.Model):
    name: Optional[str] = None
    agent: Any = Field(default=None)

    def __init__(self, agent: Any, name: str = None):
        super().__init__() # Important: call weave.Model's __init__
        self.agent = agent
        self.name = name if name else agent.name

    @weave.op()
    async def predict(self, prompt: str) -> dict:
        result = await Runner.run(self.agent, prompt)
        return {
            "final_output": result.final_output,
            "new_items": result.new_items,
            "last_agent": result.last_agent,
            "raw_responses": result.raw_responses,
        }

@weave.op()
def evaluate_final_output(
    expected_validator: Callable[[str], bool], model_output: dict
) -> dict:
    """
    Evaluates the final output of the model against an expected behavior.
    """
    is_correct = expected_validator(model_output.get("final_output", ""))
    return {"correct": is_correct, "score": float(is_correct)}

@weave.op()
def evaluate_tool_calls(expected_tools: List[str], model_output: dict) -> dict:
    """
    Evaluates the tool calls made by the model against expected tool calls.
    """
    actual_tool_calls = []
    for item in model_output.get("new_items", []):
        if hasattr(item, "type") and item.type == "tool_call_item":
            if hasattr(item, "raw_item"):
                tool_name = item.raw_item.name
                actual_tool_calls.append(tool_name)
        
        correct = all(
            any(expected_tool.lower() == actual.lower() for actual in actual_tool_calls)
            for expected_tool in expected_tools
        )
        return {
            "correct": correct,
            "score": float(correct),
            "actual_calls": actual_tool_calls,
        }
    
@weave.op()
def evaluate_agent_routing(expected_sequence: List[str], model_output: dict) -> dict:
    """Evaluate if agents were routed correctly"""
    if len(expected_sequence) == 1:
        correct = expected_sequence[0] == model_output["last_agent"].name
    else:
        correct = model_output["last_agent"].name == expected_sequence[-1]

    return {
        "correct": correct,
        "score": float(correct),
        "final_agent": model_output["last_agent"].name,
    }


@weave.op()
def evaluate_step_count(min_steps: int, max_steps: int, model_output: dict) -> dict:
    """Evaluate if the number of steps is appropriate"""
    step_count = len(model_output["new_items"])
    correct = min_steps <= step_count <= max_steps
    return {"correct": correct, "score": float(correct), "step_count": step_count}

"""
Evaluates all agents using Weave.
https://weave-docs.wandb.ai/reference/python-sdk/weave/#class-evaluation
"""
async def evaluate_agent_with_weave(
    agent: Agent, tests: List[Tuple[str, ExpectedBehavior]], agent_name: str
):
    model = AgentModel(agent)
    dataset = create_evaluation_dataset(tests)

    # Create descriptive display names
    if agent_name.startswith("Triage_Agent_"):
        # For multi-agent tests, use the category name
        category = agent_name.replace("Triage_Agent_", "")
        display_name = f"Multi-Agent System - {category} Scenarios"
    else:
        # For individual agents, describe their role
        display_names = {
            "Shopping_Agent": "Shopping - Search for Items",
            "Order_Agent": "Order - Manage Orders",
            "Refund_Agent": "Refund - Manage Refunds",
            "Faq_Agent": "FAQ Service - Information Queries",
        }
        display_name = display_names.get(agent_name, agent_name)

    evaluation = weave.Evaluation(
        name=f"{agent_name}_evaluation",
        dataset=dataset,
        scorers=[
            evaluate_final_output,
            evaluate_tool_calls,
            evaluate_agent_routing,
            evaluate_step_count,
        ],
    )

    return await evaluation.evaluate(model, __weave={"display_name": display_name})

def create_evaluation_dataset(tests: List[Tuple[str, ExpectedBehavior]]) -> List[dict]:
    return [
        {
            "prompt": prompt,
            "expected_validator": expected.final_output_validator,
            "expected_tools": expected.expected_tool_calls,
            "expected_sequence": expected.expected_agent_sequence,
            "min_steps": expected.min_steps,
            "max_steps": expected.max_steps,
        }
        for prompt, expected in tests
    ]

@weave.op()
async def run_evaluations():
    from ecommerce_agents import (
        shopping_agent,
        order_agent,
        refund_agent,
        faq_agent,
        triage_agent
    )

    # Individual agent evaluations
    individual_results = {
        f"Shopping Agent ": await evaluate_agent_with_weave(
            shopping_agent, SHOPPING_AGENT_TESTS, "Shopping_Agent"
        ),
        f"Order Agent ": await evaluate_agent_with_weave(
            order_agent, ORDER_AGENT_TESTS, "Order_Agent"
        ),
        f"Refund Agent ": await evaluate_agent_with_weave(
            refund_agent, REFUND_AGENT_TESTS, "Refund_Agent"
        ),
        f"FAQ Agent ": await evaluate_agent_with_weave(
            faq_agent, FAQ_AGENT_TESTS, "Faq_Agent"
        )
    }

    # Multi-agent system evaluations
    multi_agent_results = {}
    for category, tests in MULTI_AGENT_TESTS.items():
        multi_agent_results[f"{category}"] = (
            await evaluate_agent_with_weave(
                triage_agent, tests, f"Triage_Agent_{category}"
            )
        )

    # Print summary of evaluations
    print("\n=== Evaluation Results ===")

    print("\nIndividual Agent Scores:")
    for agent_name, results in individual_results.items():
        print(f"{agent_name}:")
        print(
            f"  Final Output Score: {results['evaluate_final_output']['score']['mean']:.2%}"
        )
        print(
            f"  Tool Calls Score: {results['evaluate_tool_calls']['score']['mean']:.2%}"
        )
        print(
            f"  Agent Routing Score: {results['evaluate_agent_routing']['score']['mean']:.2%}"
        )
        print(
            f"  Step Count Score: {results['evaluate_step_count']['score']['mean']:.2%}"
        )

    print("\nMulti-agent System Scores:")
    for category, results in multi_agent_results.items():
        print(f"{category}:")
        print(
            f"  Final Output Score: {results['evaluate_final_output']['score']['mean']:.2%}"
        )
        print(
            f"  Tool Calls Score: {results['evaluate_tool_calls']['score']['mean']:.2%}"
        )
        print(
            f"  Agent Routing Score: {results['evaluate_agent_routing']['score']['mean']:.2%}"
        )
        print(
            f"  Step Count Score: {results['evaluate_step_count']['score']['mean']:.2%}"
        )

if __name__ == "__main__":
    asyncio.run(run_evaluations())
