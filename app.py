# app.py

import pandas as pd
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route("/price-data")
def price_data():
    df = pd.read_csv("data/processed/BrentOilPrices_Log.csv")
    df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%d/%m/%Y")
    # df["Date"] = pd.to_datetime(df["Date"], dayfirst=True).dt.strftime("%d/%m/%Y")
    df = df.rename(columns={"Price": "price", "Date": "date"})
    return df.to_json(orient="records")


@app.route("/change-points")
def change_points():
    df = pd.read_csv("data/processed/change_points.csv")
    df["date"] = pd.to_datetime(df["date"], dayfirst=True).dt.strftime("%d/%m/%Y")
    return df.to_json(orient="records")


@app.route("/event-overlay")
def event_overlay():
    df = pd.read_csv("data/raw/Events.csv")
    df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%d/%m/%Y")
    return df.to_json(orient="records")


@app.route("/posterior-summary")
def posterior_summary():
    df = pd.read_csv("data/processed/posterior_summary.csv")
    df = df.rename(columns={"Unnamed: 0": "parameter"})
    return df.to_json(orient="records")


if __name__ == "__main__":
    app.run(debug=True)
