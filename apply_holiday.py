import calendar
from datetime import datetime
import json
import os
from pathlib import Path
import streamlit as st


def add_system_log(detail_text):
    # 確保路徑與根目錄一致
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


def load_approval_results():
    """讀取批核結果紀錄"""
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


def get_available_holidays():
    """讀取 holidays.json 與申請紀錄及審核狀態，計算出最新的剩餘日數大於 0 的假期"""
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

    # 讀取審核狀態
    approval_results = load_approval_results()

    # 統計已被扣除的天數（排除「不準」與「取消」的申請）
    applied_counts = {}
    if application_file.exists():
        try:
            with open(application_file, "r", encoding="utf-8") as f:
                applications = json.load(f)
                for idx, app in enumerate(applications):
                    h_name = app.get("holiday_name", "").strip()
                    holiday_date = app.get("date", "")
                    app_id = f"{holiday_date}_{h_name}_{idx}"
                    
                    # 取得審核狀態（預設為待批）
                    status = approval_results.get(app_id, "待批")
                    
                    # 只有當狀態不是「不準」也不是「取消」時，才計算已使用天數
                    if h_name and status not in ["不準", "取消"]:
                        try:
                            days_val = float(app.get("days", 1))
                        except (ValueError, TypeError):
                            days_val = 1.0
                        applied_counts[h_name] = applied_counts.get(h_name, 0.0) + days_val
        except Exception:
            pass

    valid_holidays = []
    for h in holidays_list:
        try:
            original_days = float(h.get("days", 0))
            h_name = str(h.get("name", "")).strip()
            used_days = applied_counts.get(h_name, 0.0)
            remaining_days = original_days - used_days

            # 只有當最新剩餘日數大於 0 時才加入可用清單
            if remaining_days > 0:
                formatted_days = (
                    str(int(remaining_days))
                    if remaining_days.is_integer()
                    else str(remaining_days)
                )
                valid_holidays.append({
                    "year": h.get("year"),
                    "name": h_name,
                    "days": formatted_days,
                })
        except (ValueError, TypeError):
            continue
    return valid_holidays


def run():
    st.header("📋 申請假期")

    BASE_DIR = Path(__file__).resolve().parent
    application_file = BASE_DIR / "holiday_applications.json"
    BASE_DIR.mkdir(exist_ok=True)

    # 取得可用假期
    available_holidays = get_available_holidays()

    if not available_holidays:
        st.warning("目前沒有可供申請的有效假期！")
        return

    # 建立下拉選項格式
    holiday_display_list = [
        f"{h['name']} ({h['year']}年 - 剩餘 {h['days']} 天)"
        for h in available_holidays
    ]

    # 使用 Streamlit 表單
    with st.form("apply_form"):
        st.subheader("請填寫假期申請資訊")

        # 日期選擇
        now = datetime.now()
        app_date = st.date_input("申請日期", value=now)

        # 假期選擇
        selected_holiday_str = st.selectbox("選擇假期", holiday_display_list)

        # 提交按鈕
        submitted = st.form_submit_button("提交申請")

        if submitted:
            formatted_date = app_date.strftime("%Y/%m/%d")
            holiday_name_clean = selected_holiday_str.split(" (")[0].strip()

            applications = []
            if application_file.exists():
                try:
                    with open(application_file, "r", encoding="utf-8") as f:
                        applications = json.load(f)
                except Exception:
                    applications = []

            # 檢查同一日期是否重複申請
            duplicate = False
            for app in applications:
                if app.get("date") == formatted_date:
                    duplicate = True
                    break

            if duplicate:
                st.error(
                    f"您在 【{formatted_date}】"
                    " 已經有申請過假期記錄了，同一日期不能重複申請！"
                )
            else:
                app_data = {
                    "date": formatted_date,
                    "holiday_name": holiday_name_clean,
                    "full_info": selected_holiday_str,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "days": 1,  # 確保每筆申請記錄帶有天數欄位
                }
                applications.append(app_data)

                try:
                    with open(application_file, "w", encoding="utf-8") as f:
                        json.dump(applications, f, ensure_ascii=False, indent=4)

                    add_system_log(
                        f"【申請假期】提交申請：日期 {formatted_date}，項目：{holiday_name_clean}"
                    )

                    st.success(
                        f"已成功提交假期申請！\n\n日期：{formatted_date}\n假期：{holiday_name_clean}"
                    )
                except Exception as e:
                    st.error(f"儲存申請失敗：{e}")


if __name__ == "__main__":
    run()