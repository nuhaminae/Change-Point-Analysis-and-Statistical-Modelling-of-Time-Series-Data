/*PriceChart.js*/

import React, { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from "recharts";

function PriceChart() {
  const [data, setData] = useState([]);

  useEffect(() => {
    fetch("http://localhost:5000/price-data")
      .then((res) => res.json())
      .then((json) => setData(json));
  }, []);

  return (
    <div>
      <h3>Brent Oil Price Over Time with Trend</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="Year"
            textAnchor="end"
          />
          <YAxis
            label={{ value: "Price (USD per barrel)", angle: -90, position: "outsideLeft", dx:-20, }}
          />

          <Tooltip />
          <Line type="monotone" dataKey="Price" stroke="#ff0000ff" dot={false} />
          <Line type="monotone" dataKey="RollingMean" stroke="#2600ffff" dot={false} />
        <Legend verticalAlign="top" align="center" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default PriceChart;
