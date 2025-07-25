# E-Commerce AI System

The customer will interact with a general assistant to:

1. Shop for products
2. Place orders
3. Track or refund orders
4. Ask FAQs about store policies

Each function is handled by a specialized agent, and the Triage Agent decides where to route the user.

*NOTE: I created this to understand how to build an AI agentic system with Weights & Biases library. The E-Commerce idea was more flushed out with ChatGPT. I built the rest.*

| Agent              | Responsibilities                                     | Tools                             |
| ------------------ | ---------------------------------------------------- | --------------------------------- |
| **Triage Agent**   | Analyze user's request & hand off to correct agent.  | N/A                               |
| **Shopping Agent** | Search items, filter by category, brand, price, etc. | `search_items`, `add_to_cart`     |
| **Order Agent**    | Confirm cart, place order, show order ref.           | `place_order`, `get_order_status` |
| **Refund Agent**   | Take return reason, create refund request.           | `submit_refund`                   |
| **FAQ Agent**      | General policies on shipping, returns, etc.          | `get_store_faq`                   |

## 🔁 Sample Handoff Flows
### 🔹 Flow 1: Browse and Buy
Prompt: “I want to buy Pokemon cards.”
Path: `Triage → Shopping Agent → Order Agent`
Tools: `search_items`, `add_to_cart`, `place_order`

### 🔹 Flow 2: Check Order Status
Prompt: “What’s the status of my order ORD-9001?”
Path: `Triage → Order Agent`
Tool: `get_order_status`

### 🔹 Flow 3: Refund
Prompt: “I want to return my blender because it’s broken.”
Path: `Triage → Refund Agent`
Tool: `submit_refund`

### 🔹 Flow 4: Ask About Return Policy
Prompt: “How long do I have to return something?”
Path: `Triage → FAQ Agent`
Tool: `get_store_faq("returns")`

### 🔹 Flow 5: Combo Flow
Prompt: “Buy a Charizard figure and tell me the return policy.”
Path: `Triage → Shopping Agent → Order Agent → FAQ Agent`
Tools: `search_items`, `add_to_cart`, `place_order`, `get_store_faq`

## Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/TheBookKnight/ecommerce-ai-system.git
    cd ecommerce-ai-system
    ```

2. **Create and activate a virtual environment with all dependencies:**
    ```bash
    uv venv .venv
    uv sync
    ```

3. **Set up your environment variables:**
    Create a `.env` file in the project root with:
    ```env
    OPENAI_API_KEY=your_openai_api_key
    WANDB_API_KEY=your_wandb_api_key
    ```

## Prerequisites

- Python 3.11 or higher (note: issue with Python 3.13)
- [uv](https://github.com/astral-sh/uv) package manager (recommended for dependency management)
- OpenAI API key
- Weights & Biases (wandb) API key
