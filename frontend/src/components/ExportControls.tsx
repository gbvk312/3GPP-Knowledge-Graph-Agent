interface Props {
  onExportPng: () => void;
  onCopyResponse: () => void;
  onShareUrl: () => void;
  hasResponse: boolean;
}

export default function ExportControls({ onExportPng, onCopyResponse, onShareUrl, hasResponse }: Props) {
  return (
    <div className="export-controls">
      <button onClick={onExportPng} className="export-btn" title="Export graph as PNG" aria-label="Export graph as PNG">
        📷
      </button>
      <button onClick={onShareUrl} className="export-btn" title="Copy shareable URL" aria-label="Copy shareable URL">
        🔗
      </button>
      {hasResponse && (
        <button onClick={onCopyResponse} className="export-btn" title="Copy response" aria-label="Copy agent response">
          📋
        </button>
      )}
    </div>
  );
}
