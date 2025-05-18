import numpy as np
from scipy.signal import find_peaks

def pr_score_vvr(t, e, h, s):
    lPR = np.nan
    rPR = np.nan
    saccade_positions = []

    if s == 1:
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

        peaks, props = find_peaks(
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

    if len(latency_L) > 3:
        lPR = round(np.std(latency_L) / np.mean(latency_L) * 100)
    if len(latency_R) > 3:
        rPR = round(np.std(latency_R) / np.mean(latency_R) * 100)

    lPR = min(lPR, 100) if not np.isnan(lPR) else lPR
    rPR = min(rPR, 100) if not np.isnan(rPR) else rPR

    return lPR, rPR, saccade_positions