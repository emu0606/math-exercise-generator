# Function Plot 生成器增強計畫

> **日期**: 2025-10-20
> **目的**: 增強 function_plot 生成器，支援多曲線、靈活座標軸控制、點標註等功能
> **狀態**: 研擬中

---

## 🎯 需求背景

二次函數極值生成器需要在詳解中繪製示意圖，要求：
1. **多條曲線疊加**：不同顏色的拋物線線段（紅色區間 + 灰色區間外）
2. **隱藏座標軸**：純粹的示意圖，不顯示 xy 軸
3. **點和標籤**：標記頂點、端點及其座標
4. **單一圖形環境**：所有元素在同一個 tikzpicture/axis 中

當前使用 composite 組合多個 function_plot 失敗：
- ❌ 每個 function_plot 創建獨立的 axis 環境
- ❌ 無法疊合，變成多張分離的圖
- ❌ 無法隱藏座標軸（硬編碼 `axis lines=middle`）

---

## 📋 增強方案

### **方案選擇：最小修改增強**

採用向後兼容的設計，添加新參數而不破壞現有功能。

---

## 🔧 具體修改內容

### 1. 參數模型增強 (`figures/params/function_plot.py`)

#### 新增參數：

```python
# === 圖形尺寸控制（新增）===
figure_width: str = Field(
    default='10cm',
    description="圖形寬度（LaTeX 單位，如 '10cm', '0.8\\textwidth'）"
)

figure_height: str = Field(
    default='7cm',
    description="圖形高度（LaTeX 單位，如 '7cm', '0.6\\textwidth'）"
)

# === 座標軸控制 ===
axis_lines_style: Literal['none', 'middle', 'box', 'left', 'right', 'center'] = Field(
    default='middle',
    description="座標軸樣式：none=隱藏, middle=居中穿過, box=邊框"
)

show_ticks: bool = Field(
    default=True,
    description="是否顯示刻度標記"
)

# === 主曲線繪圖範圍（新增）===
main_plot_domain: Optional[Tuple[float, float]] = Field(
    default=None,
    description="主曲線繪製範圍 (x_min, x_max)，None 則使用完整 x_range"
)

# === 多曲線支援 ===
additional_plots: Optional[List[Dict[str, Any]]] = Field(
    default=None,
    description="""額外曲線列表，每個字典包含：
    - domain: (x_min, x_max) - 繪製範圍（必需）
    - color: 顏色（預設 'blue'）
    - thickness: 線條粗細（預設 'thick'）
    - expression: TikZ 表達式（可選，預設使用主函數）
    """
)

# === 點標註支援 ===
plot_points: Optional[List[Dict[str, Any]]] = Field(
    default=None,
    description="""要標記的點列表，每個字典包含：
    - x, y: 座標（必需）
    - color: 顏色（預設 'black'）
    - size: 點大小（預設 '3pt'）
    """
)

plot_labels: Optional[List[Dict[str, Any]]] = Field(
    default=None,
    description="""標籤列表，每個字典包含：
    - x, y: 位置（必需）
    - text: 標籤文字（必需）
    - position: 'above', 'below', 'left', 'right'（預設 'above'）
    - color: 顏色（預設 'black'）
    - math_mode: 是否使用數學模式（預設 True）
    """
)
```

---

### 2. 生成器修改 (`figures/function_plot.py`)

#### 2.1 `_build_axis_options()` 修改

**當前代碼（第 393-398 行）**：
```python
options = [
    f"xmin={xmin:.6g}, xmax={xmax:.6g}",
    f"ymin={ymin:.6g}, ymax={ymax:.6g}",
    "axis lines=middle",  # ← 硬編碼
    "width=10cm, height=7cm"  # ← 硬編碼
]
```

**修改後**：
```python
options = [
    f"xmin={xmin:.6g}, xmax={xmax:.6g}",
    f"ymin={ymin:.6g}, ymax={ymax:.6g}",
    f"axis lines={params.axis_lines_style}",  # ← 可配置
    f"width={params.figure_width}, height={params.figure_height}"  # ← 可配置
]

# 控制刻度顯示
if not params.show_ticks:
    options.append("xtick=\\empty, ytick=\\empty")
```

