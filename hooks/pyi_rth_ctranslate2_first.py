# PyInstaller runtime hook — runs before user code at bundle startup.
#
# ctranslate2 and Qt both ship OpenMP runtime DLLs. Whichever loads first
# claims the shared allocator. If Qt loads first (via PyInstaller's rthooks),
# ctranslate2 segfaults when it initialises its thread pool at model-load time.
#
# This hook forces ctranslate2 to import (and thus load its DLLs) before any
# Qt module can load, mirroring the import-order fix in main.py.
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
import ctranslate2  # noqa: F401 — side-effect: loads OpenMP runtime DLL first
