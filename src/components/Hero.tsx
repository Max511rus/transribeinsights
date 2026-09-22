export default function Hero() {
  return (
    <section className="pt-28 pb-16 px-4 relative overflow-hidden">
      {/* Background effects */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl" />
        <div className="absolute top-40 right-1/4 w-80 h-80 bg-pink-500/10 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-full h-px bg-gradient-to-r from-transparent via-purple-500/30 to-transparent" />
      </div>

      <div className="max-w-5xl mx-auto text-center relative">
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-purple-500/10 border border-purple-500/20 rounded-full text-sm text-purple-300 mb-8">
          <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
          Powered by Groq AI — Whisper + LLM
        </div>

        <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold mb-6 leading-tight">
          <span className="bg-gradient-to-r from-white via-purple-200 to-white bg-clip-text text-transparent">
            Транскрибация
          </span>
          <br />
          <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-purple-400 bg-clip-text text-transparent">
            и анализ аудио
          </span>
        </h1>

        <p className="text-lg md:text-xl text-slate-400 max-w-3xl mx-auto mb-10 leading-relaxed">
          Загрузите аудио или видео — получите транскрибацию, ключевые выводы, 
          конспект, резюме или план действий. Всё через AI за минуты.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-12">
          <a
            href="#app"
            className="px-8 py-4 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl text-lg font-semibold hover:from-purple-600 hover:to-pink-600 transition-all shadow-xl shadow-purple-500/25 hover:shadow-purple-500/40 hover:scale-105"
          >
            Загрузить файл
          </a>
          <a
            href="#api"
            className="px-8 py-4 bg-slate-800/50 border border-slate-600/50 rounded-xl text-lg font-semibold hover:bg-slate-700/50 transition-all"
          >
            API документация
          </a>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-3xl mx-auto">
          {[
            { value: '25MB', label: 'Макс. размер' },
            { value: '4', label: 'Режима анализа' },
            { value: '< 2мин', label: 'Время обработки' },
            { value: 'PDF', label: 'Формат вывода' },
          ].map((stat) => (
            <div key={stat.label} className="bg-slate-800/30 border border-slate-700/30 rounded-xl p-4">
              <div className="text-2xl font-bold text-white">{stat.value}</div>
              <div className="text-sm text-slate-400">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
