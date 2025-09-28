#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""三角函數角度轉換生成器

基於舊版已驗證的數學邏輯重寫，整合新架構的統一標準和動態配置UI支援。
生成三種類型的角度轉換題目：
- 第一象限轉換: 將任意角度轉換為0°-90°範圍（70%預設）
- 公式問答: 基本三角函數關係公式題（10%預設）
- 窄角轉換: 進一步轉換為0°-45°範圍（20%預設）

注意：此處為代碼文檔註釋，使用普通度數符號°，非LaTeX語法

新架構整合特點：
- 自動註冊機制：使用@register_generator自動註冊到系統
- 動態配置支援：整合percentage_group控件，支援題型比例調整
- 統一元數據：採用_get_standard_metadata()標準格式
- 完整錯誤處理：現代化的異常處理和日誌記錄
"""

import random
from typing import Dict, Any, List, Tuple

from utils import get_logger
from generators.base import QuestionGenerator, register_generator


@register_generator
class TrigAngleConversionGenerator(QuestionGenerator):
    """三角函數角度轉換生成器

    生成三種類型的三角函數角度轉換題目，使用基礎招式配置處理，
    整合動態配置UI系統支援。

    Args:
        options (Dict[str, Any], optional): 生成器配置選項
            mode_weights (Dict[str, int]): 題型權重配置
                original: 第一象限轉換權重，預設70
                formula: 公式問答權重，預設10
                narrow_angle: 窄角轉換權重，預設20
            angle_range (str): 角度範圍選項，預設"basic"
                basic: -80°~260°範圍
                extended: -180°~540°範圍
                negative: 包含更多負角練習

                注意：參數文檔使用普通度數符號°，題目內容才用LaTeX語法

    Returns:
        Dict[str, Any]: 包含完整題目資訊的字典
            question (str): 題目LaTeX字串
            answer (str): 答案LaTeX字串
            explanation (str): 詳細解析LaTeX字串
            size (int): 題目顯示大小
            difficulty (str): 難度等級
            category (str): 主類別（三角函數）
            subcategory (str): 子類別（三角函數角度轉換）
            grade (str): 年級分類（G10S2 = 高一下學期）

    Example:
        >>> generator = TrigAngleConversionGenerator()
        >>> question = generator.generate_question()
        >>> print(question['question'])
        以 $0\\sim90^\\circ$ 表示 $\\sin(150^\\circ)$
        >>> print(question['answer'])
        $\\sin(30^\\circ)$
    """

    # 三角函數的LaTeX表示映射
    FUNC_LATEX = {
        "sin": "\\sin",
        "cos": "\\cos",
        "tan": "\\tan",
        "cot": "\\cot"
    }

    # 公式問答題庫（從archived版本保留）
    FORMULA_QUESTIONS = {
        "sin": [
            {"question": "\\sin(180^\\circ-\\theta) = ", "answer": "\\sin(\\theta)"},
            {"question": "\\sin(\\theta \\pm 180^\\circ) = ", "answer": "-\\sin(\\theta)"},
            {"question": "\\sin(-\\theta) = ", "answer": "-\\sin(\\theta)"},
            {"question": "\\sin(90^\\circ-\\theta) = ", "answer": "\\cos(\\theta)"},
            {"question": "\\sin(90^\\circ+\\theta) = ", "answer": "\\cos(\\theta)"}
        ],
        "cos": [
            {"question": "\\cos(180^\\circ-\\theta) = ", "answer": "-\\cos(\\theta)"},
            {"question": "\\cos(\\theta \\pm 180^\\circ) = ", "answer": "-\\cos(\\theta)"},
            {"question": "\\cos(-\\theta) = ", "answer": "\\cos(\\theta)"},
            {"question": "\\cos(90^\\circ-\\theta) = ", "answer": "\\sin(\\theta)"},
            {"question": "\\cos(90^\\circ+\\theta) = ", "answer": "-\\sin(\\theta)"}
        ],
        "tan": [
            {"question": "\\tan(180^\\circ-\\theta) = ", "answer": "-\\tan(\\theta)"},
            {"question": "\\tan(\\theta \\pm 180^\\circ) = ", "answer": "\\tan(\\theta)"},
            {"question": "\\tan(-\\theta) = ", "answer": "-\\tan(\\theta)"},
            {"question": "\\tan(90^\\circ-\\theta) = ", "answer": "\\cot(\\theta)"},
            {"question": "\\tan(90^\\circ+\\theta) = ", "answer": "-\\cot(\\theta)"}
        ]
    }

    def __init__(self, options: Dict[str, Any] = None):
        """初始化三角函數角度轉換生成器

        使用基礎招式的配置處理，整合動態配置UI支援。

        Args:
            options (Dict[str, Any], optional): 生成器配置選項
        """
        super().__init__(options)
        self.logger = get_logger(self.__class__.__name__)
        options = options or {}

        # 固定三角函數類型（基於教學標準）
        self.functions = ["sin", "cos", "tan"]

        # percentage_group控件在UI層已驗證總和=100%，此處直接使用配置值
        # 避免在生成器中重複進行總和檢查或正規化處理
        mode_config = options.get("mode_weights", {})
        if mode_config:
            # UI-Backend協作範例：percentage_group已處理總和驗證，後端信任接收
            # 避免重複實施已由UI控件保證的約束條件
            self.mode_weights = [
                mode_config.get("original", 70),
                mode_config.get("formula", 10),
                mode_config.get("narrow_angle", 20)
            ]
            self.logger.info(f"使用自定義題型權重: {self.mode_weights}")
        else:
            # 無配置時使用預設值
            self.mode_weights = [70, 10, 20]

        # 角度範圍配置處理
        self.angle_range_mode = options.get("angle_range", "basic")
        self._setup_angle_ranges()

        self.logger.info("三角函數角度轉換生成器初始化完成")

    def _setup_angle_ranges(self):
        """設置角度範圍

        統一使用 -80° 到 260° 基礎範圍，避免90度的倍數。
        角度範圍模式只影響是否添加週期性旋轉：
        - basic: 直接使用基礎角度
        - extended: 基礎角度 + 隨機旋轉圈數
        """
        # 統一基礎角度範圍（來自舊版驗證的有效範圍）
        min_angle, max_angle = -80, 260

        # 生成基本角度列表，避開90度的倍數
        self.base_angles = [angle for angle in range(min_angle, max_angle + 1, 10)
                           if angle % 90 != 0]

        # 日誌訊息使用普通度數符號，不用LaTeX語法（日誌是給終端機看的）
        self.logger.info(f"設定基礎角度範圍: {min_angle}°到{max_angle}°，共{len(self.base_angles)}個角度")
        self.logger.info(f"角度範圍模式: {self.angle_range_mode}")

    @classmethod
    def get_config_schema(cls):
        """提供動態配置UI描述

        定義percentage_group控件和其他配置選項，支援教師調整題型比例。

        Returns:
            Dict[str, Any]: 配置選項描述字典
        """
        return {
            "mode_weights": {
                "type": "percentage_group",
                "label": "題型比例分配",
                "description": "調整三種題型的出現頻率，總和自動保持為100%",
                "items": {
                    "original": {
                        "label": "0~90°轉換",
                        "default": 70
                    },
                    "formula": {
                        "label": "公式問答",
                        "default": 10
                    },
                    "narrow_angle": {
                        "label": "0~45°轉換",
                        "default": 20
                    }
                }
            },
            "angle_range": {
                "type": "select",
                "label": "角度範圍",
                "options": ["basic", "extended"],
                "default": "basic",
                "description": "basic(-80°~260°)，extended(基礎角度+n*360°)",
                # 重新設計：basic直接使用基礎角度，extended加上隨機旋轉
            }
        }

    def generate_question(self) -> Dict[str, Any]:
        """生成題目的主要方法

        使用重試機制和完整錯誤處理，確保題目生成的穩定性。
        採用三層保護：重試機制 → 異常捕獲 → 後備題目。

        Returns:
            Dict[str, Any]: 包含完整題目資訊的字典
        """
        self.logger.info("開始生成三角函數角度轉換題目")

        # 重試機制確保生成穩定性
        for attempt in range(10):
            try:
                # 使用配置的權重選擇題型
                mode = random.choices(
                    ["original", "formula", "narrow_angle"],
                    weights=self.mode_weights
                )[0]

                # 根據題型調用對應方法
                if mode == "original":
                    result = self._generate_original_question()
                elif mode == "formula":
                    result = self._generate_formula_question()
                else:  # narrow_angle
                    result = self._generate_narrow_angle_question()

                # 驗證生成結果的完整性
                if self._is_valid_result(result):
                    self.logger.info(f"題目生成成功（嘗試 {attempt + 1} 次）")
                    return result
                else:
                    self.logger.warning(f"生成結果驗證失敗，重試（嘗試 {attempt + 1}）")
                    continue

            except Exception as e:
                self.logger.warning(f"生成嘗試 {attempt + 1} 失敗: {str(e)}")
                if attempt < 9:  # 不是最後一次嘗試
                    continue

        # 所有嘗試失敗時使用後備機制確保系統穩定
        self.logger.warning("所有生成嘗試失敗，使用預設題目")
        return self._get_fallback_question()

    def _generate_original_question(self) -> Dict[str, Any]:
        """生成第一象限轉換題

        將任意角度的三角函數值轉換為第一象限（0° - 90°）的等價表示。

        根據 angle_range_mode 決定是否包含週期性旋轉：
        - basic: 直接使用基礎角度 (-80° ~ 260°)
        - extended: 基礎角度 + 隨機旋轉圈數

        Returns:
            Dict[str, Any]: 第一象限轉換題目字典
        """
        func = random.choice(self.functions)
        func_latex = self.FUNC_LATEX[func]

        # 選擇基本角度（basic模式需要篩選避免廢問題）
        if self.angle_range_mode == "basic":
            # basic模式：排除第一象限角度 (0°~90°)，因為它們已經在目標範圍內，會造成廢問題
            # 例：「以0~90°表示 sin(60°)」答案就是 sin(60°)，沒有教學意義
            valid_angles = [angle for angle in self.base_angles if not (0 < angle <= 90)]
            base_angle = random.choice(valid_angles)
            turns = 0
            question_angle = base_angle
        else:  # extended模式
            base_angle = random.choice(self.base_angles)
            turns = random.choice([t for t in range(-4, 5) if t != 0])
            question_angle = base_angle + turns * 360

        # 確保tan函數角度的有效性
        if func == "tan" and (question_angle % 180 in [90, -90]):
            question_angle += 10  # 避開tan的不連續點

        # 執行第一象限轉換
        first_quad_angle, sign = self._convert_to_first_quadrant(base_angle, func)

        # 構建題目和答案
        sign_text = "-" if sign == -1 else ""
        question_text = f"以 $0\\sim90^\\circ$ 表示 ${func_latex}({question_angle}^\\circ)$"
        answer_text = f"${sign_text}{func_latex}({first_quad_angle}^\\circ)$"

        # 生成解釋
        explanation_text = self._generate_first_quadrant_explanation(
            func, question_angle, base_angle, first_quad_angle, sign, turns
        )

        return {
            "question": question_text,
            "answer": answer_text,
            "explanation": explanation_text,
            "figure_data_question": None,
            "figure_data_explanation": None,
            **self._get_standard_metadata()
        }

    def _generate_formula_question(self) -> Dict[str, Any]:
        """生成公式問答題

        從內建的公式題庫中隨機選擇一個公式問答題，測試學生對
        三角函數基本關係的理解。

        Returns:
            Dict[str, Any]: 公式問答題目字典
        """
        # 選擇一個三角函數
        func = random.choice(self.functions)

        # 從該函數的題庫中隨機選一題
        question_data = random.choice(self.FORMULA_QUESTIONS[func])

        # 使用f字串格式化（基礎招式）
        question_text = f"計算 ${question_data['question']}$"
        answer_text = f"${question_data['answer']}$"

        # 公式問答題不提供詳解
        explanation_text = "公式基本關係題，請熟記三角函數基本公式和變換關係。"

        return {
            "question": question_text,
            "answer": answer_text,
            "explanation": explanation_text,
            "figure_data_question": None,
            "figure_data_explanation": None,
            **self._get_standard_metadata()
        }

    def _generate_narrow_angle_question(self) -> Dict[str, Any]:
        """生成窄角（0° - 45°）轉換題

        將任意角度的三角函數值轉換為窄角（0° - 45°）表示。

        根據 angle_range_mode 決定是否包含週期性旋轉：
        - basic: 直接使用基礎角度 (-80° ~ 260°)
        - extended: 基礎角度 + 隨機旋轉圈數
        需要結合象限轉換和餘角關係。

        Returns:
            Dict[str, Any]: 窄角轉換題目字典
        """
        func = random.choice(self.functions)
        func_latex = self.FUNC_LATEX[func]

        # 選擇基本角度（basic模式需要篩選避免廢問題）
        if self.angle_range_mode == "basic":
            # basic模式：排除窄角範圍內的角度 (10°, 20°, 30°, 40°)，因為它們已經在目標範圍內
            # 例：「以0~45°表示 sin(30°)」答案就是 sin(30°)，沒有轉換意義
            # 保留50°~90°等需要餘角轉換的角度，以及其他象限的所有角度
            valid_angles = [angle for angle in self.base_angles if angle not in [10, 20, 30, 40]]
            base_angle = random.choice(valid_angles)
            turns = 0
            question_angle = base_angle
        else:  # extended模式
            base_angle = random.choice(self.base_angles)
            turns = random.choice([t for t in range(-4, 5) if t != 0])
            question_angle = base_angle + turns * 360

        # 確保tan函數角度的有效性
        if func == "tan" and (question_angle % 180 in [90, -90]):
            question_angle += 10

        # 執行兩階段轉換：第一象限 → 窄角
        first_quad_angle, first_sign = self._convert_to_first_quadrant(base_angle, func)
        narrow_angle, final_sign, new_func = self._convert_to_narrow_angle(
            func, first_quad_angle, first_sign
        )

        # 構建題目和答案
        new_func_latex = self.FUNC_LATEX[new_func]
        sign_text = "-" if final_sign == -1 else ""
        question_text = f"以 $0\\sim45^\\circ$ 表示 ${func_latex}({question_angle}^\\circ)$"
        answer_text = f"${sign_text}{new_func_latex}({narrow_angle}^\\circ)$"

        # 生成解釋
        explanation_text = self._generate_narrow_angle_explanation(
            func, question_angle, base_angle, first_quad_angle, first_sign,
            new_func, narrow_angle, final_sign, turns
        )

        return {
            "question": question_text,
            "answer": answer_text,
            "explanation": explanation_text,
            "figure_data_question": None,
            "figure_data_explanation": None,
            **self._get_standard_metadata()
        }

    def _convert_to_first_quadrant(self, angle: int, func: str) -> Tuple[int, int]:
        """將給定角度轉換為對應的第一象限角，並返回符號

        基於三角函數在各象限的符號規律，將任意角度轉換為第一象限
        的等價角度，並返回相應的符號。

        Args:
            angle (int): 基本角度
            func (str): 三角函數名稱 ("sin", "cos", "tan")

        Returns:
            Tuple[int, int]: (第一象限角度, 符號)，符號為1或-1

        Mathematics:
            基於三角函數的象限特性：
            - 第二象限：sin正，cos負，tan負
            - 第三象限：sin負，cos負，tan正
            - 第四象限：sin負，cos正，tan負
            - 負角：sin負，cos正，tan負
        """
        # 根據象限和函數特性轉換為第一象限角並確定符號
        if 0 <= angle <= 90:  # 第一象限
            return angle, 1

        elif 90 < angle < 180:  # 第二象限
            # sin(180-x) = sin(x), cos(180-x) = -cos(x), tan(180-x) = -tan(x)
            equivalent_angle = 180 - angle
            if func == "sin":
                return equivalent_angle, 1
            else:  # cos or tan
                return equivalent_angle, -1

        elif 180 <= angle < 270:  # 第三象限
            # sin(180+x) = -sin(x), cos(180+x) = -cos(x), tan(180+x) = tan(x)
            equivalent_angle = angle - 180
            if func == "tan":
                return equivalent_angle, 1
            else:  # sin or cos
                return equivalent_angle, -1

        elif 270 <= angle < 360:  # 第四象限
            # sin(360-x) = -sin(x), cos(360-x) = cos(x), tan(360-x) = -tan(x)
            equivalent_angle = 360 - angle
            if func == "cos":
                return equivalent_angle, 1
            else:  # sin or tan
                return equivalent_angle, -1

        else:  # 處理負角 -90 < angle < 0
            # sin(-x) = -sin(x), cos(-x) = cos(x), tan(-x) = -tan(x)
            equivalent_angle = -angle
            if func == "cos":
                return equivalent_angle, 1
            else:  # sin or tan
                return equivalent_angle, -1

    def _convert_to_narrow_angle(self, func: str, angle: int, sign: int) -> Tuple[int, int, str]:
        """將第一象限角度轉換為窄角（0~45度）

        使用餘角關係將第一象限角度進一步轉換為0~45度範圍，
        應用sin(90°-θ) = cos(θ)等餘角公式。

        注意：函數文檔中的數學公式使用普通符號，只有生成的LaTeX內容用$語法。

        Args:
            func (str): 原始三角函數名稱
            angle (int): 第一象限角度（0~90度）
            sign (int): 原始符號（1或-1）

        Returns:
            Tuple[int, int, str]: (窄角度, 最終符號, 新函數名稱)

        Mathematics:
            餘角關係：
            - sin(90°-θ) = cos(θ)
            - cos(90°-θ) = sin(θ)
            - tan(90°-θ) = cot(θ)

            注意：文檔中數學公式使用普通符號，生成的題目內容才用LaTeX語法。
        """
        if 0 <= angle <= 45:
            return angle, sign, func  # 已在窄角範圍內
        else:  # 45 < angle <= 90
            # 應用餘角公式
            new_angle = 90 - angle
            if func == "sin":
                return new_angle, sign, "cos"
            elif func == "cos":
                return new_angle, sign, "sin"
            else:  # tan
                return new_angle, sign, "cot"

    def _generate_first_quadrant_explanation(self, func: str, question_angle: int,
                                           base_angle: int, first_quad_angle: int,
                                           sign: int, turns: int) -> str:
        """生成第一象限轉換的詳細解析

        根據 angle_range_mode 生成不同的解析格式：
        - basic: 直接象限轉換，無週期性說明
        - extended: 先週期性化簡，再象限轉換

        Args:
            func (str): 三角函數名稱
            question_angle (int): 題目角度
            base_angle (int): 基本角度（移除週期後）
            first_quad_angle (int): 第一象限等價角度
            sign (int): 符號（1或-1）
            turns (int): 旋轉圈數

        Returns:
            str: LaTeX格式的詳細解析文字
        """
        func_latex = self.FUNC_LATEX[func]
        explanation = f"${func_latex}({question_angle}^\\circ)"

        # 根據模式決定是否包含週期性說明
        if self.angle_range_mode == "extended" and turns != 0:
            # Extended模式：先處理週期性
            if turns > 0:
                explanation += f" = {func_latex}({question_angle}^\\circ - {turns} \\cdot 360^\\circ) = {func_latex}({base_angle}^\\circ)"
            else:
                explanation += f" = {func_latex}({question_angle}^\\circ + {-turns} \\cdot 360^\\circ) = {func_latex}({base_angle}^\\circ)"
        # Basic模式或extended但turns=0：直接進入象限轉換

        # 第二步：象限轉換
        if 0 <= base_angle <= 90:
            pass  # 已在第一象限，無需轉換
        elif 90 < base_angle < 180:  # 第二象限
            if func == "sin":
                explanation += f" = {func_latex}(180^\\circ - {base_angle}^\\circ) = {func_latex}({first_quad_angle}^\\circ)"
            else:
                explanation += f" = -{func_latex}(180^\\circ - {base_angle}^\\circ) = -{func_latex}({first_quad_angle}^\\circ)"
        elif 180 <= base_angle < 270:  # 第三象限
            if func == "tan":
                explanation += f" = {func_latex}({base_angle}^\\circ - 180^\\circ) = {func_latex}({first_quad_angle}^\\circ)"
            else:
                explanation += f" = -{func_latex}({base_angle}^\\circ - 180^\\circ) = -{func_latex}({first_quad_angle}^\\circ)"
        elif 270 <= base_angle < 360:  # 第四象限
            if func == "cos":
                explanation += f" = {func_latex}(360^\\circ - {base_angle}^\\circ) = {func_latex}({first_quad_angle}^\\circ)"
            else:
                explanation += f" = -{func_latex}(360^\\circ - {base_angle}^\\circ) = -{func_latex}({first_quad_angle}^\\circ)"
        elif -90 < base_angle < 0:  # 負角
            if func == "cos":
                explanation += f" = {func_latex}(-({base_angle}^\\circ)) = {func_latex}({first_quad_angle}^\\circ)"
            else:
                explanation += f" = -{func_latex}(-({base_angle}^\\circ)) = -{func_latex}({first_quad_angle}^\\circ)"

        explanation += "$"
        return explanation

    def _generate_narrow_angle_explanation(self, func: str, original_angle: int,
                                         base_angle: int, first_quadrant_angle: int, first_sign: int,
                                         new_func: str, narrow_angle: int,
                                         new_sign: int, turns: int) -> str:
        """生成窄角轉換的詳細解析

        結合第一象限轉換和餘角關係的完整解析步驟。
        根據 angle_range_mode 生成不同的解析格式。

        Args:
            func (str): 原始三角函數名稱
            original_angle (int): 原始角度
            base_angle (int): 基本角度（移除週期後）
            first_quadrant_angle (int): 第一象限角度
            first_sign (int): 第一階段符號（1或-1）
            new_func (str): 轉換後的三角函數名稱
            narrow_angle (int): 轉換後的0~45度角度
            new_sign (int): 最終符號（1或-1）
            turns (int): 完整轉動圈數

        Returns:
            str: LaTeX格式的詳細解析文字
        """
        # 先生成第一象限轉換的解釋（會根據模式自動調整）
        first_stage = self._generate_first_quadrant_explanation(
            func, original_angle, base_angle, first_quadrant_angle, first_sign, turns
        )

        # 如果角度已經在0~45度範圍內，直接返回
        if first_quadrant_angle <= 45:
            return first_stage

        # 移除末尾的$ 符號
        if first_stage.endswith("$"):
            first_stage = first_stage[:-1]

        # 添加轉換為0~45度的步驟
        func_latex = self.FUNC_LATEX[func]
        new_func_latex = self.FUNC_LATEX[new_func]
        sign_text = "-" if first_sign == -1 else ""
        final_sign_text = "-" if new_sign == -1 else ""

        # 根據函數類型添加餘角轉換步驟
        second_stage = (f" = {sign_text}{func_latex}(90^\\circ - {narrow_angle}^\\circ) = "
                       f"{final_sign_text}{new_func_latex}({narrow_angle}^\\circ)$")

        return first_stage + second_stage

    def _is_valid_result(self, result: Dict[str, Any]) -> bool:
        """驗證生成結果的有效性

        檢查生成的題目是否包含必要欄位且內容非空。

        Args:
            result (Dict[str, Any]): 生成的題目結果

        Returns:
            bool: 結果是否有效
        """
        required_keys = ['question', 'answer', 'explanation']
        return (isinstance(result, dict) and
                all(key in result and result[key] for key in required_keys))

    def get_grade(self) -> str:
        """獲取適用年級"""
        return "G10S2"  # 高一下學期（三角函數）

    def _get_fallback_question(self) -> Dict[str, Any]:
        """提供預設題目確保系統穩定性

        Returns:
            Dict[str, Any]: 預設題目的完整資訊
        """
        return {
            'question': "以 $0\\sim90^\\circ$ 表示 $\\sin(150^\\circ)$",
            'answer': "$\\sin(30^\\circ)$",
            'explanation': "$\\sin(150^\\circ) = \\sin(180^\\circ - 150^\\circ) = \\sin(30^\\circ)$",
            'figure_data_question': None,
            'figure_data_explanation': None,
            **self._get_standard_metadata()
        }

    def get_category(self) -> str:
        """獲取題目主類別"""
        return "三角函數"

    def get_subcategory(self) -> str:
        """獲取題目子類別"""
        return "三角函數角度轉換"

    def get_question_size(self) -> int:
        """獲取題目顯示大小"""
        return 2  # 中等大小，適合角度轉換題目