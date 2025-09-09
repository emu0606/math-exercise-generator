"""
題目分配和排序邏輯

從原始 pdf_generator.py 中提取的複雜題目分配邏輯，
重構為獨立的模組，提供更清晰的介面和更好的可測試性。

主要功能：
- 題目生成邏輯
- 題目分配策略
- 題目排序算法
- 回合管理

使用方式：
    from utils.orchestration import QuestionDistributor
    
    distributor = QuestionDistributor()
    questions = distributor.generate_questions(selected_data)
    ordered = distributor.distribute_questions(questions, rounds, per_round)
"""

import random
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from ..core.logging import get_logger
from ..core.registry import registry

# 模組專用日誌器
logger = get_logger(__name__)


class DistributionStrategy(Enum):
    """題目分配策略"""
    RANDOM = "random"           # 隨機分配
    BALANCED = "balanced"       # 平衡分配
    DIFFICULTY_BASED = "difficulty"  # 基於難度分配
    TOPIC_GROUPED = "grouped"   # 按主題分組


@dataclass
class QuestionGenerationConfig:
    """題目生成配置"""
    strategy: DistributionStrategy = DistributionStrategy.BALANCED
    ensure_variety: bool = True
    max_retries: int = 3
    random_seed: Optional[int] = None


@dataclass
class DistributionStats:
    """分配統計資訊"""
    total_questions: int
    questions_per_round: int
    rounds_count: int
    topic_distribution: Dict[str, int]
    generation_retries: int = 0


