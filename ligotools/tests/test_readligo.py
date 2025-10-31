import numpy as np
from pathlib import Path
from ligotools import readligo as rl

DATA_DIR = Path("data")
FN_H1 = DATA_DIR / "H-H1_LOSC_4_V2-1126259446-32.hdf5"

def test_loaddata_basic_shapes():
    """Checks that loaddata returns aligned arrays and a channel dict"""
    assert FN_H1.exists(), f"Missing test file: {FN_H1}"
    strain, time, ch = rl.loaddata(str(FN_H1)) 
    assert isinstance(ch, dict)
    assert isinstance(strain, np.ndarray) and isinstance(time, np.ndarray)
    assert len(strain) == len(time) and len(strain) > 0

def test_loaddata_sampling_rate():
    """Checks that time step should be ~1/4096 s for LOSC 4 kHz files"""
    strain, time, _ = rl.loaddata(str(FN_H1))
    dt = float(time[1] - time[0])
    assert np.isclose(dt, 1/4096, atol=1e-5)

def test_dq_channel_to_seglist():
    """Checks that dq_channel_to_seglist maps a 1 Hz mask to fs-scaled slices"""
    mask = np.zeros(10, dtype=int)
    mask[2:5] = 1  #valid from 2s to 5s
    segs = rl.dq_channel_to_seglist(mask, fs=4096)
    assert len(segs) == 1
    s = segs[0]
    assert s.start == 2*4096 and s.stop == 5*4096
