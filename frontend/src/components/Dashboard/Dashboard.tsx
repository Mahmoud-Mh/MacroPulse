import { Container, Box, Typography } from '@mui/material';
import IndicatorCard from '../IndicatorCard/IndicatorCard';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

interface Indicator {
  id: number;
  name: string;
  value: string;
  previous_value: string;
  unit: string;
  country: string;
  category: string;
  last_update: string;
}

const Dashboard = () => {
  const { data: indicators, isLoading, error } = useQuery<Indicator[]>({
    queryKey: ['indicators'],
    queryFn: async () => {
      const response = await axios.get('http://localhost:8000/api/indicators/');
      return response.data.results;
    },
  });

  if (isLoading) {
    return <Typography>Loading...</Typography>;
  }

  if (error) {
    return <Typography color="error">Error loading indicators</Typography>;
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Economic Indicators Dashboard
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3 }}>
          {indicators?.map((indicator) => (
            <Box key={indicator.id} sx={{ width: { xs: '100%', sm: '45%', md: '30%' } }}>
              <IndicatorCard indicator={indicator} />
            </Box>
          ))}
        </Box>
      </Box>
    </Container>
  );
};

export default Dashboard; 