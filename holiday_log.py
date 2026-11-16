from datetime import datetime
import json
import os
from pathlib import Path
import streamlit as st


def load_logs():
  """從日誌檔案中讀取操作紀錄"""
  BASE_DIR = Path(__file__).resolve().parent
  log_file = BASE_DIR / "holiday_logs.json"
  if log_file.exists():
    try:
      with open(log_file, "r", encoding="utf-8") as f:
        return json.load(f)
    except Exception:
      return []
  return []


def run():
  st.header("📜 系統操作日誌")

  # 重新載入按鈕
  if st.button("重新載入日誌"):
    st.success("已成功同步最新的系統操作日誌！")

  logs = load_logs()

  if not logs:
    st.info("目前沒有任何系統日誌紀錄。")
    return

  # 整理成表格顯示資料
  table_data = []
  for idx, log_text in enumerate(logs):
    table_data.append({
        "序號": idx + 1,
        "詳細內容": log_text,
    })

  # 使用 Streamlit 的 dataframe 呈現，支援自動延展與捲動
  st.dataframe(table_data, use_container_width=True, height=450)
  st.caption("💡 提示：網頁版會自動適應畫面，並可透過表格內建捲軸或直接滑動來檢視詳細日誌。")


if __name__ == "__main__":
  run()