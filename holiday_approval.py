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


def load_applications():
  BASE_DIR = Path(__file__).resolve().parent
  application_file = BASE_DIR / "holiday_applications.json"
  if application_file.exists():
    try:
      with open(application_file, "r", encoding="utf-8") as f:
        return json.load(f)
    except Exception:
      return []
  return []


def load_results():
  """讀取批核結果紀錄，並確保格式一定是字典 (dict)"""
  BASE_DIR = Path(__file__).resolve().parent
  result_file = BASE_DIR / "holiday_approval_results.json"
  if result_file.exists():
    try:
      with open(result_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        if isinstance(data, dict):
          return data
    except Exception:
      pass
  return {}


def save_results(results):
  """儲存批核結果紀錄"""
  BASE_DIR = Path(__file__).resolve().parent
  result_file = BASE_DIR / "holiday_approval_results.json"
  try:
    with open(result_file, "w", encoding="utf-8") as f:
      json.dump(results, f, ensure_ascii=False, indent=4)
  except Exception as e:
    st.error(f"儲存批核結果失敗：{e}")


def run():
  st.header("📋 假期批核與結果管理")

  applications = load_applications()
  results = load_results()

  if not applications:
    st.info("目前沒有任何假期申請紀錄。")
    return

  # 整理表格資料以供顯示
  table_data = []
  for idx, app in enumerate(applications):
    holiday_date = app.get("date", "")
    holiday_name = app.get("holiday_name", "")
    app_date = app.get("created_at", "").split(" ")[0]
    app_id = f"{holiday_date}_{holiday_name}_{idx}"
    status = results.get(app_id, "待批")

    table_data.append({
        "序號": idx + 1,
        "休假日期": holiday_date,
        "假期名稱": holiday_name,
        "申請日期": app_date,
        "審核狀態": status,
        "app_id": app_id,
    })

  # 1. 顯示完整總覽表格
  st.subheader("申請清單與審核狀態總覽")
  display_df_data = [
      {k: v for k, v in item.items() if k != "app_id"} for item in table_data
  ]
  st.dataframe(display_df_data, use_container_width=True)

  st.markdown("---")

  # 2. 審核操作區
  st.subheader("變更審核狀態")
  options = [
      f"序號 {item['序號']} | 日期: {item['休假日期']} | 假期: {item['假期名稱']} | 現狀: {item['審核狀態']}"
      for item in table_data
  ]

  selected_option = st.selectbox("選擇要審核的項目", options)

  if selected_option:
    selected_idx = options.index(selected_option)
    target_item = table_data[selected_idx]
    app_id = target_item["app_id"]
    current_status = target_item["審核狀態"]

    with st.form("approval_form"):
      st.write(
          f"**正在審核項目：** {target_item['假期名稱']}（休假日期："
          f" {target_item['休假日期']}）"
      )

      status_options = ["待批", "批準", "不準", "取消"]
      default_index = (
          status_options.index(current_status)
          if current_status in status_options
          else 0
      )

      new_status = st.selectbox(
          "選擇新的批核結果", status_options, index=default_index
      )

      submitted = st.form_submit_button("確認更新狀態")

      if submitted:
        results[app_id] = new_status
        save_results(results)

        add_system_log(
            f"【批核結果】審核更新：{target_item['假期名稱']}"
            f" ({target_item['休假日期']}) 狀態變更為 【{new_status}】"
        )
        st.success(f"已成功更新 {target_item['假期名稱']} 的批核結果為：{new_status}")
        st.rerun()


if __name__ == "__main__":
  run()