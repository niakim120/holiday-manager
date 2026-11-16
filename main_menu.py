import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

# 嘗試匯入各個模組的 App 類別
try:
    from holiday_list import HolidayManagerApp
except ImportError:
    HolidayManagerApp = None

try:
    from holiday_balance import HolidayBalanceApp
except ImportError:
    HolidayBalanceApp = None

try:
    from apply_holiday import ApplyHolidayApp
except ImportError:
    ApplyHolidayApp = None

try:
    from holiday_approval import HolidayApprovalApp
except ImportError:
    HolidayApprovalApp = None

try:
    from holiday_log import HolidayLogApp
except ImportError:
    HolidayLogApp = None


class MainMenuApp:

    def __init__(self, root):
        self.root = root
        self.root.title("假期管理 - 主選單")
        self.root.geometry("520x510")  # 稍微加高以容納底部兩個按鈕
        self.root.resizable(False, False)

        self.setup_styles()
        self.setup_main_ui()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

    def setup_main_ui(self):
        # 置中主容器
        main_container = tk.Frame(self.root, bg="#F9F9F9")
        main_container.pack(expand=True, fill="both")

        # 頂部標題
        title_frame = tk.Frame(main_container, bg="#F9F9F9")
        title_frame.pack(pady=(20, 15))

        tk.Label(
            title_frame,
            text="假期管理",
            font=("Microsoft JhengHei", 16, "bold"),
            fg="#2C3E50",
            bg="#F9F9F9",
        ).pack()

        tk.Label(
            title_frame,
            text="請選擇要操作的功能項目",
            font=("Microsoft JhengHei", 10),
            fg="#7F8C8D",
            bg="#F9F9F9",
        ).pack(pady=(5, 0))

        # 按鈕群組容器（左右兩欄對稱排版：共 4 個按鈕）
        btn_grid_frame = tk.Frame(main_container, bg="#F9F9F9")
        btn_grid_frame.pack(pady=5)

        btn_config = {
            "font": ("Microsoft JhengHei", 11, "bold"),
            "width": 16,
            "height": 2,
            "bg": "#FFFFFF",
            "activebackground": "#E0E0E0",
            "relief": "raised",
            "bd": 2,
        }

        # --- 左側欄位按鈕（假期列表、批核結果） ---
        left_col = tk.Frame(btn_grid_frame, bg="#F9F9F9")
        left_col.pack(side="left", padx=20)

        tk.Button(
            left_col,
            text="假期列表",
            command=self.open_holiday_list,
            **btn_config,
        ).pack(pady=8)
        tk.Button(
            left_col,
            text="批核結果",
            command=self.open_holiday_approval,
            **btn_config,
        ).pack(pady=8)

        # --- 右側欄位按鈕（申請假期、假期結餘） ---
        right_col = tk.Frame(btn_grid_frame, bg="#F9F9F9")
        right_col.pack(side="left", padx=20)

        tk.Button(
            right_col,
            text="申請假期",
            command=self.open_apply_holiday,
            **btn_config,
        ).pack(pady=8)
        tk.Button(
            right_col,
            text="假期結餘",
            command=self.open_holiday_balance,
            **btn_config,
        ).pack(pady=8)

        # --- 底部按鈕區（依要求：上方是「日誌」，下方是「還原出廠設定」） ---
        bottom_frame = tk.Frame(main_container, bg="#F9F9F9")
        bottom_frame.pack(pady=(10, 20))

        # 1. 日誌按鈕（放在還原上方）
        btn_log = tk.Button(
            bottom_frame,
            text="日誌",
            font=("Microsoft JhengHei", 11, "bold"),
            width=38,  # 寬度配合上方兩欄的總寬度
            height=2,
            bg="#FFFFFF",
            activebackground="#E0E0E0",
            relief="raised",
            bd=2,
            command=self.open_holiday_log,
        )
        btn_log.pack(pady=(0, 50))

        # 2. 還原出廠設定按鈕（放在日誌下方）
        btn_reset = tk.Button(
            bottom_frame,
            text="⚠️ 重設(將清除所有資料)",
            font=("Microsoft JhengHei", 10, "bold"),
            width=20,
            height=2,
            bg="#FFCDD2",
            fg="#B71C1C",
            activebackground="#EF9A9A",
            relief="raised",
            command=self.factory_reset,
        )
        btn_reset.pack()

    def open_sub_window(self, title, app_class):
        if app_class is None:
            messagebox.showerror(
                "錯誤",
                f"找不到對應的模組程式碼檔案，請確保檔案名稱正確並與主選單放在同一資料夾！",
            )
            return

        win = tk.Toplevel(self.root)
        app_class(win)

    def open_holiday_list(self):
        self.open_sub_window("假期列表", HolidayManagerApp)

    def open_apply_holiday(self):
        self.open_sub_window("申請假期", ApplyHolidayApp)

    def open_holiday_approval(self):
        self.open_sub_window("批核結果", HolidayApprovalApp)

    def open_holiday_balance(self):
        self.open_sub_window("假期結餘", HolidayBalanceApp)

    def open_holiday_log(self):
        self.open_sub_window("系統日誌", HolidayLogApp)

    def factory_reset(self):
        confirm = messagebox.askyesno(
            "警告 - 重設將會清除全部資料",
            "這將會清除所有假期列表、申請紀錄、批核結果以及系統日誌！\n\n確定要將還原至初始狀態嗎？",
            icon="warning",
        )

        if not confirm:
            return

        folder_path = "假期"
        target_files = [
            "holidays.json",
            "holiday_applications.json",
            "holiday_approval_results.json",
            "holiday_logs.json",
        ]

        success_count = 0
        for filename in target_files:
            file_path = os.path.join(folder_path, filename)
            try:
                os.makedirs(folder_path, exist_ok=True)
                if filename == "holiday_logs.json":
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    initial_log = [f"[{timestamp}] 【系統】執行了還重設，所有資料已清空。"]
                    with open(file_path, "w", encoding="utf-8") as f:
                        json.dump(initial_log, f, ensure_ascii=False, indent=4)
                else:
                    with open(file_path, "w", encoding="utf-8") as f:
                        json.dump([], f, ensure_ascii=False, indent=4)
                success_count += 1
            except Exception as e:
                print(f"清理檔案 {filename} 失敗: {e}")

        if success_count > 0:
            messagebox.showinfo("成功", "系統已成功重設！所有資料已清空。")
        else:
            messagebox.showinfo("提示", "目前沒有發現需要清除的資料檔案。")


if __name__ == "__main__":
    root = tk.Tk()
    app = MainMenuApp(root)
    root.mainloop()