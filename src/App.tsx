import { useState } from 'react';
import Header from './components/Header';
import Hero from './components/Hero';
import UploadSection from './components/UploadSection';
import ModeSelector from './components/ModeSelector';
import TaskProgress from './components/TaskProgress';
import ResultsView from './components/ResultsView';
import ApiDocs from './components/ApiDocs';
import Features from './components/Features';
import Footer from './components/Footer';
import { ProcessingMode, TaskState, TaskStatus } from './types';

export default function App() {
  const [taskState, setTaskState] = useState<TaskState>({
    status: 'idle',
    fileName: '',
    fileSize: 0,
    mode: null,
    progress: 0,
    transcript: '',
    result: '',
    error: null,
  });

  const [activeSection, setActiveSection] = useState<string>('upload');

  const handleFileSelected = (file: File) => {
    setTaskState(prev => ({
      ...prev,
      status: 'uploaded' as TaskStatus,
      fileName: file.name,
      fileSize: file.size,
      error: null,
    }));
    setActiveSection('mode');
  };

  const handleModeSelected = (mode: ProcessingMode) => {
    setTaskState(prev => ({
      ...prev,
      mode,
      status: 'processing' as TaskStatus,
      progress: 0,
    }));
    setActiveSection('progress');
    simulateProcessing(mode);
  };

  const simulateProcessing = (mode: ProcessingMode) => {
    const steps = [
      { progress: 10, delay: 500 },
      { progress: 25, delay: 1000 },
      { progress: 40, delay: 1500 },
      { progress: 55, delay: 2000 },
      { progress: 70, delay: 2500 },
      { progress: 85, delay: 3000 },
      { progress: 95, delay: 3500 },
      { progress: 100, delay: 4000 },
    ];

    steps.forEach(({ progress, delay }) => {
      setTimeout(() => {
        setTaskState(prev => ({ ...prev, progress }));
      }, delay);
    });

    setTimeout(() => {
      const mockTranscript = generateMockTranscript();
      const mockResult = generateMockResult(mode);
      setTaskState(prev => ({
        ...prev,
        status: 'completed' as TaskStatus,
        transcript: mockTranscript,
        result: mockResult,
        progress: 100,
      }));
      setActiveSection('results');
    }, 4500);
  };

  const handleReset = () => {
    setTaskState({
      status: 'idle',
      fileName: '',
      fileSize: 0,
      mode: null,
      progress: 0,
      transcript: '',
      result: '',
      error: null,
    });
    setActiveSection('upload');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white">
      <Header />
      <main>
        <Hero />
        <Features />
        
        <section id="app" className="py-16 px-4">
          <div className="max-w-5xl mx-auto">
            <div className="text-center mb-12">
              <h2 className="text-3xl md:text-4xl font-bold mb-4 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                Начать обработку
              </h2>
              <p className="text-slate-400 text-lg">
                Загрузите аудио или видео файл и выберите режим обработки
              </p>
            </div>

            <div className="bg-slate-800/50 backdrop-blur-xl rounded-3xl border border-slate-700/50 p-6 md:p-10 shadow-2xl">
              {/* Step indicators */}
              <div className="flex items-center justify-center mb-10 gap-2 md:gap-4">
                {['upload', 'mode', 'progress', 'results'].map((step, idx) => (
                  <div key={step} className="flex items-center">
                    <div className={`w-8 h-8 md:w-10 md:h-10 rounded-full flex items-center justify-center text-sm font-bold transition-all duration-300 ${
                      activeSection === step
                        ? 'bg-purple-500 text-white shadow-lg shadow-purple-500/30 scale-110'
                        : ['upload', 'mode', 'progress', 'results'].indexOf(activeSection) > idx
                          ? 'bg-green-500/20 text-green-400 border border-green-500/50'
                          : 'bg-slate-700/50 text-slate-500 border border-slate-600/50'
                    }`}>
                      {['upload', 'mode', 'progress', 'results'].indexOf(activeSection) > idx ? '✓' : idx + 1}
                    </div>
                    {idx < 3 && (
                      <div className={`w-8 md:w-16 h-0.5 mx-1 md:mx-2 transition-all duration-300 ${
                        ['upload', 'mode', 'progress', 'results'].indexOf(activeSection) > idx
                          ? 'bg-green-500/50'
                          : 'bg-slate-700/50'
                      }`} />
                    )}
                  </div>
                ))}
              </div>

              {activeSection === 'upload' && (
                <UploadSection onFileSelected={handleFileSelected} />
              )}
              {activeSection === 'mode' && (
                <ModeSelector
                  fileName={taskState.fileName}
                  onModeSelected={handleModeSelected}
                  onBack={() => setActiveSection('upload')}
                />
              )}
              {activeSection === 'progress' && (
                <TaskProgress taskState={taskState} />
              )}
              {activeSection === 'results' && (
                <ResultsView taskState={taskState} onReset={handleReset} />
              )}
            </div>
          </div>
        </section>

        <ApiDocs />
      </main>
      <Footer />
    </div>
  );
}

