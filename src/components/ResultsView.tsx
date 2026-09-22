import { useState } from 'react';
import { TaskState } from '../types';
import { PROCESSING_MODES } from '../types';

interface ResultsViewProps {
  taskState: TaskState;
  onReset: () => void;
}

export default function ResultsView({ taskState, onReset }: ResultsViewProps) {
  const [activeTab, setActiveTab] = useState<'transcript' | 'result'>('result');
  const modeInfo = PROCESSING_MODES.find(m => m.key === taskState.mode);

  const downloadFile = (content: string, filename: string, mimeType: string) => {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div>
      {/* Success header */}
      <div className="text-center mb-8">
        <div className="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br from-green-500/20 to-emerald-500/20 border border-green-500/30 flex items-center justify-center mb-4">
          <svg className="w-8 h-8 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h3 className="text-xl font-semibold mb-1">Обработка завершена!</h3>
        <p className="text-slate-400">
          {taskState.fileName} • {modeInfo?.icon} {modeInfo?.title}
        </p>
      </div>

      {/* Download buttons */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-6">
        <button
          onClick={() => downloadFile(taskState.transcript, 'transcript.txt', 'text/plain')}
          className="flex items-center gap-3 p-4 bg-slate-700/30 border border-slate-600/30 rounded-xl hover:bg-slate-700/50 hover:border-blue-500/30 transition-all group"
        >
          <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center group-hover:bg-blue-500/30 transition-colors">
            <svg className="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div className="text-left">
            <p className="text-sm font-medium text-white">transcript.txt</p>
            <p className="text-xs text-slate-400">Полная транскрибация</p>
          </div>
        </button>

        <button
          onClick={() => downloadFile(taskState.result, 'result.md', 'text/markdown')}
          className="flex items-center gap-3 p-4 bg-slate-700/30 border border-slate-600/30 rounded-xl hover:bg-slate-700/50 hover:border-purple-500/30 transition-all group"
        >
          <div className="w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center group-hover:bg-purple-500/30 transition-colors">
            <svg className="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
            </svg>
          </div>
          <div className="text-left">
            <p className="text-sm font-medium text-white">result.pdf</p>
            <p className="text-xs text-slate-400">Обработанный результат</p>
          </div>
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 p-1 bg-slate-700/30 rounded-lg mb-4">
        <button
          onClick={() => setActiveTab('transcript')}
          className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all ${
            activeTab === 'transcript'
              ? 'bg-slate-600/50 text-white shadow-sm'
              : 'text-slate-400 hover:text-white'
          }`}
        >
          📄 Транскрибация
        </button>
        <button
          onClick={() => setActiveTab('result')}
          className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all ${
            activeTab === 'result'
              ? 'bg-slate-600/50 text-white shadow-sm'
              : 'text-slate-400 hover:text-white'
          }`}
        >
          {modeInfo?.icon} {modeInfo?.title}
        </button>
      </div>

      {/* Content */}
      <div className="bg-slate-900/50 border border-slate-700/30 rounded-xl p-6 max-h-96 overflow-y-auto">
        <pre className="text-sm text-slate-300 whitespace-pre-wrap font-sans leading-relaxed">
          {activeTab === 'transcript' ? taskState.transcript : taskState.result}
        </pre>
      </div>

      {/* Actions */}
      <div className="flex flex-col sm:flex-row gap-3 mt-6">
        <button
          onClick={onReset}
          className="flex-1 px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl font-medium hover:from-purple-600 hover:to-pink-600 transition-all shadow-lg shadow-purple-500/20"
        >
          Обработать другой файл
        </button>
        <button
          onClick={() => {
            const text = activeTab === 'transcript' ? taskState.transcript : taskState.result;
            navigator.clipboard.writeText(text);
          }}
          className="px-6 py-3 bg-slate-700/50 border border-slate-600/50 rounded-xl font-medium hover:bg-slate-700 transition-all"
        >
          📋 Копировать
        </button>
      </div>
    </div>
  );
}
