import numpy as np
import matplotlib.pyplot as plt

def update_all_plots(axs, t, e, h, s, metrics, plot4="Fourier Gain"):
    # Ajuste global de espaciado entre subplots
    plt.subplots_adjust(hspace=0.4, wspace=0.3)
    plt.rcParams.update({'axes.edgecolor': '#555', 'axes.linewidth': 0.8})

    color_head = "#37474F"
    color_eye = "#FF6F00"
    color_left = "#1E88E5"
    color_right = "#E53935"
    color_ref_left = (0.2, 0.2, 0.2, 0.58)
    color_ref_right = (0, 0, 0, 0.85)
    color_saccade = "#212121"

    font_title = {'fontsize': 10, 'fontweight': 'bold'}
    font_tick = {'labelsize': 8}
    font_legend = {'fontsize': 8}

    # === Raw Data ===
    ax = axs[0, 0]
    ax.clear()
    ax.plot(t, h, color=color_head, label='Head', linewidth=2.0, alpha=0.9)
    ax.plot(t, e, color=color_eye, label='Eye', linewidth=1.2, alpha=0.65)
    ax.fill_between(t, h, e, color="#FFE0B2", alpha=0.12)
    ymin = np.min(h) - 50
    ymax = np.max(h) + 50
    ax.set_ylim(ymin, ymax)
    ax.set_title("Raw Data", **font_title)
    ax.legend(loc='upper right', **font_legend)
    ax.tick_params(**font_tick)
    ax.set_ylabel("Velocity (°/s)", fontsize=8)
    
    ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.6)
    for spine in ax.spines.values():
        spine.set_visible(False)

    # === Desaccaded Data ===
    ax = axs[0, 1]
    ax.clear()
    desac_e = metrics.get("desac_e", np.zeros_like(e))
    ax.plot(t, h, color=color_head, label='Head', linewidth=2.0, alpha=0.9)
    ax.plot(t, desac_e, color=color_eye, label='Desacc Eye', linewidth=1.2, alpha=0.65)
    ax.fill_between(t, h, desac_e, color="#FFE0B2", alpha=0.12)
    ymin = np.min(h) - 50
    ymax = np.max(h) + 50
    ax.set_ylim(ymin, ymax)
    ax.set_title(f"Desaccaded – AUC Gain: L={metrics.get('gain_auc_L', 0):.2f} R={metrics.get('gain_auc_R', 0):.2f}", **font_title)
    ax.legend(loc='upper right', **font_legend)
    ax.tick_params(**font_tick)
    ax.set_ylabel("Velocity (°/s)", fontsize=8)
    
    ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.6)
    for spine in ax.spines.values():
        spine.set_visible(False)

    # === FFT Spectrum ===
    ax = axs[1, 0]
    ax.clear()
    fH = metrics.get("fH", [])
    P1H = metrics.get("P1H", [])
    fE = metrics.get("fE", [])
    P1E = metrics.get("P1E", [])

    if len(fH) > 0 and len(P1H) > 0:
        ax.vlines(fH, 0, P1H, colors=color_head, linewidth=1.5, label='Head', zorder=1)
        ax.scatter(fH, P1H, color=color_head, s=24, marker='o', zorder=2)

    if len(fE) > 0 and len(P1E) > 0:
        ax.vlines(fE, 0, P1E, colors=color_eye, linewidth=1.0, label='Eye', zorder=3)
        ax.scatter(fE, P1E, color=color_eye, s=18, marker='^', zorder=4)

    ax.set_xlim(0, 5)
    ax.set_title(f"FFT Spectrum – Head Peak: {metrics.get('maxFreqHeadFour', 0):.2f} Hz", **font_title)
    ax.legend(loc='upper right', **font_legend)
    ax.tick_params(**font_tick)
    ax.set_ylabel("Amplitude", fontsize=8)
    
    ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.6)
    for spine in ax.spines.values():
        spine.set_visible(False)

    # === Fourth Plot ===
    ax = axs[1, 1]
    ax.clear()
    ax.tick_params(**font_tick)
    
    if plot4 == "Fourier Gain":
        leftFouGain = metrics.get("leftFouGain", 0)
        rightFouGain = metrics.get("rightFouGain", 0)
        ax.scatter(['Left Gain'], [leftFouGain], s=160, c=[color_left], edgecolor="k", label="Left Gain", zorder=3)
        ax.scatter(['Right Gain'], [rightFouGain], s=160, c=[color_right], edgecolor="k", label="Right Gain", zorder=3)
        ax.axhline(1, color="#888", linestyle="--", linewidth=2.1, zorder=4)
        ax.set_ylim(0, 1.25)
        ax.set_xlim(-0.5, 1.5)
        ax.set_title(f"Fourier Gain – L={leftFouGain:.2f} R={rightFouGain:.2f}", **font_title)
        ax.set_xticks([0, 1])
        ax.set_xticklabels(["Left Gain", "Right Gain"])
        ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.6)
        for spine in ax.spines.values():
            spine.set_visible(False)
    elif plot4 == "Regression Gain":
        plot_regression_gain(ax, t, e, h, s, metrics)
    elif plot4 == "Saccade Detection":
        plot_saccade_detection(ax, t, e, h, s, metrics)

