#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""三角函數值計算題目生成器模組

本模組提供統一的三角函數值計算題目生成功能，支援度數、弧度和混合模式。
採用預計算查詢表系統提升計算效率，使用sympy確保數學精確性。

主要特色：
- 統一度數/弧度處理架構，避免UI重複選項問題
- 難度控制：normal(3函數) vs hard(6函數)
- 查詢表系統：一次性預計算所有特殊角度值
- 四段式教學邏輯：定義→意義→座標→計算
- 完整的未定義值處理和錯誤恢復機制

使用範例：
    >>> from generators.trigonometry import TrigonometricFunctionGenerator
    >>>
    >>> # 基本使用
    >>> generator = TrigonometricFunctionGenerator()
    >>> question = generator.generate_question()
    >>>
    >>> # 弧度模式
    >>> radian_gen = TrigonometricFunctionGenerator({'angle_mode': 'radian'})
    >>> radian_question = radian_gen.generate_question()
    >>>
    >>> # 困難模式（6個函數）
    >>> hard_gen = TrigonometricFunctionGenerator({'difficulty': 'hard'})
    >>> hard_question = hard_gen.generate_question()

技術架構：
    採用現代化的生成器架構標準，使用sympy確保數學計算的精確性，
    內建完整的Sphinx文檔和類型提示。
"""

import random
from typing import Dict, Any, List, Tuple, Union, Optional
from sympy import sin, cos, tan, cot, sec, csc, pi, latex, simplify

from utils import get_logger
from generators.base import QuestionGenerator, QuestionSize, register_generator


@register_generator
class TrigonometricFunctionGenerator(QuestionGenerator):
    """三角函數值計算題目生成器

    生成特殊角度的三角函數計算題目，支援度數/弧度/混合模式。
    使用預計算查詢表提升性能，sympy確保數學精確性。

    Attributes:
        functions (List[Any]): 根據配置選擇的三角函數列表
        angles_degrees (List[int]): 預定義特殊角度列表
        angle_mode (str): 角度顯示模式 'degree'/'radian'/'mixed'
        trig_values (Dict): 預建構的函數值查詢表

    Example:
        >>> # 基本使用
        >>> gen = TrigonometricFunctionGenerator()
        >>> question = gen.generate_question()
        >>> print(question['question'])
        $\\sin(30^\\circ) = $

        >>> # 弧度模式
        >>> gen = TrigonometricFunctionGenerator({'angle_mode': 'radian'})
        >>> question = gen.generate_question()
        >>> print(question['question'])
        $\\cos(\\frac{\\pi}{6}) = $
    """

    # 使用類內模版組織，避免外部依賴和模版散落問題
    EXPLANATION_TEMPLATES = {
        # 正常情況模版：四段式教學邏輯
        "sin_normal": """因為 $\\sin \\theta = \\frac{{y}}{{r}}$，即單位圓上點的y座標值
當 $\\theta = {angle_display}$ 時，點的座標為 $({x_coord}, {y_coord})$
所以 $\\sin({angle_display}) = {y_coord}$""",

        "cos_normal": """因為 $\\cos \\theta = \\frac{{x}}{{r}}$，即單位圓上點的x座標值
當 $\\theta = {angle_display}$ 時，點的座標為 $({x_coord}, {y_coord})$
所以 $\\cos({angle_display}) = {x_coord}$""",

        "tan_normal": """因為 $\\tan \\theta = \\frac{{y}}{{x}}$，即y座標除以x座標
當 $\\theta = {angle_display}$ 時，點的座標為 $({x_coord}, {y_coord})$
所以 $\\tan({angle_display}) = \\frac{{{y_coord}}}{{{x_coord}}} = {result}$""",

        "cot_normal": """因為 $\\cot \\theta = \\frac{{x}}{{y}}$，即x座標除以y座標
當 $\\theta = {angle_display}$ 時，點的座標為 $({x_coord}, {y_coord})$
所以 $\\cot({angle_display}) = \\frac{{{x_coord}}}{{{y_coord}}} = {result}$""",

        "sec_normal": """因為 $\\sec \\theta = \\frac{{r}}{{x}} = \\frac{{1}}{{\\cos \\theta}}$，即半徑除以x座標
