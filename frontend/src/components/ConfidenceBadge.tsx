interface Props {
  confidence: number | null;
}

export function ConfidenceBadge({ confidence }: Props) {
  if (confidence === null) return <span className="badge badge-none">—</span>;

  let color: string;
  let label: string;
  if (confidence >= 0.7) {
    color = 'var(--color-green)';
    label = 'High';
  } else if (confidence >= 0.4) {
    color = 'var(--color-yellow)';
    label = 'Medium';
  } else {
    color = 'var(--color-gray)';
    label = 'Low';
  }

  return (
    <span className="badge" style={{ backgroundColor: color }} title={`Confidence: ${(confidence * 100).toFixed(0)}%`}>
      {label}
    </span>
  );
}
