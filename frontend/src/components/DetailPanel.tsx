import ReactMarkdown from 'react-markdown';
import { AgentResponse } from '../api/agent';

interface Props {
  response: AgentResponse | null;
}

export default function DetailPanel({ response }: Props) {
  if (!response) {
    return (
      <div style={{ color: '#6b7280', textAlign: 'center', marginTop: 80 }}>
        <p style={{ fontSize: 48 }}>🔬</p>
        <p style={{ marginTop: 12 }}>Search for a 3GPP spec, feature, or ask a question</p>
      </div>
    );
  }

  const specLink = (spec: string) =>
    `https://www.3gpp.org/ftp/Specs/archive/${spec}/`;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      {/* Summary */}
      <section>
        <h3 style={{ color: '#1d9bf0', marginBottom: 8, fontSize: 14 }}>Summary</h3>
        <div style={{ fontSize: 13, lineHeight: 1.6 }}>
          <ReactMarkdown>{response.summary}</ReactMarkdown>
        </div>
      </section>

      {/* Metadata Table */}
      {response.citations.length > 0 && (
        <section>
          <h3 style={{ color: '#1d9bf0', marginBottom: 8, fontSize: 14 }}>Metadata</h3>
          <table style={{ width: '100%', fontSize: 12, borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid #2f3336' }}>
                {['Spec', 'Release', 'Section'].map(h => (
                  <th key={h} style={{ padding: '6px 8px', textAlign: 'left', color: '#9ca3af' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {response.citations.map((c, i) => (
                <tr key={i} style={{ borderBottom: '1px solid #2f3336' }}>
                  <td style={{ padding: '6px 8px' }}>{c.spec}</td>
                  <td style={{ padding: '6px 8px' }}>{c.release}</td>
                  <td style={{ padding: '6px 8px' }}>§{c.section}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}

      {/* Citations */}
      {response.citations.length > 0 && (
        <section>
          <h3 style={{ color: '#1d9bf0', marginBottom: 8, fontSize: 14 }}>Citations</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {response.citations.map((c, i) => (
              <div key={i} style={{ background: '#1a1f25', borderRadius: 8, padding: 12, fontSize: 12 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <a
                    href={specLink(c.spec)}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{ color: '#1d9bf0', textDecoration: 'none' }}
                  >
                    📄 TS {c.spec} · {c.release} · §{c.section}
                  </a>
                  <button
                    onClick={() => navigator.clipboard.writeText(c.text)}
                    style={{
                      background: 'none', border: '1px solid #2f3336', borderRadius: 4,
                      color: '#9ca3af', cursor: 'pointer', padding: '2px 8px', fontSize: 11,
                    }}
                  >
                    Copy
                  </button>
                </div>
                <p style={{ marginTop: 6, color: '#9ca3af', lineHeight: 1.5 }}>{c.text}</p>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
