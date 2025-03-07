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


@contextlib.contextmanager
def get_peak_memory_usage():
    """Führt die Funktion aus und gibt den Peak Memory Usage zurück (in Bytes)."""
    with tempfile.TemporaryDirectory() as temp_dir_path:
        temp_filepath = os.path.join(temp_dir_path, 'memray.bin')
        tracker = memray.Tracker(temp_filepath)

        result = PeakMemoryMonitor()
        with tracker:
            yield result

        reader = memray.FileReader(temp_filepath)
        result.value = sum(r.size for r in reader.get_high_watermark_allocation_records(merge_threads=True))
