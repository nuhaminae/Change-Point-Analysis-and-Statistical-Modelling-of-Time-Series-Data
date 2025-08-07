import React, { useEffect, useState } from 'react';
import axios from 'axios';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine
} from 'recharts';

const ChangePointChart = () => {
  const [data, setData] = useState([]);
  const [events, setEvents] = useState([]);

  const eventColors = {
    'Geopolitical': '#d9534f',
    'Economic Shock': '#5bc0de',
    'OPEC Decision': '#5cb85c',
    'Sanctions': '#f0ad4e',
    'Natural Disaster': '#9370DB'
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [changeRes, eventRes] = await Promise.all([
          axios.get('http://localhost:5000/change-points'),
          axios.get('http://localhost:5000/event-overlay')
        ]);

        const formattedChangePoints = changeRes.data.map(d => ({
          ...d,
          date: d.date // keep as string
        }));

        const parsedEvents = eventRes.data.map(event => ({
          ...event,
          date: event.Date // normalize to lowercase 'date'
        }));

        setData(formattedChangePoints);
        setEvents(parsedEvents);
      } catch (err) {
        console.error('Error fetching data:', err);
      }
    };

    fetchData();
  }, []);

  return (
    <div style={{ width: '100%', height: 500 }}>
      <h2>Brent Oil Price Change Points with Event Overlays</h2>
      <ResponsiveContainer>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="date" tick={{ fontSize: 12 }} />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="mean_before" stroke="#8884d8" name="Mean Before" />
          <Line type="monotone" dataKey="mean_after" stroke="#82ca9d" name="Mean After" />

          {/* Event overlays */}
          {events.map((event, i) => (
            <ReferenceLine
              key={`event-${i}`}
              x={event.date}
              stroke={eventColors[event["Event Type"]] || '#ffa500'}
              strokeDasharray="4 2"
              label={{
                value: event["Event Name"],
                position: i % 2 === 0 ? 'top' : 'insideTop',
                fill: eventColors[event["Event Type"]] || '#ffa500',
                fontSize: 11,
              }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ChangePointChart;