#### 2.2 `generate_tikz()` 修改 - 支援主曲線 domain 和多曲線

**修改主曲線的 domain 處理**：
```python
# 決定主曲線的繪製範圍
if params.main_plot_domain:
    domain_min, domain_max = params.main_plot_domain
else:
    domain_min, domain_max = params.x_range

plot_options = f"{params.plot_color}, {params.line_thickness}, domain={domain_min}:{domain_max}, samples={params.samples}"
tikz_code = f"\\addplot[{plot_options}] {{{expression}}};\n"
```

**添加額外曲線（新增）**：
```python
# 額外曲線
if params.additional_plots:
    for i, plot_spec in enumerate(params.additional_plots):
        domain = plot_spec['domain']  # 必需參數
        color = plot_spec.get('color', 'blue')
        thickness = plot_spec.get('thickness', 'thick')
        samples = plot_spec.get('samples', params.samples)

        # 使用指定表達式或主函數
        expr = plot_spec.get('expression', expression)

        add_options = f"{color}, {thickness}, domain={domain[0]}:{domain[1]}, samples={samples}"
        tikz_code += f"\\addplot[{add_options}] {{{expr}}};\n"
```

#### 2.3 添加點標註渲染

```python
# 繪製標記點（在 axis 環境內）
if params.plot_points:
    for point in params.plot_points:
        x, y = point['x'], point['y']
        color = point.get('color', 'black')
        size = point.get('size', '3pt')
        tikz_code += f"\\node[circle, fill={color}, inner sep={size}] at (axis cs:{x},{y}) {{}};\n"

# 添加標籤
if params.plot_labels:
    for label in params.plot_labels:
        x, y = label['x'], label['y']
        text = label['text']
        pos = label.get('position', 'above')
        color = label.get('color', 'black')
        math_mode = label.get('math_mode', True)

        # 根據 math_mode 決定是否包裹 $...$
        label_text = f"${text}$" if math_mode else text
        tikz_code += f"\\node[{pos}, color={color}] at (axis cs:{x},{y}) {{{label_text}}};\n"
```

---

## 📊 使用範例

### 範例 1：隱藏座標軸的單一曲線

```python
params = {
    'variant': 'explanation',
    'function_type': 'polynomial',
    'coefficients': [1/3, 0, 0],  # (1/3)x²
    'x_range': (-3, 3),
    'y_range': (-0.5, 3.5),
    'axis_lines_style': 'none',  # ← 隱藏座標軸
    'show_grid': False,
    'show_ticks': False,
    'show_axes_labels': False,
    'plot_color': 'red',
    'line_thickness': 'very thick'
}
```

### 範例 2：多條分段曲線 + 點標註（二次極值示意圖）

```python
params = {
    'variant': 'explanation',
    'function_type': 'polynomial',
    'coefficients': [1/3, 0, 0],  # y = (1/3)x²

    # 座標系範圍（顯示區域）
    'x_range': (-3, 3),
    'y_range': (-0.5, 3.5),

    # 圖形尺寸
    'figure_width': '12cm',
    'figure_height': '8cm',

    # 隱藏所有座標元素
    'axis_lines_style': 'none',
    'show_grid': False,
    'show_ticks': False,
    'show_axes_labels': False,

    # 主曲線：灰色左段
    'main_plot_domain': (-3, -1),  # ← 只繪製 -3 到 -1
    'plot_color': 'gray',
    'line_thickness': 'thick',

    # 額外曲線：紅色中段 + 灰色右段
    'additional_plots': [
        {
            'domain': (-1, 2),
            'color': 'red',
            'thickness': 'very thick'
        },
        {
            'domain': (2, 3),
            'color': 'gray',
            'thickness': 'thick'
        }
    ],

    # 標記點
    'plot_points': [
        {'x': -1, 'y': 1/3, 'color': 'black', 'size': '3pt'},
        {'x': 0, 'y': 0, 'color': 'red', 'size': '3pt'},
        {'x': 2, 'y': 4/3, 'color': 'black', 'size': '3pt'}
    ],

    # 標籤
    'plot_labels': [
        {'x': -1, 'y': 1/3, 'text': '-3', 'position': 'below'},
        {'x': 0, 'y': 0, 'text': '(5, -2)', 'position': 'below', 'color': 'red'},
        {'x': 2, 'y': 4/3, 'text': '7', 'position': 'below'}
    ]
}
```

