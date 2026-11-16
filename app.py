from datetime import datetime
import json
import os
from pathlib import Path
import streamlit as st

# 嘗試匯入各個模組
try:
  import apply_holiday
except ImportError:
  apply_system = None

try:
  import holiday_approval
except ImportError:
  holiday_approval = None

try:
  import holiday_balance
except ImportError:
  holiday_balance = None

try:
  import holiday_log
except ImportError:
  holiday_log = None

try:
  import holiday_list
except ImportError:
  holiday_list = None


def factory_reset():
  """還原出廠設定：清空所有 JSON 資料"""
  BASE_DIR = Path(__file__).resolve().parent
  target_files = [
      "holidays.json",
      "holiday_applications.json",
      "holiday_approval_results.json",
      "holiday_logs.json",
  ]

  for filename in target_files:
    file_path = BASE_DIR / filename
    try:
      BASE_DIR.mkdir(exist_ok=True)
      if filename == "holiday_logs.json":
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        initial_log = [f"[{timestamp}] 【系統】執行了系統重設，所有資料已清空。"]
        with open(file_path, "w", encoding="utf-8") as f:
          json.dump(initial_log, f, ensure_ascii=False, indent=4)
      else:
        with open(file_path, "w", encoding="utf-8") as f:
          json.dump([], f, ensure_ascii=False, indent=4)
    except Exception as e:
      print(f"清理檔案 {filename} 失敗: {e}")


def main():
  st.set_page_config(page_title="假期管理系統", page_icon="🏢", layout="wide")

  st.title("🏢 假期管理系統")

  # 建立頂部導航分頁 (Tabs)
  tab_names = ["🏠 首頁總覽", "📅 假期列表", "📋 申請假期", "📊 假期結餘", "✅ 批核結果", "📜 系統日誌"]
  tabs = st.tabs(tab_names)

  with tabs[0]:
    st.subheader("歡迎使用假期管理系統")
    st.write("你可以直接透過上方的分頁標籤切換不同的功能，不必再頻繁點選側邊欄！")
    
    # 這裡明確宣告了 5 個欄位 (col1 ~ col5)
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
      st.info("💡 提示：點擊上方「假期列表」可新增所有假期。")
    with col2:
      st.info("💡 提示：點擊上方「申請假期」即可申請假期。")
    with col3:
      st.info("💡 提示：點擊上方「假期結餘」可查詢假期剩餘天數。")
    with col4:
      st.info("💡 提示：點擊上方「批核結果」即可更改假期批核狀態。")
    with col5:
      st.info("💡 提示：側邊欄設有 '重設' 按鈕，請小心使用。")

  with tabs[1]:
    if holiday_list:
      holiday_list.run()
    else:
      st.error("找不到 holiday_list.py 模組！")

  with tabs[2]:
    if apply_holiday:
      apply_holiday.run()
    else:
      st.error("找不到 apply_holiday.py 模組！")

  with tabs[3]:
    if holiday_balance:
      holiday_balance.run()
    else:
      st.error("找不到 holiday_balance.py 模組！")

  with tabs[4]:
    if holiday_approval:
      holiday_approval.run()
    else:
      st.error("找不到 holiday_approval.py 模組！")

  with tabs[5]:
    if holiday_log:
      holiday_log.run()
    else:
      st.error("找不到 holiday_log.py 模組！")

  # 側邊欄保留較少用或危險的操作（例如系統重設）
  st.sidebar.title("⚙️ 系統設定")
  st.sidebar.markdown("---")
  if st.sidebar.button("⚠️ 重設系統（清除所有資料）", type="primary"):
    factory_reset()
    st.sidebar.success("系統已成功重設！")
    st.rerun()


if __name__ == "__main__":
  main()