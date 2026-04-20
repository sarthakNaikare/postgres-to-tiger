'use client';

import { useState } from 'react';

export default function MigrationSQL({ sql }: { sql: string }) {
  const [copied, setCopied] = useState(false);

  function handleCopy() {
    navigator.clipboard.writeText(sql);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <div className="bg-gray-900 rounded-2xl p-8 border border-gray-800">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-200">Migration SQL</h3>
        <button
          onClick={handleCopy}
          className="text-xs bg-gray-800 hover:bg-gray-700 text-gray-300 px-4 py-2 rounded-lg transition-colors"
        >
          {copied ? '✅ Copied!' : 'Copy SQL'}
        </button>
      </div>
      <pre className="text-sm text-green-400 overflow-x-auto whitespace-pre-wrap bg-gray-950 rounded-xl p-6 border border-gray-800">
        {sql}
      </pre>
    </div>
  );
}
