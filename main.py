#VVOR main file

import tkinter as tk
from tkinter import filedialog, messagebox
import re
from analysis import analyze_test_block
import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


# ----- Step 1: Load .txt and parse tests -----
def load_and_parse_tests(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        raw_text = f.read()

    start_indices = [m.start() for m in re.finditer(r'<TestUID>', raw_text)]
    if not start_indices:
        return []

    end_indices = start_indices[1:] + [len(raw_text)]

    tests = []
    for start, end in zip(start_indices, end_indices):
        block = raw_text[start:end]
        uid = re.search(r'<TestUID>(.*?)</TestUID>', block)
        tipo = re.search(r'<TestType>(.*?)</TestType>', block)
        fecha = re.search(r'<StartDateTime>(.*?)</StartDateTime>', block)
        
        if uid and tipo and fecha:
            tests.append({
                'uid': uid.group(1),
                'tipo': tipo.group(1),
                'fecha': fecha.group(1),
                'raw': block
            })
    return tests

# ----- Step 2: GUI Application -----
class VORApp:
    def __init__(self, root):
        self.root = root
        self.root.title("VOR Test Selector")

        self.tests = []
        self.file_path = None

        # GUI layout
        self.load_button = tk.Button(root, text="Open .txt File", command=self.open_file)
        self.load_button.pack(pady=10)

        self.listbox = tk.Listbox(root, width=80, height=10)
        self.listbox.pack(pady=5)

        self.select_button = tk.Button(root, text="Analyze Selected Test", command=self.select_test)
        self.select_button.pack(pady=5)

    def open_file(self):
        filetypes = [('Text files', '*.txt')]
        filepath = filedialog.askopenfilename(title="Select VOR data file", filetypes=filetypes)
        if not filepath:
            return

        self.file_path = filepath
        self.load_tests_from_path(filepath)

    def load_tests_from_path(self, filepath):
        self.tests = load_and_parse_tests(filepath)
        self.listbox.delete(0, tk.END)

        if not self.tests:
            messagebox.showerror("No Tests Found", "No <TestUID> blocks found in file.")
            return

        for i, test in enumerate(self.tests):
            label = f"{test['fecha']} | {test['tipo']}"
            self.listbox.insert(tk.END, label)

    def select_test(self):
        index = self.listbox.curselection()
        if not index:
            messagebox.showwarning("No Selection", "Please select a test from the list.")
            return

        test = self.tests[index[0]]
        analyze_test_block(test)


if __name__ == '__main__':
    root = tk.Tk()
    icon_path = resource_path('vvor_icon.ico')
    root.iconbitmap(icon_path)
    app = VORApp(root)
    root.mainloop()
