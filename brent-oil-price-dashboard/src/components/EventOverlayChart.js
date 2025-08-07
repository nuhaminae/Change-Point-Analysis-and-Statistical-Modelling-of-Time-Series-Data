import React, { useEffect, useState } from 'react';
import axios from 'axios';

const EventOverlayChart = () => {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    axios.get('http://localhost:5000/event-overlay')
      .then(res => setEvents(res.data))
      .catch(err => console.error('Error fetching event data:', err));
  }, []);

  return (
    <div style={{ padding: '20px' }}>
      <h2>Historical Events Overlay</h2>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr style={{ backgroundColor: '#f0f0f0' }}>
            <th style={{ padding: '10px', border: '1px solid #ccc' }}>Date</th>
            <th style={{ padding: '10px', border: '1px solid #ccc' }}>Event</th>
          </tr>
        </thead>
        <tbody>
          {events.map((event, i) => (
            <tr key={i}>
              <td style={{ padding: '10px', border: '1px solid #ccc' }}>{event.Date}</td>
              <td style={{ padding: '10px', border: '1px solid #ccc' }}>{event.description || event.name}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default EventOverlayChart;
