import { useState, useCallback } from 'react';

interface Props {
  nodeLabels: string[];
  onHighlight: (label: string) => void;
  onClear: () => void;
}

export default function GraphSearch({ nodeLabels, onHighlight, onClear }: Props) {
  const [search, setSearch] = useState('');
  const [suggestions, setSuggestions] = useState<string[]>([]);

  const handleChange = useCallback((value: string) => {
    setSearch(value);
    if (value.trim().length > 0) {
      const lower = value.toLowerCase();
      setSuggestions(nodeLabels.filter(l => l.toLowerCase().includes(lower)).slice(0, 8));
    } else {
      setSuggestions([]);
      onClear();
    }
  }, [nodeLabels, onClear]);

  const handleSelect = useCallback((label: string) => {
    setSearch(label);
    setSuggestions([]);
    onHighlight(label);
  }, [onHighlight]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && suggestions.length > 0) {
      handleSelect(suggestions[0]);
    } else if (e.key === 'Escape') {
      setSearch('');
      setSuggestions([]);
      onClear();
    }
  }, [suggestions, handleSelect, onClear]);

  return (
    <div className="graph-search">
      <input
        type="text"
        value={search}
        onChange={e => handleChange(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Find node..."
        className="graph-search-input"
        aria-label="Search nodes in graph"
      />
      {suggestions.length > 0 && (
        <ul className="graph-search-suggestions" role="listbox">
          {suggestions.map(s => (
            <li key={s} role="option" className="graph-search-item" onClick={() => handleSelect(s)}>
              {s}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
