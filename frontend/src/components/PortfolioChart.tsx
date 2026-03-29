import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import type { PortfolioSnapshot } from '../types';

interface Props {
  history: PortfolioSnapshot[];
}

export function PortfolioChart({ history }: Props) {
  if (history.length === 0) {
    return <div className="chart-empty">No valuation history yet. Add appraisals to see your portfolio over time.</div>;
  }

  const data = history.map((s) => ({
    date: new Date(s.timestamp).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    value: s.total_value,
    confidence: s.confidence,
  }));

  return (
    <div className="chart-container">
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="valueGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#333" />
          <XAxis dataKey="date" stroke="#888" fontSize={12} />
          <YAxis
            stroke="#888"
            fontSize={12}
            tickFormatter={(v: number) => `$${v.toLocaleString()}`}
          />
          <Tooltip
            contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #333' }}
            formatter={(value) => [`$${Number(value).toLocaleString()}`, 'Value']}
          />
          <Area
            type="monotone"
            dataKey="value"
            stroke="#6366f1"
            strokeWidth={2}
            fill="url(#valueGradient)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
