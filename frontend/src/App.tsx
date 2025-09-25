import { useState, useEffect } from 'react'
import axios from 'axios';
import{
  Container, Typography, Box, FormControl, InputLabel,
  MenuItem, Select, Button, CircularProgress, Paper
} from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'; 
import './App.css'

const API_URL = 'http://localhost:8000/api';

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
  detail:string;
}


interface LiveRate {
  pair: string;
  rate: number;
  timestamp: string;
  source: string;
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

  // Fetch live rates
  const fetchLiveRates = async () => {
    setLoadingRates(true);
    try {
      const response = await axios.get<{ live_rates: {[key: string]: LiveRate} }>(`${API_URL}/live-rates`);
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
        const response = await axios.get<{ pairs: string[] }>(`${API_URL}/pairs`);
        setPairs(response.data.pairs);
        if (response.data.pairs.length > 0){
          setSelectedPair(response.data.pairs[0])
        }
        // Fetch live rates after getting pairs
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
      const response = await axios.post(`${API_URL}/predict`, {
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
      let errorMsg = 'An unknown error occured.';
      if (axios.isAxiosError<ApiError>(err) && err.response) {
        errorMsg = err.response.data.detail
      }
      setError('Failed to get prediction, Please try again later.')
    } finally{
      setLoading(false);
    }
  };

  return(
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          Forex Forecast
        </Typography>

        {/* Live Rates Display */}
        <Paper sx={{ p: 2, mb: 3, bgcolor: '#f5f5f5' }}>
          <Typography variant="h6" gutterBottom>
            Live Exchange Rates {loadingRates && <CircularProgress size={16} />}
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
            {Object.entries(liveRates).map(([pair, rateData]) => (
              <Box key={pair} sx={{ 
                border: '1px solid #ddd', 
                borderRadius: 1, 
                p: 1, 
                minWidth: 120,
                bgcolor: selectedPair === pair ? '#e3f2fd' : 'white'
              }}>
                <Typography variant="subtitle2" fontWeight="bold">
                  {pair}
                </Typography>
                <Typography variant="body2">
                  {rateData.rate.toFixed(5)}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {new Date(rateData.timestamp).toLocaleTimeString()}
                </Typography>
              </Box>
            ))}
          </Box>
          <Button 
            size="small" 
            onClick={fetchLiveRates} 
            sx={{ mt: 1 }}
            disabled={loadingRates}
          >
            Refresh Rates
          </Button>
        </Paper>
        
        {error && (
          <Paper sx={{ p: 2, mb: 2, bgcolor: '#ffebee' }}>
            <Typography color="error">{error}</Typography>
          </Paper>
        )}
        
        <Box sx={{ mb: 4, display: 'flex', gap: 2, alignItems: 'flex-end' }}>
          <FormControl sx={{ minWidth: 200 }}>
            <InputLabel>Currency Pair</InputLabel>
            <Select
              value={selectedPair}
              onChange={(e) => setSelectedPair(e.target.value)}
              label="Currency Pair"
            >
              {pairs.map((pair) => (
                <MenuItem key={pair} value={pair}>
                  {pair}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          
          <FormControl sx={{ width: 100 }}>
            <InputLabel>Days</InputLabel>
            <Select
              value={days}
              onChange={(e) => setDays(e.target.value)}
              label="Days"
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
          >
            {loading ? <CircularProgress size={24} /> : 'Predict'}
          </Button>
        </Box>
        
        {forecast && (
          <Box sx={{ height: 500 }}>
            <Typography variant="h5" gutterBottom>
              {forecast.pair} - {days} Day Forecast
            </Typography>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart
                data={forecast.chartData}
                margin={{ top: 20, right: 30, left: 20, bottom: 50 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="date" 
                  angle={-45}
                  textAnchor="end"
                  height={70}
                />
                <YAxis />
                <Tooltip />
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
        )}
      </Box>
    </Container>
  );
}
export default App;
