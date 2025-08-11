/*App.js*/

import React from "react";
import './App.css';
import EventTypeDonutChart from "./components/EventTypeDonutChart";
import LogReturnChart from"./components/LogReturnChart";
import PriceChart from "./components/PriceChart";
import RegimeBarChart from "./components/RegimeBarChart";
import RollingStdChart from "./components/RollingStdChart"

function App() {
  return (
    <div className="App">
      <h1>Brent Oil Dashboard: Price, Volatility & Events</h1>

      <div className="dashboard-layout">
        <div className="chart-container">
          <PriceChart />
        </div>

        <div className="chart-row">
          <div className="chart-container">
            <LogReturnChart />
          </div>
          <div className="chart-container">
            <RollingStdChart />
          </div>
        </div>

        <div className="chart-row">
          <div className="chart-container">
            <RegimeBarChart />
          </div>
          <div className="chart-container">
            <EventTypeDonutChart />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
