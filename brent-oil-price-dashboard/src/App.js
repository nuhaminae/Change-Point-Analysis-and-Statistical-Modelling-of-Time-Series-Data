// App.js

import React, { useState } from 'react';
import './App.css';
import PriceChart from './components/PriceChart';
import RollingMeanChart from './components/RollingMeanChart';
import RollingStdChart from './components/RollingStdChart';
import LogReturnChart from './components/LogReturnChart';
import PosteriorSummary from './components/PosteriorSummary';
import ChangePointChart from './components/ChangePointChart';
import { Box, Typography, Select, MenuItem, FormControl, InputLabel } from '@mui/material';

function App() {
  const [view, setView] = useState('price');

  return (
    <div className="App">
      <header className="App-header">
        <Typography variant="h4" gutterBottom>
          Brent Oil Price Dashboard
        </Typography>
        <FormControl sx={{ minWidth: 250 }}>
          <InputLabel id="view-select-label">Select Chart View</InputLabel>
          <Select
            labelId="view-select-label"
            value={view}
            label="Select Chart View"
            onChange={(e) => setView(e.target.value)}
          >
            <MenuItem value="price">Price Chart</MenuItem>
            <MenuItem value="rollingMean">Rolling Mean</MenuItem>
            <MenuItem value="rollingStd">Rolling Std Dev</MenuItem>
            <MenuItem value="logReturn">Log Return</MenuItem>
            <MenuItem value="changePoints">Change Point Chart</MenuItem>
            <MenuItem value="posterior">Posterior Summary</MenuItem>
          </Select>
        </FormControl>
      </header>

      <main>
        <Box sx={{ mt: 4 }}>
          {view === 'price' && <PriceChart />}
          {view === 'rollingMean' && <RollingMeanChart />}
          {view === 'rollingStd' && <RollingStdChart />}
          {view === 'logReturn' && <LogReturnChart />}
          {view === 'changePoints' && <ChangePointChart />}
          {view === 'posterior' && <PosteriorSummary />}
        </Box>
      </main>
    </div>
  );
} export default App;
