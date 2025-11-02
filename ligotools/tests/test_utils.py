import numpy as np
from pathlib import Path
from scipy.io import wavfile
from ligotools.utils import whiten, reqshift, write_wavfile


def test_whiten_identity_psd_preserves_shape_and_correlation():
    """
    Checks that whiten() preserves the input signal shape and structure 
    when given a flat (constant) PSD.

    - Creates a simple test signal (sum of sine waves).
    - Uses an identity PSD (no frequency weighting).
    - Checks that:
        * Output has same length as input.
        * Output is finite (no NaNs/Infs).
        * Output remains highly correlated with the input (> 0.99).
    This ensures that whitening behaves as a scaled pass-through when the PSD is uniform.
    
    """
    fs = 4096.0
    dt = 1.0 / fs
    t = np.arange(0, 1.0, dt)
    x = np.sin(2*np.pi*123*t) + 0.3*np.sin(2*np.pi*300*t)
    interp_psd = lambda freqs: np.ones_like(freqs)  # flat PSD

    y = whiten(x, interp_psd, dt)

    assert y.shape == x.shape
    assert np.isfinite(y).all()
    corr = np.corrcoef(x, y)[0, 1]
    assert corr > 0.99


def test_reqshift_moves_peak_frequency():
    """
    Checks that reqshift() correctly shifts the signal's dominant frequency.

    - Creates a pure 440 Hz sine wave.
    - Shifts it upward by 100 Hz using reqshift().
    - Uses FFT to find dominant frequency before and after.
    - Checks that the peak moves by approximately the shift amount.
    This verifies that reqshift performs the expected frequency translation.
    """
    fs = 4096
    T = 1.0
    t = np.arange(0, T, 1.0/fs)
    f0 = 440.0
    fshift = 100.0

    x = np.sin(2*np.pi*f0*t)
    y = reqshift(x, fshift=fshift, sample_rate=fs)

    def dom_freq(sig):
        spectrum = np.fft.rfft(sig)
        freqs = np.fft.rfftfreq(sig.size, d=1.0/fs)
        return freqs[np.argmax(np.abs(spectrum))]

    f_x = dom_freq(x)
    f_y = dom_freq(y)

    assert abs(f_x - f0) <= 2.0
    assert abs(f_y - (f0 + fshift)) <= 2.0


def test_write_wavfile_roundtrip(tmp_path: Path):
    """
    Checks that write_wavfile() correctly writes a WAV file readable by SciPy.

    - Creates a small synthetic float array.
    - Writes it to a temporary .wav file using write_wavfile().
    - Reads the file back using scipy.io.wavfile.read().
    - Checks that:
        * The file exists and is non-empty.
        * The sample rate matches the input.
        * The data type is int16 (as expected).
        * The number of samples matches the original data length.
    This ensures correct scaling and encoding of waveform data.
    
    """
    fs = 4096
    data = np.array([0.0, 0.5, -0.5, 0.25, -0.25], dtype=float)
    out = tmp_path / "tiny.wav"

    write_wavfile(out, fs, data)
    assert out.exists() and out.stat().st_size > 0

    sr, d = wavfile.read(out)
    assert sr == fs
    assert d.dtype == np.int16
    assert len(d) == len(data)
