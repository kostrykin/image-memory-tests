#!/usr/bin/env python

import numpy as np
import tifffile
from PIL import Image


np.random.seed(0)

# The image size should be 30 MiB
img1 = np.random.randint(0, 255, size=(1024 * 10, 1024, 3), dtype=np.uint8)
assert img1.nbytes == 30 * 1024 * 1024, 'Unexpected image size'

# Write the image files
Image.fromarray(img1).save('test-data/img1.png')
tifffile.imwrite('test-data/img1.tiff', img1)