**生成的 TikZ 代碼**：
```latex
\begin{tikzpicture}
  \begin{axis}[
    xmin=-3, xmax=3, ymin=-0.5, ymax=3.5,
    axis lines=none,
    width=12cm, height=8cm,
    xtick=\empty, ytick=\empty
  ]
    % 主曲線：灰色左段
    \addplot[gray, thick, domain=-3:-1, samples=100] {(1/3)*x^2};

    % 額外曲線：紅色中段
    \addplot[red, very thick, domain=-1:2, samples=100] {(1/3)*x^2};

    % 額外曲線：灰色右段
    \addplot[gray, thick, domain=2:3, samples=100] {(1/3)*x^2};

    % 標記點
    \node[circle, fill=black, inner sep=3pt] at (axis cs:-1, 0.333) {};
    \node[circle, fill=red, inner sep=3pt] at (axis cs:0, 0) {};
    \node[circle, fill=black, inner sep=3pt] at (axis cs:2, 1.333) {};

    % 標籤
    \node[below, color=black] at (axis cs:-1, 0.333) {$-3$};
    \node[below, color=red] at (axis cs:0, 0) {$(5, -2)$};
    \node[below, color=black] at (axis cs:2, 1.333) {$7$};
  \end{axis}
\end{tikzpicture}
```

---

## ✅ 向後兼容性

所有新參數都有預設值，現有代碼無需修改：
- `axis_lines_style='middle'` - 保持現有行為
- `show_ticks=True` - 保持現有行為
- `additional_plots=None` - 不添加額外曲線
- `plot_points=None` - 不添加點標註
- `plot_labels=None` - 不添加標籤

---

## 🚧 實施步驟

1. **修改參數模型**（`figures/params/function_plot.py`）
   - [ ] 添加新參數定義
   - [ ] 添加文檔字串和範例
   - [ ] 添加驗證器（如果需要）

2. **修改生成器**（`figures/function_plot.py`）
   - [ ] 修改 `_build_axis_options()` 支援可配置座標軸
   - [ ] 修改 `generate_tikz()` 支援多曲線
   - [ ] 添加點和標籤渲染邏輯

3. **更新二次極值生成器**（`generators/algebra/quadratic_extremum.py`）
   - [ ] 移除 composite 方式
   - [ ] 改用增強後的 function_plot
   - [ ] 簡化 `_generate_schematic_figure()` 方法

4. **測試**
   - [ ] 單元測試：驗證新參數
   - [ ] 整合測試：生成示意圖
   - [ ] PDF 測試：確認渲染效果

---

## ✅ 設計決策（已確認）

1. **圖形尺寸**：不該硬編碼
   - ✅ 添加 `figure_width` 和 `figure_height` 參數
   - 支援 LaTeX 單位（'10cm', '0.8\\textwidth' 等）

2. **座標系範圍 vs 繪圖範圍**：應該分離
   - ✅ `x_range`, `y_range`：座標系的可視範圍（軸的屬性）
   - ✅ `main_plot_domain`：主曲線的繪製範圍（函數的屬性）
   - ✅ `additional_plots[].domain`：額外曲線的繪製範圍

3. **參數命名**：使用 `domain`
   - ✅ 符合 TikZ/PGFPlots 原生術語
   - ✅ 數學正確性：domain（定義域）vs range（值域）
   - ✅ 避免與 `x_range` 混淆

4. **點的渲染位置**：在 axis 環境內
   - ✅ 使用座標系統，確保位置準確

5. **標籤的 math_mode**：預設啟用
   - ✅ 自動包裹 `$...$`
   - ✅ 添加 `math_mode` 開關允許關閉

---

## 📝 備註

- 此方案避免了 composite 的複雜性
- 保持了 function_plot 的單一職責
- 為未來更複雜的圖形需求打下基礎
- 可考慮未來添加：
  - 填充區域
  - 箭頭標註
  - 虛線樣式
  - 自定義刻度

---

**下一步：等待審核確認後開始實施**
