# 數學測驗生成器 - 可用圖形類型

本文檔列出了數學測驗生成器中所有可用的圖形類型，包括基礎圖形和預定義複合圖形。

---

## 📑 快速導航

### 基礎概念
- [圖形排版位置](#圖形排版位置)
- [渲染選項](#渲染選項)
- [使用示例](#使用示例)
- [擴展說明](#擴展)

### 基礎圖形類型
- [1. 單位圓 (unit_circle)](#1-單位圓-unit_circle)
- [2. 圓形 (circle)](#2-圓形-circle)
- [3. 坐標系 (coordinate_system)](#3-坐標系-coordinate_system)
- [4. 點 (point)](#4-點-point)
- [5. 線段 (line)](#5-線段-line)
- [6. 角度 (angle)](#6-角度-angle)
- [7. 標籤 (label)](#7-標籤-label)
- [8. 基礎三角形 (basic_triangle)](#8-基礎三角形-basic_triangle)
- [9. 圓弧 (arc)](#9-圓弧-arc)
- [10. 函數圖形 (function_plot)](#10-函數圖形-function_plot)

### 複合圖形類型
- [1. 複合圖形 (composite)](#1-複合圖形-composite)

### 預定義複合圖形類型
- [1. 標準單位圓 (standard_unit_circle)](#1-標準單位圓-standard_unit_circle)
- [2. 數線 (number_line)](#2-數線-number_line)
- [3. 預定義三角形 (predefined_triangle)](#3-預定義三角形-predefined_triangle)

---

## 📊 圖形類型快速參考

| 分類 | 圖形類型 | `type` 參數值 | 主要用途 | 詳細說明 |
|------|---------|--------------|---------|---------|
| **基礎** | 單位圓 | `unit_circle` | 三角函數基礎圖形 | [跳轉](#1-單位圓-unit_circle) |
| **基礎** | 圓形 | `circle` | 一般圓形繪製 | [跳轉](#2-圓形-circle) |
| **基礎** | 坐標系 | `coordinate_system` | 座標平面 | [跳轉](#3-坐標系-coordinate_system) |
| **基礎** | 點 | `point` | 標記座標點 | [跳轉](#4-點-point) |
| **基礎** | 線段 | `line` | 直線、射線、線段 | [跳轉](#5-線段-line) |
| **基礎** | 角度 | `angle` | 角度標記弧線 | [跳轉](#6-角度-angle) |
| **基礎** | 標籤 | `label` | 文字標註 | [跳轉](#7-標籤-label) |
| **基礎** | 基礎三角形 | `basic_triangle` | 簡單三角形 | [跳轉](#8-基礎三角形-basic_triangle) |
| **基礎** | 圓弧 | `arc` | 圓弧線段 | [跳轉](#9-圓弧-arc) |
| **基礎** | 函數圖形 | `function_plot` | 繪製數學函數曲線 | [跳轉](#10-函數圖形-function_plot) |
| **複合** | 複合圖形 | `composite` | 組合多個基礎圖形 | [跳轉](#1-複合圖形-composite) |
| **預定義** | 標準單位圓 | `standard_unit_circle` | 完整配置的單位圓 | [跳轉](#1-標準單位圓-standard_unit_circle) |
| **預定義** | 數線 | `number_line` | 對數內插法視覺化 | [跳轉](#2-數線-number_line) |
| **預定義** | 預定義三角形 | `predefined_triangle` | 高度可配置的三角形 | [跳轉](#3-預定義三角形-predefined_triangle) |

---

## 圖形排版位置

生成器可以通過重寫以下方法控制圖形在 PDF 中的排版位置：

### 題目圖形位置 (`get_figure_position()`)
- **`"right"`** (預設): 圖在右側 (40% 寬)，文字在左側 (60% 寬)
- **`"left"`**: 圖在左側，文字在右側
- **`"bottom"`**: 圖在文字下方，使用全寬
- **`"none"`**: 無圖形，文字使用全寬

### 詳解圖形位置 (`get_explanation_figure_position()`)
- **`"right"`** (預設): 圖在右側 (38% 寬)，文字在左側 (58% 寬)
- **`"bottom"`**: 圖在文字下方，使用全寬
- **`"none"`**: 無圖形，文字使用全寬
- ⚠️ **不支援 `"left"` 選項**（與題目圖形不同）

**注意**: 僅當 `get_figure_data_question()` 或 `get_figure_data_explanation()` 返回有效圖形數據時，位置設定才會生效。

---

## 基礎圖形類型

基礎圖形是最基本的圖形元素，可以單獨使用或組合成複合圖形。

### 1. 單位圓 (`unit_circle`)

生成一個單位圓及其上的點、角度等。

**參數**：
```python
{
    'variant': 'question',  # 或 'explanation'
    'angle': 45.0,          # 角度（0-360）
    'show_coordinates': True,  # 是否顯示坐標軸
    'line_color': 'black',  # 圓的顏色
    'point_color': 'red',   # 點的顏色
    'angle_color': 'blue',  # 角度弧的顏色
    'radius': 1.0           # 半徑
}
```

**示例**：
```python
'figure_data_question': {
    'type': 'unit_circle',
    'params': {
        'variant': 'question',
        'angle': 45.0,
        'show_coordinates': True
    },
    'options': {
        'scale': 1.0 # 可選
    }
}
```

### 2. 圓形 (`circle`)

生成一個一般圓形。

**參數**：
```python
{
    'variant': 'question',  # 或 'explanation'
    'radius': 1.0,          # 半徑
    'center_x': 0.0,        # 圓心 x 坐標
    'center_y': 0.0,        # 圓心 y 坐標
    'fill': False,          # 是否填充
    'fill_color': 'white',  # 填充顏色
    'line_color': 'black',  # 線條顏色
    'line_style': 'solid',  # 線條樣式（'solid', 'dashed', 'dotted'）
    'line_width': 'thin'    # 線條寬度（'thin', 'thick', 'ultra thick'）
}
```

**示例**：
```python
'figure_data_question': {
    'type': 'circle',
    'params': {
        'variant': 'question',
        'radius': 2.0,
        'center_x': 1.0,
        'center_y': 1.0,
        'line_color': 'blue'
    },
    'options': {
        'scale': 1.0 # 可選
    }
}
```

### 3. 坐標系 (`coordinate_system`)

生成一個坐標系。

**參數**：
```python
{
    'variant': 'question',      # 或 'explanation'
    'x_range': (-5, 5),         # x 軸顯示範圍 [最小值, 最大值]
    'y_range': (-5, 5),         # y 軸顯示範圍 [最小值, 最大值]
    'show_axes': True,          # 是否顯示坐標軸
    'show_grid': False,         # 是否顯示網格線
    'show_axes_labels': True,   # 是否顯示軸標籤
    'x_label': 'x',            # x 軸標籤文字
    'y_label': 'y',            # y 軸標籤文字
    'axes_color': 'black',     # 坐標軸顏色
    'grid_color': 'lightgray'  # 網格線顏色
}
```

**示例**：
```python
'figure_data_question': {
    'type': 'coordinate_system',
    'params': {
        'variant': 'question',
        'x_range': (-3, 3),
        'y_range': (-3, 3),
        'show_grid': True
    },
    'options': {
        'scale': 1.0 # 可選
    }
}
```

### 4. 點 (`point`)

生成一個點。

**參數**：
```python
{
    'variant': 'question',  # 或 'explanation'
    'x': 0.0,               # x 坐標
    'y': 0.0,               # y 坐標
    'label': None,          # 點的標籤文字（可選）
    'color': 'red',         # 點的顏色
    'size': '2pt',          # 點的大小
    'shape': 'circle'       # 點的形狀 ('circle', 'square', 'triangle')
}
```

**示例**：
```python
'figure_data_question': {
    'type': 'point',
    'params': {
        'variant': 'question',
        'x': 2.0,
        'y': 3.0,
        'label': 'A',
        'color': 'red'
    },
    'options': {
        'scale': 1.0 # 可選
    }
}
```

### 5. 線段 (`line`)

生成一個線段。

**參數**：
```python
{
    'variant': 'question',  # 或 'explanation'
    'x1': 0.0,              # 起點 x 坐標
    'y1': 0.0,              # 起點 y 坐標
    'x2': 1.0,              # 終點 x 坐標
    'y2': 0.0,              # 終點 y 坐標
    'color': 'black',       # 線條顏色
    'style': 'solid',       # 線條樣式（'solid', 'dashed', 'dotted'）
    'width': 'thin',        # 線條寬度（'thin', 'thick', 'ultra thick'）
    'arrow': False,         # 是否顯示箭頭
    'arrow_style': 'stealth',  # 箭頭樣式
    'label': None,          # 標籤（可選）
    'label_position': 'above'  # 標籤位置
}
```

**示例**：
```python
'figure_data_question': {
    'type': 'line',
    'params': {
        'variant': 'question',
        'x1': 0.0,
        'y1': 0.0,
        'x2': 3.0,
        'y2': 4.0,
        'color': 'blue',
        'style': 'dashed',
        'label': 'c'
    },
    'options': {
        'scale': 1.0 # 可選
    }
}
```

### 6. 角度 (`angle`)

生成一個角度弧。

**參數**：
```python
{
    'variant': 'question',  # 或 'explanation'
    'start_angle': 0.0,     # 起始角度
    'end_angle': 90.0,      # 結束角度
    'radius': 1.0,          # 半徑
    'center_x': 0.0,        # 中心 x 坐標
    'center_y': 0.0,        # 中心 y 坐標
    'color': 'blue',        # 弧的顏色
    'style': 'solid',       # 線條樣式
    'width': 'thin',        # 線條寬度
    'show_arrow': True,     # 是否顯示箭頭
    'arrow_style': 'stealth',  # 箭頭樣式
    'label': None,          # 標籤（可選）
    'label_position': 'above right',  # 標籤位置
    'label_distance': 0.5   # 標籤距離中心的比例
}
```

**示例**：
```python
'figure_data_question': {
    'type': 'angle',
    'params': {
        'variant': 'question',
        'start_angle': 0.0,
        'end_angle': 45.0,
        'radius': 0.5,
        'label': '45^\\circ'
    },
    'options': {
        'scale': 1.0 # 可選
    }
}
```

### 7. 標籤 (`label`)

在指定的絕對座標處放置一個可配置樣式的文本標籤。

**參數** (`LabelParams`):
```python
{
    'variant': 'question',      # 或 'explanation' (繼承自 BaseFigureParams)
    'x': 0.0,                   # 標籤節點放置的絕對 x 座標
    'y': 0.0,                   # 標籤節點放置的絕對 y 座標
    'text': '',                 # 標籤文本內容
    'position_modifiers': None, # 可選的 TikZ 定位修飾詞, 例如 'above', 'below left', 'right=0.1cm of other_node_id'
    'anchor': None,             # 可選的標籤節點自身的錨點, 例如 'north west', 'center'
    'rotate': None,             # 可選的旋轉角度 (度)
    'color': 'black',           # 文本顏色
    'font_size': None,          # 可選的 TikZ 字體大小命令, 例如 '\\small', '\\tiny'
    'math_mode': True,          # 文本是否使用數學模式 ($...$)
    'additional_node_options': None # 可選的其他傳遞給 TikZ node 的原始選項字符串, 例如 'draw, circle'
}
```

**示例**：
```python
'figure_data_example': {
    'type': 'label',
    'params': {
        'variant': 'question',
        'x': 2.5,
        'y': -1.0,
        'text': 'P_1',
        'math_mode': True,
        'color': 'purple',
        'font_size': '\\footnotesize',
        'rotate': 15,
        'anchor': 'south east',
        'additional_node_options': 'draw=gray'
    },
    'options': {'scale': 1.0}
}
```

### 8. 基礎三角形 (`basic_triangle`)

繪製一個由三個頂點座標直接定義的基礎三角形。

**參數** (`BasicTriangleParams`):
```python
{
    'variant': 'question',      # 或 'explanation' (繼承自 BaseFigureParams)
    'p1': (0.0, 0.0),           # 頂點 P1 的座標 (x,y)
    'p2': (1.0, 0.0),           # 頂點 P2 的座標 (x,y)
    'p3': (0.0, 1.0),           # 頂點 P3 的座標 (x,y)
    'draw_options': None,       # 可選的 TikZ 繪製選項, 例如 "thick,blue"
    'fill_color': None          # 可選的三角形填充顏色, 例如 "yellow!30"
}
```

**示例**：
```python
'figure_data_example': {
    'type': 'basic_triangle',
    'params': {
        'variant': 'question',
        'p1': [0,0],
        'p2': [3,0],
        'p3': [1.5, 2.5],
        'draw_options': 'blue, thick',
        'fill_color': 'blue!20'
    },
    'options': {'scale': 1.0}
}
```

### 9. 圓弧 (`arc`)

根據中心點、半徑以及起始和結束角度（度數制）繪製一段圓弧。

**參數** (`ArcParams`):
```python
{
    'variant': 'question',      # 或 'explanation' (繼承自 BaseFigureParams)
    'center': (0.0, 0.0),       # 圓弧中心點的座標 (x,y)
    'radius': 1.0,              # 圓弧半徑 (必須為正數)
    'start_angle': 0,           # 起始角度 (度數制, 0-360)
    'end_angle': 90,            # 結束角度 (度數制, 0-360)
    'color': 'black',           # 弧線顏色
    'line_width': 'thick',      # 線條粗細
    'show_endpoints': False,    # 是否標記端點
    'arrow': None               # 箭頭樣式
}
```

**示例**：
```python
'figure_data_example': {
    'type': 'arc',
    'params': {
        'variant': 'question',
        'center': [1,1],
        'radius': 0.5,
        'start_angle': 0,
        'end_angle': 90,            # 90 degrees
        'color': 'orange',
        'line_width': 'very thick'
    },
    'options': {'scale': 1.0}
}
```

### 10. 函數圖形 (`function_plot`)

萬用函數圖形生成器，支援多項式、指數、對數、三角函數等常見高中數學函數。使用 PGFPlots 繪製高品質圖形，自動處理 tan 函數不連續點。

**✨ 新增功能（2025-10-20）**：
- 🎨 **多曲線支援**：在同一圖形中繪製多條不同顏色/樣式的曲線段
- 📍 **點和標籤標註**：直接在圖形上添加點標記和文字標籤
- 🎛️ **靈活座標軸控制**：可完全隱藏座標軸、刻度、網格
- 📏 **可配置尺寸**：自定義圖形寬度和高度
- 🎯 **精確繪圖範圍**：主曲線和額外曲線可分別指定繪製區間

**支援的函數類型**：
- **polynomial**: 多項式函數（如 x² - 2x + 1）
- **exponential**: 指數函數（如 2ˣ, eˣ）
- **logarithmic**: 對數函數（如 log₂(x), ln(x)）
- **trigonometric**: 三角函數（如 sin(x), cos(x), tan(x)）

**基礎參數** (`FunctionPlotParams`):
```python
{
    'function_type': 'polynomial',  # 'polynomial', 'exponential', 'logarithmic', 'trigonometric'

    # 多項式專用（降冪排列）
    'coefficients': [1, -2, 1],     # x^2 - 2x + 1，polynomial 類型必需

    # 指數/對數專用
    'base': 2.0,                    # 底數，None 表示自然底數 e

    # 三角函數專用
    'trig_function': 'sin',         # 'sin', 'cos', 'tan'，trigonometric 類型必需
    'amplitude': 1.0,               # 振幅（可選）
    'period': 6.283185,             # 週期 2π（可選）

    # 座標系統範圍（定義可視區域）
    'x_range': (-5, 5),             # x 軸顯示範圍
    'y_range': (-5, 5),             # y 軸顯示範圍

    # 🆕 圖形尺寸（NEW）
    'figure_width': '10cm',         # 圖形寬度（LaTeX 單位，可用 '0.8\\textwidth'）
    'figure_height': '7cm',         # 圖形高度

    # 🆕 座標軸控制（NEW）
    'axis_lines_style': 'middle',   # 'none', 'middle', 'box', 'left', 'right', 'center'
    'show_ticks': True,             # 是否顯示刻度標記
    'show_grid': True,              # 是否顯示網格
    'show_axes_labels': True,       # 是否顯示座標軸標籤

    # 繪圖選項
    'samples': 100,                 # 採樣點數量（20-500）
    'plot_color': 'blue',           # 主曲線顏色
    'line_thickness': 'thick',      # 主曲線線條粗細
    'show_y_intercept': False,      # 是否標記 y 截距點（可選）
    'y_intercept_color': 'red',     # y 截距標記顏色

    # 🆕 主曲線繪製範圍（NEW）
    'main_plot_domain': None,       # (x_min, x_max)，None 則使用完整 x_range

    # 🆕 多曲線支援（NEW）
    'additional_plots': [           # 額外曲線列表
        {
            'domain': (-1, 2),      # 繪製範圍（必需）
            'color': 'red',         # 顏色（預設 'blue'）
            'thickness': 'very thick',  # 線條粗細（預設 'thick'）
            'samples': 100,         # 採樣點數（預設使用主曲線的 samples）
            'expression': None      # TikZ 表達式（可選，預設使用主函數）
        }
        # 可添加更多曲線...
    ],

    # 🆕 點標註（NEW）
    'plot_points': [                # 標記點列表
        {
            'x': 0, 'y': 0,         # 座標（必需）
            'color': 'red',         # 顏色（預設 'black'）
            'size': '3pt'           # 點大小（預設 '3pt'）
        }
        # 可添加更多點...
    ],

    # 🆕 標籤標註（NEW）
    'plot_labels': [                # 標籤列表
        {
            'x': 0, 'y': 0,         # 位置（必需）
            'text': 'Origin',       # 標籤文字（必需）
            'position': 'above',    # 'above', 'below', 'left', 'right'（預設 'above'）
            'color': 'black',       # 顏色（預設 'black'）
            'math_mode': True       # 是否使用數學模式 $...$ （預設 True）
        }
        # 可添加更多標籤...
    ]
}
```

**示例 1 - 多項式函數**：
```python
'figure_data_question': {
    'type': 'function_plot',
    'params': {
        'function_type': 'polynomial',
        'coefficients': [1, -2, 1],  # x^2 - 2x + 1
        'x_range': (-1, 4),
        'y_range': (-1, 5),
        'show_y_intercept': True
    }
}
```

**示例 2 - 三角函數（自動處理 tan 不連續）**：
```python
'figure_data_question': {
    'type': 'function_plot',
    'params': {
        'function_type': 'trigonometric',
        'trig_function': 'tan',
        'x_range': (-4.71, 4.71),  # -3π/2 到 3π/2
        'y_range': (-4, 4),
        'samples': 200  # tan 建議更多採樣點
    }
}
```

**特點**：
- 使用 PGFPlots 繪製，自動處理邊界條件
- 三角函數使用弧度模式（trig format=rad）
- tan 函數自動添加 `unbounded coords=jump` 處理漸近線
- y 截距標記含安全檢查（超出範圍不顯示）
- 對數函數定義域應從 0.001 開始避免無效值

**詳細參數說明**：`figures/params/function_plot.py`
**使用範例**：`tests/test_function_plot_integration.py`

## 複合圖形類型

複合圖形是由多個基礎圖形組合而成的。

### 1. 複合圖形 (`composite`)

組合多個基礎圖形，處理命名空間和定位問題。

**參數**：
```python
{
    'variant': 'question',  # 或 'explanation'
    'sub_figures': [        # 子圖形列表
        {
            'id': 'figure1',  # 子圖形 ID（用於相對定位）
            'type': 'circle',  # 子圖形類型
            'params': {        # 子圖形參數
                'radius': 1.0,
                'variant': 'question'
                # 其他參數...
            },
            'position': {      # 子圖形位置
                'mode': 'absolute',  # 絕對定位
                'x': 0.0,
                'y': 0.0,
                'anchor': 'center'
            }
        },
        {
            'id': 'figure2',
            'type': 'point',
            'params': {
                'x': 1.0,
                'y': 0.0,
                'variant': 'question'
                # 其他參數...
            },
            'position': {
                'mode': 'relative',  # 相對定位
                'relative_to': 'figure1',  # 相對於哪個子圖形
                'placement': 'right',      # 放置方向
                'distance': '2cm',         # 距離
                'my_anchor': 'center',     # 當前子圖形用於對齊的錨點
                'target_anchor': 'east'    # 相對目標用於對齊的錨點
            }
        }
        # 更多子圖形...
    ]
}
```

**示例**：
```python
'figure_data_question': {
    'type': 'composite',
    'params': {
        'variant': 'question',
        'sub_figures': [
            {
                'id': 'circle1',
                'type': 'circle',
                'params': {
                    'radius': 1.0,
                    'variant': 'question'
                },
                'position': {
                    'mode': 'absolute',
                    'x': 0.0,
                    'y': 0.0
                }
            },
            {
                'id': 'point1',
                'type': 'point',
                'params': {
                    'x': 0.0,
                    'y': 0.0,
                    'label': 'O',
                    'variant': 'question'
                },
                'position': {
                    'mode': 'absolute',
                    'x': 0.0,
                    'y': 0.0
                }
            }
        ]
    },
    'options': {
        'scale': 1.0 # 可選
    }
}
```

## 預定義複合圖形類型

預定義複合圖形是常用的複合圖形，提供簡化的接口。

### 1. 標準單位圓 (`standard_unit_circle`)

生成一個標準單位圓，包含坐標軸、圓、點、角度等。專為三角函數教學設計。

**參數**：
```python
{
    'variant': 'question',      # 或 'explanation'
    'angle': 45.0,              # 標記的角度（度，0-360）
    'show_coordinates': True,    # 是否顯示點的坐標值
    'show_angle': True,         # 是否顯示角度弧線標記
    'show_point': True,         # 是否顯示角度對應的點
    'show_radius': True,        # 是否顯示半徑線
    'line_color': 'black',      # 圓周線條顏色
    'point_color': 'red',       # 角度點顏色
    'angle_color': 'blue',      # 角度弧線顏色
    'radius_color': 'red',      # 半徑線顏色
    'coordinate_color': 'gray', # 坐標標籤顏色
    'radius': 1.0,              # 圓的半徑
    'label_point': True,        # 是否為角度點添加標籤
    'point_label': 'P'          # 角度點的標籤文字
}
```

**示例**：
```python
'figure_data_question': {
    'type': 'standard_unit_circle',
    'params': {
        'variant': 'question',
        'angle': 45.0,
        'show_coordinates': True,
        'show_angle': True,
        'show_point': True,
        'show_radius': True
    },
    'options': {
        'scale': 1.0 # 可選
    }
}
```

### 2. 數線 (`number_line`)

生成水平數線及其刻度和標籤，用於對數內插法等數學概念的視覺化展示。數線由水平線段、三個刻度點（左端、中間、右端）和對應的上下雙層標籤組成。

**參數**：
```python
{
    'lower_value': 2.0,      # 左端點數值（用於計算中間點位置比例）
    'upper_value': 3.0,      # 右端點數值
    'middle_value': 2.5,     # 中間點數值
    'lower_label': '0.3010', # 左端點上方標籤（如對數值）
    'upper_label': '0.4771', # 右端點上方標籤
    'middle_label': '?',     # 中間點上方標籤
    'lower_bottom': '2',     # 左端點下方標籤（如真數）
    'upper_bottom': '3',     # 右端點下方標籤
    'middle_bottom': '2.5',  # 中間點下方標籤
    'line_length': 6.0,      # 數線總長度（TikZ 單位，預設 6.0）
    'tick_height': 0.2       # 刻度線高度（預設 0.2）
}
```

**特點**：
- **線性比例定位**: 中間點位置根據 `(middle_value - lower_value) / (upper_value - lower_value)` 自動計算
- **雙層標註**: 上方標籤用於顯示對數值，下方標籤用於顯示真數
- **自動偏移**: 當中間點靠近端點時（比例 < 0.25 或 > 0.75），標籤自動向外偏移避免重疊
- **輕量設計**: 不依賴複雜參數模型，直接接受字典參數

**示例 1 - 正向內插法（已知真數求對數）**：
```python
'figure_data_question': {
    'type': 'number_line',
    'params': {
        'lower_value': 2,
        'upper_value': 3,
        'middle_value': 2.5,
        'lower_label': '0.3010',     # log(2)
        'upper_label': '0.4771',     # log(3)
        'middle_label': '?',         # 待求的 log(2.5)
        'lower_bottom': '2',
        'upper_bottom': '3',
        'middle_bottom': '2.5',      # 已知真數
        'line_length': 6.0
    },
    'options': {'scale': 1.0}
}
```

**示例 2 - 反向內插法（已知對數求真數）**：
```python
'figure_data_question': {
    'type': 'number_line',
    'params': {
        'lower_value': 2,
        'upper_value': 3,
        'middle_value': 2.45,        # 內部計算用
        'lower_label': '0.3010',
        'upper_label': '0.4771',
        'middle_label': '0.39',      # 已知對數值
        'lower_bottom': '2',
        'upper_bottom': '3',
        'middle_bottom': '?',        # 待求的真數
        'line_length': 6.0
    },
    'options': {'scale': 1.0}
}
```

### 3. 預定義三角形 (`predefined_triangle`)

根據詳細配置繪製三角形，包括其幾何定義、頂點、邊、角和特殊點的標記與樣式。這是一個高度可配置的生成器，用於創建各種帶標註的三角形圖形。

**參數** (`PredefinedTriangleParams`):

由於 `PredefinedTriangleParams` 包含大量可配置字段，這裡僅列出其主要結構和一些關鍵參數。詳細字段請參考源代碼中 `figures.params.PredefinedTriangleParams` 的定義。

```python
{
    "variant": "question", # 或 "explanation"
    "definition_mode": "sss", # 支持 'sss', 'sas', 'asa', 'aas', 'coordinates'
    
    # --- 對應 definition_mode 的幾何參數 ---
    # 例如，對於 'sss' 模式:
    "side_a": 3.0,
    "side_b": 4.0,
    "side_c": 5.0,
    # 例如，對於 'coordinates' 模式:
    # "p1": [0,0], "p2": [5,0], "p3": [0,0],
    # ... (其他模式的參數，如 sas_side1, asa_angle1_rad 等)

    # --- 頂點顯示配置 (以 P1 為例) ---
    "vertex_p1_display_config": {
        "show_point": True,
        "point_style": {"color": "blue"}, # 可配置點的顏色、標記、大小等
        "show_label": True,
        "label_style": {"text_override": "V_alpha", "color": "darkblue"} # 可配置標籤文本、顏色、字體、旋轉等
    },
    # "vertex_p2_display_config": { ... },
    # "vertex_p3_display_config": { ... },
    "default_vertex_labels": ["A", "B", "C"], # 若未在 label_style 中覆蓋文本，則使用這些默認名

    # --- 邊顯示配置 (以 P1P2 邊為例) ---
    "side_p1p2_display_config": { # 通常對應邊 'c'
        "show_label": True,
        "label_text_type": "length", # 可選 'default_name', 'length', 'custom'
        "length_format": "len={value:.1f} units", # 當 label_text_type='length' 時使用
        # "custom_label_text": "Side {name} is {value:.2f}", # 當 label_text_type='custom' 時使用
        "label_style": {"color": "green"} # 可配置標籤樣式
    },
    # "side_p2p3_display_config": { ... }, # 通常對應邊 'a'
    # "side_p3p1_display_config": { ... }, # 通常對應邊 'b'
    "default_side_names": ["c", "a", "b"], # P1P2, P2P3, P3P1 的默認名

    # --- 角顯示配置 (以 P1 頂點處的角為例) ---
    "angle_at_p1_display_config": {
        "show_arc": True,
        "arc_style": {"draw_options": "orange, dashed"}, # 可配置角弧的 TikZ 選項
        "arc_radius_config": 0.6, # 可選 'auto', 浮點數, 或 None (使用全局配置)
        "show_label": True,
        "label_text_type": "value", # 可選 'default_name', 'value', 'custom'
        "value_format": "{value:.0f}°", # 角度值格式
        "label_style": {"color": "purple"}
    },
    # "angle_at_p2_display_config": { ... },
    # "angle_at_p3_display_config": { ... },
    "default_angle_names": ["Alpha", "Beta", "Gamma"], # 角的默認名稱

    # --- 特殊點顯示配置 (以質心為例) ---
    "display_centroid": { # 如果為 null 或省略，則不顯示該特殊點
        "show_point": True,
        "point_style": {"color": "red"},
        "show_label": True,
        "label_text": "G_c", # 覆蓋默認標籤 'G'
        "label_style": {"color": "darkred"}
    },
    # "display_incenter": { ... },
    # "display_circumcenter": { ... },
    # "display_orthocenter": { ... },
    "default_special_point_labels": {"centroid": "G", "incenter": "I", "circumcenter": "O", "orthocenter": "H"},

    # --- 全局默認配置 ---
    "global_angle_arc_radius_config": "auto", # 用於 get_arc_render_params
    "global_label_default_offset": 0.15,    # 用於 get_label_placement_params
    "triangle_draw_options": "black, thin", # 主三角形輪廓的 TikZ 選項
    "triangle_fill_color": None             # 主三角形的填充顏色
}
```

**示例**：
```python
'figure_data_example': {
    'type': 'predefined_triangle',
    'params': {
        'variant': 'question',
        'definition_mode': 'sss',
        'side_a': 3, 'side_b': 4, 'side_c': 5, # 3-4-5 直角三角形
        
        'vertex_p1_display_config': {'show_label': True}, # 顯示 P1 標籤 (默認 'A')
        'vertex_p2_display_config': {'show_label': True}, # 顯示 P2 標籤 (默認 'B')
        'vertex_p3_display_config': {'show_label': True}, # 顯示 P3 標籤 (默認 'C')
        
        'side_p1p2_display_config': {'show_label': True, 'label_text_type': 'value', 'length_format': "c = {value:.0f}"}, # 顯示邊 c 的長度
        
        'angle_at_p3_display_config': { # P3 是直角頂點
            'show_arc': True,
            # 'arc_radius_config': 0.3, # 可以用 is_right_angle_symbol (未來)
            'arc_style': {"draw_options": "blue"},
            'show_label': True,
            'label_text_type': 'custom',
            'custom_label_text': 'Rt.'
            },
        
        'triangle_draw_options': 'very thick, blue'
    },
    'options': {'scale': 1.0}
}
```

## 渲染選項

所有圖形類型都支持以下渲染選項：

```python
'options': {
    'scale': 1.0       # 縮放比例 (用於調整圖形內部相對大小)
}
```

## 使用示例

以下是一個完整的使用示例：

```python
def generate_question(self) -> Dict[str, Any]:
    # 生成題目邏輯...
    
    # 創建圖形數據
    figure_data_question = {
        'type': 'standard_unit_circle',
        'params': {
            'variant': 'question',
            'angle': 45.0,
            'show_coordinates': True
        },
        'options': {
            'scale': 1.0 # 可選
        }
    }
    
    figure_data_explanation = {
        'type': 'standard_unit_circle',
        'params': {
            'variant': 'explanation',
            'angle': 45.0,
            'show_coordinates': True
        },
        'options': {
            'scale': 1.2 # 示例保留 scale
        }
    }
    
    return {
        "question": "題目文字",
        "answer": "答案",
        "explanation": "解析",
        "size": self.get_question_size(),
        "difficulty": "MEDIUM",
        "figure_data_question": figure_data_question,
        "figure_data_explanation": figure_data_explanation
    }
```

## 擴展

如需添加新的圖形類型，請參考 [圖形生成器開發指南](figure_development_guide.md)。