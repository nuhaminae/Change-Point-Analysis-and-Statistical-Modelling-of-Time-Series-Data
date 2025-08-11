/*LogReturnChart.js*/

import React, { useEffect, useState } from "react";
import {LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, ReferenceLine, Label} from "recharts";

function LogReturnChart() {
  const [priceData, setPriceData] = useState([]);
  const [events, setEvents] = useState([]);
  const eventColors = {
    'Economic Shock': '#4c00ffff',
    'Geopolitical': '#ff0800ff',
    'Natural Disaster': '#f99900ff',
    'OPEC Decision': '#00ff00ff',
    'Sanctions': '#fff200ff',
  };
  const getLabelPosition = (index, type) => {
    const positions = ["top", "middle", "bottom"];
    return positions[index % positions.length];
  };
  
  useEffect(() => {
    fetch("http://localhost:5000/price-data")
      .then((res) => res.json())
      .then((json) => setPriceData(json));

    fetch("http://localhost:5000/matched-events")
      .then((res) => res.json())
      .then((json) => setEvents(json));
  }, []);

  
  return (
    <div>
      <h3>Price Change with Event Overlays</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={priceData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="Date"
            tickFormatter={(dateStr) => dateStr.split("/")[2]} // Extract year from "dd/mm/yyyy"
            interval="preserveStartEnd"
            textAnchor="end"
            />
          <YAxis
            label={{ value: "Log Returns", angle: -90, position: "outsideLeft", dx:-20, }}
            />
          <Tooltip />
          <Line type="monotone" dataKey="LogReturn" stroke="#000000c8" dot={false} />

          {/* Overlay matched events */}
          {events.map((event, index) => (
            <ReferenceLine
              key={index}
              x={event.Date}
              stroke={eventColors[event["Event Type"]]}
              strokeDasharray="3 3"
              
            >
              <Label
                value={event["Event Name"]}
                position={getLabelPosition(index, event["Event Type"])}
                angle={45}
                offset={-95}
                style={{ fontSize: "12px", fill: eventColors[event["Event Type"]]}}
              />
            </ReferenceLine>
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default LogReturnChart;
