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
  if data_file.exists():
    try:
      with open(data_file, "r", encoding="utf-8") as f:
        return json.load(f)
    except Exception:
      return []
  return []


def save_data(holidays):
  BASE_DIR = Path(__file__).resolve().parent
  data_file = BASE_DIR / "holidays.json"
  try:
    with open(data_file, "w", encoding="utf-8") as f:
      json.dump(holidays, f, ensure_ascii=False, indent=4)
  except Exception as e:
    st.error(f"儲存資料失敗：{e}")


def run():
  st.header("📅 假期列表與維護管理")

  holidays = load_data()

  # 1. 新增假期表單區
  with st.expander("➕ 新增一筆假期資料", expanded=True):
    with st.form("add_holiday_form"):
      now_year = str(datetime.now().year)
      new_year = st.text_input("假期年份", value=now_year)
      new_name = st.text_input("假期名稱")
      new_days = st.text_input("假期總日數")

      submitted = st.form_submit_button("確認新增")

      if submitted:
        year_str = new_year.strip()
        name_str = new_name.strip()
        days_str = new_days.strip()

        if not year_str or not name_str or not days_str:
          st.error("請完整輸入年份、名稱與總日數！")
        elif not year_str.isdigit() or not days_str.isdigit():
          st.error("「假期年份」與「假期總日數」只限輸入整數！")
        else:
          holidays.append({
              "year": year_str,
              "name": name_str,
              "days": days_str,
          })
          save_data(holidays)
          add_system_log(
              f"【假期列表】新增假期：{name_str} (年份: {year_str}, 總日數: {days_str}天)"
          )
          st.success(f"成功新增假期：{name_str}！")
          st.rerun()

  st.markdown("---")

  # 2. 現有假期列表與編輯/刪除區
  st.subheader("現有假期清單")

  if not holidays:
    st.info("目前沒有任何假期資料。")
    return

  # 整理成表格顯示
  table_data = []
  for idx, data in enumerate(holidays):
    table_data.append({
        "序號": idx + 1,
        "年份": data["year"],
        "名稱": data["name"],
        "總日數": data["days"],
    })

  st.dataframe(table_data, use_container_width=True)

  # 選擇要修改或刪除的項目
  st.subheader("修改或刪除指定假期")
  options = [
      f"序號 {item['序號']} | 年份: {item['年份']} | 名稱: {item['名稱']} | 總日數: {item['總日數']}"
      for item in table_data
  ]

  selected_option = st.selectbox("選擇要編輯的項目", options)

  if selected_option:
    selected_idx = options.index(selected_option)
    target_data = holidays[selected_idx]

    with st.form("edit_delete_form"):
      st.write(f"**正在編輯序號 {selected_idx + 1} 的資料**")

      edit_year = st.text_input("修改年份", value=target_data["year"])
      edit_name = st.text_input("修改名稱", value=target_data["name"])
      edit_days = st.text_input("修改總日數", value=target_data["days"])

      col1, col2 = st.columns(2)
      with col1:
        modify_btn = st.form_submit_button("💾 儲存修改")
      with col2:
        delete_btn = st.form_submit_button("🗑️ 刪除此假期")

      if modify_btn:
        y_str = edit_year.strip()
        n_str = edit_name.strip()
        d_str = edit_days.strip()

        if not y_str or not n_str or not d_str:
          st.error("所有欄位皆不可為空！")
        elif not y_str.isdigit() or not d_str.isdigit():
          st.error("「假期年份」與「假期總日數」只限輸入整數！")
        else:
          holidays[selected_idx] = {
              "year": y_str,
              "name": n_str,
              "days": d_str,
          }
          save_data(holidays)
          add_system_log(
              f"【假期列表】修改假期序號 {selected_idx + 1} 為：{y_str}年 {n_str} ({d_str}天)"
          )
          st.success("修改成功！")
          st.rerun()

      if delete_btn:
        deleted_item = holidays.pop(selected_idx)
        save_data(holidays)
        add_system_log(f"【假期列表】刪除了假期序號 {selected_idx + 1}")
        st.warning(f"已刪除假期：{deleted_item['name']}")
        st.rerun()


if __name__ == "__main__":
  run()