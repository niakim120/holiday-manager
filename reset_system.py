from datetime import datetime
import json
import os
from pathlib import Path
import streamlit as st


def add_system_log(detail_text):
  """重設時同步寫入系統日誌"""
  BASE_DIR = Path(__file__).resolve().parent
  log_file = BASE_DIR / "holiday_logs.json"
  BASE_DIR.mkdir(exist_ok=True)

  logs = []
  if log_file.exists():
    try:
      with open(log_file, "r", encoding="utf-8") as f:
        logs = json.load(f)
    except Exception:
      logs = []

  timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  full_log = f"[{timestamp}] {detail_text}"
  logs.append(full_log)
  try:
    with open(log_file, "w", encoding="utf-8") as f:
      json.dump(logs, f, ensure_ascii=False, indent=4)
  except Exception as e:
    print(f"寫入日誌失敗: {e}")


def factory_reset():
  """執行重設/還原出廠設定：清除或刪除假期資料夾內的所有 JSON 檔案"""
  BASE_DIR = Path(__file__).resolve().parent
  target_files = [
      "holidays.json",
      "holiday_applications.json",
      "holiday_approval_results.json",
      "holiday_logs.json",
  ]

  success_count = 0
  for filename in target_files:
    file_path = BASE_DIR / filename
    try:
      BASE_DIR.mkdir(exist_ok=True)
      if filename == "holiday_logs.json":
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        initial_log = [f"[{timestamp}] 【系統】執行了重設，所有資料已清空。"]
        with open(file_path, "w", encoding="utf-8") as f:
          json.dump(initial_log, f, ensure_ascii=False, indent=4)
      else:
        with open(file_path, "w", encoding="utf-8") as f:
          json.dump([], f, ensure_ascii=False, indent=4)
      success_count += 1
    except Exception as e:
      print(f"清理檔案 {filename} 失敗: {e}")

  return success_count


def run():
  st.header("⚙️ 系統還原與重設工具")

  st.warning(
      "**警告：** 執行重設將會清除所有假期列表、申請紀錄、批核結果，並將日誌"
      "歸零！此動作無法復原。"
  )

  # 使用 Streamlit 的 checkbox 或 toggle 作為二次確認機制
  confirm_check = st.checkbox("我已了解風險，並確認要清除所有資料")

  if st.button("🚨 一鍵還原出廠設定", type="primary", disabled=not confirm_check):
    success_count = factory_reset()
    if success_count > 0:
      st.success("已成功重設！所有資料已清空。")
      st.balloons()
    else:
      st.error("重設過程發生錯誤，請檢查檔案權限。")


if __name__ == "__main__":
  run()