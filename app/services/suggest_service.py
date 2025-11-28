import json
from app.services.llm_client import client

def generate_suggestions(text: str, cursor: dict):
    """
    根据用户输入生成下一个单词的 3 个并行建议，返回的每个单词应该是可以直接接在文本后面的单独建议。
    且返回格式应严格遵循：3 个单词，单独且用空格分隔。
    """
    # 设计严格的 prompt，确保返回的结果为 3 个单词
    prompt = (
        f"Given the sentence: '{text}', suggest the next word "
        "that could logically follow. Return exactly three choices., "
        "separated by spaces, with no additional explanation, punctuation, or extra text."
    )

    # 构建消息列表，传递给 OpenAI
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]

    try:
        # 调用 OpenAI API 获取补全建议
        completion = client.chat.completions.create(model="gpt-4o-mini", messages=messages)

        # 获取模型返回的文本（应该是 3 个单词）
        suggestions = completion.choices[0].message.content.strip()

        # 确保返回的文本严格是 3 个单词，按空格分隔
        suggestion_list = suggestions.split()

        # 如果返回的单词数不是 3 个，打印错误信息
        if len(suggestion_list) == 3:
            response = [
                {"text": suggestion, "explain": f"Suggested next word: {suggestion}"}
                for suggestion in suggestion_list
            ]

            # 将结果转化为 JSON 格式并返回
            return json.dumps(response)
        else:
            # 如果返回的单词数不为 3，输出错误信息
            print(f"Error: Expected 3 words, but received: {len(suggestion_list)}")
            return json.dumps([])  # 返回空数组，表示错误
    except Exception as e:
        print(f"Error generating suggestions: {e}")
        return json.dumps([])  # 返回空数组，表示错误
