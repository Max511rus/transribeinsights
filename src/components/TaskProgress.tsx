import { TaskState } from '../types';
import { PROCESSING_MODES } from '../types';

interface TaskProgressProps {
  taskState: TaskState;
}

const PROCESSING_STEPS = [
  { label: 'Приём файла', threshold: 5 },
  { label: 'Извлечение аудио (ffmpeg)', threshold: 15 },
  { label: 'Подготовка чанков', threshold: 25 },
  { label: 'Транскрибация (Groq Whisper)', threshold: 50 },
  { label: 'Очистка текста', threshold: 60 },
  { label: 'Обработка LLM (Groq)', threshold: 80 },
  { label: 'Генерация PDF', threshold: 95 },
];

export default function TaskProgress({ taskState }: TaskProgressProps) {
  const modeInfo = PROCESSING_MODES.find(m => m.key === taskState.mode);
  const currentStepIndex = PROCESSING_STEPS.findIndex(step => taskState.progress < step.threshold);
  const activeStep = currentStepIndex === -1 ? PROCESSING_STEPS.length : currentStepIndex;

  return (
    <div>
      {/* Header */}
      <div className="text-center mb-8">
        <div className="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br from-purple-500/20 to-pink-500/20 border border-purple-500/30 flex items-center justify-center mb-4">
          <div className="w-8 h-8 border-3 border-purple-400 border-t-transparent rounded-full animate-spin" />
        </div>
        <h3 className="text-xl font-semibold mb-1">Обработка файла</h3>
        <p className="text-slate-400">
          {taskState.fileName} • Режим: {modeInfo?.title}
        </p>
      </div>

      {/* Progress bar */}
      <div className="mb-8">
        <div className="flex justify-between text-sm mb-2">
          <span className="text-slate-400">Прогресс</span>
          <span className="text-purple-400 font-medium">{taskState.progress}%</span>
        </div>
        <div className="h-3 bg-slate-700/50 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-purple-500 to-pink-500 rounded-full transition-all duration-700 ease-out relative"
            style={{ width: `${taskState.progress}%` }}
          >
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-pulse" />
          </div>
        </div>
      </div>

      {/* Steps */}
      <div className="space-y-3">
        {PROCESSING_STEPS.map((step, idx) => {
          const isCompleted = idx < activeStep;
          const isCurrent = idx === activeStep;
          const isPending = idx > activeStep;

          return (
            <div
              key={step.label}
              className={`flex items-center gap-3 p-3 rounded-lg transition-all duration-300 ${
                isCurrent ? 'bg-purple-500/10 border border-purple-500/30' :
                isCompleted ? 'bg-green-500/5' : ''
              }`}
            >
              <div className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 ${
                isCompleted ? 'bg-green-500/20' :
                isCurrent ? 'bg-purple-500/20' :
                'bg-slate-700/50'
              }`}>
                {isCompleted ? (
                  <svg className="w-3.5 h-3.5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                  </svg>
                ) : isCurrent ? (
                  <div className="w-2.5 h-2.5 bg-purple-400 rounded-full animate-pulse" />
                ) : (
                  <div className="w-2 h-2 bg-slate-600 rounded-full" />
                )}
              </div>
              <span className={`text-sm ${
                isCompleted ? 'text-green-300' :
                isCurrent ? 'text-purple-300 font-medium' :
                'text-slate-500'
              } ${isPending ? 'opacity-50' : ''}`}>
                {step.label}
              </span>
              {isCompleted && (
                <span className="ml-auto text-xs text-green-500/70">✓</span>
              )}
              {isCurrent && (
                <span className="ml-auto text-xs text-purple-400">выполняется...</span>
              )}
            </div>
          );
        })}
      </div>

      {/* Info */}
      <div className="mt-8 p-4 bg-slate-700/20 border border-slate-600/20 rounded-xl">
        <p className="text-xs text-slate-500 text-center">
          Обработка может занять от 30 секунд до нескольких минут в зависимости от размера файла.
          <br />Не закрывайте страницу до завершения.
        </p>
      </div>
    </div>
  );
}
