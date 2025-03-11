import numpy as np
import pytest
import rasterio
import tifffile

from tools import (
    get_hist,
    get_peak_memory_usage,
    raises,
    timeit,
)


def get_image_size_nbytes(filepath):
    return tifffile.imread(filepath).nbytes


def get_image_hist(filepath):
    arr = tifffile.imread(filepath)
    return get_hist(arr)


def rasterio_hist_patchwise(filepath):
    hist = np.zeros(256, int)
    with rasterio.open(filepath) as src:
        for _, window in src.block_windows(1):
            for bidx in range(src.count):
                data = src.read(1 + bidx, window=window)
                hist += get_hist(data)
    return hist


@pytest.mark.parametrize(
    'filename',
    [
        'img1.tiff',
        'img1_czlib.tiff',
        'img1_tiled.tiff',
    ],
)
def test_rasterio_patchwise(filename):
    hist = get_image_hist('test-data/img1.tiff')
    hist2 = rasterio_hist_patchwise(f'test-data/{filename}')
    assert (hist == hist2).all()


def tifffile_read_segments(filepath):
    file = tifffile.TiffFile(filepath)
    page = file.pages[0]
    reader = page.parent.filehandle

    for segment_idx, (segment_offset, segment_size) in enumerate(zip(page.dataoffsets, page.databytecounts)):
        reader.seek(segment_offset)
        segment_data = reader.read(segment_size)
        yield page.decode(segment_data, segment_idx)[0]


def tifffile_hist_mmap_patchwise(filepath):
    file = tifffile.TiffFile(filepath)
    page = file.pages[0]
    arr = page.asarray(out='memmap')

    hist = np.zeros(256, int)
    window_size = (64, 64, 3)
    steps = np.divide(arr.shape, window_size).astype(int)
    for step in np.ndindex(*steps):
        p = np.multiply(window_size, step)
        q = p + window_size
        window = arr[p[0] : q[0], p[1] : q[1]]
        hist += get_hist(window)

    return hist


def test_tifffile_segment():
    with get_peak_memory_usage() as peak_memory_usage:
        next(tifffile_read_segments('test-data/img1.tiff'))

    with raises(AssertionError):
        assert int(peak_memory_usage) < get_image_size_nbytes('test-data/img1.tiff'), 'Memory limit exceeded'


def test_tifffile_mmap_czlib():
    """
    Test that a whole TIFF file that is compressed cannot be memory mapped into virtual memory.
    """
    with pytest.raises(ValueError):
        tifffile.memmap('test-data/img1_czlib.tiff')


@pytest.mark.parametrize(
    'filename,error',
    [
        ('img1.tiff', None),
        ('img1_czlib.tiff', None),
        ('img1_tiled.tiff', AssertionError),
    ],
)
def test_tifffile_mmap_patchwise(filename, error):
    hist = get_image_hist('test-data/img1.tiff')
    with get_peak_memory_usage() as peak_memory_usage:
        hist2 = tifffile_hist_mmap_patchwise(f'test-data/{filename}')

    with raises(error):
        assert int(peak_memory_usage) < get_image_size_nbytes('test-data/img1.tiff'), 'Memory limit exceeded'
    if error is not None:
        assert (hist == hist2).all()


def tifffile_hist_segments(filepath):
    file = tifffile.TiffFile(filepath)
    page = file.pages[0]
    hist = np.zeros(256, int)
    for segment in tifffile_read_segments(filepath):
        hist += get_hist(segment)
    return hist


def tifffile_hist_combined(filepath):
    file = tifffile.TiffFile(filepath)
    page = file.pages[0]

    if len(page.dataoffsets) > 1:
        # This is a tiled TIFF
        return tifffile_hist_segments(filepath)
    else:
        # This is not a tiled TIFF
        return tifffile_hist_mmap_patchwise(filepath)


@pytest.mark.parametrize(
    'filename',
    [
        'img1.tiff',
        'img1_czlib.tiff',
        'img1_tiled.tiff',
    ],
)
def test_tifffile_combined(filename):
    hist = get_image_hist('test-data/img1.tiff')
    filepath = f'test-data/{filename}'
    with get_peak_memory_usage() as peak_memory_usage:
        hist2 = tifffile_hist_combined(filepath)

    assert int(peak_memory_usage) < get_image_size_nbytes('test-data/img1.tiff'), 'Memory limit exceeded'
    assert (hist == hist2).all()


def test_tifffile_runtime_mmap_vs_segments():
    """
    Test that processing a tiled TIFF file by incrementally loading its segments is faster than via memory mapping.
    """
    filepath = 'test-data/img1_czlib.tiff'
    with timeit() as runtime_mmap:
        hist1 = tifffile_hist_mmap_patchwise(filepath)
    with timeit() as runtime_segments:
        hist2 = tifffile_hist_segments(filepath)
    assert (hist1 == hist2).all()
    assert float(runtime_mmap) > float(runtime_segments)
