#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TikZ測試API修復工具：批量修復常見的API不匹配問題
"""

import os
import re
from pathlib import Path

def fix_tikz_coordinate_usage(file_path):
    """修復TikZCoordinate Union類型的實例化問題"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修復 TikZCoordinate(x, y) -> Point(x, y)
    fixes = [
        (r'TikZCoordinate\(([^)]+)\)', r'Point(\1)'),
        (r'from.*TikZCoordinate', r'from utils.geometry.types import Point'),
    ]
    
    modified = False
    for pattern, replacement in fixes:
        new_content = re.sub(pattern, replacement, content)
        if new_content != content:
            content = new_content
            modified = True
    
    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed TikZCoordinate issues in {file_path}")
        return True
    return False

def fix_method_names(file_path):
    """修復不存在的方法名稱"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 常見的方法名修復
    method_fixes = [
        (r'\.render_circle_arc\(', r'.render_custom_arc('),
        (r'\.render_angle_arc_with_config\(', r'.render_angle_arc('),
        (r'\.position_label_auto\(', r'.position_vertex_label_auto('),
    ]
    
    modified = False
    for pattern, replacement in method_fixes:
        new_content = re.sub(pattern, replacement, content)
        if new_content != content:
            content = new_content
            modified = True
    
    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed method names in {file_path}")
        return True
    return False

def fix_config_parameters(file_path):
    """修復配置類參數問題"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # ArcConfig參數修復示例
    # 將 color="blue", line_width="thick" 等直接參數
    # 轉換為 style_options={"color": "blue", "line_width": "thick"}
    
    # 查找ArcConfig(...)模式
    pattern = r'ArcConfig\s*\(\s*([^)]+)\s*\)'
    matches = re.finditer(pattern, content)
    
    modified = False
    for match in matches:
        params_str = match.group(1)
        
        # 檢查是否有直接的樣式參數
        if 'color=' in params_str or 'line_width=' in params_str or 'style=' in params_str:
            # 需要重構參數
            print(f"Found ArcConfig with direct style params in {file_path}: {params_str}")
            # 這需要更複雜的解析，先標記
            modified = True
    
    return modified

def analyze_test_files():
    """分析測試文件中的問題"""
    test_dir = Path("tests/test_utils/test_tikz")
    
    print("Analyzing TikZ test files for common issues...")
    
    issues = {
        'tikz_coordinate': [],
        'method_names': [],
        'config_params': [],
        'import_errors': []
    }
    
    for test_file in test_dir.glob("*.py"):
        if test_file.name == "__init__.py":
            continue
            
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 檢查TikZCoordinate實例化
        if 'TikZCoordinate(' in content:
            issues['tikz_coordinate'].append(test_file)
        
        # 檢查不存在的方法
        problematic_methods = [
            'render_circle_arc', 'render_angle_arc_with_config',
            'position_label_auto'
        ]
        for method in problematic_methods:
            if f'.{method}(' in content:
                issues['method_names'].append((test_file, method))
        
        # 檢查配置參數問題
        if 'ArcConfig(' in content and ('color=' in content or 'line_width=' in content):
            issues['config_params'].append(test_file)
    
    return issues

def main():
    """主要修復流程"""
    print("TikZ Test API Fix Tool")
    print("=" * 40)
    
    # 分析問題
    issues = analyze_test_files()
    
    print("\nFound issues:")
    print(f"TikZCoordinate instantiation: {len(issues['tikz_coordinate'])} files")
    print(f"Method name problems: {len(issues['method_names'])} cases")  
    print(f"Config parameter issues: {len(issues['config_params'])} files")
    
    # 修復TikZCoordinate問題
    print("\nFixing TikZCoordinate issues...")
    for file_path in issues['tikz_coordinate']:
        fix_tikz_coordinate_usage(file_path)
    
    # 修復方法名問題
    print("\nFixing method name issues...")
    for file_path, method in issues['method_names']:
        fix_method_names(file_path)
    
    print("\nAutomatic fixes completed!")
    print("Some issues may require manual review.")

if __name__ == "__main__":
    main()