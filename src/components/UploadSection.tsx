import { useRef, useState } from 'react';

interface UploadSectionProps {
  onFileSelected: (file: File) => void;
}

const ACCEPTED_EXTENSIONS = [
  'mp3', 'wav', 'ogg', 'm4a', 'flac', 'aac', 'wma',
  'mp4', 'avi', 'mkv', 'mov', 'webm', 'flv', 'wmv',
];

const MAX_FILE_SIZE = 25 * 1024 * 1024; // 25MB

export default function UploadSection({ onFileSelected }: UploadSectionProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const validateFile = (file: File): boolean => {
    const ext = file.name.split('.').pop()?.toLowerCase();
    if (!ext || !ACCEPTED_EXTENSIONS.includes(ext)) {
      setError(`Неподдерживаемый формат: .${ext}. Допустимые: ${ACCEPTED_EXTENSIONS.slice(0, 6).join(', ')}...`);
      return false;
    }
    if (file.size > MAX_FILE_SIZE) {
      setError(`Файл слишком большой (${(file.size / 1024 / 1024).toFixed(1)} МБ). Максимум: 25 МБ`);
      return false;
    }
    setError(null);
    return true;
  };

  const handleFile = (file: File) => {
    if (validateFile(file)) {
      onFileSelected(file);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => {
    setDragOver(false);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  };

  return (
    <div>
      <div
        className={`relative border-2 border-dashed rounded-2xl p-10 md:p-16 text-center transition-all duration-300 cursor-pointer ${
          dragOver
            ? 'border-purple-400 bg-purple-500/10 scale-[1.02]'
            : 'border-slate-600/50 hover:border-purple-500/50 hover:bg-slate-700/20'
        }`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          accept={ACCEPTED_EXTENSIONS.map(e => `.${e}`).join(',')}
          onChange={handleInputChange}
        />

        <div className="mb-6">
          <div className="w-20 h-20 mx-auto rounded-2xl bg-gradient-to-br from-purple-500/20 to-pink-500/20 border border-purple-500/30 flex items-center justify-center">
            <svg className="w-10 h-10 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
          </div>
        </div>

        <h3 className="text-xl font-semibold mb-2">
          Перетащите файл сюда
        </h3>
        <p className="text-slate-400 mb-4">
          или нажмите для выбора
        </p>
        <p className="text-sm text-slate-500">
          Аудио: MP3, WAV, OGG, M4A, FLAC, AAC • Видео: MP4, AVI, MKV, MOV, WebM
        </p>
        <p className="text-sm text-slate-500 mt-1">
          Максимальный размер: 25 МБ
        </p>
      </div>

      {error && (
        <div className="mt-4 p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-300 text-sm flex items-center gap-3">
          <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {error}
        </div>
      )}

      {/* Demo hint */}
      <div className="mt-6 p-4 bg-slate-700/30 border border-slate-600/30 rounded-xl">
        <p className="text-sm text-slate-400">
          <span className="text-purple-400 font-medium">💡 Демо-режим:</span> Загрузите любой аудио/видео файл для демонстрации. 
          Обработка будет симулирована с примером результата.
        </p>
      </div>
    </div>
  );
}
