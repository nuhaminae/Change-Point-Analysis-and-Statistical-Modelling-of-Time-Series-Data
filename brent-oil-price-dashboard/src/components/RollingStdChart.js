/*RollingStdChart.js*/

import React, { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

function RollingStdChart() {
  const [data, setData] = useState([]);

  useEffect(() => {
    fetch("http://localhost:5000/price-data")
      .then((res) => res.json())
      .then((json) => setData(json));
  }, []);

  return (
    <div>
      <h3>Price Volatility</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="Year"
            textAnchor="end" />
          <YAxis
            label={{ value: "Rollind St.D", angle: -90, position: "outsideLeft", dx:-20, }}
            />
          <Tooltip />
          <Line type="monotone" dataKey="RollingStd" stroke="#0d00ffff" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default RollingStdChart;
