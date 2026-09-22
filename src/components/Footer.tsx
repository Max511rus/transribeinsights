export default function Footer() {
  return (
    <footer className="border-t border-slate-700/50 py-10 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
          {/* Brand */}
          <div>
            <div className="flex items-center gap-3 mb-4">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-xs font-bold">
                T&I
              </div>
              <span className="font-bold text-white">Transcribe & Insight</span>
            </div>
            <p className="text-sm text-slate-400 leading-relaxed">
              Сервис транскрибации и AI-анализа аудио/видео. 
              Powered by Groq Whisper и LLM.
            </p>
          </div>

          {/* Links */}
          <div>
            <h4 className="font-semibold text-white mb-3">Сервис</h4>
            <ul className="space-y-2 text-sm text-slate-400">
              <li><a href="#app" className="hover:text-white transition-colors">Обработка файла</a></li>
              <li><a href="#api" className="hover:text-white transition-colors">API документация</a></li>
              <li><a href="#features" className="hover:text-white transition-colors">Возможности</a></li>
            </ul>
          </div>

          {/* Modes */}
          <div>
            <h4 className="font-semibold text-white mb-3">Режимы обработки</h4>
            <ul className="space-y-2 text-sm text-slate-400">
              <li>💡 Ключевые выводы</li>
              <li>📚 Конспект лекции</li>
              <li>📝 Краткое резюме</li>
              <li>🎯 План действий</li>
            </ul>
          </div>
        </div>

        <div className="border-t border-slate-700/50 pt-6 flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-sm text-slate-500">
            © 2024 Transcribe & Insight. Все права защищены.
          </p>
          <div className="flex items-center gap-4 text-sm text-slate-500">
            <span>Python 3.10+</span>
            <span>•</span>
            <span>FastAPI</span>
            <span>•</span>
            <span>Groq AI</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
