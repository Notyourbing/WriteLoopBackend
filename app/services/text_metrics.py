"""
文本指标计算工具
计算 TTR (Type-Token Ratio) 和 MLU (Mean Length of Utterance)
"""
import re
from typing import Tuple


def calculate_ttr(text: str) -> float:
    """
    计算 Type-Token Ratio (TTR) - 词汇丰富度
    TTR = 唯一词数 / 总词数
    
    返回 0-100 的分数（基于 TTR 值，理想情况下 TTR 在 0.4-0.7 之间）
    """
    if not text or not text.strip():
        return 0.0
    
    # 转换为小写并提取单词（仅字母）
    words = re.findall(r'\b[a-z]+\b', text.lower())
    
    if not words:
        return 0.0
    
    total_tokens = len(words)
    unique_types = len(set(words))
    
    # 计算 TTR
    ttr = unique_types / total_tokens if total_tokens > 0 else 0.0
    
    # 将 TTR 转换为 0-100 分数
    # TTR 通常在 0.2-0.7 之间，我们将其映射到 0-100
    # 理想 TTR: 0.4-0.7 -> 60-100 分
    # 较低 TTR: 0.2-0.4 -> 30-60 分
    # 很低 TTR: <0.2 -> 0-30 分
    if ttr >= 0.7:
        score = 100.0
    elif ttr >= 0.4:
        score = 60.0 + (ttr - 0.4) / 0.3 * 40.0  # 0.4->60, 0.7->100
    elif ttr >= 0.2:
        score = 30.0 + (ttr - 0.2) / 0.2 * 30.0  # 0.2->30, 0.4->60
    else:
        score = ttr / 0.2 * 30.0  # 0->0, 0.2->30
    
    return min(100.0, max(0.0, score))


def calculate_mlu(text: str) -> float:
    """
    计算 Mean Length of Utterance (MLU) - 句法复杂度
    MLU = 平均句子长度（以单词数计算）
    
    返回 0-100 的分数（基于平均句长，理想情况下 15-25 单词/句）
    """
    if not text or not text.strip():
        return 0.0
    
    # 分割句子（以 . ! ? 结尾）
    sentences = re.split(r'[.!?]+\s+', text.strip())
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        return 0.0
    
    # 计算每个句子的单词数
    sentence_lengths = []
    for sentence in sentences:
        words = re.findall(r'\b[a-z]+\b', sentence.lower())
        if words:  # 只计算非空句子
            sentence_lengths.append(len(words))
    
    if not sentence_lengths:
        return 0.0
    
    # 计算平均句长
    avg_length = sum(sentence_lengths) / len(sentence_lengths)
    
    # 将平均句长转换为 0-100 分数
    # 理想句长: 15-25 单词 -> 70-100 分
    # 较短: 10-15 单词 -> 50-70 分
    # 很长: 25-35 单词 -> 70-90 分（可能过于复杂）
    # 很短: <10 单词 -> 0-50 分
    # 很长: >35 单词 -> 60-80 分（过于复杂）
    
    if 15 <= avg_length <= 25:
        score = 70.0 + (avg_length - 15) / 10.0 * 30.0  # 15->70, 25->100
    elif 10 <= avg_length < 15:
        score = 50.0 + (avg_length - 10) / 5.0 * 20.0  # 10->50, 15->70
    elif 25 < avg_length <= 35:
        score = 100.0 - (avg_length - 25) / 10.0 * 20.0  # 25->100, 35->80
    elif avg_length < 10:
        score = avg_length / 10.0 * 50.0  # 0->0, 10->50
    else:  # > 35
        score = max(60.0, 100.0 - (avg_length - 35) / 10.0 * 20.0)  # 35->80, >45->60
    
    return min(100.0, max(0.0, score))


def calculate_all_metrics(text: str) -> Tuple[float, float]:
    """
    计算所有文本指标
    返回 (ttr_score, mlu_score)
    """
    ttr = calculate_ttr(text)
    mlu = calculate_mlu(text)
    return ttr, mlu


