# 导入必要的库和模块
import re
import numpy as np
from loguru import logger


def simple_text_similarity(text1, text2):
    """
    简单的文本相似度计算（本地计算，无需 API 调用
    
    Args:
        text1 (str): 第一个文本
        text2 (str): 第二个文本
        
    Returns:
        float: 相似度分数，范围 0-1，值越高表示越相似
    """
    # 清理文本
    def clean_text(text):
        text = re.sub(r'[\s\t\n\r.,;!?()\[\]{}:"\'`~@#$%^&amp;*+=|\\/]', '', text.lower())
        return text
    
    cleaned_text1 = clean_text(text1)
    cleaned_text2 = clean_text(text2)
    
    # 如果文本为空
    if not cleaned_text1 and not cleaned_text2:
        return 1.0
    if not cleaned_text1 or not cleaned_text2:
        return 0.0
    
    # 计算共同字符的数量（适用于中文）
    common_chars = 0
    for char in set(cleaned_text1):
        if char in cleaned_text2:
            common_chars += min(cleaned_text1.count(char), cleaned_text2.count(char))
    
    # 计算总字符数
    total_chars = len(cleaned_text1) + len(cleaned_text2) - common_chars
    
    # 计算相似度
    similarity = common_chars / total_chars
    
    return similarity


def calculate_hotness_score(likes, comments, collection):
    """
    计算热度评分（简化版，移除不必要的日志）
    
    Args:
        likes (int): 点赞数
        comments (int): 评论数
        collection (int): 收藏数
        
    Returns:
        float: 热度评分
    """
    # 基于点赞、评论、收藏的加权计算
    return likes * 0.6 + comments * 0.3 + collection * 0.1
