/* EventTypeDonutChart */

import React, { useEffect, useState } from "react";
import {
  PieChart,
  Pie,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

function EventTypeDonutChart() {
  const [data, setData] = useState([]);

  useEffect(() => {
    fetch("http://localhost:5000/event-overlay")
      .then((res) => res.json())
      .then((json) => setData(json));
  }, []);

  const COLORS = ["#0064d6ff", "#D0021B", "#e08a00ff", "#6bcf00ff", "#7000d2ff", "#00cea2ff"];

  return (
    <div>
      <h3>Event Type Distribution (%)</h3>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={data}
            dataKey="percentage"
            nameKey="type"
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={100}
            label={({ type, percentage }) => `${type}: ${percentage}%`}
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip formatter={(value) => `${value}%`} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}

export default EventTypeDonutChart;
