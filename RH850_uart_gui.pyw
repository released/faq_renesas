import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from itertools import product
import threading

LPRS_values = [1, 2, 4, 8, 16, 32, 64, 128]
NSPB_values = list(range(6, 17))
BRP0_range = range(0, 65536)
FREQ_LIST = [8000000, 16000000, 20000000, 24000000, 40000000, 80000000, 96000000, 120000000]

def calculate_baud_rates(base_freq, target_baud, progress_callback=None):
    results = []
    total = len(LPRS_values) * len(NSPB_values)
    count = 0

    for LPRS, NSPB in product(LPRS_values, NSPB_values):
        for BRP0 in BRP0_range:
            baud_rate = base_freq / LPRS / (BRP0 + 1) / NSPB
            error = abs((baud_rate - target_baud) / target_baud) * 100
            results.append((LPRS, BRP0, NSPB, baud_rate, error))
        count += 1
        if progress_callback:
            progress_callback(int(count / total * 100))

    df = pd.DataFrame(results, columns=["LPRS", "BRP0", "NSPB", "baud_rate", "error_percent"])
    return df.sort_values(by="error_percent").head(50)  # 預先排序並擷取前50筆

def on_auto_calculate():
    try:
        base_freq = float(entry_base_freq.get())
        target_baud = float(entry_baud.get())
        row_limit = int(entry_row_limit.get())
        if row_limit <= 0 or row_limit > 50:
            raise ValueError("顯示筆數必須是 1~50 的整數")

        label_status.config(text="計算中，請稍候...", fg="blue")
        root.update_idletasks()

        def update_progress(pct):
            progress["value"] = pct
            root.update_idletasks()

        result_df = calculate_baud_rates(base_freq, target_baud, update_progress)

        for row in tree.get_children():
            tree.delete(row)

        for _, row in result_df.head(row_limit).iterrows():
            iid = tree.insert("", "end", values=(row["LPRS"], row["BRP0"], row["NSPB"],
                                                f"{row['baud_rate']:.2f}", f"{row['error_percent']:.4f}"))
            # 高亮誤差 < 1%
            if row["error_percent"] < 1.0:
                tree.item(iid, tags=("highlight",))

        label_status.config(text="完成！", fg="green")
        progress["value"] = 0

    except ValueError as e:
        messagebox.showerror("輸入錯誤", f"請確認輸入正確：\n{e}")

def on_manual_calculate():
    try:
        base_freq = float(entry_base_freq.get())
        # LPRS 取分母部分，"1/16" -> 16
        LPRS = int(combo_LPRS.get().split('/')[1])
        NSPB = int(combo_NSPB.get().split()[0])
        BRP0 = int(entry_BRP0.get())
        if not (0 <= BRP0 <= 65535):
            raise ValueError("BRP0 超出範圍 (0 ~ 65535)")
        target_baud = float(entry_manual_baud.get())
        baud_rate = base_freq / LPRS / (BRP0 + 1) / NSPB
        error = abs((baud_rate - target_baud) / target_baud) * 100
        label_manual_result.config(
            text=f"Baud Rate: {baud_rate:.2f}，誤差: {error:.4f}%", fg="green"
        )
    except Exception as e:
        messagebox.showerror("輸入錯誤", f"請確認輸入正確：\n{e}")

root = tk.Tk()
root.title("RH850 UART Baud Rate 計算工具")
root.geometry("800x480")

# Base Frequency 共用輸入區
frame_freq = tk.Frame(root)
frame_freq.pack(pady=5)
tk.Label(frame_freq, text="Base Frequency (Hz):").pack(side=tk.LEFT)
entry_base_freq = tk.Entry(frame_freq, width=15)
entry_base_freq.insert(0, "40000000")
entry_base_freq.pack(side=tk.LEFT, padx=5)

# Notebook 分頁
notebook = ttk.Notebook(root)
notebook.pack(padx=10, pady=5, fill="both", expand=True)

# 第一分頁 Auto Calculate
tab_auto = tk.Frame(notebook)
notebook.add(tab_auto, text="Auto Calculate")

frame_top = tk.Frame(tab_auto)
frame_top.pack(pady=5)

tk.Label(frame_top, text="目標 Baud Rate:").pack(side=tk.LEFT, padx=5)
entry_baud = tk.Entry(frame_top, width=12)
entry_baud.insert(0, "460800")
entry_baud.pack(side=tk.LEFT, padx=5)

tk.Label(frame_top, text="顯示筆數:").pack(side=tk.LEFT, padx=5)
entry_row_limit = tk.Entry(frame_top, width=5)
entry_row_limit.insert(0, "15")  # 預設15筆
entry_row_limit.pack(side=tk.LEFT, padx=5)

tk.Button(frame_top, text="開始計算", command=on_auto_calculate).pack(side=tk.LEFT, padx=5)

progress = ttk.Progressbar(tab_auto, length=300, mode="determinate")
progress.pack(pady=5)

columns = ("LPRS", "BRP0", "NSPB", "Baud Rate", "誤差 (%)")
tree = ttk.Treeview(tab_auto, columns=columns, show="headings", height=15)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=130, anchor="center")
tree.pack(side=tk.LEFT, fill="both", expand=True)

scrollbar = ttk.Scrollbar(tab_auto, orient="vertical", command=tree.yview)
scrollbar.pack(side=tk.RIGHT, fill="y")
tree.configure(yscrollcommand=scrollbar.set)

tree.tag_configure("highlight", background="#d0f0c0")  # 淡綠色高亮

