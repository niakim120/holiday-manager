from datetime import datetime
import json
import os
from pathlib import Path
import streamlit as st


def add_system_log(detail_text):
  """共用的日誌寫入輔助函式"""
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


def load_data():
  BASE_DIR = Path(__file__).resolve().parent
  data_file = BASE_DIR / "holidays.json"
  application_file = BASE_DIR / "holiday_applications.json"

  holidays_list = []
  if data_file.exists():
    try:
      with open(data_file, "r", encoding="utf-8") as f:
        holidays_list = json.load(f)
    except Exception:
      holidays_list = []

  # 統計每個假期被申請了幾次
  applied_counts = {}
  if application_file.exists():
    try:
      with open(application_file, "r", encoding="utf-8") as f:
        applications = json.load(f)
        for app in applications:
          h_name = app.get("holiday_name", "").strip()
          if h_name:
            applied_counts[h_name] = applied_counts.get(h_name, 0) + 1
    except Exception:
      pass

  processed_holidays = []
  for h in holidays_list:
    try:
      original_days = float(h.get("days", 0))
      h_name = str(h.get("name", "")).strip()
      used_days = applied_counts.get(h_name, 0)
      remaining_days = original_days - used_days

      formatted_days = (
          str(int(remaining_days))
          if remaining_days.is_integer()
          else str(remaining_days)
      )

      # 只有當剩餘日數大於 0 時才加入
      if remaining_days > 0:
        processed_holidays.append({
            "year": h.get("year"),
            "name": h_name,
            "days": formatted_days,
            "_raw_days": remaining_days,
        })
    except (ValueError, TypeError):
      continue

  return processed_holidays


def run():
  st.header("📊 假期結餘查詢")

  # 重新載入按鈕
  if st.button("重新載入資料"):
    add_system_log("【假期結餘】重新載入並同步了最新的假期結餘與申請扣減資料")
    st.success("已成功同步「假期列表」與「申請假期」的最新數據！")

  holidays = load_data()

  if not holidays:
    st.info("目前沒有剩餘日數大於 0 的假期資料。")
    return

  # 整理顯示用的表格資料
  table_data = []
  for idx, data in enumerate(holidays):
    table_data.append({
        "序號": idx + 1,
        "年份": data["year"],
        "名稱": data["name"],
        "剩餘日數": data["days"],
    })

  # Streamlit 的 dataframe 內建支援點擊欄位標題進行排序
  st.dataframe(table_data, use_container_width=True)
  st.caption("💡 提示：點擊表格上方的欄位標題即可進行排序。")


if __name__ == "__main__":
  run()