import { useState, useEffect } from 'react'
import { isAxiosError } from 'axios';
import {
  Container, Typography, Box, FormControl, InputLabel,
  MenuItem, Select, Button, CircularProgress, Paper, Drawer,
  IconButton, Divider, Slider, Switch, FormControlLabel, Card, CardContent
} from '@mui/material';
import type { SelectChangeEvent } from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { apiClient } from './config/api';
import './App.css'

interface ChartDataItem{
  date: string;
  forecast: number;
  lowerBound: number;
  upperBound: number;
}

interface ForecastData{
  pair: string;
  chartData: ChartDataItem[];
}


interface ApiError{
  detail?:string;
}


interface LiveRate {
  pair: string;
  rate: number;
  timestamp: string;
  source: string;
}

interface ThemeSettings{
  backgroundColor: string;
  textColor: string;
  cardColor: string;
  containerMaxWidth: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  fontSize: number;
  darkMode: boolean;
}

function App() {
  const [pairs, setPairs] = useState<string[]>([]);
  const [selectedPair, setSelectedPair] = useState<string>('');
  const [days, setDays] = useState<number>(30);
  const [loading, setLoading] = useState<boolean>(false);
  const [forecast, setForecast] = useState<ForecastData | null>(null);
  const [error, setError] = useState<string>('');
  const [liveRates, setLiveRates] = useState<{[key: string]: LiveRate}>({});
  const [loadingRates, setLoadingRates] = useState<boolean>(false);
  const [settingsOpen, setSettingsOpen] = useState<boolean>(false);

  const [themeSettings, setThemeSettings] = useState<ThemeSettings>({
    backgroundColor: '#000000',
    textColor: '#ffffff',
    cardColor: '#1a1a1a',
    containerMaxWidth: 'lg',
    fontSize: 14,
    darkMode: true
   });

   const backgroundOptions = [
    {label: 'Black', value: '#000000'},
    {label: 'Dark Grey', value: '#212121'},
    {label: 'Navy Blue', value: '#1a237e'},
    {label: 'Dark Green', value: '#1b5e20'},
    {label: 'White', value: '#ffffff'},
    {label: 'Light Gray', value: '#f5f5f5'}
   ];

  const containerSizeOptions = [
    {label: 'Extra Small', value: 'xs' as const},
    {label: 'Small', value: 'sm' as const},
    {label: 'Medium', value: 'md' as const},
    {label: 'Large', value: 'lg' as const},
    {label: 'Extra Large', value: 'xl' as const}
  ];

  useEffect(() => {
    document.body.style.backgroundColor = themeSettings.backgroundColor;
    document.body.style.color = themeSettings.textColor;
    document.body.style.fontSize = `${themeSettings.fontSize}px`;
    document.body.style.margin = '0';
    document.body.style.minHeight = '100vh';
  }, [themeSettings]);

  const fetchLiveRates = async () => {
    setLoadingRates(true);
    try {
      const response = await apiClient.get<{ live_rates: {[key: string]: LiveRate} }>('/api/live-rates');
      setLiveRates(response.data.live_rates);
    } catch (err) {
      console.error('Error fetching live rates:', err);
    } finally {
      setLoadingRates(false);
    }
  };

  useEffect(() => {
    const fetchPairs = async () => {
      try{
        const response = await apiClient.get<{ pairs: string[] }>('/api/pairs');
        setPairs(response.data.pairs);
        if (response.data.pairs.length > 0){
          setSelectedPair(response.data.pairs[0])
        }
        await fetchLiveRates();
      } catch (err){
        console.error('Error fetching currency pairs:', err);
        setError('Failed to load currency pairs. Is the server running ?')
      }
    };

    fetchPairs();
  }, []);

  const handlePredict = async () => {
    if (!selectedPair) return;

    setLoading(true);
    setError('');
    setForecast(null);

    try {
      const response = await apiClient.post('/api/predict', {
        pair: selectedPair,
        days: days
      });

      console.log("API Response Data:", response.data)

      const chartData: ChartDataItem[]  = response.data.dates.map((date: string, index: number) => ({
        date,
        forecast: response.data.forecast[index],
        lowerBound: response.data.lower_bound[index],
        upperBound: response.data.upper_bound[index]
      }));
      
      console.log("Formatted Chart Data:", chartData)

      setForecast({
        pair: response.data.pair,
        chartData
      });

    } catch (err){
      if (isAxiosError<ApiError>(err) && err.response) {
        setError(err.response.data?.detail || 'Failed to get prediction. Please try again later.');
      } else {
        setError('Failed to get prediction. Please try again later.');
      }
    } finally{
      setLoading(false);
    }
  };

  const handleThemeChange = <K extends keyof ThemeSettings>(key: K, value: ThemeSettings[K]) => {
    setThemeSettings(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const toggleDarkMode = () => {
    if (themeSettings.darkMode) {
        handleThemeChange('backgroundColor', '#ffffff');
        handleThemeChange('textColor', '#000000');
        handleThemeChange('cardColor', '#f5f5f5');
        handleThemeChange('darkMode', false);
    }
    else {
        handleThemeChange('backgroundColor', '#000000');
        handleThemeChange('textColor', '#ffffff');
        handleThemeChange('cardColor', '#1a1a1a');
        handleThemeChange('darkMode', true);  
    }
  };
  return(
    <div style={{ 
      backgroundColor: themeSettings.backgroundColor, 
      minHeight: '100vh',
      color: themeSettings.textColor,
      transition: 'all 0.3s ease'
    }}>
      <Container maxWidth={themeSettings.containerMaxWidth}>
        <Box sx={{ py: 4 }}>
          {/* Header with Settings Button */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h3" component="h1" sx={{ color: themeSettings.textColor }}>
              Forex Forecast
            </Typography>
            <IconButton 
              onClick={() => setSettingsOpen(true)}
              sx={{ color: themeSettings.textColor }}
              aria-label="Open settings"
            >
              <span role="img" aria-hidden="true">⚙️</span>
            </IconButton>
          </Box>

          {/* Settings Drawer */}
          <Drawer
            anchor="right"
            open={settingsOpen}
            onClose={() => setSettingsOpen(false)}
            sx={{
              '& .MuiDrawer-paper': {
                width: 320,
                backgroundColor: themeSettings.cardColor,
                color: themeSettings.textColor
              }
            }}
          >
            <Box sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <span role="img" aria-hidden="true">🎨</span>
                Theme Settings
              </Typography>
              <Divider sx={{ my: 2, borderColor: themeSettings.textColor + '30' }} />
              
              {/* Dark Mode Toggle */}
              <FormControlLabel
                control={
                  <Switch
                    checked={themeSettings.darkMode}
                    onChange={toggleDarkMode}
                    color="primary"
                  />
                }
                label="Dark Mode"
                sx={{ mb: 3, color: themeSettings.textColor }}
              />

              {/* Background Color */}
              <Typography variant="subtitle2" gutterBottom sx={{ color: themeSettings.textColor }}>
                Background Color
              </Typography>
              <FormControl fullWidth sx={{ mb: 3 }}>
                <Select
                  value={themeSettings.backgroundColor}
                  onChange={(e) => handleThemeChange('backgroundColor', e.target.value)}
                  size="small"
                  sx={{ 
                    color: themeSettings.textColor,
                    '& .MuiOutlinedInput-notchedOutline': {
                      borderColor: themeSettings.textColor + '50'
                    }
                  }}
                >
                  {backgroundOptions.map((option) => (
                    <MenuItem key={option.value} value={option.value}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Box
                          sx={{
                            width: 20,
                            height: 20,
                            backgroundColor: option.value,
                            border: '1px solid #ccc',
                            borderRadius: 0.5
                          }}
                        />
                        {option.label}
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              {/* Container Size */}
              <Typography variant="subtitle2" gutterBottom sx={{ color: themeSettings.textColor }}>
                Container Size
              </Typography>
              <FormControl fullWidth sx={{ mb: 3 }}>
                <Select
                  value={themeSettings.containerMaxWidth}
                  onChange={(e: SelectChangeEvent<ThemeSettings['containerMaxWidth']>) =>
                    handleThemeChange('containerMaxWidth', e.target.value as ThemeSettings['containerMaxWidth'])
                  }
                  size="small"
                  sx={{ 
                    color: themeSettings.textColor,
                    '& .MuiOutlinedInput-notchedOutline': {
                      borderColor: themeSettings.textColor + '50'
                    }
                  }}
                >
                  {containerSizeOptions.map((option) => (
                    <MenuItem key={option.value} value={option.value}>
                      {option.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              {/* Font Size */}
              <Typography variant="subtitle2" gutterBottom sx={{ color: themeSettings.textColor }}>
                Font Size: {themeSettings.fontSize}px
              </Typography>
              <Slider
                value={themeSettings.fontSize}
                onChange={(_, value) =>
                  handleThemeChange('fontSize', (Array.isArray(value) ? value[0] : value) as ThemeSettings['fontSize'])
                }
                min={12}
                max={20}
                sx={{ mb: 3, color: 'primary.main' }}
              />

              <Button
                fullWidth
                variant="outlined"
                onClick={() => setSettingsOpen(false)}
                sx={{ 
                  color: themeSettings.textColor,
                  borderColor: themeSettings.textColor + '50'
                }}
              >
                Close Settings
              </Button>
            </Box>
          </Drawer>

          {/* Live Rates Display */}
          <Paper sx={{ 
            p: 2, 
            mb: 3, 
            backgroundColor: themeSettings.cardColor,
            color: themeSettings.textColor 
          }}>
            <Typography variant="h6" gutterBottom>
              Live Exchange Rates {loadingRates && <CircularProgress size={16} />}
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
              {Object.entries(liveRates).map(([pair, rateData]) => (
                <Box key={pair} sx={{ 
                  border: `1px solid ${themeSettings.textColor}30`, 
                  borderRadius: 1, 
                  p: 1, 
                  minWidth: 120,
                  backgroundColor: selectedPair === pair ? (themeSettings.darkMode ? '#1976d2' : '#e3f2fd') : 'transparent'
                }}>
                  <Typography variant="subtitle2" fontWeight="bold">
                    {pair}
                  </Typography>
                  <Typography variant="body2">
                    {rateData.rate.toFixed(5)}
                  </Typography>
                  <Typography variant="caption" sx={{ opacity: 0.7 }}>
                    {new Date(rateData.timestamp).toLocaleTimeString()}
                  </Typography>
                </Box>
              ))}
            </Box>
            <Button 
              size="small" 
              onClick={fetchLiveRates} 
              sx={{ 
                mt: 1,
                color: themeSettings.darkMode ? '#90caf920' : '#1976d2',
                borderColor: themeSettings.darkMode ? '#90caf9' : '#1976d2',
                '&:hover': {
                  backgroundColor: themeSettings.darkMode ? '#90caf920' : '#1976d220',
                  borderColor: themeSettings.darkMode ? '#64b5f6' : '#1565c0'
                },
                '&:disabled': {
                  color: themeSettings.darkMode ? '#666666' : '#bdbdbd',
                  borderColor: themeSettings.darkMode ? '#404040' : '#e0e0e0'
                } 
              }}
              disabled={loadingRates}
              variant="outlined"
            >
              Refresh Rates
            </Button>
          </Paper>
          
          {error && (
            <Paper sx={{ 
              p: 2, 
              mb: 2, 
              backgroundColor: '#d32f2f20',
              color: '#d32f2f',
              border: '1px solid #d32f2f50' 
            }}>
              <Typography>{error}</Typography>
            </Paper>
          )}
          
          <Box sx={{ mb: 4, display: 'flex', gap: 2, alignItems: 'flex-end', flexWrap: 'wrap' }}>
            <FormControl sx={{ minWidth: 200 }}>
              <InputLabel sx={{ 
                color: themeSettings.textColor + '80',
                '&.Mui-focused': {color: themeSettings.darkMode ? '#90caf9' : '#1976d2'}
              }}>Currency Pair</InputLabel>
              <Select
                value={selectedPair}
                onChange={(e) => setSelectedPair(e.target.value)}
                label="Currency Pair"
                IconComponent={() => null}
                sx={{ 
                  color: themeSettings.textColor,
                  backgroundColor: themeSettings.darkMode ? '#2a2a2a' : '#fafafa',
                  '& .MuiOutlinedInput-notchedOutline': {
                    borderColor: themeSettings.textColor + '50'
                  },
                  '&:hover .MuiOutlinedInput-notechedOutline': {
                    borderColor: themeSettings.textColor + '70'
                  },
                  '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                    borderColor: themeSettings.darkMode ? '#90caf9' : '#1976d2'
                  }
                }}
                MenuProps={{
                  PaperProps: {
                    sx: {
                      backgroundColor: themeSettings.cardColor,
                      color: themeSettings.textColor,
                      border: `1px solid ${themeSettings.textColor}30`,
                      '& .MuiMenuItem-root': {
                        '&:hover': {
                          backgroundColor: themeSettings.darkMode ? '#404040' : '#e0e0e0'
                        },
                        '&.Mui-selected': {
                          backgroundColor: themeSettings.darkMode ? '#1976d2' : '#bbdefb',
                          '&:hover': {
                            backgroundColor: themeSettings.darkMode ? '#1565c0' : '#90caf9'
                          }
                        }
                      }
                    }
                  }
                }}
              >
                {pairs.map((pair) => (
                  <MenuItem key={pair} value={pair}>
                    {pair}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <FormControl sx={{ width: 100 }}>
              <InputLabel sx={{ 
                color: themeSettings.textColor + '80',
                '&.Mui-focused': {color: themeSettings.darkMode ? '#90caf9' : '#1976d2'}
                }}>
                  Days
              </InputLabel>
              <Select
                value={days}
                onChange={(e: SelectChangeEvent<number>) => setDays(Number(e.target.value))}
                label="Days"
                IconComponent={() => null}
                sx={{ 
                  color: themeSettings.textColor,
                  backgroundColor: themeSettings.darkMode ? '#2a2a2a' : '#fafafa',
                  '& .MuiOutlinedInput-notchedOutline': {
                    borderColor: themeSettings.textColor + '50'
                  },
                  '&:hover .MuiOutlinedInput-notchedOutline': {
                    borderColor: themeSettings.textColor + '70'
                  },
                  '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                    borderColor: themeSettings.darkMode ? '#90caf9' : '#1976d2',
                    borderWidth: 2
                  }
                }}
                MenuProps={{
                  PaperProps: {
                    sx: {
                      backgrounColor: themeSettings.cardColor,
                      color: themeSettings.textColor,
                      border: `1px solid ${themeSettings.textColor}30`,
                      '& .MuiMenuItem-root': {
                        '&:hover': {
                          backgroundColor: themeSettings.darkMode ? '#404040' : '#e0e0e0'
                        },
                        '&.Mui-selected': {
                          backgroundColor: themeSettings.darkMode ? '#1976d2' : '#bbdefb',
                          '&:hover': {
                            backgroundColor: themeSettings.darkMode ? '#1565c0' : '#90caf9'
                          }
                        }
                      }
                    }
                  }
                }}
              >
                <MenuItem value={7}>7</MenuItem>
                <MenuItem value={14}>14</MenuItem>
                <MenuItem value={30}>30</MenuItem>
                <MenuItem value={60}>60</MenuItem>
                <MenuItem value={90}>90</MenuItem>
              </Select>
            </FormControl>
            
            <Button 
              variant="contained" 
              onClick={handlePredict}
              disabled={!selectedPair || loading}
              sx={{
                height: 40,
                px: 3,
                backgroundColor: themeSettings.darkMode ? '#1976d2' : '#1976d2',
                color: '#ffffff',
                fontWeight: 600,
                '&:hover': {
                  backgroundColor: themeSettings.darkMode ? '#1565c0' : '#1565c0'
                },
                '&:disabled': {
                  backgroundColor: themeSettings.darkMode ? '#404040' : '#bdbdbd',
                  color: themeSettings.darkMode ? '#666666' : '#ffffff'  
                }
              }}
            >
              {loading ? <CircularProgress size={24} /> : 'Predict'}
            </Button>
          </Box>
          
          {forecast && (
            <Card sx={{ 
              backgroundColor: themeSettings.cardColor,
              color: themeSettings.textColor 
            }}>
              <CardContent>
                <Typography variant="h5" gutterBottom>
                  {forecast.pair} - {days} Day Forecast
                </Typography>
                <Box sx={{ height: 500 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart
                      data={forecast.chartData}
                      margin={{ top: 20, right: 30, left: 20, bottom: 50 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke={themeSettings.textColor + '20'} />
                      <XAxis 
                        dataKey="date" 
                        angle={-45}
                        textAnchor="end"
                        height={70}
                        tick={{ fill: themeSettings.textColor }}
                      />
                      <YAxis tick={{ fill: themeSettings.textColor }} />
                      <Tooltip 
                        contentStyle={{
                          backgroundColor: themeSettings.cardColor,
                          color: themeSettings.textColor,
                          border: `1px solid ${themeSettings.textColor}30`
                        }}
                      />
                      <Legend />
                      <Line 
                        type="monotone" 
                        dataKey="forecast" 
                        stroke="#8884d8" 
                        name="Forecast" 
                        strokeWidth={2}
                      />
                      <Line 
                        type="monotone" 
                        dataKey="upperBound" 
                        stroke="#82ca9d" 
                        name="Upper Bound" 
                        strokeDasharray="5 5"
                      />
                      <Line 
                        type="monotone" 
                        dataKey="lowerBound" 
                        stroke="#ff8042" 
                        name="Lower Bound" 
                        strokeDasharray="5 5"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </Box>
              </CardContent>
            </Card>
          )}
        </Box>
      </Container>
    </div>
  );
}
export default App;