def plot_regression_gain(ax, t, e, h, s, metrics):
    color_left = "#1E88E5"
    color_right = "#E53935"
    color_ref_left = (0.2, 0.2, 0.2, 0.58)
    color_ref_right = (0, 0, 0, 0.95)

    desac_e = metrics.get("desac_e", np.zeros_like(e))
    posH = h[h > 0]
    posE = desac_e[h > 0] if len(desac_e) == len(h) else np.array([])
    negH = h[h < 0]
    negE = desac_e[h < 0] if len(desac_e) == len(h) else np.array([])
    m_pos = metrics.get("m_pos", 0)
    m_neg = metrics.get("m_neg", 0)

    ax.scatter(posH, posE, s=7, c=color_left, alpha=0.22, label='Left data', zorder=1)
    ax.scatter(negH, negE, s=7, c=color_right, alpha=0.22, label='Right data', zorder=1)

    if len(posH) > 1:
        xL = np.linspace(np.min(posH), np.max(posH), 50)
        ax.plot(xL, xL, '--', color=color_ref_left, lw=1.1, zorder=3, label="Expected Left")
        ax.plot(xL, m_pos * xL, color=color_left, lw=2.5, zorder=2, label="Left regression")
    if len(negH) > 1:
        xR = np.linspace(np.min(negH), np.max(negH), 50)
        ax.plot(xR, xR, '--', color=color_ref_right, lw=1.3, zorder=3, label="Expected Right")
        ax.plot(xR, m_neg * xR, color=color_right, lw=2.5, zorder=2, label="Right regression")

    ax.set_title(f"Regression Gain – L={m_pos:.2f} R={m_neg:.2f}", fontsize=10, fontweight="bold")
    ax.legend(loc='lower right', fontsize=8)
    ax.tick_params(axis='both', which='major', labelsize=8)
    ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.6)
    for spine in ax.spines.values():
        spine.set_visible(False)

def plot_saccade_detection(ax, t, e, h, s, metrics):
    color_head = "#37474F"
    color_eye = "#FF6F00"
    color_saccade = "#212121"
    desac_e = metrics.get("desac_e", np.zeros_like(e))
    lPR = metrics.get("lPR", "-")
    rPR = metrics.get("rPR", "-")

    ax.plot(t, h, color=color_head, label='Head', linewidth=2.0, alpha=0.9)
    ax.plot(t, e, color=color_eye, label='Eye', linewidth=1.2, alpha=0.65)
    saccades = metrics.get("saccades", [])
    if len(saccades) > 0 and len(e) > 0 and len(t) > 0:
        sacades_y = np.interp(saccades, t, e)
        ax.scatter(saccades, sacades_y, s=28, c="none", edgecolors=color_saccade, linewidths=1.5, marker="o", label='Saccades')

    ymin = np.min(h) - 75
    ymax = np.max(h) + 75
    ax.set_ylim(ymin, ymax)
    ax.set_title(f"Saccade Detection – PR L={lPR if not np.isnan(lPR) else '-'} R={rPR if not np.isnan(rPR) else '-'}", fontsize=10, fontweight="bold")
    ax.legend(loc='upper right', fontsize=8)
    ax.tick_params(axis='both', which='major', labelsize=8)
    ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.6)
    for spine in ax.spines.values():
        spine.set_visible(False)

def update_six_plots(axs, t, e, h, s, metrics):
    update_all_plots(axs[:2, :], t, e, h, s, metrics, plot4="Fourier Gain")
    plot_regression_gain(axs[2, 0], t, e, h, s, metrics)
    axs[2, 0].set_ylabel("Eye Velocity (°/s)", fontsize=8)
    plot_saccade_detection(axs[2, 1], t, e, h, s, metrics)
    axs[2, 1].set_ylabel("Velocity (°/s)", fontsize=8)
    
