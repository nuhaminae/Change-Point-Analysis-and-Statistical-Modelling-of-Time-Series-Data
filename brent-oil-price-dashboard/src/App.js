// App.js

import React, { useState } from 'react';
import './App.css';
import PriceChart from './components/PriceChart';
import PosteriorSummary from './components/PosteriorSummary';
import { Box, Typography, Select, MenuItem, FormControl, InputLabel } from '@mui/material';

function App() {
  const [view, setView] = useState('price');

  return (
    <div className="App">
      <header className="App-header">
        <Typography variant="h4" gutterBottom>
          Brent Oil Price Dashboard
        </Typography>
        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel id="view-select-label">Select View</InputLabel>
          <Select
            labelId="view-select-label"
            value={view}
            label="Select View"
            onChange={(e) => setView(e.target.value)}
          >
            <MenuItem value="price">Price Chart</MenuItem>
            <MenuItem value="posterior">Posterior Summary</MenuItem>
          </Select>
        </FormControl>
      </header>

      <main>
        <Box sx={{ mt: 4 }}>
          {view === 'price' && <PriceChart />}
          {view === 'posterior' && <PosteriorSummary />}
        </Box>
      </main>
    </div>
  );
}

export default App;