function generateMockTranscript(): string {
  return `Добрый день, уважаемые коллеги. Сегодня мы собрались, чтобы обсудить результаты третьего квартала и наметить планы на следующий период.

Начну с общих показателей. Выручка компании за квартал составила 247 миллионов рублей, что на 18% выше аналогичного периода прошлого года. Операционная прибыль выросла на 23% и составила 52 миллиона рублей.

Особенно хочу отметить работу отдела разработки. Мы запустили три новых продукта, два из которых уже показали положительную динамику по ключевым метрикам. Конверсия в платную подписку увеличилась с 4.2% до 7.8%.

По клиентской базе — мы привлекли 1200 новых корпоративных клиентов.Retention rate составил 94%, что является лучшим результатом за всю историю компании.

Теперь о вызовах. Нам необходимо уделить внимание масштабированию инфраструктуры. Текущие мощности позволяют обрабатывать до 50 тысяч одновременных запросов, но к концу года мы ожидаем рост до 80 тысяч.

Финансовый директор подготовил презентацию по бюджету на следующий квартал. Основные статьи расходов: расширение команды разработки на 15 человек, миграция на новую облачную платформу и запуск маркетинговой кампании в регионах.

Есть вопросы? Давайте обсудим детали.`;
}

function generateMockResult(mode: ProcessingMode): string {
  switch (mode) {
    case 'insights':
      return `# Ключевые выводы из записи

## 📊 Финансовые показатели
- **Выручка Q3**: 247 млн ₽ (+18% YoY)
- **Операционная прибыль**: 52 млн ₽ (+23% YoY)
- **Retention rate**: 94% (рекордный показатель)

## 🚀 Достижения
1. Запущено 3 новых продукта
2. Конверсия в подписку выросла с 4.2% до 7.8%
3. Привлечено 1200 новых корпоративных клиентов

## ⚠️ Проблемные зоны
- Инфраструктура не готова к прогнозируемому росту (50K → 80K запросов)
- Необходимо расширение команды на 15 человек
- Требуется миграция на новую облачную платформу

## 💡 Рекомендации
- Приоритизировать масштабирование инфраструктуры
- Ускорить найм в отдел разработки
- Запустить региональную маркетинговую кампанию`;
    case 'lecture':
      return `# Конспект: Итоги третьего квартала

## Введение
Спикер представил результаты компании за третий квартал, отметив значительный рост по ключевым финансовым показателям.

## Основная часть

### 1. Финансовые результаты
Выручка достигла 247 миллионов рублей — рост на 18% по сравнению с аналогичным периодом прошлого года. Операционная прибыль выросла ещё значительнее — на 23%, составив 52 миллиона рублей. Это свидетельствует об улучшении операционной эффективности.

### 2. Продуктовые достижения
Отдел разработки продемонстрировал высокую продуктивность:
- Запущены 3 новых продукта
- Два из них уже показывают положительную динамику
- Конверсия в платную подписку выросла почти вдвое (4.2% → 7.8%)

### 3. Клиентская база
- 1200 новых корпоративных клиентов
- Retention rate 94% — исторический рекорд

### 4. Вызовы и риски
Главная проблема — масштабирование инфраструктуры. Текущие мощности (50K одновременных запросов) не покрывают прогноз на конец года (80K).

## Планы на следующий квартал
- Расширение команды: +15 разработчиков
- Миграция на новую облачную платформу
- Маркетинговая кампания в регионах

## Ключевые тезисы
> Рост бизнеса опережает рост инфраструктуры — это главный вызов следующего периода.`;
    case 'summary':
      return `# Краткое резюме встречи

**Тема**: Итоги Q3 и планы на следующий квартал

**Главное**:
Компания показала рекордные результаты: выручка 247 млн ₽ (+18%), прибыль 52 млн ₽ (+23%). Запущено 3 новых продукта, конверсия в подписку выросла вдвое. Привлечено 1200 корпоративных клиентов при retention rate 94%.

**Ключевая проблема**: инфраструктура не справится с прогнозируемым ростом нагрузки (50K → 80K запросов).

**Решения**: нанять 15 разработчиков, мигрировать на новую облачную платформу, запустить региональный маркетинг.`;
    case 'action_plan':
      return `# План действий

## Приоритет 1: Масштабирование инфраструктуры (Срок: 4 недели)
- [ ] Провести аудит текущей инфраструктуры
- [ ] Подготовить ТЗ на миграцию облачной платформы
- [ ] Выбрать провайдера и согласовать бюджет
- [ ] Начать миграцию в тестовом режиме
- [ ] Провести нагрузочное тестирование на 100K запросов

## Приоритет 2: Расширение команды (Срок: 6 недель)
- [ ] Открыть 15 вакансий разработчиков
- [ ] Определить стек и требования для каждой позиции
- [ ] Запустить рекрутинговую кампанию
- [ ] Провести первые собеседования к концу 2-й недели
- [ ] Онбординг первых сотрудников к концу 4-й недели

## Приоритет 3: Маркетинг в регионах (Срок: 8 недель)
- [ ] Определить приоритетные регионы
- [ ] Подготовить региональные маркетинговые материалы
- [ ] Запустить пилотную кампанию в 3 регионах
- [ ] Оценить результаты через 4 недели
- [ ] Масштабировать на все регионы

## Контрольные точки
| Дата | Мероприятие | Ответственный |
|------|-------------|---------------|
| +1 неделя | Аудит инфраструктуры | CTO |
| +2 недели | Первые собеседования | HR |
| +4 недели | Завершение миграции | DevOps |
| +6 недель | Команда укомплектована | HR + CTO |
| +8 недель | Результаты регионального маркетинга | CMO |`;
    default:
      return '';
  }
}