當 $\\theta = {angle_display}$ 時，點的座標為 $({x_coord}, {y_coord})$
所以 $\\sec({angle_display}) = \\frac{{1}}{{{x_coord}}} = {result}$""",

        "csc_normal": """因為 $\\csc \\theta = \\frac{{r}}{{y}} = \\frac{{1}}{{\\sin \\theta}}$，即半徑除以y座標
當 $\\theta = {angle_display}$ 時，點的座標為 $({x_coord}, {y_coord})$
所以 $\\csc({angle_display}) = \\frac{{1}}{{{y_coord}}} = {result}$""",

        # 未定義情況模版：同樣四段式教學邏輯
        "tan_undefined": """因為 $\\tan \\theta = \\frac{{y}}{{x}}$，即y座標除以x座標
當 $\\theta = {angle_display}$ 時，點的座標為 $({x_coord}, {y_coord})$
因為 $x = {x_coord} = 0$，所以 $\\tan({angle_display})$ 無意義""",

        "cot_undefined": """因為 $\\cot \\theta = \\frac{{x}}{{y}}$，即x座標除以y座標
當 $\\theta = {angle_display}$ 時，點的座標為 $({x_coord}, {y_coord})$
因為 $y = {y_coord} = 0$，所以 $\\cot({angle_display})$ 無意義""",

        "sec_undefined": """因為 $\\sec \\theta = \\frac{{1}}{{\\cos \\theta}} = \\frac{{1}}{{x}}$，即1除以x座標
當 $\\theta = {angle_display}$ 時，點的座標為 $({x_coord}, {y_coord})$
因為 $x = {x_coord} = 0$，所以 $\\sec({angle_display})$ 無意義""",

        "csc_undefined": """因為 $\\csc \\theta = \\frac{{1}}{{\\sin \\theta}} = \\frac{{1}}{{y}}$，即1除以y座標
