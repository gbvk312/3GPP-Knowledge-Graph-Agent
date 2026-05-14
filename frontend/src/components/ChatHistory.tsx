import { useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';

export interface ChatMessage {
  role: 'user' | 'agent';
  content: string;
  timestamp: number;
}

interface Props {
  messages: ChatMessage[];
  visible: boolean;
  onClose: () => void;
}

export default function ChatHistory({ messages, visible, onClose }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (!visible) return null;

  return (
    <div className="chat-history-overlay" role="dialog" aria-label="Chat history">
      <div className="chat-history-panel">
        <div className="chat-history-header">
          <span className="chat-history-title">💬 Conversation History</span>
          <button className="chat-history-close" onClick={onClose} aria-label="Close history">✕</button>
        </div>
        <div className="chat-history-body">
          {messages.length === 0 && (
            <p className="chat-history-empty">No messages yet. Ask a question to get started.</p>
          )}
          {messages.map((msg, i) => (
            <div key={i} className={`chat-msg chat-msg-${msg.role}`}>
              <span className="chat-msg-icon">{msg.role === 'user' ? '👤' : '🤖'}</span>
              <div className="chat-msg-content">
                {msg.role === 'agent' ? (
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                ) : (
                  <span>{msg.content}</span>
                )}
                <span className="chat-msg-time">{new Date(msg.timestamp).toLocaleTimeString()}</span>
              </div>
            </div>
          ))}
          <div ref={bottomRef} />
        </div>
      </div>
    </div>
  );
}