label_status = tk.Label(tab_auto, text="", fg="green")
label_status.pack()

# 第二分頁 Manual Calculate
tab_manual = tk.Frame(notebook)
notebook.add(tab_manual, text="Manual Calculate")

frame_manual = tk.Frame(tab_manual)
frame_manual.pack(pady=10)

tk.Label(frame_manual, text="LPRS:").grid(row=0, column=0, sticky="e", padx=5, pady=3)
combo_LPRS = ttk.Combobox(frame_manual, values=[
    "1/1", "1/2", "1/4", "1/8", "1/16", "1/32", "1/64", "1/128"
], width=10, state="readonly")
combo_LPRS.current(3)
combo_LPRS.grid(row=0, column=1)

tk.Label(frame_manual, text="BRP0:").grid(row=1, column=0, sticky="e", padx=5, pady=3)
entry_BRP0 = tk.Entry(frame_manual, width=10)
entry_BRP0.insert(0, "0")
entry_BRP0.grid(row=1, column=1)
tk.Label(frame_manual, text="(0 ~ 65535)").grid(row=1, column=2, sticky="w")

tk.Label(frame_manual, text="NSPB:").grid(row=2, column=0, sticky="e", padx=5, pady=3)
combo_NSPB = ttk.Combobox(frame_manual,
    values=[f"{i} sample" for i in range(6, 17)],
    width=10, state="readonly"
)
combo_NSPB.current(2)
combo_NSPB.grid(row=2, column=1)

tk.Label(frame_manual, text="Baud Rate:").grid(row=3, column=0, sticky="e", padx=5, pady=3)
entry_manual_baud = tk.Entry(frame_manual, width=15)
entry_manual_baud.insert(0, "460800")
entry_manual_baud.grid(row=3, column=1)

tk.Button(tab_manual, text="計算", command=on_manual_calculate).pack(pady=5)
label_manual_result = tk.Label(tab_manual, text="", fg="blue", font=("Arial", 10))
label_manual_result.pack()

# ========== 第三分頁：Best Match Finder ==========
tab_best = tk.Frame(notebook)
notebook.add(tab_best, text="Best Match Finder")

frame_best_input = tk.Frame(tab_best)
frame_best_input.pack(pady=10)

tk.Label(frame_best_input, text="目標 Baud Rate:").grid(row=0, column=0, padx=5)
entry_best_baud = tk.Entry(frame_best_input, width=10)
entry_best_baud.insert(0, "460800")
entry_best_baud.grid(row=0, column=1, padx=5)

tk.Label(frame_best_input, text="可接受誤差 (%):").grid(row=0, column=2, padx=5)
entry_best_error = tk.Entry(frame_best_input, width=10)
entry_best_error.insert(0, "1")
entry_best_error.grid(row=0, column=3, padx=5)

def find_best_match():
    try:
        target_baud = float(entry_best_baud.get())
        max_error = float(entry_best_error.get())
        tree_best.delete(*tree_best.get_children())
        progress_best["value"] = 0
        progress_best["maximum"] = len(FREQ_LIST)

        def worker():
            best_results = []

            for idx, freq in enumerate(FREQ_LIST):
                min_error = float("inf")
                best_combo = None

                for LPRS in LPRS_values:
                    for NSPB in NSPB_values:
                        for BRP0 in range(0, 65536):
                            actual_baud = freq / LPRS / (BRP0 + 1) / NSPB
                            error = abs((actual_baud - target_baud) / target_baud) * 100

                            if error < min_error:
                                min_error = error
                                best_combo = (freq, LPRS, BRP0, NSPB, actual_baud, error)

                            if error < 0.0001:
                                break  # 提早結束內圈以加速

                    # 可加入這裡的條件式提早結束 NSPB loop

                if best_combo and best_combo[-1] <= max_error:
                    best_results.append(best_combo)

                progress_best["value"] = idx + 1
                progress_best.update_idletasks()

            # 結果顯示
            for result in sorted(best_results, key=lambda x: x[-1]):
                tree_best.insert("", "end", values=(
                    f"{result[0]:,}", result[1], result[2], result[3],
                    f"{result[4]:.2f}", f"{result[5]:.4f}%"
                ))

            progress_best["value"] = 0

        threading.Thread(target=worker).start()

    except Exception as e:
        messagebox.showerror("錯誤", str(e))


tk.Button(tab_best, text="尋找最佳解", command=find_best_match).pack(pady=5)

progress_best = ttk.Progressbar(tab_best, orient="horizontal", mode="determinate")
progress_best.pack(fill="x", padx=10, pady=5)

# 顯示結果表格
frame_best_tree = tk.Frame(tab_best)
frame_best_tree.pack(padx=10, pady=5, fill="both", expand=True)

tree_best = ttk.Treeview(frame_best_tree, columns=("Base Freq", "LPRS", "BRP0", "NSPB", "Baud", "Error"), show="headings", height=10)
for col in ("Base Freq", "LPRS", "BRP0", "NSPB", "Baud", "Error"):
    tree_best.heading(col, text=col)
    tree_best.column(col, anchor="center", width=110)

tree_best.pack(side=tk.LEFT, fill="both", expand=True)

scrollbar_best = ttk.Scrollbar(frame_best_tree, orient="vertical", command=tree_best.yview)
scrollbar_best.pack(side=tk.RIGHT, fill="y")
tree_best.configure(yscrollcommand=scrollbar_best.set)




root.mainloop()
