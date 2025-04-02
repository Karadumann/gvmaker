import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Container,
  Paper,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  CircularProgress,
  Snackbar,
  Alert,
} from '@mui/material';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import axios from 'axios';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
  },
});

function App() {
  const [recording, setRecording] = useState(false);
  const [format, setFormat] = useState('video');
  const [fps, setFps] = useState(30);
  const [quality, setQuality] = useState('high');
  const [region, setRegion] = useState({ x: 0, y: 0, width: 800, height: 600 });
  const [shareUrl, setShareUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });

  const handleStartRecording = async () => {
    try {
      setLoading(true);
      await axios.post('http://localhost:8000/start-recording', {
        region,
        format,
        fps,
        quality,
      });
      setRecording(true);
      setSnackbar({
        open: true,
        message: 'Recording started',
        severity: 'success',
      });
    } catch (error) {
      setSnackbar({
        open: true,
        message: 'Error starting recording',
        severity: 'error',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleStopRecording = async () => {
    try {
      setLoading(true);
      const response = await axios.post('http://localhost:8000/stop-recording');
      setRecording(false);
      setShareUrl(response.data.share_url);
      setSnackbar({
        open: true,
        message: 'Recording stopped',
        severity: 'success',
      });
    } catch (error) {
      setSnackbar({
        open: true,
        message: 'Error stopping recording',
        severity: 'error',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Container maxWidth="md">
        <Box sx={{ my: 4 }}>
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h4" component="h1" gutterBottom>
              Screen Recorder
            </Typography>

            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Format</InputLabel>
              <Select
                value={format}
                label="Format"
                onChange={(e) => setFormat(e.target.value)}
              >
                <MenuItem value="video">Video</MenuItem>
                <MenuItem value="gif">GIF</MenuItem>
              </Select>
            </FormControl>

            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>FPS</InputLabel>
              <Select
                value={fps}
                label="FPS"
                onChange={(e) => setFps(e.target.value)}
              >
                <MenuItem value={30}>30 FPS</MenuItem>
                <MenuItem value={60}>60 FPS</MenuItem>
                <MenuItem value={120}>120 FPS</MenuItem>
              </Select>
            </FormControl>

            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Quality</InputLabel>
              <Select
                value={quality}
                label="Quality"
                onChange={(e) => setQuality(e.target.value)}
              >
                <MenuItem value="high">High</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="low">Low</MenuItem>
              </Select>
            </FormControl>

            <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
              <TextField
                label="X Position"
                type="number"
                value={region.x}
                onChange={(e) => setRegion({ ...region, x: parseInt(e.target.value) })}
                fullWidth
              />
              <TextField
                label="Y Position"
                type="number"
                value={region.y}
                onChange={(e) => setRegion({ ...region, y: parseInt(e.target.value) })}
                fullWidth
              />
            </Box>

            <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
              <TextField
                label="Width"
                type="number"
                value={region.width}
                onChange={(e) => setRegion({ ...region, width: parseInt(e.target.value) })}
                fullWidth
              />
              <TextField
                label="Height"
                type="number"
                value={region.height}
                onChange={(e) => setRegion({ ...region, height: parseInt(e.target.value) })}
                fullWidth
              />
            </Box>

            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
              <Button
                variant="contained"
                color="primary"
                onClick={handleStartRecording}
                disabled={recording || loading}
                startIcon={loading && <CircularProgress size={20} />}
              >
                Start Recording
              </Button>
              <Button
                variant="contained"
                color="secondary"
                onClick={handleStopRecording}
                disabled={!recording || loading}
                startIcon={loading && <CircularProgress size={20} />}
              >
                Stop Recording
              </Button>
            </Box>

            {shareUrl && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="h6">Share URL:</Typography>
                <TextField
                  fullWidth
                  value={shareUrl}
                  InputProps={{
                    readOnly: true,
                  }}
                />
              </Box>
            )}
          </Paper>
        </Box>
      </Container>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
      >
        <Alert
          onClose={handleCloseSnackbar}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </ThemeProvider>
  );
}

export default App; 