# Master model configuration - single source of truth
MODELS = {
    # Free tier models

    "anthropic/claude-sonnet-4-20250514": {
        "aliases": ["claude-sonnet-4"],
        "pricing": {
            "input_cost_per_million_tokens": 3.00,
            "output_cost_per_million_tokens": 15.00
        },
        "tier_availability": ["free", "paid"]
    },
    # "openrouter/deepseek/deepseek-chat": {
    #     "aliases": ["deepseek"],
    #     "pricing": {
    #         "input_cost_per_million_tokens": 0.38,
    #         "output_cost_per_million_tokens": 0.89
    #     },
    #     "tier_availability": ["free", "paid"]
    # },
    # "openrouter/qwen/qwen3-235b-a22b": {
    #     "aliases": ["qwen3"],
    #     "pricing": {
    #         "input_cost_per_million_tokens": 0.13,
    #         "output_cost_per_million_tokens": 0.60
    #     },
    #     "tier_availability": ["free", "paid"]
    # },
    # "openrouter/google/gemini-2.5-flash-preview-05-20": {
    #     "aliases": ["gemini-flash-2.5"],
    #     "pricing": {
    #         "input_cost_per_million_tokens": 0.15,
    #         "output_cost_per_million_tokens": 0.60
    #     },
    #     "tier_availability": ["free", "paid"]
    # },
    # "openrouter/deepseek/deepseek-chat-v3-0324": {
    #     "aliases": ["deepseek/deepseek-chat-v3-0324"],
    #     "pricing": {
    #         "input_cost_per_million_tokens": 0.38,
    #         "output_cost_per_million_tokens": 0.89
    #     },
    #     "tier_availability": ["free", "paid"]
    # },
    "openrouter/moonshotai/kimi-k2": {
        "aliases": ["moonshotai/kimi-k2"],
        "pricing": {
            "input_cost_per_million_tokens": 1.00,
            "output_cost_per_million_tokens": 3.00
        },
        "tier_availability": ["free", "paid"]
    },
    "xai/grok-4": {
        "aliases": ["grok-4", "x-ai/grok-4"],
        "pricing": {
            "input_cost_per_million_tokens": 5.00,
            "output_cost_per_million_tokens": 15.00
        },
        "tier_availability": ["paid"]
    },
    
    # Paid tier only models
    "gemini/gemini-2.5-pro": {
        "aliases": ["google/gemini-2.5-pro"],
        "pricing": {
            "input_cost_per_million_tokens": 1.25,
            "output_cost_per_million_tokens": 10.00
        },
        "tier_availability": ["paid"]
    },
    "openai/gpt-4o": {
        "aliases": ["gpt-4o"],
        "pricing": {
            "input_cost_per_million_tokens": 2.50,
            "output_cost_per_million_tokens": 10.00
        },
        "tier_availability": ["paid"]
    },
    "openai/gpt-4.1": {
        "aliases": ["gpt-4.1"],
        "pricing": {
            "input_cost_per_million_tokens": 15.00,
            "output_cost_per_million_tokens": 60.00
        },
        "tier_availability": ["paid"]
    },
    "openai/gpt-4.1-mini": {
        "aliases": ["gpt-4.1-mini"],
        "pricing": {
            "input_cost_per_million_tokens": 1.50,
            "output_cost_per_million_tokens": 6.00
        },
        "tier_availability": ["paid"]
    },
    "anthropic/claude-3-7-sonnet-latest": {
        "aliases": ["sonnet-3.7"],
        "pricing": {
            "input_cost_per_million_tokens": 3.00,
            "output_cost_per_million_tokens": 15.00
        },
        "tier_availability": ["paid"]
    },
    "anthropic/claude-3-5-sonnet-latest": {
        "aliases": ["sonnet-3.5"],
        "pricing": {
            "input_cost_per_million_tokens": 3.00,
            "output_cost_per_million_tokens": 15.00
        },
        "tier_availability": ["paid"]
    },   
}

