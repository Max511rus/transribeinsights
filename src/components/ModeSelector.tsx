import { ProcessingMode, PROCESSING_MODES } from '../types';

interface ModeSelectorProps {
  fileName: string;
  onModeSelected: (mode: ProcessingMode) => void;
  onBack: () => void;
}

export default function ModeSelector({ fileName, onModeSelected, onBack }: ModeSelectorProps) {
  return (
    <div>
      {/* File info */}
      <div className="flex items-center gap-3 mb-8 p-4 bg-slate-700/30 border border-slate-600/30 rounded-xl">
        <div className="w-10 h-10 rounded-lg bg-green-500/20 flex items-center justify-center">
          <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-white truncate">{fileName}</p>
          <p className="text-xs text-slate-400">Файл загружен и готов к обработке</p>
        </div>
        <button
          onClick={onBack}
          className="text-sm text-slate-400 hover:text-white transition-colors"
        >
          Заменить
        </button>
      </div>

      {/* Mode selection */}
      <h3 className="text-lg font-semibold mb-4">Выберите режим обработки</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {PROCESSING_MODES.map((mode) => (
          <button
            key={mode.key}
            onClick={() => onModeSelected(mode.key)}
            className="group relative p-6 bg-slate-700/30 border border-slate-600/30 rounded-xl text-left hover:border-purple-500/50 hover:bg-slate-700/50 transition-all duration-300 hover:scale-[1.02] hover:shadow-xl hover:shadow-purple-500/10"
          >
            <div className="flex items-start gap-4">
              <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${mode.color} flex items-center justify-center text-2xl shadow-lg flex-shrink-0`}>
                {mode.icon}
              </div>
              <div>
                <h4 className="font-semibold text-white mb-1 group-hover:text-purple-300 transition-colors">
                  {mode.title}
                </h4>
                <p className="text-sm text-slate-400 leading-relaxed">
                  {mode.description}
                </p>
              </div>
            </div>
            <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-purple-500/0 to-pink-500/0 group-hover:from-purple-500/5 group-hover:to-pink-500/5 transition-all duration-300 pointer-events-none" />
          </button>
        ))}
      </div>
    </div>
  );
}
