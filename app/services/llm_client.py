from openai import OpenAI
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# OpenAI 配置（从环境变量读取）
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

# 初始化 OpenAI 客户端
client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL,
)

def rewrite_sentence(sentence: str) -> str:
    """
    使用 GPT-3.5 模型对句子进行润色
    """
    try:
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Rewrite this sentence in better English: {sentence}"}
        ]

        completion = client.chat.completions.create(model=OPENAI_MODEL, messages=messages)
        return completion.choices[0].message.content.strip()

    except Exception as e:
        print(f"Error during rewriting sentence: {e}")
        return ""

def generate_suggestions(text: str) -> list:
    """
    根据当前输入的文本，生成下一个词或短语的建议
    """
    try:
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Complete this sentence: {text}"}
        ]

        # 调用 OpenAI API 生成补全建议
        completion = client.chat.completions.create(model=OPENAI_MODEL, messages=messages)
        suggestions = completion.choices[0].message.content.strip().split()

        return suggestions[:3]  # 返回前 3 个补全建议

    except Exception as e:
        print(f"Error during generating suggestions: {e}")
        return []

# 测试函数
if __name__ == '__main__':
    test_sentence = "The quick brown fox"
    print("Rewritten sentence:", rewrite_sentence(test_sentence))

    test_text = "The quick brown fox"
    print("Suggestions:", generate_suggestions(test_text))
