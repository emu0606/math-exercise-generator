#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TikZ異常系統單元測試
測試 utils.tikz.exceptions 模組的異常類和錯誤處理
"""

import pytest
from utils.tikz.exceptions import (
    TikZError, RenderingError, ArcRenderingError, LabelPlacementError,
    CoordinateTransformError, TikZConfigError, TikZSyntaxError,
    invalid_arc_config_error, invalid_label_offset_error, invalid_tikz_position_error
)


class TestTikZErrorHierarchy:
    """TikZ錯誤層次結構測試"""
    
    def test_tikz_error_base_class(self):
        """測試TikZ錯誤基類"""
        error = TikZError("Base TikZ error", {"component": "test"})
        
        assert isinstance(error, Exception)
        assert str(error) == "Base TikZ error"
        assert error.details["component"] == "test"
    
    def test_rendering_error_inheritance(self):
        """測試渲染錯誤繼承"""
        error = RenderingError("operation", "Rendering failed", test_param="value")
        
        assert isinstance(error, TikZError)
        assert isinstance(error, Exception)
        assert error.operation == "operation"
        assert error.reason == "Rendering failed"
        assert error.details["test_param"] == "value"
    
    def test_arc_rendering_error_inheritance(self):
        """測試弧線渲染錯誤繼承"""
        error = ArcRenderingError("arc_draw", "Invalid radius", radius=-1.0)
        
        assert isinstance(error, RenderingError)
        assert isinstance(error, TikZError)
        assert error.operation == "arc_draw"
        assert error.reason == "Invalid radius"
        assert error.details["radius"] == -1.0
    
    def test_label_placement_error_inheritance(self):
        """測試標籤放置錯誤繼承"""
        error = LabelPlacementError("label_position", "Invalid position", position="invalid")
        
        assert isinstance(error, RenderingError)
        assert isinstance(error, TikZError)
        assert error.operation == "label_position"
        assert error.details["position"] == "invalid"
    
    def test_coordinate_transform_error_inheritance(self):
        """測試座標轉換錯誤繼承"""
        error = CoordinateTransformError("transform", "Zero scale factor", scale_x=0.0)
        
        assert isinstance(error, TikZError)
        assert error.details["scale_x"] == 0.0
    
    def test_tikz_config_error_inheritance(self):
        """測試TikZ配置錯誤繼承"""
        error = TikZConfigError("config", "Invalid unit", unit="invalid")
        
        assert isinstance(error, TikZError)
        assert error.details["unit"] == "invalid"
    
    def test_tikz_syntax_error_inheritance(self):
        """測試TikZ語法錯誤繼承"""
        error = TikZSyntaxError("syntax", "Malformed TikZ code", code="\\invalid")
        
        assert isinstance(error, TikZError)
        assert error.details["code"] == "\\invalid"


class TestErrorMessageFormatting:
    """錯誤訊息格式化測試"""
    
    def test_basic_error_message(self):
        """測試基礎錯誤訊息"""
        error = TikZError("Simple error message")
        assert str(error) == "Simple error message"
    
    def test_error_with_details(self):
        """測試帶詳情的錯誤"""
        error = TikZError("Error with details", {
            "parameter": "test_param",
            "value": 123,
            "expected": "positive number"
        })
        
        error_str = str(error)
        assert "Error with details" in error_str
        # 詳情可能以不同格式顯示
        assert error.details["parameter"] == "test_param"
    
    def test_rendering_error_message_format(self):
        """測試渲染錯誤訊息格式"""
        error = RenderingError("arc_rendering", "Radius too small", 
                              radius=0.001, minimum=0.01)
        
        error_str = str(error)
        assert "渲染錯誤" in error_str or "rendering" in error_str.lower()
        assert "arc_rendering" in error_str
        assert "Radius too small" in error_str
    
    def test_detailed_error_information(self):
        """測試詳細錯誤資訊"""
        error = ArcRenderingError(
            operation="draw_angle_arc",
            reason="Invalid angle configuration",
            vertex=(0, 0),
            point1=(1, 0),
            point2=(1, 0),  # 相同點
            radius=0.5
        )
        
        # 檢查所有詳情都被保存
        assert error.details["vertex"] == (0, 0)
        assert error.details["point1"] == (1, 0)
        assert error.details["point2"] == (1, 0)
        assert error.details["radius"] == 0.5


class TestErrorConvenienceFunctions:
    """錯誤便利函數測試"""
    
    def test_invalid_arc_config_error_function(self):
        """測試無效弧線配置錯誤函數"""
        error = invalid_arc_config_error("negative_radius", radius=-0.5)
        
        assert isinstance(error, ArcRenderingError)
        assert error.operation == "arc_config_validation"
        assert "negative_radius" in error.reason
        assert error.details["radius"] == -0.5
    
    def test_invalid_label_offset_error_function(self):
        """測試無效標籤偏移錯誤函數"""
        error = invalid_label_offset_error(offset=-0.1, minimum=0.0)
        
        assert isinstance(error, LabelPlacementError)
        assert error.operation == "label_offset_validation"
        assert error.details["offset"] == -0.1
        assert error.details["minimum"] == 0.0
    
    def test_invalid_tikz_position_error_function(self):
        """測試無效TikZ位置錯誤函數"""
        error = invalid_tikz_position_error("invalid_position", valid_positions=["above", "below"])
        
        assert isinstance(error, TikZConfigError)
        assert error.operation == "position_validation"
        assert error.details["position"] == "invalid_position"
        assert error.details["valid_positions"] == ["above", "below"]


class TestErrorHandlingScenarios:
    """錯誤處理場景測試"""
    
    def test_multiple_error_details(self):
        """測試多個錯誤詳情"""
        error = CoordinateTransformError(
            operation="matrix_transform",
            reason="Singular matrix",
            matrix=[[0, 0], [0, 0]],
            determinant=0.0,
            input_coordinate=(1.0, 1.0)
        )
        
        assert error.details["matrix"] == [[0, 0], [0, 0]]
        assert error.details["determinant"] == 0.0
        assert error.details["input_coordinate"] == (1.0, 1.0)
    
    def test_error_chaining(self):
        """測試錯誤鏈接"""
        try:
            # 模擬內部錯誤
            raise ValueError("Internal calculation error")
        except ValueError as e:
            # 包裝為TikZ錯誤
            tikz_error = TikZError("TikZ operation failed")
            tikz_error.__cause__ = e
            
            assert tikz_error.__cause__ == e
            assert isinstance(tikz_error.__cause__, ValueError)
    
    def test_error_context_information(self):
        """測試錯誤上下文資訊"""
        error = RenderingError(
            operation="complex_diagram_render",
            reason="Multiple rendering failures",
            context={
                "diagram_type": "triangle",
                "num_vertices": 3,
                "num_labels": 6,
                "render_mode": "production"
            }
        )
        
        context = error.details["context"]
        assert context["diagram_type"] == "triangle"
        assert context["num_vertices"] == 3
        assert context["render_mode"] == "production"


class TestExceptionRaising:
    """異常拋出測試"""
    
    def test_raise_tikz_error(self):
        """測試拋出TikZ錯誤"""
        with pytest.raises(TikZError) as exc_info:
            raise TikZError("Test error")
        
        assert str(exc_info.value) == "Test error"
    
    def test_raise_rendering_error(self):
        """測試拋出渲染錯誤"""
        with pytest.raises(RenderingError) as exc_info:
            raise RenderingError("test_op", "Test rendering error")
        
        error = exc_info.value
        assert error.operation == "test_op"
        assert error.reason == "Test rendering error"
    
    def test_raise_arc_rendering_error(self):
        """測試拋出弧線渲染錯誤"""
        with pytest.raises(ArcRenderingError) as exc_info:
            raise ArcRenderingError("arc_test", "Arc error", radius=0.0)
        
        error = exc_info.value
        assert error.operation == "arc_test"
        assert error.details["radius"] == 0.0
    
    def test_raise_label_placement_error(self):
        """測試拋出標籤放置錯誤"""
        with pytest.raises(LabelPlacementError) as exc_info:
            raise LabelPlacementError("label_test", "Label error", text="")
        
        error = exc_info.value
        assert error.operation == "label_test"
        assert error.details["text"] == ""
    
    def test_raise_coordinate_transform_error(self):
        """測試拋出座標轉換錯誤"""
        with pytest.raises(CoordinateTransformError) as exc_info:
            raise CoordinateTransformError("transform_test", "Transform error", scale=0.0)
        
        error = exc_info.value
        assert error.details["scale"] == 0.0
    
    def test_raise_tikz_config_error(self):
        """測試拋出TikZ配置錯誤"""
        with pytest.raises(TikZConfigError) as exc_info:
            raise TikZConfigError("config_test", "Config error", precision=-1)
        
        error = exc_info.value
        assert error.details["precision"] == -1
    
    def test_raise_tikz_syntax_error(self):
        """測試拋出TikZ語法錯誤"""
        with pytest.raises(TikZSyntaxError) as exc_info:
            raise TikZSyntaxError("syntax_test", "Syntax error", tikz_code="\\bad")
        
        error = exc_info.value
        assert error.details["tikz_code"] == "\\bad"


class TestErrorCatching:
    """錯誤捕獲測試"""
    
    def test_catch_specific_error(self):
        """測試捕獲特定錯誤"""
        try:
            raise ArcRenderingError("test", "Arc error")
        except ArcRenderingError as e:
            assert e.operation == "test"
        except Exception:
            pytest.fail("Should catch ArcRenderingError specifically")
    
    def test_catch_base_error(self):
        """測試捕獲基類錯誤"""
        try:
            raise LabelPlacementError("test", "Label error")
        except TikZError as e:
            assert isinstance(e, LabelPlacementError)
        except Exception:
            pytest.fail("Should catch as TikZError base class")
    
    def test_catch_rendering_error_hierarchy(self):
        """測試捕獲渲染錯誤層次"""
        # ArcRenderingError 應該可以被 RenderingError 捕獲
        try:
            raise ArcRenderingError("test", "Arc error")
        except RenderingError as e:
            assert isinstance(e, ArcRenderingError)
        except Exception:
            pytest.fail("ArcRenderingError should be caught as RenderingError")


class TestErrorDebugInformation:
    """錯誤調試資訊測試"""
    
    def test_error_debug_representation(self):
        """測試錯誤調試表示"""
        error = RenderingError(
            operation="debug_test",
            reason="Debug information test",
            debug_info={
                "stack_depth": 5,
                "memory_usage": "12MB",
                "execution_time": "0.05s"
            }
        )
        
        debug_info = error.details["debug_info"]
        assert debug_info["stack_depth"] == 5
        assert debug_info["memory_usage"] == "12MB"
        assert debug_info["execution_time"] == "0.05s"
    
    def test_error_with_traceback_info(self):
        """測試帶回溯資訊的錯誤"""
        import traceback
        
        try:
            # 創建一個有調用棧的錯誤
            def inner_function():
                raise TikZError("Inner error")
            
            def outer_function():
                inner_function()
            
            outer_function()
            
        except TikZError as e:
            tb = traceback.format_exc()
            # 回溯資訊應該包含函數調用
            assert "inner_function" in tb
            assert "outer_function" in tb


class TestErrorRecovery:
    """錯誤恢復測試"""
    
    def test_error_with_recovery_suggestion(self):
        """測試帶恢復建議的錯誤"""
        error = TikZConfigError(
            operation="precision_config",
            reason="Precision out of range",
            precision=-1,
            valid_range=(0, 10),
            suggestion="Use precision between 0 and 10"
        )
        
        assert error.details["precision"] == -1
        assert error.details["valid_range"] == (0, 10)
        assert error.details["suggestion"] == "Use precision between 0 and 10"
    
    def test_error_with_alternative_options(self):
        """測試帶替代選項的錯誤"""
        error = ArcRenderingError(
            operation="arc_style",
            reason="Unsupported arc style",
            style="invalid_style",
            supported_styles=["solid", "dashed", "dotted"],
            alternatives={
                "invalid_style": "dashed",
                "similar_styles": ["solid", "dashed"]
            }
        )
        
        assert error.details["style"] == "invalid_style"
        assert "solid" in error.details["supported_styles"]
        assert error.details["alternatives"]["invalid_style"] == "dashed"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])