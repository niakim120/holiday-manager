import calendar
from datetime import datetime
import json
import os
from pathlib import Path
import streamlit as st


def add_system_log(detail_text):
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
    """計算扣除有效申請後的剩餘假期"""
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

    approval_results = load_approval_results()

    applied_counts = {}
    if application_file.exists():
        try:
            with open(application_file, "r", encoding="utf-8") as f:
                applications = json.load(f)
                for idx, app in enumerate(applications):
                    h_name = app.get("holiday_name", "").strip()
                    holiday_date = app.get("date", "")
                    app_id = f"{holiday_date}_{h_name}_{idx}"
                    
                    status = approval_results.get(app_id, "待批")
                    
                    # 只有狀態不是「不準」也不是「取消」時才計入扣除
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

    # 1. 檢查重複申請邏輯必須在送出時嚴格執行，且不能影響結餘計算
    with st.form("apply_form"):
        st.subheader("請填寫假期申請資訊")

        now = datetime.now()
        app_date = st.date_input("申請日期", value=now)

        # 動態載入當前最新的可用假期
        available_holidays = get_available_holidays()

        if not available_holidays:
            st.warning("目前沒有可供申請的有效假期！")
            holiday_display_list = []
        else:
            holiday_display_list = [
                f"{h['name']} ({h['year']}年 - 剩餘 {h['days']} 天)"
                for h in available_holidays
            ]

        selected_holiday_str = st.selectbox(
            "選擇假期", 
            holiday_display_list if holiday_display_list else ["無可用假期"]
        )

        submitted = st.form_submit_button("提交申請")

        if submitted:
            if not holiday_display_list:
                st.error("目前沒有可供申請的有效假期！")
                return

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
                    "days": 1,
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
                    # 提交成功後強制重新整理以更新畫面結餘
                    st.rerun()
                except Exception as e:
                    st.error(f"儲存申請失敗：{e}")


if __name__ == "__main__":
    run()