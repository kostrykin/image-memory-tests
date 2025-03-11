# Image/Memory Tests

Before running the tests for the first time:

```python
mkdir test-data
./create_test_images.py
```

Running the tests:
```python
pytest -s --durations=0 tests_*.py
```

## Chunked reading PNG

### What we have tried:

- **Pillow** does not seem to support chunked reading, at least for PNG. The documentation ([link](https://pillow.readthedocs.io/en/stable/reference/Image.html)) kind of suggests between the lines, that the `crop` and `histogram` methods do not load the entire image into memory (loading is explicitly mentioned for other methods, but not for this one). However, our tests showed that both `crop` and `histogram` will load the entire image into memory.
- **imageio** does not seem to support chunked reading or anything similar.
- **pyvips** comes with external dependencies and seems a bit too heavy-weight.
- **pypng** is a PNG reader written entirely in Python, has no dependencies, and supports row-wise reading of PNG files. License is MIT.

### Conclusion:

Overall, using **pypng** seems to be most promising. The downside of it is that it is much slower than Pillow.

## Chunked reading TIFF

### Findings:

- **tifffile** supports chunked reading for TIFF files that are *tiled* (reading the tiles aka segments incrementally). This means, that the whole file does not have to be loaded entirely into memory. However, not all TIFF files are tiled, and even large TIFF files sometimes have just a single tile. In that case, loading the tile into memory would be equivalent to loading the entire image, which is discouraged.
- **tifffile** also support reading TIFF files via memory mapping, that can be used for chunked processing of the image data. However, there are some pitfalls:
  - This is somewhat slower than reading an image into memory directly (and can also be slower than loading the image tiles incrementally).
  - According to our tests, TIFF files that are *uncompressed and tiled*, cannot be mapped into virtual memory (it looks like the memory is actually allocated). Strangely though, it *does* work for tiled TIFF files that are *compressed*. The take-home message here is, that it works for *some tiled* files, but not for others.
- **rasterio** is too heavy-weight.
- There seem to be no useful alternatives out there.

### Conclusion:

Large TIFF files can be first checked for whether they are tiled or not (i.e. if they have more than one segment). In case of a tiled TIFF file, *chunked reading* directly supported by **tifffile** can be leveraged. Apparently, this is the same thing that rasterio does ([link](https://github.com/kostrykin/image-memory-tests/issues/1#issuecomment-2709021342)). If there is only a single segment, then chunked reading is inefficient, but the TIFF file can still be *mapped into virtual memory* and processed patch-wise, so that only small sections of the image data are loaded into memory, one at a time. This combined strategy of *chunked reading* and *memory mapping* should be at least as efficient as what rasterio does. Our benchmark supports that claim (see [below](#benchmark-results)).

## Test results

<!-- BEGIN TEST OUTPUT -->
```
============================= test session starts ==============================
platform linux -- Python 3.12.9, pytest-8.3.5, pluggy-1.5.0
rootdir: /home/runner/work/image-memory-tests/image-memory-tests
collected 17 items

tests_aux.py .
tests_png.py ....
tests_tiff.py ............

============================== slowest durations ===============================
34.31s call     tests_tiff.py::test_rasterio_patchwise[img1_tiled.tiff]
27.00s call     tests_png.py::test_pypng
25.18s call     tests_tiff.py::test_tifffile_combined[img1_tiled.tiff]
20.13s call     tests_tiff.py::test_rasterio_patchwise[img1.tiff]
17.00s call     tests_tiff.py::test_tifffile_combined[img1.tiff]
16.88s call     tests_tiff.py::test_tifffile_mmap_patchwise[img1.tiff-None]
16.62s call     tests_tiff.py::test_tifffile_mmap_patchwise[img1_tiled.tiff-AssertionError]
16.14s call     tests_tiff.py::test_tifffile_mmap_patchwise[img1_czlib.tiff-None]
11.35s call     tests_tiff.py::test_tifffile_runtime_mmap_vs_segments
5.63s call     tests_tiff.py::test_rasterio_patchwise[img1_czlib.tiff]
5.61s call     tests_tiff.py::test_tifffile_combined[img1_czlib.tiff]
0.33s call     tests_png.py::test_pil_histogram
0.32s call     tests_png.py::test_pil_crop
0.20s call     tests_png.py::test_full_image_load
0.03s call     tests_tiff.py::test_tifffile_segment
0.03s call     tests_aux.py::test_memory_monitoring

(35 durations < 0.005s hidden.  Use -vv to show these durations.)
======================== 17 passed in 197.04s (0:03:17) ========================
```
<!-- END OUTPUT -->

## Benchmark results

<!-- BEGIN BENCHMARK OUTPUT -->
| Function                  | Filename        |   Runtime (seconds) |   Memory usage (MiB) |
|---------------------------|-----------------|---------------------|----------------------|
| `rasterio_hist_patchwise` | img1.tiff       |            17.2943  |            31.428    |
| `rasterio_hist_patchwise` | img1_czlib.tiff |             2.8368  |            30.8933   |
| `rasterio_hist_patchwise` | img1_tiled.tiff |            31.8752  |            33.0092   |
| `tifffile_hist_combined`  | img1.tiff       |             8.61437 |             0.150497 |
| `tifffile_hist_combined`  | img1_czlib.tiff |             2.697   |             1.03949  |
| `tifffile_hist_combined`  | img1_tiled.tiff |            12.017   |             2.54209  |
<!-- END OUTPUT -->

# See also

- [Writing a (simple) PNG decoder might be easier than you think](https://pyokagan.name/blog/2019-10-14-png/)
- [tifffile: Compressed vs. Uncompressed TIFF](https://github.com/kostrykin/image-memory-tests/issues/1)