class QuestionGenerator:
    """題目生成器
    
    負責根據選定的題型數據生成具體的題目。
    """
    
    def __init__(self, config: Optional[QuestionGenerationConfig] = None):
        """初始化題目生成器
        
        Args:
            config: 可選的生成配置
        """
        self.config = config or QuestionGenerationConfig()
        
        if self.config.random_seed is not None:
            random.seed(self.config.random_seed)
            logger.debug(f"設置隨機種子: {self.config.random_seed}")
        
        logger.debug("題目生成器初始化完成")
    
    def generate_questions(self, selected_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成題目列表
        
        Args:
            selected_data: 選定的題型數據，格式為 [{"topic": "題型名稱", "count": 數量}, ...]
            
        Returns:
            生成的題目列表
            
        Raises:
            ValueError: 當題型數據無效時
        """
        logger.info(f"開始生成題目，題型數量: {len(selected_data)}")
        
        if not selected_data:
            raise ValueError("選定的題型數據不能為空")
        
        all_questions = []
        
        for item in selected_data:
            topic = item.get('topic')
            count = item.get('count', 0)
            
            if not topic or count <= 0:
                logger.warning(f"跳過無效的題型項目: {item}")
                continue
            
            logger.debug(f"生成 {topic} 題型，數量: {count}")
            
            # 解析題型格式 (UI格式為 "category - subcategory")
            if ' - ' in topic:
                category, subcategory = topic.split(' - ', 1)
            else:
                # 如果topic格式不包含' - ', 嘗試從registry中查找
                logger.warning(f"題型格式可能不正確: {topic}")
                # 暫時跳過檢查，直接嘗試獲取
                category, subcategory = None, None
            
            # 檢查題型是否已註冊
            if category and subcategory:
                if not registry.has_generator(category, subcategory):
                    logger.error(f"題型 {topic} ({category}/{subcategory}) 未註冊")
                    raise ValueError(f"未知的題型: {topic}")
                
                # 生成該題型的題目
                generator = registry.get_generator(category, subcategory)
            else:
                # 降級處理：嘗試從所有生成器中查找匹配的
                all_generators = registry.get_all_generators()
                generator = None
                for (cat, subcat), gen_class in all_generators.items():
                    if topic == cat or topic == subcat or topic == f"{cat}/{subcat}":
                        generator = gen_class
                        break
                
                if generator is None:
                    logger.error(f"無法找到題型生成器: {topic}")
                    raise ValueError(f"未知的題型: {topic}")
            
            for i in range(count):
                try:
                    # 這裡應該調用具體的題目生成邏輯
                    # 暫時使用簡單的結構，後續可以擴展
                    question_data = {
                        'topic': topic,
                        'index': i,
                        'generator': generator,
                        'params': self._generate_question_params(topic, i)
                    }
                    all_questions.append(question_data)
                    
                except Exception as e:
                    logger.error(f"生成 {topic} 第 {i+1} 題失敗: {e}")
                    if self.config.ensure_variety:
                        # 如果需要確保多樣性，重新生成
                        continue
                    else:
                        raise
        
        logger.info(f"題目生成完成，總數: {len(all_questions)}")
        return all_questions
    
    def _generate_question_params(self, topic: str, index: int) -> Dict[str, Any]:
        """生成題目參數
        
        Args:
            topic: 題型名稱
            index: 題目索引
            
        Returns:
            題目參數字典
        """
        # 這裡可以實現更複雜的參數生成邏輯
        # 暫時返回基本結構
        return {
            'topic': topic,
            'question_index': index,
            'difficulty': 'normal',
            'style': 'default'
        }


class QuestionDistributor:
    """題目分配器
    
    負責將生成的題目按照指定的回合數和每回合題目數進行分配和排序。
    """
    
    def __init__(self, strategy: DistributionStrategy = DistributionStrategy.BALANCED):
        """初始化題目分配器
        
        Args:
            strategy: 分配策略
        """
        self.strategy = strategy
        logger.debug(f"題目分配器初始化，策略: {strategy.value}")
    
    def distribute_questions(self, questions: List[Dict[str, Any]], 
                           rounds: int, questions_per_round: int) -> List[Dict[str, Any]]:
        """分配和排序題目
        
        Args:
            questions: 原始題目列表
            rounds: 回合數
            questions_per_round: 每回合題目數
            
        Returns:
            排序後的題目列表
            
        Raises:
            ValueError: 當參數無效時
        """
        logger.info(f"開始分配題目：{len(questions)} 題 → {rounds} 回合 × {questions_per_round} 題")
        
        if not questions:
            raise ValueError("題目列表不能為空")
        
        if rounds <= 0 or questions_per_round <= 0:
            raise ValueError("回合數和每回合題目數必須大於 0")
        
        total_needed = rounds * questions_per_round
        
        if len(questions) < total_needed:
            logger.warning(f"題目數量不足：需要 {total_needed} 題，僅有 {len(questions)} 題")
            # 可以選擇重複題目或調整回合數
            questions = self._pad_questions(questions, total_needed)
        elif len(questions) > total_needed:
            logger.info(f"題目過多，將從 {len(questions)} 題中選取 {total_needed} 題")
            questions = self._select_questions(questions, total_needed)
        
        # 根據策略分配題目
        if self.strategy == DistributionStrategy.RANDOM:
            ordered_questions = self._random_distribution(questions, rounds, questions_per_round)
        elif self.strategy == DistributionStrategy.BALANCED:
            ordered_questions = self._balanced_distribution(questions, rounds, questions_per_round)
        else:
            # 預設使用平衡分配
            ordered_questions = self._balanced_distribution(questions, rounds, questions_per_round)
        
        logger.info(f"題目分配完成，最終題目數: {len(ordered_questions)}")
        return ordered_questions
    
    def _pad_questions(self, questions: List[Dict[str, Any]], target_count: int) -> List[Dict[str, Any]]:
        """補足題目數量
        
        Args:
            questions: 原始題目列表
            target_count: 目標題目數量
            
        Returns:
            補足後的題目列表
        """
        if len(questions) >= target_count:
            return questions
        
        padded = questions.copy()
        needed = target_count - len(questions)
        
        logger.debug(f"補足題目：需要額外 {needed} 題")
        
        # 重複現有題目來補足
        for i in range(needed):
            original_question = questions[i % len(questions)]
            duplicated_question = original_question.copy()
            duplicated_question['duplicated'] = True
            duplicated_question['original_index'] = i % len(questions)
            padded.append(duplicated_question)
        
        return padded
    
    def _select_questions(self, questions: List[Dict[str, Any]], target_count: int) -> List[Dict[str, Any]]:
        """從題目中選取指定數量
        
        Args:
            questions: 原始題目列表
            target_count: 目標題目數量
            
        Returns:
            選取後的題目列表
        """
        if len(questions) <= target_count:
            return questions
        
        # 隨機選取
        selected = random.sample(questions, target_count)
        logger.debug(f"從 {len(questions)} 題中選取 {target_count} 題")
        
        return selected
    
    def _random_distribution(self, questions: List[Dict[str, Any]], 
                           rounds: int, questions_per_round: int) -> List[Dict[str, Any]]:
        """隨機分配策略
        
        Args:
            questions: 題目列表
            rounds: 回合數
            questions_per_round: 每回合題目數
            
        Returns:
            隨機排序的題目列表
        """
        shuffled = questions.copy()
        random.shuffle(shuffled)
        logger.debug("使用隨機分配策略")
        return shuffled
    
    def _balanced_distribution(self, questions: List[Dict[str, Any]], 
                             rounds: int, questions_per_round: int) -> List[Dict[str, Any]]:
        """平衡分配策略
        
        嘗試在每個回合中均勻分配不同的題型。
        
        Args:
            questions: 題目列表
            rounds: 回合數
            questions_per_round: 每回合題目數
            
        Returns:
            平衡分配的題目列表
        """
        logger.debug("使用平衡分配策略")
        
        # 按題型分組
        topic_groups = {}
        for question in questions:
            topic = question.get('topic', 'unknown')
            if topic not in topic_groups:
                topic_groups[topic] = []
            topic_groups[topic].append(question)
        
        # 為每個回合分配題目
        ordered_questions = []
        
        for round_idx in range(rounds):
            round_questions = []
            
            # 嘗試從每個題型中選取題目
            topics = list(topic_groups.keys())
            random.shuffle(topics)  # 隨機化題型順序
            
            for q_idx in range(questions_per_round):
                topic_idx = q_idx % len(topics)
                topic = topics[topic_idx]
                
                if topic_groups[topic]:
                    question = topic_groups[topic].pop(0)
                    round_questions.append(question)
                else:
                    # 如果該題型已用完，從其他題型選取
                    available_topics = [t for t in topics if topic_groups[t]]
                    if available_topics:
                        backup_topic = random.choice(available_topics)
                        question = topic_groups[backup_topic].pop(0)
                        round_questions.append(question)
            
            # 打亂本回合內的題目順序
            random.shuffle(round_questions)
            ordered_questions.extend(round_questions)
        
        return ordered_questions


class QuestionSorter:
    """題目排序器
    
    提供各種題目排序策略。
    """
    
    @staticmethod
    def sort_by_difficulty(questions: List[Dict[str, Any]], ascending: bool = True) -> List[Dict[str, Any]]:
        """按難度排序
        
        Args:
            questions: 題目列表
            ascending: 是否升序排列
            
        Returns:
            排序後的題目列表
        """
        def get_difficulty_score(question: Dict[str, Any]) -> int:
            """獲取題目難度分數"""
            difficulty = question.get('difficulty', 'normal')
            if difficulty == 'easy':
                return 1
            elif difficulty == 'normal':
                return 2
            elif difficulty == 'hard':
                return 3
            else:
                return 2  # 預設為普通難度
        
        sorted_questions = sorted(questions, key=get_difficulty_score, reverse=not ascending)
        logger.debug(f"按難度排序完成，升序: {ascending}")
        return sorted_questions
    
    @staticmethod
    def sort_by_topic(questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """按題型排序
        
        Args:
            questions: 題目列表
            
        Returns:
            按題型排序的題目列表
        """
        sorted_questions = sorted(questions, key=lambda q: q.get('topic', ''))
        logger.debug("按題型排序完成")
        return sorted_questions
    
    @staticmethod
    def shuffle_questions(questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """隨機打亂題目順序
        
        Args:
            questions: 題目列表
            
        Returns:
            打亂後的題目列表
        """
        shuffled = questions.copy()
        random.shuffle(shuffled)
        logger.debug("題目順序隨機打亂完成")
        return shuffled


class QuestionDistributor:
    """題目分配器（統一介面）
    
    整合題目生成、分配和排序功能的統一介面。
    """
    
    def __init__(self, config: Optional[QuestionGenerationConfig] = None):
        """初始化題目分配器
        
        Args:
            config: 可選的配置
        """
        self.config = config or QuestionGenerationConfig()
        self.generator = QuestionGenerator(self.config)
        self.distributor = QuestionDistributor(self.config.strategy)
        self.sorter = QuestionSorter()
        
        logger.info("題目分配器初始化完成")
    
    def generate_and_distribute(self, selected_data: List[Dict[str, Any]], 
                               rounds: int, questions_per_round: int) -> Tuple[List[Dict[str, Any]], DistributionStats]:
        """生成並分配題目
        
        Args:
            selected_data: 選定的題型數據
            rounds: 回合數
            questions_per_round: 每回合題目數
            
        Returns:
            (排序後的題目列表, 分配統計資訊)
        """
        try:
            # 生成題目
            questions = self.generator.generate_questions(selected_data)
            
            # 分配題目
            ordered_questions = self.distributor.distribute_questions(
                questions, rounds, questions_per_round
            )
            
            # 收集統計資訊
            stats = self._collect_stats(ordered_questions, rounds, questions_per_round)
            
            return ordered_questions, stats
            
        except Exception as e:
            logger.error(f"題目生成和分配失敗: {e}")
            raise
    
    def _collect_stats(self, questions: List[Dict[str, Any]], 
                      rounds: int, questions_per_round: int) -> DistributionStats:
        """收集分配統計資訊
        
        Args:
            questions: 題目列表
            rounds: 回合數
            questions_per_round: 每回合題目數
            
        Returns:
            DistributionStats 統計資訊
        """
        # 統計題型分布
        topic_distribution = {}
        for question in questions:
            topic = question.get('topic', 'unknown')
            topic_distribution[topic] = topic_distribution.get(topic, 0) + 1
        
        return DistributionStats(
            total_questions=len(questions),
            questions_per_round=questions_per_round,
            rounds_count=rounds,
            topic_distribution=topic_distribution
        )


# 便利函數 - 向後相容

def generate_raw_questions(selected_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """生成原始題目列表 (向後相容函數)
    
    Args:
        selected_data: 選定的題型數據
        
    Returns:
        原始題目列表
    """
    generator = QuestionGenerator()
    return generator.generate_questions(selected_data)


def distribute_questions(raw_questions: List[Dict[str, Any]], 
                        rounds: int, questions_per_round: int) -> List[Dict[str, Any]]:
    """分配題目 (向後相容函數)
    
    Args:
        raw_questions: 原始題目列表
        rounds: 回合數
        questions_per_round: 每回合題目數
        
    Returns:
        分配後的題目列表
    """
    distributor_instance = QuestionDistributor()
    return distributor_instance.distribute_questions(raw_questions, rounds, questions_per_round)


# 工廠函數

def create_question_generator(config: Optional[QuestionGenerationConfig] = None) -> QuestionGenerator:
    """創建題目生成器
    
    Args:
        config: 可選配置
        
    Returns:
        QuestionGenerator 實例
    """
    return QuestionGenerator(config)


def create_question_distributor(strategy: DistributionStrategy = DistributionStrategy.BALANCED) -> QuestionDistributor:
    """創建題目分配器
    
    Args:
        strategy: 分配策略
        
    Returns:
        QuestionDistributor 實例
    """
    return QuestionDistributor(strategy)


# 模組資訊
__version__ = "1.0.0"
__author__ = "Math Exercise Generator Team"

logger.debug(f"題目分配器模組載入完成: {__version__}")