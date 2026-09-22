import { useState } from 'react';

export default function ApiDocs() {
  const [activeEndpoint, setActiveEndpoint] = useState(0);

  const endpoints = [
    {
      method: 'GET',
      path: '/health',
      description: 'Проверка здоровья сервиса',
      auth: false,
      response: `{
  "status": "ok",
  "version": "1.0.0",
  "groq_available": true
}`,
    },
    {
      method: 'POST',
      path: '/api/v1/tasks',
      description: 'Создание задачи на обработку',
      auth: true,
      body: `// multipart/form-data
// file: аудио или видео файл
// mode: insights | lecture | summary | action_plan`,
      response: `{
  "task_id": "abc123def456",
  "status": "pending",
  "file_name": "meeting.mp3",
  "mode": "insights",
  "created_at": "2024-01-15T10:30:00Z"
}`,
    },
    {
      method: 'GET',
      path: '/api/v1/tasks/:task_id',
      description: 'Получение статуса задачи',
      auth: true,
      response: `{
  "task_id": "abc123def456",
  "status": "completed",
  "progress": 100,
  "file_name": "meeting.mp3",
  "mode": "insights",
  "created_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:31:45Z"
}`,
    },
    {
      method: 'GET',
      path: '/api/v1/tasks/:task_id/transcript',
      description: 'Получение транскрибации',
      auth: true,
      response: `// text/plain
Добрый день, уважаемые коллеги. Сегодня мы собрались...`,
    },
    {
      method: 'GET',
      path: '/api/v1/tasks/:task_id/result',
      description: 'Получение обработанного текста',
      auth: true,
      response: `// text/markdown
# Ключевые выводы из записи

## 📊 Финансовые показатели
- **Выручка Q3**: 247 млн ₽ (+18% YoY)...`,
    },
    {
      method: 'GET',
      path: '/api/v1/tasks/:task_id/pdf',
      description: 'Скачать результат в PDF',
      auth: true,
      response: `// application/pdf
// Бинарный файл PDF с форматированным результатом`,
    },
  ];

  return (
    <section id="api" className="py-16 px-4">
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold mb-4 bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
            HTTP API
          </h2>
          <p className="text-slate-400 text-lg max-w-2xl mx-auto">
            Интегрируйте сервис транскрибации в ваше приложение через REST API.
            Все эндпоинты защищены Bearer-токеном.
          </p>
        </div>

        <div className="bg-slate-800/50 backdrop-blur-xl rounded-3xl border border-slate-700/50 overflow-hidden shadow-2xl">
          {/* Endpoint list */}
          <div className="border-b border-slate-700/50">
            {endpoints.map((ep, idx) => (
              <button
                key={idx}
                onClick={() => setActiveEndpoint(idx)}
                className={`w-full flex items-center gap-3 px-6 py-3 text-left transition-all border-b border-slate-700/30 last:border-b-0 ${
                  activeEndpoint === idx
                    ? 'bg-slate-700/30'
                    : 'hover:bg-slate-700/20'
                }`}
              >
                <span className={`px-2 py-0.5 rounded text-xs font-bold ${
                  ep.method === 'GET' ? 'bg-green-500/20 text-green-400' : 'bg-blue-500/20 text-blue-400'
                }`}>
                  {ep.method}
                </span>
                <code className="text-sm text-slate-300 font-mono flex-1">{ep.path}</code>
                {ep.auth && (
                  <span className="text-xs text-amber-400/70 hidden sm:inline">🔒 Auth</span>
                )}
              </button>
            ))}
          </div>

          {/* Endpoint detail */}
          <div className="p-6">
            <div className="mb-4">
              <div className="flex items-center gap-3 mb-2">
                <span className={`px-2 py-0.5 rounded text-xs font-bold ${
                  endpoints[activeEndpoint].method === 'GET' ? 'bg-green-500/20 text-green-400' : 'bg-blue-500/20 text-blue-400'
                }`}>
                  {endpoints[activeEndpoint].method}
                </span>
                <code className="text-sm text-white font-mono">{endpoints[activeEndpoint].path}</code>
              </div>
              <p className="text-slate-400 text-sm">{endpoints[activeEndpoint].description}</p>
              {endpoints[activeEndpoint].auth && (
                <p className="text-xs text-amber-400/70 mt-1">
                  Требуется заголовок: <code className="bg-slate-700/50 px-1.5 py-0.5 rounded">Authorization: Bearer {'<API_AUTH_TOKEN>'}</code>
                </p>
              )}
            </div>

            {endpoints[activeEndpoint].body && (
              <div className="mb-4">
                <p className="text-xs text-slate-500 mb-2 uppercase tracking-wider">Request Body</p>
                <pre className="bg-slate-900/50 border border-slate-700/30 rounded-lg p-4 text-sm text-slate-300 overflow-x-auto font-mono">
                  {endpoints[activeEndpoint].body}
                </pre>
              </div>
            )}

            <div>
              <p className="text-xs text-slate-500 mb-2 uppercase tracking-wider">Response</p>
              <pre className="bg-slate-900/50 border border-slate-700/30 rounded-lg p-4 text-sm text-green-300/80 overflow-x-auto font-mono">
                {endpoints[activeEndpoint].response}
              </pre>
            </div>
          </div>
        </div>

        {/* Status codes */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-slate-800/30 border border-slate-700/30 rounded-xl p-5">
            <h4 className="font-semibold text-white mb-3">Статусы задач</h4>
            <div className="space-y-2">
              {[
                { status: 'pending', label: 'Ожидает', color: 'text-slate-400' },
                { status: 'preparing', label: 'Подготовка аудио', color: 'text-yellow-400' },
                { status: 'transcribing', label: 'Транскрибация', color: 'text-blue-400' },
                { status: 'processing', label: 'Обработка LLM', color: 'text-purple-400' },
                { status: 'generating_pdf', label: 'Генерация PDF', color: 'text-pink-400' },
                { status: 'completed', label: 'Завершено', color: 'text-green-400' },
                { status: 'failed', label: 'Ошибка', color: 'text-red-400' },
              ].map(item => (
                <div key={item.status} className="flex items-center gap-2">
                  <span className={`w-2 h-2 rounded-full ${item.color.replace('text-', 'bg-')}`} />
                  <code className="text-xs text-slate-400 font-mono">{item.status}</code>
                  <span className="text-xs text-slate-500">— {item.label}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-slate-800/30 border border-slate-700/30 rounded-xl p-5">
            <h4 className="font-semibold text-white mb-3">Режимы обработки</h4>
            <div className="space-y-2">
              {[
                { key: 'insights', label: 'Ключевые выводы', icon: '💡' },
                { key: 'lecture', label: 'Конспект лекции', icon: '📚' },
                { key: 'summary', label: 'Краткое резюме', icon: '📝' },
                { key: 'action_plan', label: 'План действий', icon: '🎯' },
              ].map(item => (
                <div key={item.key} className="flex items-center gap-2">
                  <span>{item.icon}</span>
                  <code className="text-xs text-slate-400 font-mono">{item.key}</code>
                  <span className="text-xs text-slate-500">— {item.label}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* curl example */}
        <div className="mt-8 bg-slate-800/30 border border-slate-700/30 rounded-xl p-5">
          <h4 className="font-semibold text-white mb-3">Пример: загрузка файла через curl</h4>
          <pre className="bg-slate-900/50 border border-slate-700/30 rounded-lg p-4 text-sm text-slate-300 overflow-x-auto font-mono">
{`curl -X POST https://your-domain.com/api/v1/tasks \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -F "file=@meeting.mp3" \\
  -F "mode=insights"

# Проверка статуса
curl https://your-domain.com/api/v1/tasks/TASK_ID \\
  -H "Authorization: Bearer YOUR_TOKEN"

# Скачать PDF
curl https://your-domain.com/api/v1/tasks/TASK_ID/pdf \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -o result.pdf`}
          </pre>
        </div>
      </div>
    </section>
  );
}
