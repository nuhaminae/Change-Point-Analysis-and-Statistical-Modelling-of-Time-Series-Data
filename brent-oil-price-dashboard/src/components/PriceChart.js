import React, { useEffect, useState } from 'react';
import axios from 'axios';
import DatePicker from 'react-datepicker';
import { Switch, FormControlLabel } from '@mui/material';
import 'react-datepicker/dist/react-datepicker.css';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ReferenceLine
} from 'recharts';

const PriceChart = () => {
  const [priceData, setPriceData] = useState([]);
  const [changePoints, setChangePoints] = useState([]);
  const [events, setEvents] = useState([]);
  const [startDate, setStartDate] = useState(new Date('1987-05-20'));
  const [endDate, setEndDate] = useState(new Date('2022-11-14'));
  const [showChangePoints, setShowChangePoints] = useState(true);
  const [showEvents, setShowEvents] = useState(true);

  const eventColors = {
    'Geopolitical': '#ff1206ff',
    'Economic Shock': '#00c3feff',
    'OPEC Decision': '#d400ffff',
    'Sanctions': '#3300ffff',
    'Natural Disaster': '#26ff00ff'
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [priceRes, changeRes, eventRes] = await Promise.all([
          axios.get('http://localhost:5000/price-data'),
          axios.get('http://localhost:5000/change-points'),
          axios.get('http://localhost:5000/event-overlay')
        ]);

        setPriceData(priceRes.data);
        setChangePoints(changeRes.data);
        setEvents(eventRes.data);
      } catch (err) {
        console.error('Error fetching data:', err);
      }
    };

    fetchData();
  }, []);

  const filteredData = priceData.filter(d => {
    const date = new Date(d.date);
    return date >= startDate && date <= endDate;
  });

  const filteredChangePoints = changePoints.filter(cp => {
    const date = new Date(cp.date);
    return date >= startDate && date <= endDate;
  });

  const filteredEvents = events.filter(ev => {
    const date = new Date(ev.Date);
    return date >= startDate && date <= endDate;
  });

  return (
    <div>
      <h2>Brent Oil Price Chart</h2>
      <div style={{ marginBottom: '20px' }}>
        <label>Start Date: </label>
        <DatePicker selected={startDate} onChange={date => setStartDate(date)} dateFormat="dd/MM/yyyy" />
        <label style={{ marginLeft: '20px' }}>End Date: </label>
        <DatePicker selected={endDate} onChange={date => setEndDate(date)} dateFormat="dd/MM/yyyy" />
        <FormControlLabel
          style={{ marginLeft: '40px' }}
          control={
            <Switch
              checked={showChangePoints}
              onChange={() => setShowChangePoints(!showChangePoints)}
              color="primary"
            />
          }
          label="Show Change Points"
        />
        <FormControlLabel
          style={{ marginLeft: '20px' }}
          control={
            <Switch
              checked={showEvents}
              onChange={() => setShowEvents(!showEvents)}
              color="secondary"
            />
          }
          label="Show Events"
        />
      </div>

      <LineChart width={1200} height={400} data={filteredData}>
        <CartesianGrid strokeDasharray="3 3" vertical={false} />
        <XAxis
          dataKey="date"
          minTickGap={20}
          tick={{ dy: 10 }}
          tickFormatter={(dateStr) => new Date(dateStr).getFullYear()}
          interval="preserveStartEnd"
        />
        <YAxis />
        <Tooltip />
        <Legend verticalAlign="top" align="right" wrapperStyle={{ paddingBottom: 20 }} />
        <Line type="monotone" dataKey="price" stroke="#000000ff" dot={false} name="Brent Price" />

        {showChangePoints && filteredChangePoints.map((cp, i) => (
          <ReferenceLine
            key={`cp-${i}`}
            x={cp.date}
            stroke="#10507788"
            strokeDasharray="3 3"
          />
        ))}

        {showEvents && filteredEvents.map((event, i) => {
          const labelPositions = ['top', 'insideTop', 'middle', 'bottom'];
          const position = labelPositions[i % labelPositions.length];

          return (
            <ReferenceLine
              key={`event-${i}`}
              x={event.Date}
              stroke={eventColors[event["Event Type"]] || '#ffa500'}
              strokeDasharray="4 2"
              label={{
                value: event["Event Name"],
                position,
                fill: eventColors[event["Event Type"]] || '#ffa500',
                fontSize: 11,
              }}
            />
          );
        })}

      </LineChart>
    </div>
  );
};

export default PriceChart;
