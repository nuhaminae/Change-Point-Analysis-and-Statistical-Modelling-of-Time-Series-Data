// LogReturnChart.js

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';

const LogReturnChart = () => {
  const [data, setData] = useState([]);

  useEffect(() => {
    axios.get('http://localhost:5000/price-data')
      .then(res => setData(res.data))
      .catch(err => console.error('Error fetching data:', err));
  }, []);

  return (
    <div style={{ width: '100%', height: 400 }}>
      <h3>Log Returns of Brent Oil Prices</h3>
      <ResponsiveContainer>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" tickFormatter={(d) => new Date(d).getFullYear()} />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="LogReturn" stroke="#bc2618" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default LogReturnChart;
