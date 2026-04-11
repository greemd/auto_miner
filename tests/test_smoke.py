"""Smoke tests to verify the environment is correctly set up."""


def test_import_auto_alpha_miner():
    import auto_alpha_miner

    assert auto_alpha_miner.__version__ == "0.1.0"


def test_import_numpy():
    import numpy as np

    assert np.__version__


def test_import_pandas():
    import pandas as pd

    assert pd.__version__


def test_import_scipy():
    import scipy

    assert scipy.__version__


def test_import_matplotlib():
    import matplotlib

    assert matplotlib.__version__


def test_import_sklearn():
    import sklearn

    assert sklearn.__version__
