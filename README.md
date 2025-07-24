# E-Commerce AI System

The customer will interact with a general assistant to:

1. Shop for products
2. Place orders
3. Track or refund orders
4. Ask FAQs about store policies

Each function is handled by a specialized agent, and the Triage Agent decides where to route the user.

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
