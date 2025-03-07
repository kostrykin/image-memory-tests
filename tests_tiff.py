import numpy as np
import tifffile

from tools import (
    get_hist,
    get_peak_memory_usage,
)


def get_image_size_nbytes(filepath):
    return tifffile.imread(filepath).nbytes


def get_image_hist(filepath):
    arr = tifffile.imread(filepath)
    return get_hist(arr)


def test_tifffile_segment():
    with get_peak_memory_usage() as peak_memory_usage:
        file = tifffile.TiffFile('test-data/img1.tiff')
        page = file.pages[0]
        reader = page.parent.filehandle

        for segment_idx, (segment_offset, segment_size) in enumerate(zip(page.dataoffsets, page.databytecounts)):
            reader.seek(segment_offset)
            segment_data = reader.read(segment_size)
            segment = page.decode(segment_data, segment_idx)[0]

    assert int(peak_memory_usage) > get_image_size_nbytes('test-data/img1.tiff')
