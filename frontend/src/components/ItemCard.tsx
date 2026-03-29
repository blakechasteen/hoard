import type { Item } from '../types';
import { ConfidenceBadge } from './ConfidenceBadge';
import { ValueDisplay } from './ValueDisplay';

interface Props {
  item: Item;
  onClick: (item: Item) => void;
}

export function ItemCard({ item, onClick }: Props) {
  return (
    <div className="item-card" onClick={() => onClick(item)}>
      <div className="item-card-header">
        <span className="item-category">{item.category}</span>
        {item.grade && <span className="item-grade">{item.grade}</span>}
        <ConfidenceBadge confidence={item.current_confidence} />
      </div>
      <h3 className="item-name">{item.name}</h3>
      {item.tags.length > 0 && (
        <div className="item-tags">
          {item.tags.map((tag) => (
            <span key={tag} className="tag">{tag}</span>
          ))}
        </div>
      )}
      <div className="item-card-footer">
        <div className="item-cost">
          {item.purchase_price
            ? `Cost: $${item.purchase_price.toLocaleString()}`
            : 'No cost recorded'}
        </div>
        <ValueDisplay value={item.current_value} changePct={item.value_change_pct} />
      </div>
    </div>
  );
}
