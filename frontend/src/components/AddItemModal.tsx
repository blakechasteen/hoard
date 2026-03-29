import { useState } from 'react';
import { createItem } from '../api/endpoints';
import { CATEGORIES, type Category } from '../types';

interface Props {
  onClose: () => void;
  onAdded: () => void;
}

export function AddItemModal({ onClose, onAdded }: Props) {
  const [name, setName] = useState('');
  const [category, setCategory] = useState<Category>('pokemon');
  const [grade, setGrade] = useState('');
  const [purchasePrice, setPurchasePrice] = useState('');
  const [tags, setTags] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError('');

    try {
      await createItem({
        name,
        category,
        grade: grade || undefined,
        purchase_price: purchasePrice ? parseFloat(purchasePrice) : undefined,
        tags: tags ? tags.split(',').map((t) => t.trim()).filter(Boolean) : [],
      });
      onAdded();
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create item');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>Add Item to Hoard</h2>
        <form onSubmit={handleSubmit}>
          <label>
            Name *
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Charizard Base Set Holo"
              required
            />
          </label>

          <label>
            Category *
            <select value={category} onChange={(e) => setCategory(e.target.value as Category)}>
              {CATEGORIES.map((c) => (
                <option key={c.value} value={c.value}>{c.label}</option>
              ))}
            </select>
          </label>

          <label>
            Grade
            <input
              type="text"
              value={grade}
              onChange={(e) => setGrade(e.target.value)}
              placeholder="PSA 9, CGC 8.5, raw..."
            />
          </label>

          <label>
            Purchase Price
            <input
              type="number"
              step="0.01"
              value={purchasePrice}
              onChange={(e) => setPurchasePrice(e.target.value)}
              placeholder="0.00"
            />
          </label>

          <label>
            Tags (comma-separated)
            <input
              type="text"
              value={tags}
              onChange={(e) => setTags(e.target.value)}
              placeholder="base set, holo, 1st edition"
            />
          </label>

          {error && <p className="error">{error}</p>}

          <div className="modal-actions">
            <button type="button" onClick={onClose} className="btn-secondary">Cancel</button>
            <button type="submit" disabled={submitting || !name} className="btn-primary">
              {submitting ? 'Adding...' : 'Add Item'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
