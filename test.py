import os
import tempfile

import numpy as np
import rasterio
import tifffile


def hist_uint8(img):
    assert img.dtype == np.uint8
    h = np.zeros(256, int)
    for i in range(256):
        h[i] = (img == i).sum()
    return h


# Create test image
np.random.seed(0)
img1 = np.random.randint(0, 255, size=(1024 * 10, 1024, 3), dtype=np.uint8)

# Compute expected histogram
hist1 = hist_uint8(img1)

with tempfile.TemporaryDirectory() as tmpdirpath:

    # Write the TIFF file
    filepath = os.path.join(tmpdirpath, 'img1.tiff')
    tifffile.imwrite(filepath, img1)

    # Read the TIFF file with rasterio and compute histogram
    hist2 = np.zeros(256, int)
    total_length = 0
    with rasterio.open(filepath) as src:
        for bidx in range(src.count):
            for _, window in src.block_windows(1):
                data = src.read(bidx + 1, window=window)
                hist2 += hist_uint8(data)
                total_length += np.prod(data.shape)

    print(np.prod(img1.shape))
    print(total_length)

    print('*** 1', hist1)
    print('*** 2', hist2)

    # Verify consistency
    assert (hist1 == hist2).all()
