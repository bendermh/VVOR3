import numpy as np
import re
from tkinter import messagebox
from analysis_window import launch_analysis_window


def analyze_test_block(test):
    raw = test['raw']
    tipo = test['tipo']
    fecha = test['fecha']

    # Extract lines after <DecimalSeparator>
    lines = raw.split('\n')
    idx = next((i for i, line in enumerate(lines) if '<DecimalSeparator>' in line), None)

    if idx is None or idx + 2 >= len(lines):
        messagebox.showerror("Error", "<DecimalSeparator> not found or incomplete block.")
        return

    data_lines = [line.replace(',', '.') for line in lines[idx+2:] if line.strip()]

    data = []
    for line in data_lines:
        try:
            nums = list(map(float, line.strip().split(';')))
            if len(nums) == 9:
                data.append(nums)
        except ValueError:
            continue  # skip invalid lines

    if not data:
        messagebox.showerror("Error", "No valid numeric data found in test block.")
        return

    data = np.array(data)
    t_raw = data[:, 0]
    t = (t_raw - t_raw[0]) / 10000000  # Convert to seconds
    h = data[:, 1]
    e = data[:, 2]

    # Detect test type
    tipo_lower = tipo.lower()
    if 'vvor' in tipo_lower or 'rvvo' in tipo_lower:
        s = 0
    elif 'vors' in tipo_lower or 'srvo' in tipo_lower:
        s = 1
    else:
        messagebox.showwarning("Not Implemented", f"Test type not supported: {tipo}")
        return

    label_info = f"{fecha} | {tipo}"
    launch_analysis_window(t, e, h, s, label_info)
