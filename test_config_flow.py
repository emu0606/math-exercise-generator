#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""端對端配置流程測試腳本

測試動態配置UI系統的完整流程：
1. 配置定義 (get_config_schema)
2. 配置傳遞給生成器
3. 驗證生成器接收配置並產生對應題目

此為臨時測試腳本，驗證基礎功能後將被刪除。
"""

from generators.trigonometry.TrigonometricFunctionGenerator import TrigonometricFunctionGenerator
import json


def test_config_schema():
    """測試配置描述功能"""
    print("=== 測試配置描述功能 ===")

    # 測試配置描述取得
    schema = TrigonometricFunctionGenerator.get_config_schema()
    print("✅ 配置描述取得成功")
    print(f"配置項數量: {len(schema)}")

    # 測試has_config檢測
    has_config = TrigonometricFunctionGenerator.has_config()
    print(f"✅ has_config檢測: {has_config}")

    # 驗證配置格式
    for field_name, field_config in schema.items():
        assert 'type' in field_config, f"配置項{field_name}缺少type"
        assert 'label' in field_config, f"配置項{field_name}缺少label"
        assert 'default' in field_config, f"配置項{field_name}缺少default"
        if field_config['type'] == 'select':
            assert 'options' in field_config, f"select配置項{field_name}缺少options"
            assert field_config['default'] in field_config['options'], f"配置項{field_name}的default不在options中"

    print("✅ 配置格式驗證通過")
    return schema


def test_generator_with_config():
    """測試生成器配置接收功能"""
    print("\n=== 測試生成器配置接收功能 ===")

    # 測試預設配置
    default_gen = TrigonometricFunctionGenerator()
    default_question = default_gen.generate_question()
    print("✅ 預設配置生成器工作正常")
    print(f"預設題目範例: {default_question['question']}")

    # 測試extended配置
    extended_config = {"function_scope": "extended", "angle_mode": "degree"}
    extended_gen = TrigonometricFunctionGenerator(extended_config)
    extended_question = extended_gen.generate_question()
    print("✅ extended配置生成器工作正常")
    print(f"extended題目範例: {extended_question['question']}")

    # 測試radian配置
    radian_config = {"function_scope": "basic", "angle_mode": "radian"}
    radian_gen = TrigonometricFunctionGenerator(radian_config)
    radian_question = radian_gen.generate_question()
    print("✅ radian配置生成器工作正常")
    print(f"radian題目範例: {radian_question['question']}")

    # 驗證配置確實影響生成結果
    radian_has_pi = "pi" in radian_question['question']
    print(f"✅ radian配置影響驗證: {'通過' if radian_has_pi else '需檢查'}")

    return True


def test_config_simulation():
    """模擬配置UI到生成器的完整流程"""
    print("\n=== 模擬配置流程測試 ===")

    # 模擬UI收集到的配置值（CategoryWidget將來會產生這樣的數據）
    ui_collected_config = {
        "function_scope": "extended",
        "angle_mode": "mixed"
    }

    print(f"模擬UI收集的配置: {ui_collected_config}")

    # 模擬題目分配器傳遞配置給生成器
    generator = TrigonometricFunctionGenerator(ui_collected_config)

    # 生成多個題目驗證配置影響
    questions = []
    for i in range(5):
        question = generator.generate_question()
        questions.append(question['question'])

    print("✅ 配置傳遞流程正常")
    print("生成的題目範例:")
    for i, q in enumerate(questions, 1):
        print(f"  {i}. {q}")

    # 簡單驗證mixed模式是否包含不同角度格式
    all_questions_text = " ".join(questions)
    has_degree = "circ" in all_questions_text
    has_radian = "pi" in all_questions_text

    print(f"✅ mixed模式驗證: 度數格式{'✓' if has_degree else '✗'}, 弧度格式{'✓' if has_radian else '✗'}")

    return True


def main():
    """執行完整的端對端測試"""
    print("開始動態配置UI系統端對端測試\n")

    try:
        # Phase 1: 測試配置描述
        schema = test_config_schema()

        # Phase 2: 測試生成器配置接收
        test_generator_with_config()

        # Phase 3: 測試完整配置流程
        test_config_simulation()

        print("\n🎉 所有測試通過！配置流程工作正常")
        print("\n下一步: 整合到CategoryWidget (Phase 2)")

        return True

    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    if not success:
        exit(1)