當 $\\theta = {angle_display}$ 時，點的座標為 $({x_coord}, {y_coord})$
因為 $y = {y_coord} = 0$，所以 $\\csc({angle_display})$ 無意義"""
    }

    def __init__(self, options: Dict[str, Any] = None):
        """初始化三角函數計算題目生成器

        設定三角函數計算的參數和配置系統。

        Args:
            options (Dict[str, Any], optional): 生成器配置選項
                angle_mode (str): 角度模式 'degree'/'radian'/'mixed'，預設'degree'
                difficulty (str): 難度等級 'normal'/'hard'，預設'normal'

        Note:
            建立三角函數計算的完整框架：
            - 查詢表系統：一次性建構所有角度，避免重複計算
            - 角度模式：三種模式靈活支援不同教學需求
            - 難度控制：通過函數數量區分normal(3函數)vs hard(6函數)
        """
        super().__init__(options)
        self.logger = get_logger(self.__class__.__name__)

        # 接收和處理配置
        config = options or {}
        if config:
            self.logger.info(f"三角函數生成器接收配置: {config}")

        # 使用function_scope替代difficulty，更清楚表達意圖
        function_scope = config.get("function_scope", "basic")
        if function_scope not in ["basic", "extended"]:
            self.logger.warning(f"無效的function_scope: {function_scope}，使用預設值basic")
            function_scope = "basic"

        # 根據配置設置函數範圍
        if function_scope == "extended":
            self.functions = [sin, cos, tan, cot, sec, csc]
            self.logger.info("使用擴展函數模式(6函數)")
        else:
            self.functions = [sin, cos, tan]
            self.logger.info("使用基礎函數模式(3函數)")

        # 使用所有特殊角度，確保教學完整性和系統穩定性
        self.angles_degrees = [0, 30, 45, 60, 90, 120, 135, 150, 180,
                              210, 225, 240, 270, 300, 315, 330, 360]

        # 角度顯示模式：支援degree/radian/mixed三種模式
        angle_mode = config.get("angle_mode", "degree")
        if angle_mode not in ["degree", "radian", "mixed"]:
            self.logger.warning(f"無效的angle_mode: {angle_mode}，使用預設值degree")
            angle_mode = "degree"

        self.angle_mode = angle_mode

        # 預建構三角函數值查詢表，優化計算效率
        self.trig_values = self._build_unified_trig_table()

        # 預篩選有效組合，替代重試機制
        self.valid_combinations = self._build_valid_combinations()

        self.logger.info(f"統一三角函數生成器初始化完成 - 模式: {self.angle_mode}, 函數範圍: {function_scope}, 有效組合: {len(self.valid_combinations)}")

    def _is_undefined(self, func: Any, angle_deg: int) -> bool:
        """數學常識驅動的未定義值判斷器

        使用數學常識判斷三角函數的未定義情況，基於角度值直接檢查。

        Args:
            func: sympy三角函數物件
            angle_deg: 角度值（度數，必須在0-360範圍內）

        Returns:
            bool: True表示該函數在該角度未定義，False表示有定義

        數學原理：
            未定義情況發生在分母為零的情況：
            - tan θ = sin θ / cos θ：當cos θ = 0時未定義（90°, 270°）
            - cot θ = cos θ / sin θ：當sin θ = 0時未定義（0°, 180°, 360°）
            - sec θ = 1 / cos θ：當cos θ = 0時未定義（90°, 270°）
            - csc θ = 1 / sin θ：當sin θ = 0時未定義（0°, 180°, 360°）

        實現原理：
            使用直接角度判斷的原因：
            1. 特殊角度的未定義情況是數學常識，無需複雜計算
            2. 直接判斷方式簡潔明確
            3. 代碼邏輯清晰，便於理解和維護
        """
        func_name = func.__name__

        # 使用直接的數學常識判斷
        if func_name == "tan" and angle_deg in [90, 270]:
            return True
        elif func_name == "cot" and angle_deg in [0, 180, 360]:
            return True
        elif func_name == "sec" and angle_deg in [90, 270]:
            return True
        elif func_name == "csc" and angle_deg in [0, 180, 360]:
            return True

        return False

    def _build_unified_trig_table(self) -> Dict[Tuple[Any, int], Union[Any, str]]:
        """預計算三角函數值查詢表系統

        一次性建構所有角度和函數組合的查詢表，提升查詢效率。
        將O(log n)的sympy計算優化為O(1)的查表操作。

        Returns:
            Dict[Tuple[Any, int], Union[Any, str]]: 高效查詢表
                鍵: (sympy函數物件, 角度值) 的元組
                值: sympy精確計算結果或"ERROR"（未定義情況）

        設計原因：
            使用預計算查詢表而非即時計算，因為：
            1. 三角函數值計算頻繁，預計算有明顯效益
            2. 特殊角度值固定，查詢表空間成本低
            3. 符合數學教學中的"特殊角度背誦"習慣

        算法細節：
            對每個(函數, 角度)組合：
            1. 先用_is_undefined()快速判斷是否未定義
            2. 若有定義，使用sympy.simplify()確保最簡形式
            3. 存儲結果供後續O(1)查詢使用
        """
        table = {}

        # 對每個(函數, 角度)組合進行精確計算或未定義標記
        for func in self.functions:
            for angle_deg in self.angles_degrees:
                # 檢查未定義情況
                if self._is_undefined(func, angle_deg):
                    table[(func, angle_deg)] = "ERROR"
                else:
                    # 使用sympy確保數學精確性和最簡根式形式
                    angle_rad = angle_deg * pi / 180
                    value = simplify(func(angle_rad))
                    table[(func, angle_deg)] = value

        return table

    def _build_valid_combinations(self) -> List[Tuple[int, Any]]:
        """預篩選有效的角度-函數組合

        建立所有有效的(角度, 函數)組合清單，過濾掉未定義值。
        將重試機制轉換為確定性選擇，從O(n)重試優化為O(1)直接選擇。

        Returns:
            List[Tuple[int, Any]]: 有效組合清單
                元組格式: (角度值, sympy函數物件)

        設計原理:
            使用預篩選策略而非重試機制的原因：
            1. 特殊角度數量有限，預篩選空間成本低
            2. 確定性生成避免重試的性能浪費
            3. 符合數學教學中的"有效範圍"概念

        實現邏輯:
            遍歷所有(角度, 函數)組合，篩選查詢表中非"ERROR"的項目，
            確保每次選擇都能產生有效的數學題目。
        """
        valid_combinations = []

        for angle_deg in self.angles_degrees:
            for func in self.functions:
                # 從查詢表檢查此組合是否有效
                value = self.trig_values.get((func, angle_deg))
                if value != "ERROR":
                    valid_combinations.append((angle_deg, func))

        self.logger.info(f"預篩選完成：{len(valid_combinations)} 個有效組合（總共 {len(self.angles_degrees) * len(self.functions)} 個可能組合）")
        return valid_combinations

    def _get_unit_circle_coordinates(self, angle_deg: int) -> Tuple[Any, Any]:
        """獲取單位圓上指定角度的精確座標點

        使用simplify保持根式形式，避免浮點數表達。
        為解釋生成提供精確的座標值。

        Args:
            angle_deg: 角度值（度數）

        Returns:
            Tuple[Any, Any]: (x, y) 座標的精確表示

        Note:
            使用simplify確保特殊角度的座標以最簡根式形式表示，
            這對教學解釋的準確性至關重要。
        """
        angle_rad = angle_deg * pi / 180
        x = simplify(cos(angle_rad))
        y = simplify(sin(angle_rad))
        return (x, y)

    def _generate_explanation(self, func_name: str, angle_deg: int, value: Union[Any, str],
                            display_as_radian: bool) -> str:
        """根據函數類型選擇合適的解釋模版

        根據函數類型和計算結果選擇合適的解釋模版，
        採用四段式教學邏輯：定義→意義→座標→計算。

        Args:
            func_name: 函數名稱字串
            angle_deg: 角度值（度數）
            value: 計算結果或"ERROR"
            display_as_radian: 是否以弧度顯示

        Returns:
            str: 格式化的解釋字串

        Note:
            使用結構化模版系統，確保解釋邏輯的一致性。
            採用四段式教學邏輯，提供完整的數學推導。
        """
        # 獲取單位圓上精確座標，使用simplify保持根式形式
        x_coord, y_coord = self._get_unit_circle_coordinates(angle_deg)

        # 角度顯示格式：根據display_as_radian決定
        angle_display = latex(angle_deg * pi / 180) if display_as_radian else f"{angle_deg}^\\circ"

        # 根據未定義狀態選擇對應模版
        if func_name in ["sin", "cos"] or value != "ERROR":
            template = self.EXPLANATION_TEMPLATES[f"{func_name}_normal"]
            return template.format(
                angle_display=angle_display,
                x_coord=latex(x_coord),
                y_coord=latex(y_coord),
                result=latex(value)
            )
        else:
            template = self.EXPLANATION_TEMPLATES[f"{func_name}_undefined"]
            return template.format(
                angle_display=angle_display,
                x_coord=latex(x_coord),
                y_coord=latex(y_coord)
            )

    def _build_figure_data(self, angle_deg: int, func_name: str) -> Dict[str, Any]:
        """建構題目圖形數據

        直接使用度數，無需轉換。圖形系統直接接受度數參數。

        Args:
            angle_deg: 角度值（度數）
            func_name: 函數名稱

        Returns:
            Dict[str, Any]: 圖形配置數據
        """
        return {
            'type': 'standard_unit_circle',
            'params': {
                'angle': angle_deg,  # 圖形系統直接接受度數
                'show_coordinates': True,
                'show_angle': True,
                'highlight_function': func_name
            },
            'options': {'scale': 1.0}
        }

    def _build_explanation_figure(self, angle_deg: int, func_name: str) -> Dict[str, Any]:
        """建構專用於詳解的圖形配置

        建構專用於詳解的圖形配置，提供更豐富的視覺元素。

        Args:
            angle_deg: 角度值（度數）
            func_name: 函數名稱

        Returns:
            Dict[str, Any]: 詳解圖形配置數據
        """
        return {
            'type': 'standard_unit_circle',
            'params': {
                'variant': 'explanation',  # 詳解模式
                'angle': angle_deg,
                'show_coordinates': True,
                'show_angle': True,
                'show_point': True,
                'show_radius': True,
                'highlight_function': func_name
            },
            'options': {'scale': 1.2}  # 詳解圖稍大
        }

    def get_grade(self) -> str:
        """獲取適用年級"""
        return "G10S2"  # 高一下學期（三角函數）

    def get_figure_data_question(self) -> Optional[Dict[str, Any]]:
        """獲取題目圖形數據

        根據當前生成的角度和函數參數建構單位圓圖形配置。
        圖形包含角度標記、函數高亮和基礎視覺元素。

        Returns:
            Optional[Dict[str, Any]]: 圖形配置字典，包含以下鍵值：
                type (str): 圖形類型 'standard_unit_circle'
                params (Dict): 圖形參數，包含角度、顯示選項等
                options (Dict): 渲染選項，如縮放比例

            如果當前無生成參數則返回None確保系統穩定性。

        Note:
            依賴 generate_question() 過程中設置的 _current_angle 和 _current_func。
            圖形系統直接接受度數參數，無需角度轉換。

        Example:
            >>> gen = TrigonometricFunctionGenerator()
            >>> gen._current_angle = 30
            >>> gen._current_func = 'sin'
            >>> figure_data = gen.get_figure_data_question()
            >>> figure_data['params']['angle']
            30
        """
        if hasattr(self, '_current_angle') and hasattr(self, '_current_func'):
            return self._build_figure_data(self._current_angle, self._current_func)
        return None

    def get_figure_data_explanation(self) -> Optional[Dict[str, Any]]:
        """獲取解釋圖形數據

        返回詳解專用的單位圓圖形，含更豐富的視覺元素。
        比題目圖形增加座標顯示、點標記、半徑線等。

        Returns:
            Optional[Dict[str, Any]]: 詳解圖形配置字典，包含：
                type (str): 'standard_unit_circle'
                params (Dict): 詳解模式參數，variant='explanation'
                options (Dict): 渲染選項，scale=1.2

        Note:
            依賴當前生成狀態，若無則返回None。
            詳解圖形比題目圖形提供更多視覺資訊。
        """
        if hasattr(self, '_current_angle') and hasattr(self, '_current_func'):
            return self._build_explanation_figure(self._current_angle, self._current_func)
        return None

    def _generate_core_logic(self, angle_deg: int, func: Any, value: Union[Any, str]) -> Dict[str, Any]:
        """建構完整的題目回應數據

        設置當前生成參數並建構題目，圖形數據由基類統一處理。

        設計變更:
            - 移除直接圖形設置，避免與基類metadata衝突
            - 新增狀態保存機制，供圖形方法使用
            - 簡化返回邏輯，依賴基類統一處理

        Args:
            angle_deg (int): 角度值（度數）
            func (Any): sympy三角函數物件
            value (Union[Any, str]): 計算結果或"ERROR"

        Returns:
            Dict[str, Any]: 題目數據字典，圖形由基類metadata處理
        """
        # 設置當前參數供圖形方法使用
        self._current_angle = angle_deg
        self._current_func = func.__name__
        # 角度模式處理邏輯
        if self.angle_mode == "mixed":
            display_as_radian = random.choice([True, False])
        elif self.angle_mode == "radian":
            display_as_radian = True
        else:  # degree
            display_as_radian = False

        # 題目格式化邏輯
        if display_as_radian:
            angle_rad = angle_deg * pi / 180
            question = f"$\\begin{{aligned}}&\\{func.__name__}({latex(angle_rad)}) \\\\ &= \\end{{aligned}}$"
        else:
            question = f"$\\begin{{aligned}}&\\{func.__name__}({angle_deg}^\\circ) \\\\ &= \\end{{aligned}}$"

        # 答案處理邏輯
        if value == "ERROR":
            answer = "無意義"
        else:
            answer = f"${latex(value)}$"

        # 簡化返回邏輯，圖形數據由基類統一處理
        return {
            "question": question,
            "answer": answer,
            "explanation": self._generate_explanation(func.__name__, angle_deg, value, display_as_radian),
            **self._get_standard_metadata()  # 統一metadata處理，包含圖形數據
        }

    def _get_fallback_question(self) -> Dict[str, Any]:
        """提供系統穩定性的後備機制

        確保系統穩定性，避免生成失敗時崩潰。提供可靠的後備機制。

        Returns:
            Dict[str, Any]: 預設題目數據

        Note:
            保持與正常題目相同的元數據格式，確保系統一致性。
        """
        return {
            'question': "計算：$\\sin(30^\\circ)$",
            'answer': "$\\frac{1}{2}$",
            'explanation': "因為 $\\sin \\theta = \\frac{y}{r}$，在單位圓上點 $(\\frac{\\sqrt{3}}{2}, \\frac{1}{2})$ 的y座標值為 $\\frac{1}{2}$",
            'figure_data_question': self._build_figure_data(30, "sin"),
            **self._get_standard_metadata()  # 使用標準化元數據
        }

    def _generate_core_question(self) -> Dict[str, Any]:
        """核心三角函數題目生成邏輯

        使用預篩選確定性生成，從有效組合中直接選擇，避免重試機制。
        採用查詢表系統確保數學精確性和教學邏輯一致性。

        Returns:
            Dict[str, Any]: 包含完整題目資訊的字典

        設計原理:
            使用預篩選策略而非重試機制：
            1. 從 valid_combinations 直接選擇，保證成功
            2. 保持查詢表系統的高效性
            3. 維持所有教學邏輯和圖形支援不變
        """
        # 從預篩選的有效組合中直接選擇，保證成功
        angle_deg, func = random.choice(self.valid_combinations)
        value = self.trig_values.get((func, angle_deg))  # 從查詢表獲取值

        # 建構完整的題目回應數據
        return self._generate_core_logic(angle_deg, func, value)

    def get_category(self) -> str:
        """獲取題目主類別

        Returns:
            str: 主要數學領域分類
        """
        return "三角函數"

    def get_subcategory(self) -> str:
        """獲取題目子類別

        Returns:
            str: 具體的三角函數題型分類
        """
        return "三角函數值計算"  # 統一名稱

    def get_difficulty(self) -> str:
        """獲取題目難度等級

        Returns:
            str: 難度等級標準化名稱
        """
        return "MEDIUM"

    def get_question_size(self) -> int:
        """獲取題目顯示大小

        三角函數計算題目使用SMALL尺寸，適合單一函數值計算。
        遵循QuestionSize標準，返回整數用於PDF佈局空間計算。

        Returns:
            int: 題目大小（QuestionSize.SMALL = 1）
        """
        return QuestionSize.SMALL.value

    def get_subject(self) -> str:
        """獲取科目，數學測驗生成器標準實作"""
        return "數學"

    def get_figure_position(self) -> str:
        """獲取題目圖形位置，單位圓圖形標準配置為右側"""
        return "right"

    def get_explanation_figure_position(self) -> str:
        """獲取解釋圖形位置，單位圓圖形標準配置為右側"""
        return "right"

    @classmethod
    def get_config_schema(cls) -> Dict[str, Dict[str, Any]]:
        """取得三角函數生成器配置描述

        定義用戶可調整的配置選項，UI系統將自動生成對應控件。
        支援函數範圍和角度模式的動態配置，提升教學靈活性。

        Returns:
            Dict[str, Dict[str, Any]]: 配置選項描述字典

        Example:
            >>> schema = TrigonometricFunctionGenerator.get_config_schema()
            >>> schema['function_scope']['options']
            ['basic', 'extended']
            >>> schema['angle_mode']['default']
            'degree'

        Note:
            配置選項說明：
            - function_scope: 控制可用函數範圍，basic限制在教學基礎函數
            - angle_mode: 決定題目中角度的顯示格式，支援混合模式
        """
        return {
            "function_scope": {
                "type": "select",
                "label": "函數範圍",
                "default": "basic",
                "options": ["basic", "extended"],
                # 說明基本與擴展範圍的差異，幫助教師選擇適合的教學內容
                "description": "basic(sin,cos,tan) vs extended(+cot,sec,csc)"
            },
            "angle_mode": {
                "type": "select",
                "label": "角度模式",
                "default": "degree",
                "options": ["degree", "radian", "mixed"],
                # 解釋各模式的教學用途，指導教師根據教學進度選擇
                "description": "degree(角度制) radian(弧度制) mixed(混合)"
            }
        }