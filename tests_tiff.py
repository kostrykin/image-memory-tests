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
            page.decode(segment_data, segment_idx)

    assert int(peak_memory_usage) >= get_image_size_nbytes('test-data/img1.tiff')


def test_tifffile_mmap_patchwise():
    with get_peak_memory_usage() as peak_memory_usage:
        file = tifffile.TiffFile('test-data/img1.tiff')
        page = file.pages[0]
        arr = page.asarray(out='memmap')

        hist2 = np.zeros(256, int)
        window_size = (64, 64, 3)
        steps = np.divide(arr.shape, window_size).astype(int)
        for step in np.ndindex(*steps):
            p = np.multiply(window_size, step)
            q = p + window_size
            window = arr[p[0] : q[0], p[1] : q[1]]
            hist2 += get_hist(window)

    assert int(peak_memory_usage) < get_image_size_nbytes('test-data/img1.tiff'), 'Memory limit exceeded'
