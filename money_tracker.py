import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
import datetime

DATA_FILE = "transactions.json"

BG = "#1E1E2E"
SURFACE = "#313244"
BLUE = "#89B4FA"
GREEN = "#A6E3A1"
RED = "#F38BA8"
YELLOW = "#F9E2AF"
TEXT = "#CDD6F4"
SUBTEXT = "#A6ADC8"


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"person_a": "Aさん", "person_b": "Bさん", "transactions": []}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def calc_balance(data):
    # net > 0: person_b が person_a に借りている
    # net < 0: person_a が person_b に借りている
    a = data["person_a"]
    net = 0
    for t in data["transactions"]:
        if t["payer"] == a:
            net += t["amount"]
        else:
            net -= t["amount"]
    return net


data = load_data()

root = tk.Tk()
root.title("お金の管理アプリ")
root.geometry("560x700")
root.configure(bg=BG)

tk.Label(root, text="お金の管理", font=("Arial", 22, "bold"), bg=BG, fg=TEXT).pack(pady=(20, 4))

names_label = tk.Label(root, text="", font=("Arial", 12), bg=BG, fg=SUBTEXT)
names_label.pack()

# 残高表示エリア
balance_frame = tk.Frame(root, bg=SURFACE, pady=18, padx=30)
balance_frame.pack(fill="x", padx=20, pady=12)

balance_label = tk.Label(balance_frame, text="", font=("Arial", 12), bg=SURFACE, fg=SUBTEXT)
balance_label.pack()

amount_label = tk.Label(balance_frame, text="", font=("Arial", 26, "bold"), bg=SURFACE, fg=GREEN)
amount_label.pack()

# 取引追加フォーム
input_frame = tk.Frame(root, bg=SURFACE, pady=14, padx=20)
input_frame.pack(fill="x", padx=20, pady=4)

tk.Label(input_frame, text="取引を追加", font=("Arial", 13, "bold"), bg=SURFACE, fg=TEXT).grid(
    row=0, column=0, columnspan=4, pady=(0, 8), sticky="w"
)

tk.Label(input_frame, text="支払った人", font=("Arial", 10), bg=SURFACE, fg=SUBTEXT).grid(
    row=1, column=0, padx=6
)

# 金額ラベル + ラジオボタン（一人分 / 合計）
amount_type = tk.StringVar(value="per_person")

amount_col_frame = tk.Frame(input_frame, bg=SURFACE)
amount_col_frame.grid(row=1, column=1, padx=6)

tk.Label(amount_col_frame, text="金額（円）", font=("Arial", 10), bg=SURFACE, fg=SUBTEXT).pack(side="left")

radio_style = {
    "bg": SURFACE, "fg": SUBTEXT, "selectcolor": "#45475A",
    "activebackground": SURFACE, "activeforeground": TEXT,
    "font": ("Arial", 9), "bd": 0,
}
tk.Radiobutton(amount_col_frame, text="一人分", variable=amount_type, value="per_person", **radio_style).pack(side="left", padx=(6, 2))
tk.Radiobutton(amount_col_frame, text="合計", variable=amount_type, value="total", **radio_style).pack(side="left")

tk.Label(input_frame, text="メモ（任意）", font=("Arial", 10), bg=SURFACE, fg=SUBTEXT).grid(
    row=1, column=2, padx=6
)

payer_var = tk.StringVar()

payer_combo = ttk.Combobox(input_frame, textvariable=payer_var, width=9, state="readonly", font=("Arial", 11))
payer_combo.grid(row=2, column=0, padx=6, pady=6)

amount_entry = tk.Entry(input_frame, width=12, bg="#45475A", fg=TEXT, insertbackground=TEXT, font=("Arial", 12))
amount_entry.grid(row=2, column=1, padx=6, pady=6)

note_entry = tk.Entry(input_frame, width=16, bg="#45475A", fg=TEXT, insertbackground=TEXT, font=("Arial", 12))
note_entry.grid(row=2, column=2, padx=6, pady=6)

add_btn = tk.Button(input_frame, text="追加", font=("Arial", 12), bg=BLUE, fg=BG, relief="flat", width=6)
add_btn.grid(row=2, column=3, padx=10)

# 取引履歴
history_frame = tk.Frame(root, bg=BG)
history_frame.pack(fill="both", expand=True, padx=20, pady=6)

tk.Label(history_frame, text="取引履歴", font=("Arial", 13, "bold"), bg=BG, fg=TEXT).pack(anchor="w", pady=(0, 4))

list_frame = tk.Frame(history_frame, bg=SURFACE)
list_frame.pack(fill="both", expand=True)

scrollbar = tk.Scrollbar(list_frame)
scrollbar.pack(side="right", fill="y")

history_listbox = tk.Listbox(
    list_frame,
    yscrollcommand=scrollbar.set,
    bg=SURFACE,
    fg=TEXT,
    selectbackground="#45475A",
    font=("Arial", 11),
    height=11,
    borderwidth=0,
    highlightthickness=0,
)
history_listbox.pack(fill="both", expand=True, side="left")
scrollbar.config(command=history_listbox.yview)

btn_row = tk.Frame(root, bg=BG)
btn_row.pack(pady=8)

delete_btn = tk.Button(btn_row, text="選択した取引を削除", font=("Arial", 11), bg="#45475A", fg=RED, relief="flat", padx=10)
delete_btn.pack(side="left", padx=8)

