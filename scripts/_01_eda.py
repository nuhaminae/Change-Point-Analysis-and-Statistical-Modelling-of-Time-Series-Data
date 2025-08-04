# _01_eda.py
import os
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import display
from statsmodels.tools.sm_exceptions import InterpolationWarning
from statsmodels.tsa.stattools import adfuller, kpss

warnings.filterwarnings("ignore", message="Could not infer format")


class BrentOilDiagnostics:
    """
    A class to perform diagnostic analysis on Brent Oil price data.

    This class loads Brent Oil price data, performs rolling statistics,
    stationarity tests, computes log returns, and generates plots
    to visualise the data and analysis results.
    """

    def __init__(self, price_path, plot_dir, processed_dir, rolling_window=180):
        """
        Initialises the BrentOilDiagnostics class.

        Args:
            price_path (str): Path to the CSV file containing Brent Oil prices.
            plot_dir (str): Directory to save generated plots.
            processed_dir (str): Directory to save processed data.
            rolling_window (int, optional): Window size for rolling calculations.
                                            Defaults to 180.
        """
        self.price_path = price_path
        self.plot_dir = plot_dir
        self.processed_dir = processed_dir
        self.rolling_window = rolling_window
        self.df = None

        # Create output directories if they do not exist
        if not os.path.exists(self.plot_dir):
            os.makedirs(self.plot_dir)
        if not os.path.exists(self.processed_dir):
            os.makedirs(self.processed_dir)

        self.load_data()

    @staticmethod
    def safe_relpath(path, start=None):
        """
        Return a relative path, handling cases where paths are on different drives.

        Args:
            path (str): The path to make relative.
            start (str, optional): The starting directory.
                                    Defaults to current working directory.

        Returns:
            str: The relative path if possible, otherwise the original path.
        """
        try:
            return os.path.relpath(path, start)
        except ValueError:
            # Fallback to absolute path if on different drives
            return path

    def load_data(self):
        """
        Loads the Brent Oil price data from the specified CSV file.

        The 'Date' column is converted to datetime objects and set as the index.
        """
        self.df = pd.read_csv(self.price_path)
        self.df["Date"] = pd.to_datetime(self.df["Date"], errors="coerce")
        self.df.set_index("Date", inplace=True)
        # Return the DataFrame (optional, but good practice)
        return self.df

    def plot_raw_prices(self):
        """
        Plots the raw Brent Oil prices over time.

        Saves the plot to the specified plot directory.
        """
        self.df["Price"].plot(title="Brent Oil Prices Over Time", figsize=(12, 4))
        plt.ylabel("USD/barrel")
        plt.grid()
        plt.tight_layout()

        if self.plot_dir:
            plot_path = os.path.join(self.plot_dir, "brent_oil_prices_over_time.png")
            plt.savefig(plot_path)
            # Print relative path for better readability
            print(f"\nPlot saved to {self.safe_relpath(plot_path)}")

        plt.show()
        plt.close()

    def compute_rolling_stats(self):
        """
        Computes rolling mean and standard deviation of the 'Price' column.

        The rolling window size is determined by `self.rolling_window`.
        Adds 'RollingMean' and 'RollingStd' columns to the DataFrame.
        """
        self.df["RollingMean"] = (
            self.df["Price"].rolling(window=self.rolling_window).mean()
        )
        self.df["RollingStd"] = (
            self.df["Price"].rolling(window=self.rolling_window).std()
        )

    def plot_rolling_stats(self):
        """
        Plots the rolling mean and rolling standard deviation of the 'Price' column.

        Saves the plots to the specified plot directory.
        """
        # Plot rolling mean overlay
        self.df[["Price", "RollingMean"]].plot(
            title="Rolling Mean Overlay", figsize=(12, 4)
        )
        plt.ylabel("USD/barrel")
        plt.grid()
        plt.tight_layout()

        if self.plot_dir:
            plot_path = os.path.join(self.plot_dir, "rolling_mean_overlay.png")
            plt.savefig(plot_path)
            print(f"\nPlot saved to {self.safe_relpath(plot_path)}")

        plt.show()
        plt.close()

        # Plot rolling standard deviation
        self.df["RollingStd"].plot(
            title="Rolling Volatility (Std Dev)", color="orange", figsize=(12, 4)
        )
        plt.ylabel("USD/barrel")
        plt.grid()
        plt.tight_layout()

        if self.plot_dir:
            plot_path = os.path.join(self.plot_dir, "rolling_volatility_(std_dev).png")
            plt.savefig(plot_path)
            print(f"\nPlot saved to {self.safe_relpath(plot_path)}")

        plt.show()
        plt.close()

    def run_stationarity_tests(self, series_name):
        """
        Runs Augmented Dickey-Fuller (ADF) and KPSS tests for stationarity
        on the specified time series.

        Args:
            series_name (str): The name of the column (time series) to test.
        """
        # Drop NaN values for stationarity tests
        series = self.df[series_name].dropna()
        adf_result = adfuller(series)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", InterpolationWarning)
            kpss_result = kpss(series, regression="c")

        print(
            f"{series_name} — ADF p-value:\
                {adf_result[1]:.4f} → Lower = More stationarity"
        )
        print(
            f"{series_name} — KPSS p-value:\
                {kpss_result[1]:.4f} → Higher = More stationarity\n"
        )

    def compute_log_returns(self):
        """
        Computes the log returns of the 'Price' column.

        Adds a 'LogReturn' column to the DataFrame.
        Log return is calculated as log(P_t) - log(P_t-1).
        """
        self.df["LogReturn"] = np.log(self.df["Price"]) - np.log(
            self.df["Price"].shift(1)
        )

    def plot_log_returns(self):
        """
        Plots the log returns of Brent Oil prices over time.

        Saves the plot to the specified plot directory.
        """
        self.df["LogReturn"].plot(title="Log Returns of Brent Prices", figsize=(12, 4))
        plt.ylabel("Log(P_t / P_t-1)")
        plt.grid()
        plt.tight_layout()

        if self.plot_dir:
            plot_path = os.path.join(self.plot_dir, "log_returns_of_brent_prices.png")
            plt.savefig(plot_path)
            print(f"\nPlot saved to {self.safe_relpath(plot_path)}")

        plt.show()
        plt.close()

    def run_diagnostics(self):
        """
        Runs the complete diagnostic process.

        Includes plotting raw prices, computing and plotting rolling statistics,
        running stationarity tests on raw prices, computing and plotting log returns,
        and running stationarity tests on log returns.

        Returns:
            pd.DataFrame: The DataFrame with added rolling statistics and log returns.
        """
        self.plot_raw_prices()
        self.compute_rolling_stats()
        self.plot_rolling_stats()
        self.run_stationarity_tests("Price")

        self.compute_log_returns()
        self.plot_log_returns()
        self.run_stationarity_tests("LogReturn")
        # Return the processed DataFrame
        return self.df

    def get_processed_data(self):
        """
        Prepares and saves the enriched DataFrame to a CSV file.

        Resets the index, formats the 'Date' column, saves the DataFrame
        to 'BrentOilPrices_Log.csv' in the processed data directory,
        and displays the head, shape, columns, info, and description
        of the processed DataFrame.

        Returns:
            None
        """
        # Reset the index so Date becomes a column again
        df_out = self.df.reset_index()
        # Ensure 'Date' is in datetime format, coercing errors
        df_out["Date"] = pd.to_datetime(df_out["Date"], errors="coerce")
        # Format the date to YYYY-MM-DD string
        df_out["Date"] = df_out["Date"].dt.strftime("%Y-%m-%d")
        # Convert back to datetime objects after formatting
        df_out["Date"] = pd.to_datetime(df_out["Date"])

        # Save processed data to CSV, without the pandas index
        df_out.to_csv(
            os.path.join(self.processed_dir, "BrentOilPrices_Log.csv"), index=False
        )
        print(f"Enriched DataFrame saved to {self.safe_relpath(self.processed_dir)}.")

        print("DataFrame Head:")
        display(df_out.head())
        print(f"\nShape: {df_out.shape}")
        print(f"\nColumns: {list(df_out.columns)}")
        print("\nDataFrame Info:")
        df_out.info()
        print("\nDescribe:")
        display(df_out.describe())
