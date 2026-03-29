interface Props {
  value: number | null;
  changePct: number | null;
}

export function ValueDisplay({ value, changePct }: Props) {
  if (value === null) return <span className="value-none">No value</span>;

  const formatted = value.toLocaleString('en-US', {
    style: 'currency',
    currency: 'USD',
  });

  return (
    <span className="value-display">
      <span className="value-amount">{formatted}</span>
      {changePct !== null && (
        <span className={`value-change ${changePct >= 0 ? 'up' : 'down'}`}>
          {changePct >= 0 ? '▲' : '▼'} {Math.abs(changePct).toFixed(1)}%
        </span>
      )}
    </span>
  );
}
