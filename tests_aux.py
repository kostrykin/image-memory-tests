import numpy as np

from tools import get_peak_memory_usage


def test_memory_monitoring():
    # Check that released memory is accounted
    shape = (1024, 1024, 3)
    with get_peak_memory_usage() as peak_memory_usage:
        for _ in range(5):
            np.zeros(shape, np.uint8)
    assert int(peak_memory_usage) < 1.1 * np.prod(shape)
