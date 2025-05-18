# Fourier transform, SPI, SNR calculation
import numpy as np

def compute_fft(data, Fs=250):
    """
    Computes the single-sided amplitude spectrum of a signal.
    Returns: frequency vector, amplitude spectrum, SPI, SNR
    """
    L = len(data)
    Y = np.fft.fft(data)
    P2 = np.abs(Y / L)
    P1 = P2[:L//2 + 1]
    if L > 2:
        P1[1:-1] = 2 * P1[1:-1]
    f = Fs * np.arange(0, L//2 + 1) / L

    # SPI = max peak / total energy
    max_val = np.max(P1)
    spi = max_val / np.sum(P1) if np.sum(P1) != 0 else 0

    # SNR = 10 * log10(signal / noise)
    noise_power = np.sum(P1) - max_val
    snr = 10 * np.log10(max_val / noise_power) if noise_power > 0 else 0

    return f, P1, spi, snr

