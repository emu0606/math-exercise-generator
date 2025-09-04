#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
批量修復TikZ測試的API不匹配問題
"""

import os
import re
from pathlib import Path

def apply_comprehensive_fixes():
    """應用所有已知的修復"""
    test_dir = Path("tests/test_utils/test_tikz")
    
    # 定義所有需要修復的模式
    fixes = [
        # 1. Union類型實例化問題
        (r'TikZCoordinate\(([^)]+)\)', r'Point(\1)'),
        (r'TikZDistance\(([^)]+)\)', r'\1'),  # 直接使用數值
        
        # 2. 不存在的方法名
        (r'\.render_full_circle\(', r'.render_custom_arc('),
        (r'\.render_circle_arc\(', r'.render_custom_arc('),
        (r'\.render_angle_arc_with_config\(', r'.render_angle_arc('),
        
        # 3. 配置類實例化問題 - ArcConfig直接參數
        (r'ArcConfig\(\s*radius=([^,)]+),\s*color=([^,)]+)[^)]*\)', 
         r'ArcConfig(radius=\1, style_options={"color": \2})'),
        
        # 4. 參數名修正
        (r'config=([a-zA-Z_]+)', r'radius_config=\1.radius'),
        
        # 5. 角度單位問題 (度 -> 弧度)
        (r'start_angle=([0-9]+\.?[0-9]*),\s*end_angle=([0-9]+\.?[0-9]*)', 
         lambda m: f'start_angle={float(m.group(1))*3.14159/180:.4f}, end_angle={float(m.group(2))*3.14159/180:.4f}'),
    ]
    
    for test_file in test_dir.glob("*.py"):
        if test_file.name == "__init__.py":
            continue
            
        print(f"Processing {test_file.name}...")
        
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 應用所有修復
        for i, (pattern, replacement) in enumerate(fixes):
            if callable(replacement):
                content = re.sub(pattern, replacement, content)
            else:
                content = re.sub(pattern, replacement, content)
        
        # 特殊處理：修復import語句
        if 'from utils.tikz.types import' in content:
            content = re.sub(
                r'from utils\.tikz\.types import ([^\\n]*)',
                r'from utils.tikz.types import \1\nfrom utils.geometry.types import Point',
                content
            )
        
        # 如果有修改，保存文件
        if content != original_content:
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  Applied fixes to {test_file.name}")

def create_missing_methods_fixes():
    """為缺失的方法創建修復建議"""
    print("\nCreating fixes for missing methods...")
    
    missing_methods = {
        'render_full_circle': 'render_custom_arc with 0 to 2π',
        'render_circle_arc': 'render_custom_arc', 
        'render_angle_arc_with_config': 'render_angle_arc with radius_config parameter',
        'position_label_auto': 'position_vertex_label_auto',
    }
    
    fixes_content = """
# TikZ API修復指南

## 缺失方法的替代方案

### 1. render_full_circle() -> render_custom_arc()
```python
# 舊代碼
result = renderer.render_full_circle(center=Point(0,0), radius=1.0)

# 新代碼  
result = renderer.render_custom_arc(
    center=Point(0,0), 
    radius=1.0,
    start_angle=0.0, 
    end_angle=6.2832  # 2π
)
```

### 2. render_circle_arc() -> render_custom_arc()
```python
# 直接替換方法名，參數相同
```

### 3. ArcConfig 參數問題
```python
# 舊代碼
config = ArcConfig(radius=0.5, color="blue", line_width="thick")

# 新代碼
config = ArcConfig(
    radius=0.5,
    style_options={
        "color": "blue", 
        "line_width": "thick"
    }
)
```

### 4. 角度單位統一
```python
# TikZ內部使用弧度制，但輸出時轉換為度
# 測試時需要注意這個差異
```
"""
    
    with open("TikZ_API_FIXES.md", 'w', encoding='utf-8') as f:
        f.write(fixes_content)
    
    print("Created TikZ_API_FIXES.md with detailed fix instructions")

def main():
    print("TikZ Test Comprehensive Fix Tool")
    print("=" * 40)
    
    apply_comprehensive_fixes()
    create_missing_methods_fixes()
    
    print("\nBatch fixes completed!")
    print("Run tests to see remaining issues:")
    print("py -m pytest tests/test_utils/test_tikz/ -v --tb=short")

if __name__ == "__main__":
    main()