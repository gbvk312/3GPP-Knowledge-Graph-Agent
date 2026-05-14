import { useEffect, useRef } from 'react';

interface Props {
  message: string;
  onDismiss: () => void;
}

export default function ErrorBanner({ message, onDismiss }: Props) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onDismiss();
    };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, [onDismiss]);

  return (
    <div className="error-banner" role="alert" ref={ref}>
      <span className="error-icon">⚠️</span>
      <span className="error-text">{message}</span>
      <button className="error-dismiss" onClick={onDismiss} aria-label="Dismiss error (Escape)">✕</button>
    </div>
  );
}