settings_btn = tk.Button(btn_row, text="名前の設定", font=("Arial", 11), bg="#45475A", fg=SUBTEXT, relief="flat", padx=10)
settings_btn.pack(side="left", padx=8)


def update_display():
    a = data["person_a"]
    b = data["person_b"]
    names_label.config(text=f"{a}  と  {b}")
    payer_combo["values"] = [a, b]
    if payer_var.get() not in [a, b]:
        payer_var.set(a)

    net = calc_balance(data)
    if net == 0:
        balance_label.config(text="貸し借りなし", fg=TEXT)
        amount_label.config(text="0円", fg=GREEN)
    elif net > 0:
        balance_label.config(text="精算金額", fg=SUBTEXT)
        amount_label.config(text=f"{b}  →  {a}    {net:,}円", fg=YELLOW)
    else:
        balance_label.config(text="精算金額", fg=SUBTEXT)
        amount_label.config(text=f"{a}  →  {b}    {abs(net):,}円", fg=RED)

    history_listbox.delete(0, "end")
    for t in reversed(data["transactions"]):
        receiver = t.get("receiver", b if t["payer"] == a else a)
        note_str = f"  ({t['note']})" if t.get("note") else ""
        line = f"  {t['date']}  {t['payer']} → {receiver}  {t['amount']:,}円{note_str}"
        history_listbox.insert("end", line)


def add_transaction():
    a = data["person_a"]
    b = data["person_b"]
    payer = payer_var.get()
    receiver = b if payer == a else a

    try:
        raw_amount = int(amount_entry.get())
        if raw_amount <= 0:
            raise ValueError
    except ValueError:
        messagebox.showwarning("入力エラー", "金額は1以上の整数を入力してください")
        return

    # 合計金額の場合は半分にする（1円未満は切り捨て）
    amount = raw_amount // 2 if amount_type.get() == "total" else raw_amount

    note = note_entry.get().strip()
    today = datetime.date.today().strftime("%Y-%m-%d")
    data["transactions"].append({
        "payer": payer,
        "receiver": receiver,
        "amount": amount,
        "note": note,
        "date": today,
    })
    save_data(data)
    amount_entry.delete(0, "end")
    note_entry.delete(0, "end")
    update_display()


def delete_transaction():
    selection = history_listbox.curselection()
    if not selection:
        messagebox.showinfo("確認", "削除したい取引をクリックして選択してください")
        return
    index = len(data["transactions"]) - 1 - selection[0]
    t = data["transactions"][index]
    a = data["person_a"]
    b = data["person_b"]
    receiver = t.get("receiver", b if t["payer"] == a else a)
    if messagebox.askyesno("削除確認", f"{t['payer']} → {receiver}  {t['amount']:,}円 を削除しますか？"):
        data["transactions"].pop(index)
        save_data(data)
        update_display()


def open_settings():
    win = tk.Toplevel(root)
    win.title("名前の設定")
    win.geometry("290x190")
    win.configure(bg=BG)
    win.grab_set()

    tk.Label(win, text="2人の名前を設定", font=("Arial", 14, "bold"), bg=BG, fg=TEXT).pack(pady=14)

    frame = tk.Frame(win, bg=BG)
    frame.pack()

    tk.Label(frame, text="Aさんの名前:", font=("Arial", 11), bg=BG, fg=SUBTEXT).grid(row=0, column=0, padx=8, pady=6, sticky="e")
    a_entry = tk.Entry(frame, width=13, bg="#45475A", fg=TEXT, insertbackground=TEXT, font=("Arial", 12))
    a_entry.insert(0, data["person_a"])
    a_entry.grid(row=0, column=1, padx=8, pady=6)

    tk.Label(frame, text="Bさんの名前:", font=("Arial", 11), bg=BG, fg=SUBTEXT).grid(row=1, column=0, padx=8, pady=6, sticky="e")
    b_entry = tk.Entry(frame, width=13, bg="#45475A", fg=TEXT, insertbackground=TEXT, font=("Arial", 12))
    b_entry.insert(0, data["person_b"])
    b_entry.grid(row=1, column=1, padx=8, pady=6)

    def save_names():
        new_a = a_entry.get().strip()
        new_b = b_entry.get().strip()
        if not new_a or not new_b:
            messagebox.showwarning("エラー", "名前を入力してください", parent=win)
            return
        if new_a == new_b:
            messagebox.showwarning("エラー", "同じ名前は使えません", parent=win)
            return
        old_a = data["person_a"]
        old_b = data["person_b"]
        for t in data["transactions"]:
            if t["payer"] == old_a:
                t["payer"] = new_a
            elif t["payer"] == old_b:
                t["payer"] = new_b
            if t.get("receiver") == old_a:
                t["receiver"] = new_a
            elif t.get("receiver") == old_b:
                t["receiver"] = new_b
        data["person_a"] = new_a
        data["person_b"] = new_b
        payer_var.set("")
        save_data(data)
        update_display()
        win.destroy()

    tk.Button(win, text="保存", font=("Arial", 12), bg=BLUE, fg=BG, relief="flat", width=8, command=save_names).pack(pady=10)


add_btn.config(command=add_transaction)
delete_btn.config(command=delete_transaction)
settings_btn.config(command=open_settings)

update_display()
root.mainloop()
