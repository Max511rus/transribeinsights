import { useState } from 'react';

export default function Header() {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-slate-900/80 backdrop-blur-xl border-b border-slate-700/50">
      <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-lg font-bold shadow-lg shadow-purple-500/20">
            T&I
          </div>
          <div>
            <h1 className="text-lg font-bold text-white">Transcribe & Insight</h1>
            <p className="text-xs text-slate-400 hidden sm:block">AI-powered audio processing</p>
          </div>
        </div>

        <nav className="hidden md:flex items-center gap-6">
          <a href="#features" className="text-sm text-slate-300 hover:text-white transition-colors">Возможности</a>
          <a href="#app" className="text-sm text-slate-300 hover:text-white transition-colors">Обработка</a>
          <a href="#api" className="text-sm text-slate-300 hover:text-white transition-colors">API</a>
          <a href="#app" className="px-4 py-2 bg-purple-500 hover:bg-purple-600 rounded-lg text-sm font-medium transition-colors shadow-lg shadow-purple-500/20">
            Начать
          </a>
        </nav>

        <button
          className="md:hidden p-2 text-slate-300"
          onClick={() => setMobileOpen(!mobileOpen)}
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            {mobileOpen ? (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            ) : (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            )}
          </svg>
        </button>
      </div>

      {mobileOpen && (
        <div className="md:hidden bg-slate-800/95 backdrop-blur-xl border-t border-slate-700/50 px-4 py-4 space-y-3">
          <a href="#features" className="block text-sm text-slate-300 hover:text-white" onClick={() => setMobileOpen(false)}>Возможности</a>
          <a href="#app" className="block text-sm text-slate-300 hover:text-white" onClick={() => setMobileOpen(false)}>Обработка</a>
          <a href="#api" className="block text-sm text-slate-300 hover:text-white" onClick={() => setMobileOpen(false)}>API</a>
          <a href="#app" className="block px-4 py-2 bg-purple-500 rounded-lg text-sm font-medium text-center" onClick={() => setMobileOpen(false)}>
            Начать
          </a>
        </div>
      )}
    </header>
  );
}