# Derived structures (auto-generated from MODELS)
def _generate_model_structures():
    """Generate all model structures from the master MODELS dictionary."""
    
    # Generate tier lists
    free_models = []
    paid_models = []
    
    # Generate aliases
    aliases = {}
    
    # Generate pricing
    pricing = {}
    
    for model_name, config in MODELS.items():
        # Add to tier lists
        if "free" in config["tier_availability"]:
            free_models.append(model_name)
        if "paid" in config["tier_availability"]:
            paid_models.append(model_name)
        
        # Add aliases
        for alias in config["aliases"]:
            aliases[alias] = model_name
        
        # Add pricing
        pricing[model_name] = config["pricing"]
        
        # Also add pricing for legacy model name variations
        if model_name.startswith("openrouter/deepseek/"):
            legacy_name = model_name.replace("openrouter/", "")
            pricing[legacy_name] = config["pricing"]
        elif model_name.startswith("openrouter/qwen/"):
            legacy_name = model_name.replace("openrouter/", "")
            pricing[legacy_name] = config["pricing"]
        elif model_name.startswith("gemini/"):
            legacy_name = model_name.replace("gemini/", "")
            pricing[legacy_name] = config["pricing"]
        elif model_name.startswith("anthropic/"):
            # Add anthropic/claude-sonnet-4 alias for claude-sonnet-4-20250514
            if "claude-sonnet-4-20250514" in model_name:
                pricing["anthropic/claude-sonnet-4"] = config["pricing"]
        elif model_name.startswith("xai/"):
            # Add pricing for OpenRouter x-ai models
            openrouter_name = model_name.replace("xai/", "openrouter/x-ai/")
            pricing[openrouter_name] = config["pricing"]
    
    return free_models, paid_models, aliases, pricing

# Generate all structures
FREE_TIER_MODELS, PAID_TIER_MODELS, MODEL_NAME_ALIASES, HARDCODED_MODEL_PRICES = _generate_model_structures()

