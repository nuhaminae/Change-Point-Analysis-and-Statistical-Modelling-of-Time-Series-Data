// RollingStdChart.js

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';

const RollingStdChart = () => {
  const [data, setData] = useState([]);

  useEffect(() => {
    axios.get('http://localhost:5000/price-data')
      .then(res => setData(res.data))
      .catch(err => console.error('Error fetching data:', err));
  }, []);

  return (
    <div style={{ width: '100%', height: 400 }}>
      <h3>Rolling Standard Deviation of Brent Oil Prices</h3>
      <ResponsiveContainer>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" tickFormatter={(d) => new Date(d).getFullYear()} />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="RollingStd" stroke="#ff9900" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default RollingStdChart;
