export default function Features() {
  const features = [
    {
      icon: '🎙️',
      title: 'Транскрибация',
      description: 'Groq Whisper API с поддержкой автоопределения языка и обработкой больших файлов через чанки',
      gradient: 'from-blue-500/20 to-cyan-500/20',
      border: 'border-blue-500/20',
    },
    {
      icon: '🧠',
      title: 'AI-анализ',
      description: '4 режима обработки: ключевые выводы, конспект лекции, краткое резюме, план действий',
      gradient: 'from-purple-500/20 to-pink-500/20',
      border: 'border-purple-500/20',
    },
    {
      icon: '📄',
      title: 'PDF отчёты',
      description: 'Красиво оформленные PDF-документы с поддержкой русского языка, заголовками и списками',
      gradient: 'from-green-500/20 to-emerald-500/20',
      border: 'border-green-500/20',
    },
    {
      icon: '🤖',
      title: 'Telegram-бот',
      description: 'Отправляйте аудио и видео прямо в Telegram — получайте transcript.txt и PDF',
      gradient: 'from-amber-500/20 to-orange-500/20',
      border: 'border-amber-500/20',
    },
    {
      icon: '🔌',
      title: 'REST API',
      description: 'HTTP API для интеграции с любым сайтом или приложением. Bearer-авторизация',
      gradient: 'from-red-500/20 to-rose-500/20',
      border: 'border-red-500/20',
    },
    {
      icon: '⚡',
      title: 'Быстрая обработка',
      description: 'Groq LPU обеспечивает молниеносную обработку. Большие файлы разбиваются на чанки',
      gradient: 'from-indigo-500/20 to-violet-500/20',
      border: 'border-indigo-500/20',
    },
  ];

  return (
    <section id="features" className="py-16 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold mb-4 bg-gradient-to-r from-white to-slate-300 bg-clip-text text-transparent">
            Возможности сервиса
          </h2>
          <p className="text-slate-400 text-lg max-w-2xl mx-auto">
            Полный цикл обработки аудио и видео: от загрузки файла до готового PDF-документа
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {features.map((feature) => (
            <div
              key={feature.title}
              className={`group p-6 bg-gradient-to-br ${feature.gradient} border ${feature.border} rounded-2xl hover:scale-[1.02] transition-all duration-300 hover:shadow-xl`}
            >
              <div className="text-3xl mb-4">{feature.icon}</div>
              <h3 className="text-lg font-semibold text-white mb-2">{feature.title}</h3>
              <p className="text-sm text-slate-400 leading-relaxed">{feature.description}</p>
            </div>
          ))}
        </div>

        {/* Tech stack */}
        <div className="mt-12 bg-slate-800/30 border border-slate-700/30 rounded-2xl p-6 md:p-8">
          <h3 className="text-lg font-semibold text-white mb-6 text-center">Технологический стек</h3>
          <div className="flex flex-wrap justify-center gap-3">
            {[
              'Python 3.10+', 'FastAPI', 'aiogram 3', 'Groq API',
              'Whisper', 'LLM', 'ffmpeg', 'WeasyPrint',
              'Jinja2', 'SQLAlchemy', 'Uvicorn', 'Nginx',
            ].map((tech) => (
              <span
                key={tech}
                className="px-3 py-1.5 bg-slate-700/50 border border-slate-600/30 rounded-lg text-sm text-slate-300"
              >
                {tech}
              </span>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
