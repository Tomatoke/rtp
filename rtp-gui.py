import sys
from io import StringIO
import os
import json
import tkinter as tk
import tkinter.messagebox as msgbox
from tkinter import filedialog, ttk, scrolledtext
from impl.__main__ import main

def run_rtp_gui(directory, template, count, rating, output_widget):
    output = ""
    sys_argv_original = sys.argv.copy()
    sys_stdout_original = sys.stdout
    sys.stdout = StringIO()
    try:
        sys.argv = [
            "rtp",
            "-d", directory,
            "-t", template,
            "-c", str(count),
            "-r", rating
        ]
        main()
        output = sys.stdout.getvalue()
        output_widget.config(state='normal')
        output_widget.delete("1.0", tk.END)
        output_widget.insert(tk.END, output)
        output_widget.config(state='disabled')
    except SystemExit as e:
        msgbox.showerror("エラー", sys.stdout.getvalue())
    finally:
        sys.stdout = sys_stdout_original
        sys.argv = sys_argv_original

def load_templates(directory):
    path = os.path.join(directory, "template.json")
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
            return list(data.keys())
    except Exception as e:
        print(f"テンプレート読み込み失敗: {e}")
        return []

def update_template_dropdown():
    directory = dir_var.get()
    templates = load_templates(directory)
    if templates:
        template_combo['values'] = templates
        template_combo.current(0)

root = tk.Tk()
root.title("Random Tag Picker")
root.geometry("640x360")

dir_frame = ttk.Frame(root, padding=5)
dir_frame.grid(row=0, column=0, sticky="ew")
dir_frame.grid_columnconfigure(1, weight=1)
ttk.Label(dir_frame, text="ディレクトリ:").grid(row=0, column=0, sticky="w")
dir_var = tk.StringVar()
dir_entry = ttk.Entry(dir_frame, textvariable=dir_var)
dir_entry.grid(row=0, column=1, sticky="ew", padx=5)
def choose_dir():
    path = filedialog.askdirectory()
    if path:
        dir_var.set(path)
        update_template_dropdown()
ttk.Button(dir_frame, text="参照", command=choose_dir).grid(row=0, column=2, sticky="w")

opt_frame = ttk.Frame(root, padding=5)
opt_frame.grid(row=1, column=0, sticky="w")
ttk.Label(opt_frame, text="テンプレート:").grid(row=0, column=0, sticky="w")
template_var = tk.StringVar()
template_combo = ttk.Combobox(opt_frame, textvariable=template_var, values=[], width=15)
template_combo.grid(row=0, column=1, sticky="w")
ttk.Label(opt_frame, text="レーティング:").grid(row=0, column=2, sticky="w", padx=(10,0))
rating_var = tk.StringVar(value="g")
ttk.Combobox(opt_frame, textvariable=rating_var, values=["g","p","r"], width=5).grid(row=0, column=3, sticky="w")
ttk.Label(opt_frame, text="出力タグ数:").grid(row=0, column=4, sticky="w", padx=(10,0))
count_var = tk.IntVar(value=5)
ttk.Spinbox(opt_frame, from_=1, to=20, textvariable=count_var, width=5).grid(row=0, column=5, sticky="w")

output_text = scrolledtext.ScrolledText(root, width=80, height=15, state='disabled')
output_text.grid(row=2, column=0, padx=10, pady=(5,10), sticky="nsew")
root.grid_rowconfigure(2, weight=1)
root.grid_columnconfigure(0, weight=1)

def on_run(directory=None, template=None, count=None, rating=None):
    run_rtp_gui(
        directory=directory if directory is not None else dir_var.get(),
        template=template if template is not None else template_var.get(),
        count=count if count is not None else count_var.get(),
        rating=rating if rating is not None else rating_var.get(),
        output_widget=output_text
    )

def on_run_with_template():
    template = template_var.get()
    if not template:
        msgbox.showerror("エラー", "template not selected.")
        return
    on_run(template=template)

def on_random_run():
    on_run(template="")

button_frame = ttk.Frame(root)
button_frame.grid(row=3, column=0, sticky="e", padx=10, pady=(0,10))
ttk.Button(button_frame, text="テンプレート生成", command=on_run_with_template).grid(row=0, column=0, padx=5)
ttk.Button(button_frame, text="ランダム生成", command=on_random_run).grid(row=0, column=1, padx=5)

dir_var.trace_add("write", lambda *args: update_template_dropdown())

root.mainloop()
