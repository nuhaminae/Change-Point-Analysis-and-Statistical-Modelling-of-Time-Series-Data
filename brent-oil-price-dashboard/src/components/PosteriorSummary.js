// PosteriorSummary.js

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { DataGrid } from '@mui/x-data-grid';
import { Box, Typography, Tooltip } from '@mui/material';
import '../App.css';

const PosteriorSummary = () => {
  const [rows, setRows] = useState([]);

  useEffect(() => {
    axios.get('http://localhost:5000/posterior-summary')
      .then(res => {
        const formatted = res.data.map((row, index) => ({
          id: index,
          parameter: row.parameter,
          mean: row.mean,
          sd: row.sd,
          hdi_3: row['hdi_3%'],
          hdi_97: row['hdi_97%'],
          ess_bulk: row.ess_bulk,
          ess_tail: row.ess_tail,
          r_hat: row.r_hat
        }));
        setRows(formatted);
      })
      .catch(err => console.error('Error fetching posterior summary:', err));
  }, []);

  const columns = [
    {
      field: 'parameter',
      headerName: 'Parameter',
      flex: 1,
      renderHeader: () => (
        <Tooltip title="Model parameter (e.g., mean, volatility)">
          <span>Parameter</span>
        </Tooltip>
      )
    },
    {
      field: 'mean',
      headerName: 'Mean',
      type: 'number',
      flex: 1,
      renderHeader: () => (
        <Tooltip title="Posterior mean estimate">
          <span>Mean</span>
        </Tooltip>
      )
    },
    {
      field: 'sd',
      headerName: 'SD',
      type: 'number',
      flex: 1,
      renderHeader: () => (
        <Tooltip title="Posterior standard deviation">
          <span>SD</span>
        </Tooltip>
      )
    },
    {
      field: 'hdi_3',
      headerName: 'HDI 3%',
      type: 'number',
      flex: 1,
      renderHeader: () => (
        <Tooltip title="Lower bound of 94% Highest Density Interval">
          <span>HDI 3%</span>
        </Tooltip>
      )
    },
    {
      field: 'hdi_97',
      headerName: 'HDI 97%',
      type: 'number',
      flex: 1,
      renderHeader: () => (
        <Tooltip title="Upper bound of 94% Highest Density Interval">
          <span>HDI 97%</span>
        </Tooltip>
      )
    },
    {
      field: 'ess_bulk',
      headerName: 'ESS Bulk',
      type: 'number',
      flex: 1,
      renderHeader: () => (
        <Tooltip title="Effective sample size for bulk of posterior. Low values (<400) may indicate poor mixing.">
          <span>ESS Bulk</span>
        </Tooltip>
      )
    },
    {
      field: 'ess_tail',
      headerName: 'ESS Tail',
      type: 'number',
      flex: 1,
      renderHeader: () => (
        <Tooltip title="Effective sample size for tail of posterior distribution.">
          <span>ESS Tail</span>
        </Tooltip>
      )
    },
    {
      field: 'r_hat',
      headerName: 'R-hat',
      type: 'number',
      flex: 1,
      renderHeader: () => (
        <Tooltip title="Convergence diagnostic. Values >1.01 suggest chains haven't mixed well.">
          <span>R-hat</span>
        </Tooltip>
      )
    }
  ];

  return (
    <Box sx={{ height: 500, width: '100%', mt: 4 }}>
      <Typography variant="h5" gutterBottom>
        Posterior Summary
      </Typography>
      <DataGrid
        rows={rows}
        columns={columns}
        pageSize={10}
        rowsPerPageOptions={[5, 10, 20]}
        disableRowSelectionOnClick
        getRowClassName={(params) =>
          params.row.r_hat > 1.01 ? 'rhat-warning' :
          params.row.ess_bulk < 400 ? 'ess-warning' : ''
        }
      />
    </Box>
  );
};

export default PosteriorSummary;
