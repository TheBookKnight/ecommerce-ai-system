from dataclasses import dataclass
from typing import Any, Callable, List, Optional, Tuple

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
                    term.lower() in x.lower() for term in ["charmander figure", "cart", "return"]
                ),
                expected_tool_calls=["search_items", "add_to_cart", "place_order", "get_store_faq"],
                expected_agent_sequence=[
                    "Triage Agent",
                    "Shopping Agent",
                    "Order Agent",
                    "FAQ Agent",
                ],
                min_steps=3,
                max_steps=6,
            ),
        ),
    ]
}