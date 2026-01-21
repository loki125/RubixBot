import React, { useRef, useEffect } from 'react';
import { LogEntry } from '../types';

export const StatusLog: React.FC<{ logs: LogEntry[] }> = ({ logs }) => {
  const endRef = useRef<HTMLDivElement>(null);

  // Auto scroll to bottom isn't needed if we reverse list (newest on top), 
  // but let's stick to newest on top for this UI.
  
  return (
    <div className="flex-1 overflow-y-auto font-mono text-xs space-y-1 pr-2">
      {logs.map((log) => (
        <div key={log.id} className="flex gap-2 animate-in fade-in slide-in-from-left-2 duration-300">
          <span className="text-slate-500 shrink-0">[{log.timestamp.toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })}]</span>
          <span className={`
            break-words
            ${log.type === 'error' ? 'text-red-400' : ''}
            ${log.type === 'success' ? 'text-green-400' : ''}
            ${log.type === 'warning' ? 'text-yellow-400' : ''}
            ${log.type === 'info' ? 'text-cyan-300/80' : ''}
          `}>
            {log.type === 'success' && '✓ '}
            {log.type === 'error' && '✕ '}
            {log.message}
          </span>
        </div>
      ))}
    </div>
  );
};