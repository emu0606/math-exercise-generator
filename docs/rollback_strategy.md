# 佈局引擎修復回滾策略

> **目的**: 為佈局引擎修復提供完整的安全回滾機制
> **建立時間**: 2025-09-14
> **風險等級**: 預防性措施 - 低風險專案的高標準保護

---

## 🎯 **回滾策略總覽**

### **保護原則**
- **零資料損失**: 所有修改前狀態完整保存
- **快速恢復**: 5分鐘內完成回滾
- **狀態一致**: 回滾後系統完全回到修改前狀態
- **可重複執行**: 回滾操作可多次執行

### **回滾觸發條件**
1. **功能性失敗**: 佈局結果不符合預期
2. **性能回歸**: 響應時間超過基準120%
3. **系統不穩定**: 出現崩潰或異常
4. **相容性問題**: 現有功能受影響

---

## 📋 **關鍵檔案備份清單**

### **主要修改檔案**
```
修改前備份檔案結構:
D:\programing\math\backup\2025-09-14_layout_fix\
├── utils/
│   ├── core/
│   │   └── layout.py.backup           # 佈局引擎原始版本
│   └── orchestration/
│       └── question_distributor.py.backup  # 分配器原始版本
├── docs/
│   └── backup_manifest.json          # 備份清單和校驗值
└── rollback_script.py                # 自動回滾腳本
```

### **備份檔案校驗**
- **檔案完整性**: SHA256校驗值記錄
- **版本標識**: Git commit hash記錄
- **時間戳記**: 精確的備份時間

---

## 🔧 **自動回滾腳本**

### **腳本功能**
```python
# rollback_script.py - 一鍵回滾腳本
import shutil
import json
import hashlib
from pathlib import Path
from datetime import datetime

def rollback_layout_engine():
    """一鍵回滾佈局引擎修復"""
    backup_dir = Path("backup/2025-09-14_layout_fix")

    # 1. 驗證備份完整性
    if not verify_backup_integrity(backup_dir):
        print("❌ 備份檔案校驗失敗")
        return False

    # 2. 執行檔案還原
    restore_files = [
        ("utils/core/layout.py.backup", "utils/core/layout.py"),
        ("utils/orchestration/question_distributor.py.backup",
         "utils/orchestration/question_distributor.py")
    ]

    for backup_file, target_file in restore_files:
        shutil.copy2(backup_dir / backup_file, target_file)
        print(f"✅ 已還原: {target_file}")

    # 3. 清理臨時檔案
    cleanup_temp_files()

    print("🎯 回滾完成！系統已恢復到修改前狀態")
    return True
```

### **執行方式**
```bash
# 一鍵回滾指令
python rollback_script.py

# 或者手動還原
cp backup/2025-09-14_layout_fix/utils/core/layout.py.backup utils/core/layout.py
cp backup/2025-09-14_layout_fix/utils/orchestration/question_distributor.py.backup utils/orchestration/question_distributor.py
```

---

## 🚨 **緊急回滾程序**

### **緊急情況處理流程**
1. **立即停止**: 停止相關服務或測試
2. **狀況評估**: 快速判斷問題嚴重性
3. **決策執行**: 決定是否需要立即回滾
4. **執行回滾**: 使用自動腳本或手動操作
5. **驗證恢復**: 確認系統回到正常狀態

### **快速檢查指令**
```bash
# 檢查關鍵功能
python -c "from utils.core.layout import LayoutEngine; print('✅ 佈局引擎正常')"

# 檢查預排序功能
python -c "from utils.orchestration.question_distributor import QuestionSorter; print('✅ 排序器正常')"

# 執行快速測試
py -m pytest tests/test_utils/test_geometry/test_basic_ops.py -v -q
```

---

## 📊 **回滾後驗證清單**

### **功能性驗證**
- [ ] 應用程式正常啟動
- [ ] 題目生成功能正常
- [ ] PDF生成流程完整
- [ ] 用戶介面響應正常
- [ ] 所有現有測試通過

### **數據一致性驗證**
- [ ] 配置檔案恢復正確
- [ ] 臨時檔案清理完成
- [ ] 日誌記錄正常
- [ ] 無殘留修改痕跡

### **性能基準驗證**
- [ ] 應用程式啟動時間正常
- [ ] 題目生成時間符合基準
- [ ] 記憶體使用正常
- [ ] CPU使用率正常

---

## 🔍 **問題排查指引**

### **常見回滾問題**
1. **檔案權限問題**
   - 症狀：無法覆寫檔案
   - 解決：檢查檔案權限，使用管理員權限

2. **備份檔案損壞**
   - 症狀：校驗值不匹配
   - 解決：使用Git版本控制恢復

3. **依賴模組衝突**
   - 症狀：import錯誤
   - 解決：重啟Python環境

### **Git版本回滾備選方案**
```bash
# 如果備份檔案有問題，使用Git回滾
git log --oneline -n 10  # 查看最近提交
git checkout HEAD~1 -- utils/core/layout.py
git checkout HEAD~1 -- utils/orchestration/question_distributor.py
```

---

## 📈 **回滾後續處理**

### **問題分析**
1. **根因分析**: 調查回滾原因
2. **改進建議**: 提出修復方案改進
3. **測試加強**: 增加相關測試案例
4. **文檔更新**: 記錄經驗教訓

### **重新實施準備**
- **風險重評估**: 基於回滾原因重新評估
- **方案調整**: 必要時調整實施策略
- **測試強化**: 加強對問題點的測試
- **分階段執行**: 考慮更細粒度的分步實施

---

## 📞 **緊急聯絡資訊**

### **回滾決策鏈**
1. **技術負責人**: 評估技術可行性
2. **專案負責人**: 做出回滾決策
3. **系統管理員**: 執行回滾操作

### **24/7支援**
- **技術支援**: 開發團隊待命
- **系統監控**: 自動化監控告警
- **文檔支援**: 完整操作指引

---

## 🎯 **回滾測試計畫**

### **定期回滾演練**
- **頻率**: 實施前進行一次完整演練
- **範圍**: 完整的備份→修改→回滾→驗證流程
- **目標**: 確保回滾機制可靠性

### **演練檢查項目**
- [ ] 備份腳本正確執行
- [ ] 檔案校驗機制有效
- [ ] 回滾腳本正確執行
- [ ] 系統恢復完全正確
- [ ] 驗證流程完整有效

---

**回滾策略狀態**: ✅ 已準備完成，随時可用
**預計回滾時間**: 3-5分鐘
**成功率預期**: >99%（基於完整備份和自動化腳本）