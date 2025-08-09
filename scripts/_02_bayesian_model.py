# _02_bayesian_model.py

import os

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.abspath(os.path.join("..")), ".env"))


import arviz as az
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pymc as pm
import pytensor
import ruptures as rpt
from IPython.display import display
from statsmodels.tsa.stattools import adfuller

print("PYTENSOR_FLAGS =", os.getenv("PYTENSOR_FLAGS"))
print("PyTensor Optimizer =", pytensor.config.optimizer)
print("PyTensor CXX =", pytensor.config.cxx)


class RegimeMixtureModel:
    """
    This class defines a Bayesian model to detect a change point in the volatility
    of a time series using PyMC. It includes functions for data loading,
    frequentist change point detection using ruptures, building and running the
    Bayesian model, and saving the results.
    """

    def __init__(self, log_price_path, processed_dir, plot_dir):
        """
        Initialises the BrentOilDiagnostics class.

        Args:
            log_price_path (str): Path to the CSV file containing enriched oil prices.
            plot_dir (str): Directory to save generated plots.
            processed_dir (str): Directory to save processed data.
        """
        self.log_price_path = log_price_path
        self.processed_dir = processed_dir
        self.plot_dir = plot_dir
        self.model = None
        self.trace = None
        self.tau_1_mode = None
        self.tau_2_mode = None
        self.change_date = None

        # Create output directories if they do not exist
        if not os.path.exists(self.plot_dir):
            os.makedirs(self.plot_dir)
        if not os.path.exists(self.processed_dir):
            os.makedirs(self.processed_dir)

        self.load_data()
        print("\nRegimeMixtureModel class is initalised ...")

    def safe_relpath(self, path, start=None):
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

        self.df = pd.read_csv(self.log_price_path)
        self.df["Date"] = pd.to_datetime(self.df["Date"], errors="coerce")
        self.df.set_index("Date", inplace=True)
        print(f"DataFrame loaded from {self.safe_relpath(self.log_price_path)}")
        print(f"📄 Loaded {len(self.df)} rows of Brent oil data.")
        print(
            f"📅Date range: {self.df.index.min().date()} to {self.df.index.max().date()}"
        )
        print(f"📈 Columns available: {list(self.df.columns)}")
        # Return the DataFrame (optional, but good practice)
        return self.df

    def change_point_detection_with_ruptures(self):
        """
        Performs Frequentist Change Point Detection using ruptures (PELT) on Raw Price.
        Detects shifts in mean price level and visualises the change points.
        """
        if "Price" not in self.df.columns or self.df["Price"].isna().all():
            print(
                "⚠️ Price column is missing or empty. Skipping change point detection."
            )
            return

        time_series_price = self.df["Price"].dropna()

        if time_series_price.empty:
            print("⚠️ Price time series is empty after dropping NaNs.")
            return

        print("🔍 Running PELT change point detection on raw price...")
        signal_array = time_series_price.values.reshape(-1, 1)
        model = "l2"
        algo = rpt.Pelt(model=model).fit(signal_array)

        penalty = 3 * np.log(len(signal_array))
        change_points = algo.predict(pen=penalty)

        if change_points and change_points[-1] == len(time_series_price):
            change_points = change_points[:-1]

        self.change_date = time_series_price.index[change_points]
        # print(f"📍 Detected change point indices: {change_points}")
        # print(f"\n📅 Detected change point dates: {self.change_date.tolist()}")

        # Visualisation
        import matplotlib.pyplot as plt

        plt.figure(figsize=(18, 8))
        plt.plot(
            time_series_price.index,
            time_series_price.values,
            label="Brent Oil Price",
            color="blue",
            alpha=0.7,
        )
        for i, cp_date in enumerate(self.change_date):
            plt.axvline(
                x=cp_date,
                color="red",
                linestyle="--",
                linewidth=2,
                label="Detected Change Point (ruptures)" if i == 0 else "",
            )
        plt.title(
            "Frequentist Change Point Detection (ruptures - PELT) on Brent Oil Price"
        )
        plt.xlabel("Date")
        plt.ylabel("Price (USD)")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()

        if self.plot_dir:
            plot_path = os.path.join(self.plot_dir, "change_point_detection.png")
            plt.savefig(plot_path)
            print(f"\nPlot saved to {self.safe_relpath(plot_path)}")
        plt.show()
        plt.close()

    def build_volatility_model_with_pymc(self):
        """
        Builds a Bayesian model to detect two change points in volatility
        using log returns. This allows for three volatility regimes.
        """

        print("🔍 Performing Augmented Dickey-Fuller test on log returns...")
        log_returns = self.df["LogReturn"].dropna()
        print(f"📈 Number of log return observations: {len(log_returns)}")
        result = adfuller(log_returns)
        print(f"ADF Statistic: {result[0]:.4f}")
        print(f"p-value: {result[1]:.4f}")
        if result[1] < 0.05:
            print("Log returns are likely stationary.\n")
        else:
            print("Log returns may not be stationary.\n")

        if log_returns.empty:
            print("⚠️ Log return series is empty. Cannot build volatility model.")
            return

        data = log_returns.values
        idx = np.arange(len(data))

        log_returns = self.df["LogReturn"].dropna()
        log_return_index = log_returns.index

        target_years = [2011, 2017]
        target_indices = [
            log_return_index.get_loc(log_return_index[log_return_index.year == y][0])
            for y in target_years
        ]

        with pm.Model() as model:
            # tau_1 = pm.DiscreteUniform("tau_1", lower=0, upper=len(data))
            # tau_2 = pm.DiscreteUniform("tau_2", lower=tau_1, upper=len(data))
            # tau_3 = pm.DiscreteUniform("tau_3", lower=tau_2, upper=len(data))
            tau_1 = pm.DiscreteUniform(
                "tau_1", lower=target_indices[0], upper=target_indices[1]
            )
            tau_2 = pm.DiscreteUniform(
                "tau_2", lower=target_indices[1], upper=len(data)
            )

            sigma_1 = pm.HalfNormal("sigma_1", sigma=0.1)
            sigma_2 = pm.HalfNormal("sigma_2", sigma=0.1)
            sigma_3 = pm.HalfNormal("sigma_3", sigma=0.1)

            mu = pm.Normal("mu_log_return", mu=0, sigma=0.01)

            sigma = pm.math.switch(
                idx < tau_1, sigma_1, pm.math.switch(idx < tau_2, sigma_2, sigma_3)
            )

            pm.Normal("obs", mu=mu, sigma=sigma, observed=data)

            self.model = model
            self.log_return_index = log_returns.index

    def run_volatility_inference(self):
        """
        Runs MCMC sampling for the volatility change point model and saves results.
        """
        if self.model is None:
            print("⚠️ No model found. Run build_volatility_model_with_pymc() first.")
            return

        print("🚀 Starting PyMC sampling for volatility change point detection...")
        with self.model:
            self.trace = pm.sample(
                draws=2000,
                tune=1000,
                chains=4,
                cores=4,
                random_seed=42,
                return_inferencedata=True,
            )

        # Posterior summary
        print("\n📊 Sampling complete. Summary:")
        summary_df = az.summary(self.trace)
        output_path = os.path.join(self.processed_dir, "posterior_summary.csv")
        summary_df.to_csv(output_path)
        print(f"💾 Summary saved to {self.safe_relpath(output_path)}")
        display(summary_df)

        # Extract most probable change points
        tau_1_samples = self.trace.posterior["tau_1"].values.flatten()
        tau_2_samples = self.trace.posterior["tau_2"].values.flatten()

        self.tau_1_mode = int(pd.Series(tau_1_samples).mode().iloc[0])
        self.tau_2_mode = int(pd.Series(tau_2_samples).mode().iloc[0])

        tau_1_date = self.log_return_index[self.tau_1_mode]
        tau_2_date = self.log_return_index[self.tau_2_mode]

        print(
            f"\n📍 Most probable change point index: {self.tau_1_mode, self.tau_2_mode}"
        )
        print(f"📅 Most probable change point date: {tau_1_date, tau_2_date}")

        # Visualisation
        log_returns = self.df["LogReturn"].dropna()
        plt.figure(figsize=(18, 8))
        plt.plot(
            log_returns.index,
            log_returns.values,
            label="Log Returns",
            color="blue",
            alpha=0.7,
        )
        plt.axvline(
            x=tau_1_date,
            color="green",
            linestyle="-",
            linewidth=2,
            label="Change Point 1 (PyMC)",
        )
        plt.axvline(
            x=tau_2_date,
            color="purple",
            linestyle="-",
            linewidth=2,
            label="Change Point 2 (PyMC)",
        )
        plt.hist(
            self.log_return_index[tau_1_samples],
            bins=50,
            density=True,
            alpha=0.3,
            color="green",
            label="Posterior of τ₁",
        )
        plt.hist(
            self.log_return_index[tau_2_samples],
            bins=50,
            density=True,
            alpha=0.3,
            color="purple",
            label="Posterior of τ₂",
        )
        plt.title("Bayesian Volatility Change Point Detection (PyMC)")
        plt.xlabel("Date")
        plt.ylabel("Log Return")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()

        if self.plot_dir:
            plot_path = os.path.join(
                self.plot_dir, "volatility_change_point_detection.png"
            )
            plt.savefig(plot_path)
            print(f"\nPlot saved to {self.safe_relpath(plot_path)}")
        plt.show()
        plt.close()

        return self.trace

    def quantify_volatility_impact(self):
        """
        Quantifies volatility before, between, and after the detected change points.
        Computes standard deviation of log returns in each regime.
        """
        if self.trace is None or self.log_return_index is None:
            print("⚠️ Trace or index missing. Run inference first.")
            return

        log_returns = self.df["LogReturn"].dropna().copy()
        regime_1 = log_returns.iloc[: self.tau_1_mode]
        regime_2 = log_returns.iloc[self.tau_1_mode : self.tau_2_mode]
        regime_3 = log_returns.iloc[self.tau_2_mode :]

        vol_1 = regime_1.std()
        vol_2 = regime_2.std()
        vol_3 = regime_3.std()

        print("\n📊 Volatility by regime (standard deviation of log returns):")
        print(f"Regime 1 (before τ₁): {vol_1:.4f}")
        print(f"Regime 2 (between τ₁ and τ₂): {vol_2:.4f}")
        print(f"Regime 2 (after τ₂): {vol_3:.4f}")

        # Optional: Save to CSV
        vol_df = pd.DataFrame(
            {
                "Regime": ["Before τ₁", "Between τ₁–τ₂", "After τ₂"],
                "Volatility": [vol_1, vol_2, vol_3],
            }
        )
        output_path = os.path.join(self.processed_dir, "volatility_by_regime.csv")
        vol_df.to_csv(output_path, index=False)
        print(f"\n💾 Volatility summary saved to {self.safe_relpath(output_path)}")

    def save_summary_and_trace(self):
        """
        Saves the InferenceData trace as a NetCDF file.
        """
        # Saves the InferenceData trace as a NetCDF file.
        file_path = os.path.join(self.processed_dir, "model_trace.nc")
        az.to_netcdf(self.trace, file_path)
        print(f"\n💾 Trace saved to: {self.safe_relpath(file_path)}")

    def run_model_and_infer(self):
        print("🧪 Running full model pipeline...\n")
        self.change_point_detection_with_ruptures()
        self.build_volatility_model_with_pymc()
        self.run_volatility_inference()
        self.quantify_volatility_impact()
        self.save_summary_and_trace()
