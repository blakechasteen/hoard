import { useState } from 'react';
import { AddItemModal } from '../components/AddItemModal';
import { ItemCard } from '../components/ItemCard';
import { PortfolioChart } from '../components/PortfolioChart';
import { ValueDisplay } from '../components/ValueDisplay';
import { useItems } from '../hooks/useItems';
import { usePortfolio } from '../hooks/usePortfolio';
import type { Category, Item } from '../types';
import { CATEGORIES } from '../types';

interface Props {
  onLogout: () => void;
  displayName: string;
}

export function DashboardPage({ onLogout, displayName }: Props) {
  const [categoryFilter, setCategoryFilter] = useState<Category | ''>('');
  const { items, loading: itemsLoading, refresh } = useItems(categoryFilter || undefined);
  const { summary, loading: portfolioLoading } = usePortfolio();
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedItem, setSelectedItem] = useState<Item | null>(null);

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-left">
          <h1>Hoard</h1>
          <span className="header-user">{displayName}</span>
        </div>
        <div className="header-actions">
          <button className="btn-primary" onClick={() => setShowAddModal(true)}>+ Add Item</button>
          <button className="btn-secondary" onClick={onLogout}>Log out</button>
        </div>
      </header>

      {/* Portfolio Summary */}
      <section className="portfolio-summary">
        {portfolioLoading ? (
          <div className="loading">Loading portfolio...</div>
        ) : summary ? (
          <>
            <div className="summary-stats">
              <div className="stat">
                <span className="stat-label">Total Value</span>
                <ValueDisplay value={summary.total_value} changePct={summary.gain_pct} />
              </div>
              <div className="stat">
                <span className="stat-label">Total Cost</span>
                <span className="stat-value">
                  {summary.total_cost
                    ? `$${summary.total_cost.toLocaleString()}`
                    : '—'}
                </span>
              </div>
              <div className="stat">
                <span className="stat-label">Gain/Loss</span>
                <span className={`stat-value ${(summary.total_gain ?? 0) >= 0 ? 'up' : 'down'}`}>
                  {summary.total_gain !== null
                    ? `$${summary.total_gain.toLocaleString()}`
                    : '—'}
                </span>
              </div>
              <div className="stat">
                <span className="stat-label">Items</span>
                <span className="stat-value">{summary.item_count}</span>
              </div>
              <div className="stat">
                <span className="stat-label">High Confidence</span>
                <span className="stat-value">
                  {summary.high_confidence_count}/{summary.item_count}
                </span>
              </div>
            </div>
            <PortfolioChart history={summary.history} />
          </>
        ) : (
          <div className="empty-state">Add items and appraisals to see your portfolio.</div>
        )}
      </section>

      {/* Items Grid */}
      <section className="items-section">
        <div className="items-header">
          <h2>Your Hoard</h2>
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value as Category | '')}
            className="category-filter"
          >
            <option value="">All Categories</option>
            {CATEGORIES.map((c) => (
              <option key={c.value} value={c.value}>{c.label}</option>
            ))}
          </select>
        </div>

        {itemsLoading ? (
          <div className="loading">Loading items...</div>
        ) : items.length === 0 ? (
          <div className="empty-state">
            No items yet. Click &quot;+ Add Item&quot; to start building your hoard.
          </div>
        ) : (
          <div className="items-grid">
            {items.map((item) => (
              <ItemCard key={item.id} item={item} onClick={setSelectedItem} />
            ))}
          </div>
        )}
      </section>

      {showAddModal && (
        <AddItemModal onClose={() => setShowAddModal(false)} onAdded={refresh} />
      )}

      {selectedItem && (
        <div className="modal-backdrop" onClick={() => setSelectedItem(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>{selectedItem.name}</h2>
            <div className="item-detail">
              <p><strong>Category:</strong> {selectedItem.category}</p>
              {selectedItem.grade && <p><strong>Grade:</strong> {selectedItem.grade}</p>}
              {selectedItem.description && <p><strong>Description:</strong> {selectedItem.description}</p>}
              {selectedItem.purchase_price && (
                <p><strong>Purchase Price:</strong> ${selectedItem.purchase_price.toLocaleString()}</p>
              )}
              {selectedItem.purchase_date && (
                <p><strong>Purchase Date:</strong> {selectedItem.purchase_date}</p>
              )}
              <p><strong>Current Value:</strong>{' '}
                <ValueDisplay value={selectedItem.current_value} changePct={selectedItem.value_change_pct} />
              </p>
              {selectedItem.catalog_ref && (
                <p><strong>Catalog Ref:</strong> {selectedItem.catalog_ref}</p>
              )}
              {selectedItem.tags.length > 0 && (
                <p><strong>Tags:</strong> {selectedItem.tags.join(', ')}</p>
              )}
            </div>
            <div className="modal-actions">
              <button className="btn-secondary" onClick={() => setSelectedItem(null)}>Close</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
