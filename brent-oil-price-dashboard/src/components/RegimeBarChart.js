/*RegimeBarChart*/


import React, { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from "recharts";


function getColor(volatility) {
  // Normalise volatility to a 0–1 scale (based on your data range)
  const minVol = 0.015; // adjust based on your dataset
  const maxVol = 0.06;
  const ratio = Math.min(Math.max((volatility - minVol) / (maxVol - minVol), 0), 1);

  // Interpolate between blue (#4A90E2) and red (#D0021B)
  const r = Math.round(74 + ratio * (208 - 74));
  const g = Math.round(144 + ratio * (2 - 144));
  const b = Math.round(226 + ratio * (27 - 226));

  return `rgb(${r}, ${g}, ${b})`;
}

function RegimeBarChart() {
  const [data, setData] = useState([]);

  useEffect(() => {
    fetch("http://localhost:5000/regime-volatility")
      .then((res) => res.json())
      .then((json) => setData(json));
  }, []);

  return (
    <div>
      <h3>Volatility by Regime</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="Regime"
            textAnchor="end" />
          <YAxis label={{ value: "Volatality", angle: -90, position: "outsideLeft", dx:-20, }}
          />
          <Tooltip />
          <Bar dataKey="Volatility">
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getColor(entry.Volatility)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default RegimeBarChart;
