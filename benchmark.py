#!/usr/bin/env python

import csv
import sys
from collections import Counter

import numpy as np
import rasterio

from tests_tiff import tifffile_hist_combined
from tools import (
    get_peak_memory_usage,
    timeit,
)


def count_unique_values_rasterio(file_path):
    counter = Counter()

    with rasterio.open(file_path) as src:
        for _, window in src.block_windows(1):  # Read in small windows
            data = src.read(1, window=window)  # Read only the small chunk
            unique, counts = np.unique(data, return_counts=True)
            counter.update(dict(zip(unique, counts)))

    return len(counter)


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
    tifffile_hist_combined,
    count_unique_values_rasterio,
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
            func,
            filename,
            runtime,
            peak_memory_usage / (1024 ** 2),
        ],
    )
csv_writer = csv.writer(sys.stdout)
for row in rows:
    csv_writer.writerow(row)
