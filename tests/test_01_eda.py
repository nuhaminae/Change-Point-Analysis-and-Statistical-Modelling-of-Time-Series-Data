# tet_01_eda.py

import os
import sys
import tempfile
import warnings

import matplotlib
import numpy as np
import pandas as pd
import pytest

# Append project root for test imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import your EDA class
from scripts._01_eda import BrentOilDiagnostics

matplotlib.use("Agg")  # Use Anti-Grain Geometry backend (no GUI required)
warnings.filterwarnings("ignore", message=".*FigureCanvasAgg is non-interactive.*")


@pytest.fixture
def dummy_data():

    os.makedirs(os.path.join("data", "temp"), exist_ok=True)
    np.random.seed(42)  # for reproducibility

    df = pd.DataFrame(
        {
            "Date": pd.date_range("87-May-20", periods=200, freq="D"),
            "Price": np.random.uniform(18, 100, size=200),
        }
    )

    file_path = os.path.join("data", "temp", "temp.csv")
    df.to_csv(file_path, index=False)
    return file_path


# Create an eda instance
def test_eda_instance_creation(dummy_data):
    file_path = dummy_data
    plot_dir = tempfile.mkdtemp()
    processed_dir = tempfile.mkdtemp()
    eda = BrentOilDiagnostics(
        price_path=file_path,
        plot_dir=plot_dir,
        processed_dir=processed_dir,
        rolling_window=10,
    )
    assert eda is not None


# Test safe relative path
def test_safe_relpath_handles_different_drives():
    result = BrentOilDiagnostics.safe_relpath("some/path/to/file", start=None)
    assert isinstance(result, str)


# Test load data
def test_load_data_parsing(dummy_data):
    eda = BrentOilDiagnostics(dummy_data, tempfile.mkdtemp(), tempfile.mkdtemp())
    df = eda.load_data()
    assert isinstance(df.index, pd.DatetimeIndex)
    assert "Price" in df.columns
    assert df.shape[0] == 200


# Test plot raw prices
def test_plot_raw_prices_runs(dummy_data):
    eda = BrentOilDiagnostics(dummy_data, tempfile.mkdtemp(), tempfile.mkdtemp())
    eda.plot_raw_prices()  # visual side-effect only, test no crash


# Test compute rolling stats
def test_compute_rolling_stats_creates_columns(dummy_data):
    eda = BrentOilDiagnostics(
        dummy_data, tempfile.mkdtemp(), tempfile.mkdtemp(), rolling_window=5
    )
    eda.compute_rolling_stats()
    assert "RollingMean" in eda.df.columns
    assert "RollingStd" in eda.df.columns


# Test plot rolling stats
def test_plot_rolling_stats_executes(dummy_data):
    eda = BrentOilDiagnostics(
        dummy_data, tempfile.mkdtemp(), tempfile.mkdtemp(), rolling_window=5
    )
    eda.compute_rolling_stats()
    eda.plot_rolling_stats()  # side-effect: plot


# Test run stationary tests
def test_stationarity_on_price(dummy_data, capsys):
    eda = BrentOilDiagnostics(dummy_data, tempfile.mkdtemp(), tempfile.mkdtemp())
    eda.compute_rolling_stats()  # ensure no NaNs
    eda.run_stationarity_tests("Price")
    captured = capsys.readouterr()
    assert "ADF p-value" in captured.out
    assert "KPSS p-value" in captured.out


# Test compute log returns
def test_log_return_column_created(dummy_data):
    eda = BrentOilDiagnostics(dummy_data, tempfile.mkdtemp(), tempfile.mkdtemp())
    eda.compute_log_returns()
    assert "LogReturn" in eda.df.columns


# Test plot log returns
def test_plot_log_returns(dummy_data):
    eda = BrentOilDiagnostics(dummy_data, tempfile.mkdtemp(), tempfile.mkdtemp())
    eda.compute_log_returns()
    eda.plot_log_returns()  # side-effect only


# Test run diagnostics
def test_run_diagnostics_flow(dummy_data):
    eda = BrentOilDiagnostics(dummy_data, tempfile.mkdtemp(), tempfile.mkdtemp())
    df_processed = eda.run_diagnostics()
    assert isinstance(df_processed, pd.DataFrame)
    assert "RollingMean" in df_processed.columns
    assert "LogReturn" in df_processed.columns


# Test get processed data
def test_get_processed_data_saves_file(dummy_data):
    eda = BrentOilDiagnostics(dummy_data, tempfile.mkdtemp(), tempfile.mkdtemp())
    eda.compute_log_returns()
    eda.get_processed_data()
    output_file = os.path.join(eda.processed_dir, "BrentOilPrices_Log.csv")
    assert os.path.exists(output_file)
