import contextlib
import os
import tempfile

import memray
import numpy as np


class PeakMemoryMonitor:

    def __init__(self):
        self.value = None

    def __int__(self):
        if self.value is None:
            raise ValueError('Value was not determined yet')
        else:
            return self.value


def without_mmap(allocations):
    for a in allocations:
        if any('mmap' in call[1] and 'numpy' in call[1] for call in a.stack_trace()):
            continue
        else:
            yield a


@contextlib.contextmanager
def get_peak_memory_usage(exclude_mmap=True):
    """Führt die Funktion aus und gibt den Peak Memory Usage zurück (in Bytes)."""
    with tempfile.TemporaryDirectory() as temp_dir_path:
        temp_filepath = os.path.join(temp_dir_path, 'memray.bin')
        tracker = memray.Tracker(temp_filepath)

        result = PeakMemoryMonitor()
        with tracker:
            yield result

        reader = memray.FileReader(temp_filepath)
        allocs = reader.get_high_watermark_allocation_records(merge_threads=True)
        if exclude_mmap:
            allocs = without_mmap(allocs)
        result.value = sum(r.size for r in allocs)


def get_hist(array):
    hist = np.zeros(256, int)
    for value in range(len(hist)):
        hist[value] += (array == value).sum()
    return hist
