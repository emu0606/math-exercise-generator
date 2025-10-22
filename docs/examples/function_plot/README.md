# 函數圖形生成器完整範例

> **專案**: 數學測驗生成器 - 函數圖形生成器
> **最後更新**: 2025-10-17

## 📋 範例說明

本目錄包含函數圖形生成器的完整使用範例，展示如何使用函數圖形生成器來繪製各種數學函數圖形。

## 📁 文件清單

- `complete_example.py` - 完整的 Python 測試程式，展示函數圖形生成器的各種功能
- `complete_example.tex` - 生成的 LaTeX 源碼範例，可用於參考 TikZ/PGFPlots 圖形代碼

## 🎯 範例功能展示

此範例展示了以下功能：

1. **多種函數類型繪製**
   - 多項式函數
   - 三角函數（sin, cos, tan）
   - 指數與對數函數
   - 有理函數

2. **進階繪圖特性**
   - 自動座標軸範圍調整
   - 函數間斷點處理
   - 漸近線自動偵測
   - 多函數疊加繪製

3. **LaTeX 整合**
   - TikZ 圖形生成
   - PGFPlots 函數繪製
   - PDF 輸出品質優化

## 🚀 執行範例

```bash
# 執行 Python 範例
python docs/examples/function_plot/complete_example.py

# 編譯 LaTeX 源碼（需要安裝 LaTeX 環境）
cd docs/examples/function_plot/
xelatex complete_example.tex
```

## 📚 相關文件

- 開發計畫：`docs/history/20251016_函數圖形生成器開發計畫_已完成.md`
- 函數圖形生成器：`figures/function_plot.py`
- 參數模型：`figures/params/function_plot.py`
- 單元測試：`tests/test_function_plot_*.py`

## 💡 使用建議

這些範例文件適合以下用途：

- 學習如何使用函數圖形生成器
- 參考 TikZ/PGFPlots 圖形代碼寫法
- 作為新功能開發的測試基礎
- 教學演示用途

## 🔧 技術細節

- **圖形引擎**: TikZ + PGFPlots
- **座標系統**: Cartesian 2D
- **函數解析**: 支援數學表達式字串
- **輸出格式**: LaTeX/PDF
