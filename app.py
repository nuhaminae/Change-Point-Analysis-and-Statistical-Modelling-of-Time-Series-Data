# app.py

import pandas as pd
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route("/price-data")
def price_data():
    df = pd.read_csv("data/processed/BrentOilPrices_Log.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    df["Year"] = df["Date"].dt.year
    df["Date"] = df["Date"].dt.strftime("%d/%m/%Y")
    df = df.dropna()
    return df.to_json(orient="records")


@app.route("/matched-events")
def matched_events():
    df = pd.read_csv("data/processed/matched_events.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    df["Year"] = df["Date"].dt.year
    df["Date"] = df["Date"].dt.strftime("%d/%m/%Y")
    return df.to_json(orient="records")


@app.route("/event-overlay")
def event_overlay():
    import pandas as pd

    df = pd.read_csv("data/raw/Events.csv")

    # Format date
    df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%d/%m/%Y")

    # Calculate event type percentages
    type_counts = df["Event Type"].value_counts()
    total = type_counts.sum()
    type_percentages = (type_counts / total * 100).round(2)

    # Format for frontend
    formatted = [
        {"type": event_type, "percentage": pct}
        for event_type, pct in type_percentages.items()
    ]

    return pd.DataFrame(formatted).to_json(orient="records")


@app.route("/regime-volatility")
def regime_volatility():
    df = pd.read_csv("data/processed/volatility_by_regime.csv")
    # Rename regime labels
    regime_map = {
        "Before τ₁": "Before 2011",
        "Between τ₁–τ₂": "2011–2020",
        "After τ₂": "After 2020",
    }
    df["Regime"] = df["Regime"].replace(regime_map)
    return df.to_json(orient="records")


@app.route("/change-points")
def change_points():
    df = pd.read_csv("data/processed/change_points.csv")
    df = df.rename(columns={"date": "Date"})
    df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%d/%m/%Y")
    return df.to_json(orient="records")


@app.route("/posterior-summary")
def posterior_summary():
    df = pd.read_csv("data/processed/posterior_summary.csv")
    df = df.rename(columns={"Unnamed: 0": "parameter"})
    return df.to_json(orient="records")


if __name__ == "__main__":
    app.run(debug=True)
