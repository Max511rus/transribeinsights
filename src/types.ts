export type ProcessingMode = 'insights' | 'lecture' | 'summary' | 'action_plan';

export type TaskStatus = 'idle' | 'uploaded' | 'processing' | 'completed' | 'failed';

export interface TaskState {
  status: TaskStatus;
  fileName: string;
  fileSize: number;
  mode: ProcessingMode | null;
  progress: number;
  transcript: string;
  result: string;
  error: string | null;
}

export interface ProcessingModeInfo {
  key: ProcessingMode;
  title: string;
  description: string;
  icon: string;
  color: string;
}

export const PROCESSING_MODES: ProcessingModeInfo[] = [
  {
    key: 'insights',
    title: 'Ключевые выводы',
    description: 'Извлечение главных идей, фактов и рекомендаций из записи',
    icon: '💡',
    color: 'from-amber-500 to-orange-500',
  },
  {
    key: 'lecture',
    title: 'Конспект лекции',
    description: 'Структурированный конспект с разделами, тезисами и цитатами',
    icon: '📚',
    color: 'from-blue-500 to-cyan-500',
  },
  {
    key: 'summary',
    title: 'Краткое резюме',
    description: 'Сжатое изложение основного содержания в нескольких абзацах',
    icon: '📝',
    color: 'from-green-500 to-emerald-500',
  },
  {
    key: 'action_plan',
    title: 'План действий',
    description: 'Конкретные шаги, задачи и сроки на основе записи',
    icon: '🎯',
    color: 'from-purple-500 to-pink-500',
  },
];
