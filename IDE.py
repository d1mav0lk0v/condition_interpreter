import re
import tkinter as tk
from tkinter import font
from tkinter import messagebox
from tkinter import filedialog

import condition_interpreter as ci


def command_help():
    messagebox.showinfo("help", ci.__doc__)


def command_run():
    global root, text

    code = text.get("1.0", tk.END)
    cond = ci.ConditionInterpreter(code)

    try:
        res = cond.run()
    except ci.TermBuilderError as exc:
        tag = "error"
        idx = f"1.0+{exc.code_pos}c"
        lastidx = f"1.0+{exc.code_pos+1}c"

        text.tag_add(tag, idx, lastidx)
        text.tag_config(tag, background="red")

        messagebox.showerror("error", exc)

        text.tag_delete(tag)
    except Exception as exc:
        messagebox.showerror("error", exc)
    else:
        res_root = tk.Toplevel(root)
        res_root.title("Result")
        res_root.geometry("600x400")

        res_text = tk.Text(res_root, font=text_font, wrap=tk.WORD)
        res_text.pack(fill=tk.BOTH)

        res_text.insert("1.0", res)


def command_open_file():
    global text
    filepath = filedialog.askopenfilename()
    if filepath != "":
        with open(filepath, "r") as file:
            t = file.read()
            text.delete("1.0", tk.END)
            text.insert("1.0", t)


def command_save_file():
    global text
    filepath = filedialog.asksaveasfilename()
    if filepath != "":
        t = text.get("1.0", tk.END)
        with open(filepath, "w") as file:
            file.write(t)


def on_tab(event):
    global text
    text.insert(tk.INSERT, " " * 4)
    return "break"


def on_control_mousewheel(event):
    global text_font
    new_size = text_font.cget("size")
    if event.delta < 0:
        new_size = max(8, new_size - 2)
    else:
        new_size = min(72, new_size + 2)
    text_font.config(size=new_size)
    return "break"


def pick_term():
    global root, text
    global pattern_term, color_term
    
    s = text.get("1.0", tk.END)

    for k, (p, c) in enumerate(zip(pattern_term, color_term)):
        tag = f"found {k}"
        text.tag_delete(tag)

        for g in re.finditer(p, s):
            i, j = g.span()
            text.tag_add(tag, f"1.0+{i}c", f"1.0+{j}c")

        text.tag_config(tag, foreground=c)

    root.after(500, pick_term)


# main

pattern_term = (
    r"IF\s",
    r"THEN\s",
    r"ELSE\s",
    r"TRUE\s",
    r"FALSE\s",
    r'"(?:[^"]|\s)*?"\s', # STRING
)
color_term = (
    "blue",
    "blue",
    "blue",
    "ForestGreen",
    "ForestGreen",
    "coral",
)

root = tk.Tk()
root.option_add("*Dialog.msg.font", "courier 10")
root.geometry("600x400")
root.title("Condition Interpreter")

frame_top = tk.Frame(root)
frame_top.pack(side=tk.TOP, anchor=tk.W)

btn_help = tk.Button(text="help", width=10, font="courier 14 bold",
                    bg="grey80", command=command_help)
btn_help.pack(in_=frame_top, side=tk.LEFT)

btn_run = tk.Button(text="run", width=10, font="courier 14 bold",
                    bg="grey80", command=command_run)
btn_run.pack(in_=frame_top, side=tk.LEFT)

btn_open_file = tk.Button(text="open", width=10, font="courier 14 bold",
                        bg="grey80", command=command_open_file)
btn_open_file.pack(in_=frame_top, side=tk.LEFT)

btn_save_file = tk.Button(text="save", width=10, font="courier 14 bold",
                        bg="grey80", command=command_save_file)
btn_save_file.pack(in_=frame_top, side=tk.LEFT)

text_font = font.Font(family="courier", size=28, weight=font.BOLD)

text = tk.Text(root, font=text_font, wrap=tk.NONE)

scrollX = tk.Scrollbar(root, command=text.xview, orient=tk.HORIZONTAL)
scrollX.pack(side=tk.BOTTOM, fill=tk.X)

scrollY = tk.Scrollbar(root, command=text.yview, orient=tk.VERTICAL)
scrollY.pack(side=tk.RIGHT, fill=tk.Y)

text.insert("1.0", 'IF TRUE THEN\n    "Hello, World!"\nELSE\n    "Bye, World."')
text.config(xscrollcommand=scrollX.set, yscrollcommand=scrollY.set)
text.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

text.bind("<Tab>", on_tab)
text.bind_all("<Control-MouseWheel>", on_control_mousewheel)

root.after(500, pick_term)
root.mainloop()
