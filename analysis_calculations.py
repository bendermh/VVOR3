import numpy as np
from scipy.signal import find_peaks
from fft_utils import compute_fft

def pr_score_vvr(t, e, h, s):
    lPR = np.nan
    rPR = np.nan
    saccade_positions = []
    if s == 1 or len(t) < 4 or len(e) < 4 or len(h) < 4:
        return lPR, rPR, saccade_positions
    sig_pos = h > 0
    cros = sig_pos.astype(int) - np.roll(sig_pos.astype(int), 1)
    cros_pos = np.where(cros != 0)[0]
    latency_L = []
    latency_R = []
    for n in range(1, len(cros_pos)):
        start = cros_pos[n - 1]
        end = cros_pos[n]
        h_int = h[start:end]
        e_int = e[start:end]
        t_int = t[start:end]
        if len(e_int) < 4 or np.max(np.abs(h_int)) < 15:
            continue
        left = cros[start] == 1
        peaks, _ = find_peaks(
            np.abs(e_int),
            height=180,
            prominence=130,
            width=(None, 20)
        )
        if len(peaks) > 0:
            latency = t_int[peaks[0]] - t_int[0]
            saccade_positions.append(t_int[peaks[0]])
            if left:
                latency_L.append(latency)
            else:
                latency_R.append(latency)
    if len(latency_L) > 3 and np.mean(latency_L) != 0:
        lPR = round(np.std(latency_L) / np.mean(latency_L) * 100)
    if len(latency_R) > 3 and np.mean(latency_R) != 0:
        rPR = round(np.std(latency_R) / np.mean(latency_R) * 100)
    lPR = min(lPR, 100) if not np.isnan(lPR) else lPR
    rPR = min(rPR, 100) if not np.isnan(rPR) else rPR
    return lPR, rPR, saccade_positions

def calculate_all_metrics(t, e, h, s):
    """
    Calculates and returns a dictionary with all the numerical metrics needed for plots and summary.
    Safe for empty or too-short data.
    """
    Fs = 250  # Hz
    kernel = 35 if s else 30
    desac_e = np.convolve(e, np.ones(kernel) / kernel, mode='same') if len(e) >= kernel else e.copy() if len(e) > 0 else np.array([])
    pos_mask = h > 0
    neg_mask = h < 0
    dataEyeL = desac_e[pos_mask] if len(desac_e) == len(h) else np.array([])
    dataHeadL = h[pos_mask]
    dataEyeR = desac_e[neg_mask] if len(desac_e) == len(h) else np.array([])
    dataHeadR = h[neg_mask]
    # Gains (avoid zero division and empty arrays)
    gain_auc_L = np.nan
    gain_auc_R = np.nan
    if len(dataHeadL) > 1 and np.abs(np.trapz(dataHeadL, dx=1/Fs)) > 0:
        gain_auc_L = np.trapz(dataEyeL, dx=1/Fs) / np.trapz(dataHeadL, dx=1/Fs)
    if len(dataHeadR) > 1 and np.abs(np.trapz(dataHeadR, dx=1/Fs)) > 0:
        gain_auc_R = np.trapz(np.abs(dataEyeR), dx=1/Fs) / np.trapz(np.abs(dataHeadR), dx=1/Fs)
    # FFTs and spectral metrics
    fH, P1H, spi_h, snr_h = compute_fft(h) if len(h) > 1 else ([], [], np.nan, np.nan)
    fE, P1E, spi_e, snr_e = compute_fft(e) if len(e) > 1 else ([], [], np.nan, np.nan)
    ixx = np.argmax(P1H) if len(P1H) > 0 else 0
    maxFreqHeadFour = fH[ixx] if len(fH) > 0 and ixx < len(fH) else np.nan
    # Fourier Gain
    fHeadL, P1HeadL, _, _ = compute_fft(dataHeadL) if len(dataHeadL) > 1 else ([], [], np.nan, np.nan)
    fEyeL, P1EyeL, _, _ = compute_fft(dataEyeL) if len(dataEyeL) > 1 else ([], [], np.nan, np.nan)
    fHeadR, P1HeadR, _, _ = compute_fft(dataHeadR) if len(dataHeadR) > 1 else ([], [], np.nan, np.nan)
    fEyeR, P1EyeR, _, _ = compute_fft(dataEyeR) if len(dataEyeR) > 1 else ([], [], np.nan, np.nan)
    if len(P1HeadL) > 0:
        maxHeadPwrL = np.max(P1HeadL)
        idxL = np.argmax(P1HeadL)
        maxEyeLPwr = P1EyeL[idxL] if idxL < len(P1EyeL) else np.nan
        leftFouGain = maxEyeLPwr / maxHeadPwrL if maxHeadPwrL > 0 else np.nan
    else:
        leftFouGain = np.nan
    if len(P1HeadR) > 0:
        maxHeadPwrR = np.max(P1HeadR)
        idxR = np.argmax(P1HeadR)
        maxEyeRPwr = P1EyeR[idxR] if idxR < len(P1EyeR) else np.nan
        rightFouGain = maxEyeRPwr / maxHeadPwrR if maxHeadPwrR > 0 else np.nan
    else:
        rightFouGain = np.nan
    # Regression gains
    posH = h[h > 0]
    posE = desac_e[h > 0] if len(desac_e) == len(h) else np.array([])
    negH = h[h < 0]
    negE = desac_e[h < 0] if len(desac_e) == len(h) else np.array([])
    m_pos = np.polyfit(posH, posE, 1)[0] if len(posH) > 1 and len(posE) > 1 else np.nan
    m_neg = np.polyfit(negH, negE, 1)[0] if len(negH) > 1 and len(negE) > 1 else np.nan
    # PR, saccades
    lPR, rPR, saccades = pr_score_vvr(t, e, h, s)
    # Include FFT for plotting
    # headVelocc mean data
    mean_peak_head = np.nan
    std_peak_head = np.nan
    if len(h) > 3:
        peaks_max, _ = find_peaks(h, height=30, prominence=10)
        peaks_min, _ = find_peaks(-h, height=30, prominence=10)
        all_peaks = np.concatenate((h[peaks_max], h[peaks_min]))
        all_peaks = np.abs(all_peaks)  # ← Este paso es clave
        if len(all_peaks) > 1:
            mean_peak_head = np.mean(all_peaks)
            std_peak_head = np.std(all_peaks)
    metrics = {
        "desac_e": desac_e,
        "gain_auc_L": gain_auc_L,
        "gain_auc_R": gain_auc_R,
        "leftFouGain": leftFouGain,
        "rightFouGain": rightFouGain,
        "spi_h": spi_h, "spi_e": spi_e,
        "snr_h": snr_h, "snr_e": snr_e,
        "maxFreqHeadFour": maxFreqHeadFour,
        "m_pos": m_pos, "m_neg": m_neg,
        "lPR": lPR, "rPR": rPR,
        "saccades": saccades,
        "mean_peak_head": mean_peak_head,
        "std_peak_head": std_peak_head,
        # For FFT plot
        "fH": fH, "P1H": P1H, "fE": fE, "P1E": P1E
    }
    return metrics