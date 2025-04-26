import { Card, CardContent, Typography, Box } from '@mui/material';
import { format } from 'date-fns';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';

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

interface IndicatorCardProps {
  indicator: Indicator;
}

const IndicatorCard = ({ indicator }: IndicatorCardProps) => {
  const currentValue = parseFloat(indicator.value);
  const previousValue = indicator.previous_value ? parseFloat(indicator.previous_value) : null;
  const isIncreasing = previousValue !== null && currentValue > previousValue;
  const changePercent = previousValue ? ((currentValue - previousValue) / previousValue * 100).toFixed(2) : null;

  return (
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardContent>
        <Typography variant="h6" component="div" gutterBottom noWrap>
          {indicator.name}
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <Typography variant="h4" component="div">
            {parseFloat(indicator.value).toLocaleString()} {indicator.unit}
          </Typography>
        </Box>
        {previousValue && (
          <Box sx={{ display: 'flex', alignItems: 'center', color: isIncreasing ? 'success.main' : 'error.main' }}>
            {isIncreasing ? <TrendingUpIcon /> : <TrendingDownIcon />}
            <Typography variant="body2" component="span" sx={{ ml: 1 }}>
              {changePercent}% from previous
            </Typography>
          </Box>
        )}
        <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
          Last updated: {format(new Date(indicator.last_update), 'MMM d, yyyy')}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Category: {indicator.category}
        </Typography>
      </CardContent>
    </Card>
  );
};

export default IndicatorCard; 