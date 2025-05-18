import tkinter as tk
from tkinter import Toplevel, Button, filedialog, StringVar, OptionMenu
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from analysis_calculations import calculate_all_metrics
from analysis_plots import update_all_plots, update_six_plots
import numpy as np

def launch_analysis_window(t, e, h, s, label_info):
    win = Toplevel()
    win.title(f"VOR Analysis — {label_info}")
    win.geometry("1700x950")
    win.configure(bg="#242426")

    # ========== HEADER: Results | Help | Buttons ==========
    header_frame = tk.Frame(win, bg="#242426")
    header_frame.pack(fill=tk.X, padx=0, pady=(0,0))

    # 1. Results (wide, large font)
    results_text = tk.Text(header_frame, height=7, width=67, bg="#242426", fg="white",
                           font=("Consolas", 14, "bold"), relief=tk.FLAT, borderwidth=0, wrap=tk.WORD, highlightthickness=0)
    results_text.grid(row=0, column=0, sticky='nw', padx=(15, 6), pady=(4, 2))
    results_text.config(state=tk.DISABLED)

    # 2. Help (wider, bigger font)
    help_text = tk.Text(header_frame, height=7, width=55, bg="#292930", fg="#FAFAFA",
                        font=("Arial", 13, "bold"), relief=tk.FLAT, borderwidth=0, wrap=tk.WORD)
    help_text.grid(row=0, column=1, sticky='nw', padx=(4, 6), pady=(4, 2))
    help_text.insert(tk.END,
        "Interface Help\n"
        "• Click (left): Set/adjust analysis window (on Raw/Desaccaded plots)\n"
        "• Double-click: Restore full window (on Raw/Desaccaded plots)\n"
        "• Data Cursor: Enable, then click any plot (except fourth)\n"
        "• Clear Data Cursors: Remove all markers\n"
        "• While Data Cursor is enabled, window selection is locked\n"
        "• Use selector (right) to change fourth plot"
    )
    help_text.config(state=tk.DISABLED)

    # 3. Botones (compact, vertical center)
    btn_frame = tk.Frame(header_frame, bg="#242426", width=135)
    btn_frame.grid(row=0, column=2, sticky='n', padx=(0, 10), pady=(18, 2))
    btn_frame.grid_propagate(False)

    plot_selector_var = StringVar(value="Fourier Gain")
    plot_selector_label = tk.Label(btn_frame, text="Fourth Plot:", font=('Arial', 11, 'bold'),
                                  fg="white", bg="#242426")
    plot_selector_label.pack(anchor='center', pady=(0, 3))

    plot_selector = OptionMenu(btn_frame, plot_selector_var,
                               "Fourier Gain", "Regression Gain", "Saccade Detection")
    plot_selector.config(font=('Arial', 11), width=12)
    plot_selector.pack(anchor='center', pady=(0, 8))

    save_btn = Button(btn_frame, text="💾 Save Figure", font=('Arial', 11), padx=5, pady=3, width=13)
    save_btn.pack(anchor='center', fill=tk.X, pady=2)
    cursor_btn = Button(btn_frame, text="📌 Enable Data Cursor", font=('Arial', 11), padx=5, pady=3, width=13)
    cursor_btn.pack(anchor='center', fill=tk.X, pady=2)
    clear_cursor_btn = Button(btn_frame, text="🧹 Clear Data Cursors", font=('Arial', 11), padx=5, pady=3, width=13)
    clear_cursor_btn.pack(anchor='center', fill=tk.X, pady=2)

    # ========== PLOTS (2x2 grid, full width below header) ==========
    plot_frame = tk.Frame(win, bg="#242426")
    plot_frame.pack(fill=tk.BOTH, expand=True)
    fig, axs = plt.subplots(2, 2, figsize=(15.5, 8.7))
    fig.subplots_adjust(hspace=0.37, wspace=0.22)
    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    summary_text = ""
    data_cursor_active = [False]
    all_annotations = []
    all_markers = []

    # Variables for window selection
    tmin_original = t[0]
    tmax_original = t[-1]
    tmin = [tmin_original]
    tmax = [tmax_original]

    def remove_all_cursors():
        nonlocal all_annotations, all_markers
        for annotation in all_annotations:
            try: annotation.remove()
            except Exception: pass
        all_annotations.clear()
        for marker in all_markers:
            try: marker.remove()
            except Exception: pass
        all_markers.clear()
        canvas.draw()

    def enable_data_cursor():
        if not data_cursor_active[0]:
            cursor_btn.config(text="Disable Data Cursor")
            canvas.mpl_connect('button_press_event', on_data_cursor_click)
            data_cursor_active[0] = True
        else:
            cursor_btn.config(text="📌 Enable Data Cursor")
            data_cursor_active[0] = False
            remove_all_cursors()

    def on_data_cursor_click(event):
        if not data_cursor_active[0]: return
        if event.inaxes is None or event.button != 1: return
        ax = event.inaxes
        lines = [l for l in ax.get_lines() if l.get_visible() and len(l.get_xdata()) > 0]
        if not lines: return
        x_clicked = event.xdata
        closest_x, closest_y = None, None
        min_dist = float('inf')
        for line in lines:
            xdata = line.get_xdata()
            ydata = line.get_ydata()
            idx = (np.abs(xdata - x_clicked)).argmin()
            dist = abs(xdata[idx] - x_clicked)
            if dist < min_dist:
                min_dist = dist
                closest_x, closest_y = xdata[idx], ydata[idx]
        annotation = ax.annotate(f"x={closest_x:.2f}\ny={closest_y:.2f}",
                                xy=(closest_x, closest_y), xytext=(10, 10),
                                textcoords='offset points',
                                bbox=dict(boxstyle="round,pad=0.2", fc="yellow", alpha=0.7),
                                fontsize=11, color='black')
        marker, = ax.plot(closest_x, closest_y, marker='x', markersize=13, color='#1976D2', markeredgewidth=2)
        all_annotations.append(annotation)
        all_markers.append(marker)
        canvas.draw()

    def save_figure():
        path = filedialog.asksaveasfilename(defaultextension=".png",
                                            filetypes=[("PNG Image", "*.png")])
        if path:
            metrics = calculate_all_metrics(t, e, h, s)
            # New figure for all 6 plots (3x2)
            savefig, saveaxs = plt.subplots(3, 2, figsize=(16.5, 13))
            savefig.subplots_adjust(hspace=0.38, wspace=0.22, top=0.90, bottom=0.12)
            update_all_plots(saveaxs, t, e, h, s, metrics, plot4=plot_selector_var.get())
            from analysis_plots import plot_regression_gain, plot_saccade_detection
            plot_regression_gain(saveaxs[2,0], t, e, h, s, metrics)
            plot_saccade_detection(saveaxs[2,1], t, e, h, s, metrics)
            # Prepare result text block for bottom of figure
            if not np.isnan(metrics['maxFreqHeadFour']):
                freq_str = f"Dominant Head Freq: {metrics['maxFreqHeadFour']:.2f} Hz\n"
            else:
                freq_str = "Dominant Head Freq: - Hz\n"
            summary = (
                f"Time window: {t[0]:.2f}–{t[-1]:.2f} s (Δt = {t[-1]-t[0]:.2f} s)\n"
                f"Max Head Vel: {np.nanmax(np.abs(h)) if len(h)>0 else '-'} °/s | "
                f"Max Eye Vel: {np.nanmax(np.abs(metrics['desac_e'])) if 'desac_e' in metrics and len(metrics['desac_e'])>0 else '-'} °/s\n"
                f"{freq_str}"
                f"SPI Head: {metrics['spi_h']:.2f} | Eye: {metrics['spi_e']:.2f}   SNR Head: {metrics['snr_h']:.1f} dB | Eye: {metrics['snr_e']:.1f} dB\n"
                f"Gain (slope) L: {metrics['m_pos']:.2f} | R: {metrics['m_neg']:.2f}   "
                f"AUC Gain L: {metrics['gain_auc_L']:.2f} | R: {metrics['gain_auc_R']:.2f}   "
                f"Fourier Gain L: {metrics['leftFouGain']:.2f} | R: {metrics['rightFouGain']:.2f}\n"
                f"PR Score: L = {metrics['lPR']} | R = {metrics['rPR']}"
            )
            savefig.text(0.5, 0.005, summary, ha='center', fontsize=12, color="#222", wrap=True)
            savefig.savefig(path, dpi=300)
            plt.close(savefig)

    def update_plots(*args):
        nonlocal summary_text
        # Restore selected time window (restore to full range if needed)
        idx = (t >= tmin[0]) & (t <= tmax[0])
        t_window = t[idx]
        e_window = e[idx]
        h_window = h[idx]
        for ax in axs.flatten():
            ax.clear()
        metrics = calculate_all_metrics(t_window, e_window, h_window, s)
        update_all_plots(axs, t_window, e_window, h_window, s, metrics, plot4=plot_selector_var.get())
        canvas.draw()
        if not np.isnan(metrics['maxFreqHeadFour']):
            freq_str = f"Dominant Head Freq: {metrics['maxFreqHeadFour']:.2f} Hz\n"
        else:
            freq_str = "Dominant Head Freq: - Hz\n"
        summary = (
            f"Time window: {t_window[0]:.2f}–{t_window[-1]:.2f} s (Δt = {t_window[-1]-t_window[0]:.2f} s)\n"
            f"Max Head Vel: {np.nanmax(np.abs(h_window)) if len(h_window)>0 else '-'} °/s | "
            f"Max Eye Vel: {np.nanmax(np.abs(metrics['desac_e'])) if 'desac_e' in metrics and len(metrics['desac_e'])>0 else '-'} °/s\n"
            f"{freq_str}"
            f"SPI Head: {metrics['spi_h']:.2f} | Eye: {metrics['spi_e']:.2f}   SNR Head: {metrics['snr_h']:.1f} dB | Eye: {metrics['snr_e']:.1f} dB\n"
            f"Gain (slope) L: {metrics['m_pos']:.2f} | R: {metrics['m_neg']:.2f}   "
            f"AUC Gain L: {metrics['gain_auc_L']:.2f} | R: {metrics['gain_auc_R']:.2f}   "
            f"Fourier Gain L: {metrics['leftFouGain']:.2f} | R: {metrics['rightFouGain']:.2f}\n"
            f"PR Score: L = {metrics['lPR']} | R = {metrics['rPR']}"
        )
        results_text.config(state=tk.NORMAL)
        results_text.delete('1.0', tk.END)
        results_text.insert(tk.END, summary)
        results_text.config(state=tk.DISABLED)
        summary_text = summary

    def on_plot_click(event):
        """Allow window selection with click/double-click only on Raw and Desaccaded plots."""
        if data_cursor_active[0]:
            return
        # Only first row (axs[0,0] and axs[0,1])
        if event.inaxes in [axs[0,0], axs[0,1]]:
            xt = event.xdata
            if event.dblclick:
                tmin[0], tmax[0] = t[0], t[-1]
            elif event.button == 1 and xt is not None:
                # Find closest edge
                if abs(xt - tmin[0]) < abs(xt - tmax[0]):
                    tmin[0] = max(min(xt, tmax[0]-0.1), t[0])
                else:
                    tmax[0] = min(max(xt, tmin[0]+0.1), t[-1])
                if tmin[0] > tmax[0]:
                    tmin[0], tmax[0] = tmax[0], tmin[0]
            update_plots()

    canvas.mpl_connect('button_press_event', on_plot_click)
    save_btn.config(command=save_figure)
    cursor_btn.config(command=enable_data_cursor)
    clear_cursor_btn.config(command=remove_all_cursors)
    plot_selector_var.trace_add('write', lambda *args: update_plots())

    update_plots()