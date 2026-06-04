import os

from dotenv import load_dotenv

load_dotenv()

MODEL_CONFIGS = {
    "qwen-plus": {
        "model": "qwen-plus",
        "openai_api_key": os.getenv("QWEN_API_KEY"),
        "openai_api_base": os.getenv("QWEN_API_URL")
    },
    "deepseek-chat": {
        "model": "deepseek-chat",
        "openai_api_key": os.getenv("DEEPSEEK_API_KEY"),
        "openai_api_base": os.getenv("DEEPSEEK_API_URL")
    }
}