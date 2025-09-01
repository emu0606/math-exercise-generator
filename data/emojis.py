#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數學測驗生成器 - 可愛表情符號庫
"""

import random

# 正面表情符號
POSITIVE_EMOJIS = [
    "😊", "😄", "😁", "😃", "😀", "🙂", "😉", "😍", "🥰", "😘",
    "👍", "👏", "🎉", "🎊", "✨", "⭐", "🌟", "💯", "🏆", "🥇",
    "🌈", "🦄", "🐱", "🐶", "🐼", "🐻", "🦊", "🐰", "🐨", "🐯"
]

# 鼓勵表情符號
ENCOURAGING_EMOJIS = [
    "💪", "🚀", "🔥", "✅", "🎯", "🧠", "📚", "📝", "✏️", "📖",
    "🤔", "💭", "💡", "🔍", "🧩", "🎓", "🎒", "📊", "📈", "🧮"
]

# 數學相關表情符號
MATH_EMOJIS = [
    "➕", "➖", "✖️", "➗", "🟰", "💹", "📊", "📈", "📉", "🔢",
    "🧮", "📏", "📐", "⏱️", "⏲️", "🔄", "🔁", "🔂", "🔃", "🔀"
]

# 思考表情符號
THINKING_EMOJIS = [
    "🤔", "🧐", "🤓", "😎", "🧠", "💭", "💡", "🔍", "🔎", "📝"
]

# 所有表情符號的集合
ALL_EMOJIS = POSITIVE_EMOJIS + ENCOURAGING_EMOJIS + MATH_EMOJIS + THINKING_EMOJIS

def get_random_emoji():
    """獲取隨機表情符號
    
    Returns:
        str: 隨機選擇的表情符號
    """
    return random.choice(ALL_EMOJIS)

def get_random_positive_emoji():
    """獲取隨機正面表情符號
    
    Returns:
        str: 隨機選擇的正面表情符號
    """
    return random.choice(POSITIVE_EMOJIS)

def get_random_encouraging_emoji():
    """獲取隨機鼓勵表情符號
    
    Returns:
        str: 隨機選擇的鼓勵表情符號
    """
    return random.choice(ENCOURAGING_EMOJIS)

def get_random_math_emoji():
    """獲取隨機數學相關表情符號
    
    Returns:
        str: 隨機選擇的數學相關表情符號
    """
    return random.choice(MATH_EMOJIS)

def get_random_thinking_emoji():
    """獲取隨機思考表情符號
    
    Returns:
        str: 隨機選擇的思考表情符號
    """
    return random.choice(THINKING_EMOJIS)

def get_emoji_by_score(score, total):
    """根據分數獲取表情符號
    
    Args:
        score (int): 得分
        total (int): 總分
        
    Returns:
        str: 根據得分比例選擇的表情符號
    """
    ratio = score / total if total > 0 else 0
    
    if ratio >= 0.9:
        return random.choice(["🏆", "🥇", "👑", "💯", "🌟", "⭐", "🎉", "🎊"])
    elif ratio >= 0.8:
        return random.choice(["😄", "😁", "👍", "👏", "✨", "🔥", "💪"])
    elif ratio >= 0.7:
        return random.choice(["🙂", "😊", "👌", "🌈", "🚀"])
    elif ratio >= 0.6:
        return random.choice(["🙂", "😉", "🤔", "💭", "📚"])
    elif ratio >= 0.5:
        return random.choice(["🤔", "📝", "✏️", "📖", "🧐"])
    elif ratio >= 0.4:
        return random.choice(["😐", "🧠", "💡", "🔍", "🧩"])
    elif ratio >= 0.3:
        return random.choice(["😕", "🤨", "📊", "📈", "🎯"])
    else:
        return random.choice(["😢", "😞", "📉", "🔄", "🧮"])
