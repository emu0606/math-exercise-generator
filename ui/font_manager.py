#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
字體縮放管理器
"""

import os
import json
from utils import get_logger

class FontManager:
    """字體縮放管理器"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.logger = get_logger(self.__class__.__name__)
        
        # 基礎字體大小 (從style.qss動態讀取)
        self.base_font_sizes = self.extract_font_sizes_from_css()
        
        # 縮放設定
        self.current_scale = 1.0  # 100%
        self.scale_steps = [0.5, 0.75, 0.9, 1.0, 1.1, 1.25, 1.5, 2.0]  # 50%-200%
        self.min_scale = 0.5
        self.max_scale = 2.0
        
        # 載入用戶偏好
        self.load_user_preference()
        
    def extract_font_sizes_from_css(self):
        """從CSS文件中動態提取基礎字體大小"""
        import re
        
        css_path = "assets/style.qss"
        default_sizes = {
            'widget': 14,        # 預設值，如果讀取失敗使用
            'title': 18,
            'button': 14,
            'generate_btn': 16,
            'statusbar': 12
        }
        
        try:
            with open(css_path, 'r', encoding='utf-8') as f:
                css_content = f.read()
            
            font_sizes = {}
            
            # 提取 QWidget font-size
            widget_match = re.search(r'QWidget\s*\{[^}]*font-size:\s*(\d+)px', css_content)
            if widget_match:
                font_sizes['widget'] = int(widget_match.group(1))
                self.logger.debug(f"從CSS讀取 QWidget font-size: {font_sizes['widget']}px")
            
            # 提取 QLabel#title font-size
            title_match = re.search(r'QLabel#title\s*\{[^}]*font-size:\s*(\d+)px', css_content)
            if title_match:
                font_sizes['title'] = int(title_match.group(1))
                self.logger.debug(f"從CSS讀取 QLabel#title font-size: {font_sizes['title']}px")
            
            # 提取 QPushButton#generateBtn font-size
            generate_btn_match = re.search(r'QPushButton#generateBtn\s*\{[^}]*font-size:\s*(\d+)px', css_content, re.DOTALL)
            if generate_btn_match:
                font_sizes['generate_btn'] = int(generate_btn_match.group(1))
                self.logger.debug(f"從CSS讀取 QPushButton#generateBtn font-size: {font_sizes['generate_btn']}px")
            
            # 提取 QStatusBar font-size
            statusbar_match = re.search(r'QStatusBar\s*\{[^}]*font-size:\s*(\d+)px', css_content)
            if statusbar_match:
                font_sizes['statusbar'] = int(statusbar_match.group(1))
                self.logger.debug(f"從CSS讀取 QStatusBar font-size: {font_sizes['statusbar']}px")
                
            # 對於QPushButton，如果沒有特定字體大小，使用QWidget的大小
            if 'button' not in font_sizes:
                font_sizes['button'] = font_sizes.get('widget', default_sizes['widget'])
                self.logger.debug(f"QPushButton使用QWidget字體大小: {font_sizes['button']}px")
            
            # 使用預設值填補缺失的項目
            for key, default_value in default_sizes.items():
                if key not in font_sizes:
                    font_sizes[key] = default_value
                    self.logger.warning(f"無法從CSS讀取 {key} 字體大小，使用預設值: {default_value}px")
            
            self.logger.info(f"成功從CSS讀取字體大小: {font_sizes}")
            return font_sizes
            
        except FileNotFoundError:
            self.logger.error(f"CSS文件未找到: {css_path}，使用預設字體大小")
            return default_sizes
        except Exception as e:
            self.logger.error(f"讀取CSS字體大小失敗: {e}，使用預設字體大小")
            return default_sizes
        
    def get_current_scale_index(self):
        """取得目前縮放比例的索引"""
        try:
            return self.scale_steps.index(self.current_scale)
        except ValueError:
            # 如果當前縮放不在預設步驟中，找最接近的
            closest_index = 0
            min_diff = abs(self.scale_steps[0] - self.current_scale)
            for i, scale in enumerate(self.scale_steps):
                diff = abs(scale - self.current_scale)
                if diff < min_diff:
                    min_diff = diff
                    closest_index = i
            return closest_index
            
    def apply_font_scale(self, scale_factor):
        """套用字體縮放"""
        # 輸入驗證
        if not self.validate_scale_value(scale_factor):
            self.logger.warning(f"無效的縮放比例 {scale_factor}，已限制在 {self.min_scale}-{self.max_scale}")
            scale_factor = max(self.min_scale, min(scale_factor, self.max_scale))
            
        self.current_scale = scale_factor
        
        # 生成動態CSS
        dynamic_css = f"""
        
        /* === 動態字體縮放樣式 === */
        QWidget {{
            font-size: {int(self.base_font_sizes['widget'] * scale_factor)}px;
        }}
        
        QLabel#title {{
            font-size: {int(self.base_font_sizes['title'] * scale_factor)}px;
        }}
        
        QPushButton {{
            font-size: {int(self.base_font_sizes['button'] * scale_factor)}px;
        }}
        
        QPushButton#generateBtn {{
            font-size: {int(self.base_font_sizes['generate_btn'] * scale_factor)}px;
        }}
        
        QCheckBox {{
            font-size: {int(self.base_font_sizes['widget'] * scale_factor)}px;
        }}
        
        QLineEdit {{
            font-size: {int(self.base_font_sizes['widget'] * scale_factor)}px;
        }}
        
        QSpinBox {{
            font-size: {int(self.base_font_sizes['widget'] * scale_factor)}px;
        }}
        """
        
        # 重新載入樣式表 (加入錯誤處理)
        try:
            self.main_window.load_stylesheet_with_zoom(dynamic_css)
        except Exception as e:
            self.logger.error(f"載入樣式表失敗: {e}")
            return False
        
        # 更新UI顯示
        try:
            if hasattr(self.main_window, 'font_size_label'):
                self.main_window.font_size_label.setText(f"{int(scale_factor * 100)}%")
        except Exception as e:
            self.logger.warning(f"更新字體大小標籤失敗: {e}")
            
        # 更新按鈕狀態
        try:
            self.update_button_states()
        except Exception as e:
            self.logger.warning(f"更新按鈕狀態失敗: {e}")
        
        # 儲存偏好設定 (非阻塞)
        try:
            self.save_user_preference()
        except Exception as e:
            self.logger.warning(f"儲存偏好設定失敗: {e}")
        
        self.logger.info(f"字體縮放已套用: {int(scale_factor * 100)}%")
        
        # 通知主視窗更新狀態
        if hasattr(self.main_window, 'update_font_operation_status'):
            # 判斷操作類型
            if scale_factor == 1.0:
                operation = 'reset'
            elif hasattr(self, '_last_scale') and scale_factor > self._last_scale:
                operation = 'increase'
            elif hasattr(self, '_last_scale') and scale_factor < self._last_scale:
                operation = 'decrease'
            else:
                operation = 'load'
            
            self.main_window.update_font_operation_status(operation, int(scale_factor * 100))
            
        self._last_scale = scale_factor
        return True
        
    def update_button_states(self):
        """更新按鈕啟用/停用狀態"""
        current_index = self.get_current_scale_index()
        
        # 更新按鈕狀態
        if hasattr(self.main_window, 'zoom_out_btn'):
            self.main_window.zoom_out_btn.setEnabled(current_index > 0)
        if hasattr(self.main_window, 'zoom_in_btn'):
            self.main_window.zoom_in_btn.setEnabled(current_index < len(self.scale_steps) - 1)
            
    def increase_font_size(self):
        """放大字體"""
        current_index = self.get_current_scale_index()
        if current_index < len(self.scale_steps) - 1:
            new_scale = self.scale_steps[current_index + 1]
            self.apply_font_scale(new_scale)
            return True
        return False
            
    def decrease_font_size(self):
        """縮小字體"""
        current_index = self.get_current_scale_index()
        if current_index > 0:
            new_scale = self.scale_steps[current_index - 1]
            self.apply_font_scale(new_scale)
            return True
        return False
            
    def reset_font_size(self):
        """重置字體大小"""
        self.apply_font_scale(1.0)
        
    def get_preferences_file_path(self):
        """取得偏好設定檔案路徑"""
        return os.path.join("data", "user_preferences.json")
        
    def ensure_data_directory(self):
        """確保data目錄存在"""
        data_dir = "data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            self.logger.info(f"建立設定目錄: {data_dir}")
            
    def validate_scale_value(self, scale):
        """驗證縮放值的有效性"""
        if not isinstance(scale, (int, float)):
            return False
        return self.min_scale <= scale <= self.max_scale
    
    def get_default_preferences(self):
        """取得預設偏好設定"""
        return {
            'font_scale': 1.0,
            'version': '1.0',
            'created_at': json.JSONEncoder().encode({}),  # 簡化時間戳
            'ui_settings': {
                'remember_window_size': True,
                'auto_save_preferences': True
            }
        }

    def save_user_preference(self):
        """儲存用戶字體偏好設定"""
        self.ensure_data_directory()
        config_path = self.get_preferences_file_path()
        
        try:
            # 讀取現有設定或使用預設值
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    prefs = json.load(f)
                    # 確保基本結構存在
                    if not isinstance(prefs, dict):
                        prefs = self.get_default_preferences()
            except (FileNotFoundError, json.JSONDecodeError):
                prefs = self.get_default_preferences()
            
            # 更新字體縮放設定
            prefs['font_scale'] = self.current_scale
            prefs['version'] = '1.0'
            
            # 寫入檔案
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(prefs, f, indent=2, ensure_ascii=False)
                
            self.logger.debug(f"字體偏好設定已儲存: {self.current_scale}")
                
        except Exception as e:
            self.logger.error(f"儲存字體偏好設定失敗: {e}")

    def load_user_preference(self):
        """載入用戶字體偏好設定"""
        config_path = self.get_preferences_file_path()
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                prefs = json.load(f)
                
                # 驗證設定檔格式
                if not isinstance(prefs, dict):
                    self.logger.warning("設定檔格式不正確，使用預設值")
                    self.current_scale = 1.0
                    return
                
                scale = prefs.get('font_scale', 1.0)
                
                # 驗證縮放值
                if self.validate_scale_value(scale):
                    self.current_scale = scale
                    self.logger.info(f"載入字體偏好設定: {int(scale * 100)}%")
                else:
                    self.logger.warning(f"載入的字體縮放比例 {scale} 超出範圍 ({self.min_scale}-{self.max_scale})，使用預設值")
                    self.current_scale = 1.0
                    # 修正無效設定
                    self.save_user_preference()
                    
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.logger.info("未找到有效的字體偏好設定檔案，使用預設值")
            self.current_scale = 1.0
            # 建立預設設定檔
            self.save_user_preference()
        except Exception as e:
            self.logger.error(f"載入字體偏好設定失敗: {e}")
            self.current_scale = 1.0
            
    def reset_preferences_to_default(self):
        """重置偏好設定為預設值"""
        try:
            config_path = self.get_preferences_file_path()
            self.ensure_data_directory()
            
            default_prefs = self.get_default_preferences()
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_prefs, f, indent=2, ensure_ascii=False)
                
            self.current_scale = 1.0
            self.logger.info("偏好設定已重置為預設值")
            
        except Exception as e:
            self.logger.error(f"重置偏好設定失敗: {e}")