MODEL_ACCESS_TIERS = {
    "free": [
        "openrouter/deepseek/deepseek-chat",
        "openrouter/qwen/qwen3-235b-a22b",
        "openrouter/google/gemini-2.5-flash-preview-05-20",
    ],
    "tier_2_20": [
        "openrouter/deepseek/deepseek-chat",
        # "xai/grok-3-mini-fast-beta",
        "openai/gpt-4o",
        # "openai/gpt-4-turbo",
        # "xai/grok-3-fast-latest",
        "openrouter/google/gemini-2.5-flash-preview-05-20",  # Added
        "openrouter/google/gemini-2.5-pro",  # Added Gemini 2.5 Pro
        # "openai/gpt-4",
        "anthropic/claude-3-7-sonnet-latest",
        "anthropic/claude-3-5-sonnet-latest",
        "anthropic/claude-sonnet-4-20250514",
        "openai/gpt-4.1",
        "openai/gpt-4.1-mini",
        # "openrouter/deepseek/deepseek-r1",
        "openrouter/qwen/qwen3-235b-a22b",
    ],
    "tier_6_50": [
        "openrouter/deepseek/deepseek-chat",
        # "xai/grok-3-mini-fast-beta",
        "openai/gpt-4o",
        "openai/gpt-4.1",
        "openai/gpt-4.1-mini",
        # "openai/gpt-4-turbo",
        # "xai/grok-3-fast-latest",
        "openrouter/google/gemini-2.5-flash-preview-05-20",  # Added
        "openrouter/google/gemini-2.5-pro",  # Added Gemini 2.5 Pro
        # "openai/gpt-4",
        "anthropic/claude-3-7-sonnet-latest",
        "anthropic/claude-3-5-sonnet-latest",
        "anthropic/claude-sonnet-4-20250514",
        "openai/gpt-4.1",
        "openai/gpt-4.1-mini",
        # "openrouter/deepseek/deepseek-r1",
        "openrouter/qwen/qwen3-235b-a22b",
    ],
    "tier_12_100": [
        "openrouter/deepseek/deepseek-chat",
        # "xai/grok-3-mini-fast-beta",
        "openai/gpt-4o",
        # "openai/gpt-4-turbo",
        # "xai/grok-3-fast-latest",
        "openrouter/google/gemini-2.5-flash-preview-05-20",  # Added
        "openrouter/google/gemini-2.5-pro",  # Added Gemini 2.5 Pro
        # "openai/gpt-4",
        "anthropic/claude-3-7-sonnet-latest",
        "anthropic/claude-3-5-sonnet-latest",
        "anthropic/claude-sonnet-4-20250514",
        "openai/gpt-4.1",
        "openai/gpt-4.1-mini",
        # "openrouter/deepseek/deepseek-r1",
        "openrouter/qwen/qwen3-235b-a22b",
    ],
    "tier_25_200": [
        "openrouter/deepseek/deepseek-chat",
        # "xai/grok-3-mini-fast-beta",
        "openai/gpt-4o",
        # "openai/gpt-4-turbo",
        # "xai/grok-3-fast-latest",
        "openrouter/google/gemini-2.5-flash-preview-05-20",  # Added
        "openrouter/google/gemini-2.5-pro",  # Added Gemini 2.5 Pro
        # "openai/gpt-4",
        "anthropic/claude-3-7-sonnet-latest",
        "anthropic/claude-3-5-sonnet-latest",
        "anthropic/claude-sonnet-4-20250514",
        "openai/gpt-4.1",
        "openai/gpt-4.1-mini",
        # "openrouter/deepseek/deepseek-r1",
        "openrouter/qwen/qwen3-235b-a22b",
    ],
    "tier_50_400": [
        "openrouter/deepseek/deepseek-chat",
        # "xai/grok-3-mini-fast-beta",
        "openai/gpt-4o",
        # "openai/gpt-4-turbo",
        # "xai/grok-3-fast-latest",
        "openrouter/google/gemini-2.5-flash-preview-05-20",  # Added
        "openrouter/google/gemini-2.5-pro",  # Added Gemini 2.5 Pro
        # "openai/gpt-4",
        "anthropic/claude-3-7-sonnet-latest",
        "anthropic/claude-3-5-sonnet-latest",
        "anthropic/claude-sonnet-4-20250514",
        "openai/gpt-4.1",
        "openai/gpt-4.1-mini",
        # "openrouter/deepseek/deepseek-r1",
        "openrouter/qwen/qwen3-235b-a22b",
    ],
    "tier_125_800": [
        "openrouter/deepseek/deepseek-chat",
        # "xai/grok-3-mini-fast-beta",
        "openai/gpt-4o",
        # "openai/gpt-4-turbo",
        # "xai/grok-3-fast-latest",
        "openrouter/google/gemini-2.5-flash-preview-05-20",  # Added
        "openrouter/google/gemini-2.5-pro",  # Added Gemini 2.5 Pro
        # "openai/gpt-4",
        "anthropic/claude-3-7-sonnet-latest",
        "anthropic/claude-3-5-sonnet-latest",
        "anthropic/claude-sonnet-4-20250514",
        "openai/gpt-4.1",
        "openai/gpt-4.1-mini",
        # "openrouter/deepseek/deepseek-r1",
        "openrouter/qwen/qwen3-235b-a22b",
    ],
    "tier_200_1000": [
        "openrouter/deepseek/deepseek-chat",
        # "xai/grok-3-mini-fast-beta",
        "openai/gpt-4o",
        # "openai/gpt-4-turbo",
        # "xai/grok-3-fast-latest",
        "openrouter/google/gemini-2.5-flash-preview-05-20",  # Added
        "openrouter/google/gemini-2.5-pro",  # Added Gemini 2.5 Pro
        # "openai/gpt-4",
        "anthropic/claude-3-7-sonnet-latest",
        "anthropic/claude-3-5-sonnet-latest",
        "anthropic/claude-sonnet-4-20250514",
        "openai/gpt-4.1",
        "openai/gpt-4.1-mini",
        # "openrouter/deepseek/deepseek-r1",
        "openrouter/qwen/qwen3-235b-a22b",
    ],
}
MODEL_NAME_ALIASES = {
    "openrouter/claude-sonnet-4": "openrouter/anthropic/claude-sonnet-4",
    "openrouter/gpt-5-chat": "openrouter/openai/gpt-5-chat",
    "openrouter/openai/gpt-5-mini": "openrouter/openai/gpt-5-mini",
    "openrouter/deepseek-chat-v3-0324": "openrouter/deepseek/deepseek-chat-v3-0324",
    "openrouter/kimi-k2": "openrouter/moonshotai/kimi-k2",
    "openrouter/qwen3-235b-a22b-2507": "openrouter/qwen/qwen3-235b-a22b-2507",
    
    
    
    # Short names to full names
    #"openrouter/sonnet-3.7": "openrouter/anthropic/claude-3.7-sonnet",
    # "sonnet-3.7": "anthropic/claude-3-7-sonnet-latest",
    # "sonnet-3.5": "anthropic/claude-3-5-sonnet-latest",
    # "haiku-3.5": "anthropic/claude-3-5-haiku-latest",
    # "claude-sonnet-4": "anthropic/claude-sonnet-4-20250514",
    # "gpt-4.1": "openai/gpt-4.1-2025-04-14",  # Commented out in constants.py
    # "gpt-4o": "openai/gpt-4o",
    # "gpt-4.1": "openai/gpt-4.1",
    # "gpt-4.1-mini": "openai/gpt-4.1-mini",
    # "gpt-4-turbo": "openai/gpt-4-turbo",  # Commented out in constants.py
    # "gpt-4": "openai/gpt-4",  # Commented out in constants.py
    # "gemini-flash-2.5": "openrouter/google/gemini-2.5-flash-preview",  # Commented out in constants.py
    # "grok-3": "xai/grok-3-fast-latest",  # Commented out in constants.py
    # "deepseek": "openrouter/deepseek/deepseek-chat",
    # "deepseek-r1": "openrouter/deepseek/deepseek-r1",
    # "grok-3-mini": "xai/grok-3-mini-fast-beta",  # Commented out in constants.py
    # "qwen3": "openrouter/qwen/qwen3-235b-a22b",  # Commented out in constants.py
    # "gemini-flash-2.5": "openrouter/google/gemini-2.5-flash-preview-05-20",
    # "gemini-2.5-flash:thinking": "openrouter/google/gemini-2.5-flash-preview-05-20:thinking",
    # "google/gemini-2.5-flash-preview":"openrouter/google/gemini-2.5-flash-preview",
    # "google/gemini-2.5-flash-preview:thinking":"openrouter/google/gemini-2.5-flash-preview:thinking",
    # "google/gemini-2.5-pro": "openrouter/google/gemini-2.5-pro",
    # "deepseek/deepseek-chat-v3-0324": "openrouter/deepseek/deepseek-chat-v3-0324",
    # Also include full names as keys to ensure they map to themselves
    # "anthropic/claude-3-7-sonnet-latest": "anthropic/claude-3-7-sonnet-latest",
    # "openai/gpt-4.1-2025-04-14": "openai/gpt-4.1-2025-04-14",  # Commented out in constants.py
    # "openai/gpt-4o": "openai/gpt-4o",
    # "openai/gpt-4-turbo": "openai/gpt-4-turbo",  # Commented out in constants.py
    # "openai/gpt-4": "openai/gpt-4",  # Commented out in constants.py
    # "openrouter/google/gemini-2.5-flash-preview": "openrouter/google/gemini-2.5-flash-preview",  # Commented out in constants.py
    # "xai/grok-3-fast-latest": "xai/grok-3-fast-latest",  # Commented out in constants.py
    # "deepseek/deepseek-chat": "openrouter/deepseek/deepseek-chat",
    # "deepseek/deepseek-r1": "openrouter/deepseek/deepseek-r1",
    # "qwen/qwen3-235b-a22b": "openrouter/qwen/qwen3-235b-a22b",
    # "xai/grok-3-mini-fast-beta": "xai/grok-3-mini-fast-beta",  # Commented out in constants.py
<<<<<<< HEAD
    "openrouter/sonnet-3.7": "openrouter/anthropic/claude-3.7-sonnet",
    "openrouter/claude-sonnet-4": "openrouter/anthropic/claude-sonnet-4",
    "openrouter/kimi-k2": "openrouter/moonshotai/kimi-k2",
=======
    # "free": FREE_TIER_MODELS,
    # "tier_2_20": PAID_TIER_MODELS,
    # "tier_6_50": PAID_TIER_MODELS,
    # "tier_12_100": PAID_TIER_MODELS,
    # "tier_25_200": PAID_TIER_MODELS,
    # "tier_50_400": PAID_TIER_MODELS,
    # "tier_125_800": PAID_TIER_MODELS,
    # "tier_200_1000": PAID_TIER_MODELS,
>>>>>>> e465b9e1bc7e382986da893a557cc45f44307523
}
