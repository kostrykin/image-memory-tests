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

### What we have found:

Overall, using **pypng** seems to be most promising. The downside of it is that it is much slower than Pillow, for example.

## Chunked reading TIFF

- **tifffile** does not directly support chunked reading. However, it *does* support reading TIFF files via memory mapping, which can be used to leverage chunked computation of the histogram. This is somewhat slower than reading an image into memory directly.
- There seem to be no useful alternatives out there.

## Test results

<!-- BEGIN TEST OUTPUT -->
<!-- END TEST OUTPUT -->

# See also

- [Writing a (simple) PNG decoder might be easier than you think](https://pyokagan.name/blog/2019-10-14-png/)
