from datetime import datetime
from io import BytesIO
import json
import os
from pathlib import Path
import streamlit as st

# 嘗試匯入各個模組
try:
    import apply_holiday
except ImportError:
    apply_holiday = None

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
                initial_log = [
                    f"[{timestamp}] 【系統】執行了系統重設，所有資料已清空。"
                ]
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
    tab_names = [
        "🏠 首頁總覽",
        "📅 假期列表",
        "📋 申請假期",
        "📊 假期結餘",
        "✅ 批核結果",
        "📜 系統日誌",
    ]
    tabs = st.tabs(tab_names)

    with tabs[0]:
        st.subheader("歡迎使用假期管理系統")
        
        # 使用說明區塊
        with st.expander("📖 點擊展開查看系統操作使用說明", expanded=True):
            st.markdown(
                "你可以直接透過上方的分頁標籤切換不同的功能！<br><br>"
                "<b>(1) 假期列表</b>：輸入你可使用的假期，假期名稱可輸入中/英文、假期總日數必須為整數。<br>"
                "<b>(2) 申請假期</b>：選擇休假日期及你目前尚可使用的剩餘假期。<br>"
                "<b>(3) 假期結餘</b>：你目前尚可使用的剩餘假期。<br>"
                "<b>(4) 批核結果</b>：可更改假期狀態為「批准」、「不准」或「取消」，當狀態為「不准」或「取消」時，<br>"
                "           系統會自動把相對應的假期天數加回結餘。如果你的假期永遠只有批准，你亦可視情況不更改假期狀態。<br>"
                "<b>(5) 系統日誌</b>：讓你有需要時查看甚麼時候操作過哪個部份。<br>"
                "<b>(6) 重設</b>：在左邊，清除全部記錄，請謹慎使用。",
                unsafe_allow_html=True,
            )

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

    # 側邊欄：系統設定
    st.sidebar.title("⚙️ 系統設定")
    if st.sidebar.button("⚠️ 重設系統（清除所有資料）", type="primary"):
        factory_reset()
        st.sidebar.success("系統已成功重設！")
        st.rerun()


if __name__ == "__main__":
    main()