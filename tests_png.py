import numpy as np
import png
import pytest
from PIL import Image

from tools import get_peak_memory_usage


def get_image_size_nbytes(filepath):
    return np.asarray(Image.open(filepath)).nbytes


def get_image_hist(filepath):
    arr = np.asarray(Image.open(filepath))
    return get_hist(arr)


def get_hist(array):
    hist = np.zeros(256)
    for value in range(len(hist)):
        hist[value] += (array == value).sum()
    return hist


def test_full_image_load():
    """
    Test that we can use `get_peak_memory_usage` to determine how much of an image was actually loaded into memory.

    The peak memory usage when loading the test image should be the size of the image (in bytes), at least.
    """

    # Check that the native memory allocated by NumPy is monitored
    with get_peak_memory_usage() as peak_memory_usage:
        img1 = np.asarray(Image.open('test-data/img1.png'))
    assert int(peak_memory_usage) >= img1.nbytes

    # Check that released memory is accounted
    shape = (1024, 1024, 3)
    with get_peak_memory_usage() as peak_memory_usage:
        for _ in range(5):
            np.zeros(shape, np.uint8)
    assert int(peak_memory_usage) < 1.1 * np.prod(shape)


def test_pil_histogram():
    """
    Test that the `histogram` method of an `Image` object loads the full image and is thus dangerous in terms of memory usage.
    """
    with get_peak_memory_usage() as peak_memory_usage:
        im = Image.open('test-data/img1.png')
        im.histogram()
    assert int(peak_memory_usage) >= get_image_size_nbytes('test-data/img1.png')


def test_pil_crop():
    """
    Test that the `crop` method of an `Image` object loads the full image and is thus dangerous in terms of memory usage.
    """
    with get_peak_memory_usage() as peak_memory_usage:
        im = Image.open('test-data/img1.png')
        (left, upper, right, lower) = (0, 0, 10, 10)
        im.crop((left, upper, right, lower))
    assert int(peak_memory_usage) >= get_image_size_nbytes('test-data/img1.png')


def test_pypng():
    """
    PyPNG is a pure-Python library without dependencies that allows reading PNG images row-wise.

    Extension to support 16bit PNG seems possible, albeit Pillow does not support 16bit PNG.
    """
    hist = get_image_hist('test-data/img1.png')
    with get_peak_memory_usage() as peak_memory_usage:
        reader = png.Reader(filename='test-data/img1.png')
        width, height, pixels, metadata = reader.asDirect()
        hist2 = np.zeros(256)
        for row in pixels:
            hist2 += get_hist(np.uint8(row))
    assert int(peak_memory_usage) < get_image_size_nbytes('test-data/img1.png'), 'Memory limit exceeded'
    assert (hist == hist2).all()
