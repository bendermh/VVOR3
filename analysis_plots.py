import numpy as np
import matplotlib.pyplot as plt

def update_all_plots(axs, t, e, h, s, metrics, plot4="Fourier Gain"):
    color_head = "#37474F"
    color_eye = "#FF6F00"
    color_left = "#1E88E5"
    color_right = "#E53935"
    color_ref_left = (0.2,0.2,0.2,0.58)  # greyish-black with alpha
    color_ref_right = (0,0,0,0.85)  # black, higher alpha
    color_saccade = "#212121"

    # Raw Data
    ax = axs[0, 0]
    ax.clear()
    ax.plot(t, h, color=color_head, label='Head')
    ax.plot(t, e, color=color_eye, label='Eye')
    ax.set_ylim(-300, 300)
    ax.set_title("Raw Data", fontsize=10)
    ax.legend(loc='upper right', fontsize=8)
    ax.tick_params(axis='both', which='major', labelsize=8)

    # Desaccaded Data with AUC Gain
    ax = axs[0, 1]
    ax.clear()
    desac_e = metrics.get("desac_e", np.zeros_like(e))
    ax.plot(t, h, color=color_head, label='Head')
    ax.plot(t, desac_e, color=color_eye, label='Desacc Eye')
    ax.set_ylim(-300, 300)
    ax.set_title(f"Desaccaded Data – AUC Gain: L={metrics.get('gain_auc_L', 0):.2f} R={metrics.get('gain_auc_R', 0):.2f}", fontsize=10)
    ax.legend(loc='upper right', fontsize=8)
    ax.tick_params(axis='both', which='major', labelsize=8)

    # FFT Spectrum
    ax = axs[1, 0]
    ax.clear()
    fH = metrics.get("fH", [])
    P1H = metrics.get("P1H", [])
    fE = metrics.get("fE", [])
    P1E = metrics.get("P1E", [])
    if len(fH) > 0 and len(P1H) > 0:
        ax.stem(fH, P1H, linefmt=color_head, markerfmt='o', basefmt=" ", label='Head')
    if len(fE) > 0 and len(P1E) > 0:
        ax.stem(fE, P1E, linefmt=color_eye, markerfmt='o', basefmt=" ", label='Eye')
    ax.set_xlim(0, 5)
    ax.set_title(f"FFT Spectrum – Head Peak: {metrics.get('maxFreqHeadFour', 0):.2f} Hz", fontsize=10)
    ax.legend(loc='upper right', fontsize=8)
    ax.tick_params(axis='both', which='major', labelsize=8)

    # Fourth plot
    ax = axs[1, 1]
    ax.clear()
    ax.tick_params(axis='both', which='major', labelsize=8)
    if plot4 == "Fourier Gain":
        leftFouGain = metrics.get("leftFouGain", 0)
        rightFouGain = metrics.get("rightFouGain", 0)
        ax.scatter(['Left Gain'], [leftFouGain], s=160, c=[color_left], edgecolor="k", label="Left Gain", zorder=3)
        ax.scatter(['Right Gain'], [rightFouGain], s=160, c=[color_right], edgecolor="k", label="Right Gain", zorder=3)
        # Line at 1.0
        ax.axhline(1, color="#888", linestyle="--", linewidth=2.1, zorder=4)
        ax.set_ylim(0, 1.25)
        ax.set_xlim(-0.5, 1.5)
        ax.set_title(f"Fourier Gain", fontsize=10)
        ax.set_xticks([0, 1], labels=["Left Gain", "Right Gain"], fontweight="bold")
        ax.tick_params(axis='both', which='major', labelsize=8)
    elif plot4 == "Regression Gain":
        plot_regression_gain(ax, t, e, h, s, metrics)
    elif plot4 == "Saccade Detection":
        plot_saccade_detection(ax, t, e, h, s, metrics)

def plot_regression_gain(ax, t, e, h, s, metrics):
    color_left = "#1E88E5"
    color_right = "#E53935"
    color_ref_left = (0.2,0.2,0.2,0.58)   # greyish-black, alpha
    color_ref_right = (0,0,0,0.95)   # black, higher alpha

    desac_e = metrics.get("desac_e", np.zeros_like(e))
    posH = h[h > 0]
    posE = desac_e[h > 0] if len(desac_e) == len(h) else np.array([])
    negH = h[h < 0]
    negE = desac_e[h < 0] if len(desac_e) == len(h) else np.array([])
    m_pos = metrics.get("m_pos", 0)
    m_neg = metrics.get("m_neg", 0)

    # Scatter
    ax.scatter(posH, posE, s=7, c=color_left, alpha=0.22, label='Left data', zorder=1)
    ax.scatter(negH, negE, s=7, c=color_right, alpha=0.22, label='Right data', zorder=1)

    # Reference lines (first, so always on top)
    if len(posH) > 1:
        xL = np.linspace(np.min(posH), np.max(posH), 50)
        ax.plot(xL, xL, '--', color=color_ref_left, lw=1.1, zorder=3, label="Expected Left")
    if len(negH) > 1:
        xR = np.linspace(np.min(negH), np.max(negH), 50)
        ax.plot(xR, xR, '--', color=color_ref_right, lw=1.3, zorder=3, label="Expected Right")

    # Real regression lines
    if len(posH) > 1:
        xL = np.linspace(np.min(posH), np.max(posH), 50)
        ax.plot(xL, m_pos * xL, color=color_left, lw=2.5, zorder=2, label="Left regression")
    if len(negH) > 1:
        xR = np.linspace(np.min(negH), np.max(negH), 50)
        ax.plot(xR, m_neg * xR, color=color_right, lw=2.5, zorder=2, label="Right regression")

    ax.set_title(f"Regression Gain – L={m_pos:.2f} R={m_neg:.2f}", fontsize=10)
    ax.legend(loc='lower right', fontsize=8)
    ax.tick_params(axis='both', which='major', labelsize=8)

def plot_saccade_detection(ax, t, e, h, s, metrics):
    color_head = "#37474F"
    color_eye = "#FF6F00"
    color_saccade = "#212121"
    desac_e = metrics.get("desac_e", np.zeros_like(e))
    lPR = metrics.get("lPR", "-")
    rPR = metrics.get("rPR", "-")
    ax.plot(t, h, color=color_head, label='Head')
    ax.plot(t, e, color=color_eye, label='Eye')
    saccades = metrics.get("saccades", [])
    if len(saccades) > 0 and len(e) > 0 and len(t) > 0:
        sacades_y = np.interp(saccades, t, e)
        ax.scatter(saccades, sacades_y, s=28, c="none", edgecolors=color_saccade, linewidths=1.5, marker="o", label='Saccades')
    ax.set_ylim(-300, 300)
    ax.set_title(f"Saccade Detection – PR L={lPR if not np.isnan(lPR) else '-'} R={rPR if not np.isnan(rPR) else '-'}", fontsize=10)
    ax.legend(loc='upper right', fontsize=8)
    ax.tick_params(axis='both', which='major', labelsize=8)

# Extra: for saving six plots at once
def update_six_plots(axs, t, e, h, s, metrics):
    # Raw Data
    update_all_plots(axs[:2, :], t, e, h, s, metrics, plot4="Fourier Gain")
    # Always fill the bottom row with regression and saccade
    plot_regression_gain(axs[2, 0], t, e, h, s, metrics)
    plot_saccade_detection(axs[2, 1], t, e, h, s, metrics)