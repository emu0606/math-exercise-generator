#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""三角函數值計算題目生成器模組

本模組提供統一的三角函數值計算題目生成功能，支援度數、弧度和混合模式。
採用預計算查詢表系統提升計算效率，使用sympy確保數學精確性。

主要特色：
- 統一度數/弧度處理架構，避免UI重複選項問題
- 智能難度控制：normal(3函數) vs hard(6函數)
- 優化查詢表系統：一次性預計算所有特殊角度值
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
from typing import Dict, Any, List, Tuple, Union
from sympy import sin, cos, tan, cot, sec, csc, pi, latex, simplify

from utils import get_logger
from generators.base import QuestionGenerator, QuestionSize, register_generator


@register_generator
class TrigonometricFunctionGenerator(QuestionGenerator):
    """三角函數值計算題目生成器

    生成形如 sin(30°), cos(π/4), tan(60°) 的三角函數計算題目。
    統一處理度數和弧度模式，內部使用度數計算確保精確性，根據配置調整顯示格式。


    Args:
        options (Dict[str, Any], optional): 生成器配置選項
            angle_mode (str): 角度顯示模式 'degree'/'radian'/'mixed'，預設'degree'
            difficulty (str): 難度等級 'normal'/'hard'，預設'normal'

    Returns:
        Dict[str, Any]: 包含完整題目資訊的字典，包含以下欄位：
            question (str): 題目LaTeX字串
            answer (str): 答案LaTeX字串
            explanation (str): 四段式解釋LaTeX字串
            size (int): 題目顯示大小（QuestionSize.SMALL = 1）
            difficulty (str): 難度等級
            category (str): 主類別（三角函數）
            subcategory (str): 子類別（三角函數值計算）
            grade (str): 年級分類（G10S2 = 高一下學期）
            figure_data_question (Dict): 題目圖形配置
            figure_data_explanation (Dict): 詳解圖形配置
            figure_position (str): 圖形位置
            explanation_figure_position (str): 詳解圖形位置

    Example:
        >>> # 基本度數模式
        >>> generator = TrigonometricFunctionGenerator()
        >>> question = generator.generate_question()
        >>> print(question['question'])
        $\\sin(30^\\circ) = $
        >>> print(question['answer'])
        $\\frac{1}{2}$

        >>> # 弧度模式
        >>> radian_gen = TrigonometricFunctionGenerator({'angle_mode': 'radian'})
        >>> question = radian_gen.generate_question()
        >>> print(question['question'])
        $\\cos(\\frac{\\pi}{6}) = $

        >>> # 困難模式（包含cot, sec, csc）
        >>> hard_gen = TrigonometricFunctionGenerator({'difficulty': 'hard'})
        >>> question = hard_gen.generate_question()
        >>> # 可能生成 csc(30°) = 2 等題目

    Attributes:
        logger: 日誌記錄器，用於追蹤生成過程
        functions (List): 根據難度選擇的三角函數列表
        angles_degrees (List[int]): 預定義的特殊角度列表（度數）
        angle_mode (str): 角度顯示模式配置
        trig_values (Dict): 預建構的三角函數值查詢表

    Note:
        使用sympy確保數學計算的精確性，
        所有特殊角度的三角函數值都以最簡根式形式呈現。查詢表設計
        提供高效的數值查詢功能。
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

        使用新架構的參數驗證和配置系統，建立三角函數計算的
        完整數學框架，採用標準化的組織架構。

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

        self.logger.info(f"統一三角函數生成器初始化完成 - 模式: {self.angle_mode}, 函數範圍: {function_scope}")

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

        性能優勢：
            - 時間複雜度：從每次O(log n)的sympy計算降到O(1)的查表
            - 空間換時間：預計算102個值（17角度×6函數），換取生成時的極速響應
            - 數學精確性：sympy確保所有特殊角度值以最簡根式形式存儲

        設計原因：
            使用預計算查詢表而非即時計算，因為：
            1. 三角函數值計算頻繁，預計算有明顯性能優勢
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

    def _generate_core_logic(self, angle_deg: int, func: Any, value: Union[Any, str]) -> Dict[str, Any]:
        """建構完整的題目回應數據

        根據角度模式決定顯示格式，整合題目、答案、解釋和圖形數據。
        處理三種角度模式（degree/radian/mixed）的顯示邏輯。

        Args:
            angle_deg: 角度值（度數）
            func: 三角函數物件
            value: 計算結果或"ERROR"

        Returns:
            Dict[str, Any]: 完整的題目數據

        Note:
            整合所有顯示相關邏輯：
            - 角度顯示格式決策（度數/弧度）
            - 題目和答案的LaTeX格式化
            - 圖形和元數據的完整組裝
        """
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
            question = f"$\\{func.__name__}({latex(angle_rad)}) = $"
        else:
            question = f"$\\{func.__name__}({angle_deg}^\\circ) = $"

        # 答案處理邏輯
        if value == "ERROR":
            answer = "無意義"
        else:
            answer = f"${latex(value)}$"

        # 使用標準化的元數據處理
        return {
            "question": question,
            "answer": answer,
            "explanation": self._generate_explanation(func.__name__, angle_deg, value, display_as_radian),
            "figure_data_question": self._build_figure_data(angle_deg, func.__name__),
            "figure_data_explanation": self._build_explanation_figure(angle_deg, func.__name__),
            "figure_position": "right",
            "explanation_figure_position": "right",
            **self._get_standard_metadata()  # 標準化元數據處理
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

    def generate_question(self) -> Dict[str, Any]:
        """生成一個三角函數計算題目

        使用現代化的重試機制，創建數學上有效且教育價值高的
        三角函數計算題目，確保數學有效性和教育價值。

        Returns:
            Dict[str, Any]: 包含完整題目資訊的字典

        Note:
            使用重試機制和難度篩選邏輯，確保生成的題目有教育價值。
        """
        self.logger.info(f"開始生成三角函數題目 ({self.angle_mode})")

        for attempt in range(100):
            try:
                # 隨機選擇角度和函數
                angle_deg = random.choice(self.angles_degrees)
                func = random.choice(self.functions)
                value = self.trig_values.get((func, angle_deg))  # 從查詢表獲取值

                # 根據難度築選未定義值：normal避免未定義，hard允許未定義
                if value == "ERROR":
                    if len(self.functions) == 3:  # normal難度判斷
                        continue  # 跳過未定義值，重新選擇

                # 建構完整的題目回應數據
                return self._generate_core_logic(angle_deg, func, value)

            except Exception as e:
                self.logger.warning(f"生成嘗試 {attempt+1} 失敗: {str(e)}")
                continue

        # 所有嘗試失敗時使用後備機制確保系統穩定
        self.logger.warning("所有生成嘗試失敗，使用預設題目")
        return self._get_fallback_question()

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