#!/usr/bin/env python

import csv
import sys

import numpy as np

from tests_tiff import (
    rasterio_hist_patchwise,
    tifffile_hist_combined,
)
from tools import (
    get_hist,
    get_peak_memory_usage,
    timeit,
)


def benchmark(func, *args):
    with timeit() as runtime:
        func(*args)
    with get_peak_memory_usage() as peak_memory_usage:
        func(*args)
    return float(runtime), int(peak_memory_usage)


# Run the benchmarks
filenames = [
    'img1.tiff',
    'img1_czlib.tiff',
    'img1_tiled.tiff',
]
func_list = [
    rasterio_hist_patchwise,
    tifffile_hist_combined,
]
results = dict()
for filename in filenames:
    for func in func_list:
        filepath = f'test-data/{filename}'
        results[(filename, func.__name__)] = benchmark(func, filepath)

# Write the results
rows = [
    [
        'Function',
        'Filename',
        'Runtime (seconds)',
        'Memory usage (MiB)',
    ],
]
for ((filename, func), (runtime, peak_memory_usage)) in sorted(results.items(), key=lambda r: r[0][::-1]):
    rows.append(
        [
            f'`{func}`',
            filename,
            runtime,
            peak_memory_usage / (1024 ** 2),
        ],
    )
csv_writer = csv.writer(sys.stdout)
for row in rows:
    csv_writer.writerow(row)
