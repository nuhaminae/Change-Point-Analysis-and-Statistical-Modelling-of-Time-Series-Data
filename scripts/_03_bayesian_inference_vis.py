# _03_bayesian_inference_vis.py
import logging
import os

import arviz as az
import matplotlib.pyplot as plt
import pandas as pd
from IPython.display import display


class ChangePointAnalysis:
    """
    This class performs Bayesian change point analysis on time series data,
    specifically focusing on Brent Oil prices. It includes functionality
    for loading and processing data, interpreting results from a PyMC trace,
    and matching the estimated change point to relevant events.
    """

    def __init__(self, log_price_path, trace, events_path, processed_dir, plot_dir):
        """
        Initialises the BrentOilDiagnostics class.

        Args:
            log_price_path (str): Path to the CSV file containing enriched oil prices.
            events_path (str): Path to the CSV file containing historical events.
            trace (InferenceData): Posterior samples from PyMC.
            processed_dir (str): Directory to save processed data.
            plot_dir (str): Directory to save generated plots.

        """
        self.log_price_path = log_price_path
        self.events_path = events_path
        self.processed_dir = processed_dir
        self.plot_dir = plot_dir
        self.trace = trace
        self.change_date = None

        # Create output directories if they do not exist
        if not os.path.exists(self.plot_dir):
            os.makedirs(self.plot_dir)
        if not os.path.exists(self.processed_dir):
            os.makedirs(self.processed_dir)

        self.load_data()
        print("ChangePointAnalysis Class initalised ...\n")

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
        logging.info(f"DataFrame loaded from {self.safe_relpath(self.log_price_path)}")
        # Return the DataFrame (optional, but good practice)
        return self.df

    def interpret_results(self):
        """
        Interpret results Save posterior summary statistics with visuals.
        """
        az.style.use("arviz-white")

        # Trace plot
        axes_array = az.plot_trace(self.trace)

        # Apply grid and x-axis rotation to all subplots
        for ax in axes_array.flatten():
            ax.grid(True)
            for label in ax.get_xticklabels():
                label.set_rotation(45)
                label.set_horizontalalignment("right")

        trace_path = os.path.join(self.plot_dir, "trace_plot.png")
        plt.savefig(trace_path)
        print(f"💾 Trace plot saved to {self.safe_relpath(trace_path)}")
        plt.show()
        plt.close()

        # Posterior Plot
        axes_array = az.plot_posterior(self.trace)

        # Apply grid and x-axis rotation to all subplots
        for ax in axes_array.flatten():
            ax.grid(True)
            for label in ax.get_xticklabels():
                label.set_rotation(45)
                label.set_horizontalalignment("right")

        posterior_path = os.path.join(self.plot_dir, "posterior_plot.png")
        plt.savefig(posterior_path)
        print(f"💾 Posterior plot saved to {self.safe_relpath(posterior_path)}")
        plt.show()
        plt.close()

        # Energy plot for sampler diagnostics
        az.plot_energy(self.trace)
        plt.grid()

        energy_path = os.path.join(self.plot_dir, "energy_plot.png")
        plt.savefig(energy_path)
        print(f"💾 Energy plot saved to {self.safe_relpath(energy_path)}")
        plt.show()
        plt.close()

    def load_event_data(self):
        """
        Loads event data with 'Event' and 'Date' columns.
        """
        self.events = pd.read_csv(self.events_path)
        self.events["Date"] = pd.to_datetime(self.events["Date"])
        print("Event data loaded.")
        return self.events

    def match_change_point_to_event(self, window_days=60, price_window=30):
        """
        Matches each estimated change point (τ₁, τ₂, τ₃) to nearby events.
        Adds volatility and price impact summaries. Saves all to a single CSV.
        """

        if not hasattr(self, "events"):
            print("⚠️ Event data not loaded. Call load_event_data() first.")
            return

        tau_means = {
            "τ₁": int(self.trace.posterior["tau_1"].mean().values),
            "τ₂": int(self.trace.posterior["tau_2"].mean().values),
        }

        change_dates = {label: self.df.index[idx] for label, idx in tau_means.items()}
        self.change_date = change_dates

        print("\n📍 Estimated Change Points:")
        for label, date in change_dates.items():
            print(f"  {label}: {date.date()}")

        all_matched_events = []

        print("\n🔎 Matching Events Within ±{} Days:".format(window_days))
        for label, date in change_dates.items():
            window_start = date - pd.Timedelta(days=window_days)
            window_end = date + pd.Timedelta(days=window_days)

            nearby_events = self.events[
                self.events["Date"].between(window_start, window_end)
            ].copy()

            change_idx = tau_means[label]

            # Volatility before and after
            log_returns = self.df["LogReturn"].dropna()
            vol_before = round(
                log_returns.iloc[max(0, change_idx - 60) : change_idx].std(), 4
            )
            vol_after = round(log_returns.iloc[change_idx : change_idx + 60].std(), 4)

            # Price change around τ
            prices = self.df["Price"].dropna()
            price_before = round(
                prices.iloc[max(0, change_idx - price_window) : change_idx].mean(), 4
            )
            price_after = round(
                prices.iloc[change_idx : change_idx + price_window].mean(), 4
            )
            price_change_pct = round(
                (((price_after - price_before) / price_before) * 100), 4
            )

            nearby_events["MatchedTo"] = label
            nearby_events["ChangePointDate"] = date

            # Annotate each event
            nearby_events["MatchedTo"] = label
            nearby_events["ChangePointDate"] = date
            nearby_events["VolatilityBefore"] = vol_before
            nearby_events["VolatilityAfter"] = vol_after
            nearby_events["PriceBefore"] = price_before
            nearby_events["PriceAfter"] = price_after
            nearby_events["PriceChangePct"] = price_change_pct

            print(f"🕒 Around {label} ({date.date()}):")
            if nearby_events.empty:
                print("  No events found in this window.")
            else:
                print("  Event has been found in this window.")
                all_matched_events.append(nearby_events)

        # Combine and save
        if all_matched_events:
            combined_df = pd.concat(all_matched_events, ignore_index=True)
            display(combined_df)
            output_path = os.path.join(self.processed_dir, "matched_events.csv")
            combined_df.to_csv(output_path, index=False)
            print(f"\n💾 All matched events saved to: {self.safe_relpath(output_path)}")
        else:
            print("⚠️ No events matched any change point. CSV not created.")

    def run_analysis(self):
        self.interpret_results()
        self.load_event_data()
        self.match_change_point_to_event()
