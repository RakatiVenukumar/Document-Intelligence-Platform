import { Link, Navigate, Route, Routes } from 'react-router-dom'

import AskPage from './pages/AskPage'
import BookDetailPage from './pages/BookDetailPage'
import DashboardPage from './pages/DashboardPage'

function Shell({ children }) {
  return (
    <div className="relative min-h-screen overflow-hidden bg-hero-grid text-ink">
      <div className="pointer-events-none absolute left-[-6rem] top-[-4rem] h-80 w-80 rounded-full bg-accent/10 blur-3xl" />
      <div className="pointer-events-none absolute right-[-4rem] top-40 h-96 w-96 rounded-full bg-moss/10 blur-3xl" />
      <div className="pointer-events-none absolute bottom-[-8rem] left-1/3 h-96 w-96 rounded-full bg-black/5 blur-3xl" />

      <header className="sticky top-0 z-20 border-b border-black/5 bg-white/72 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
          <div>
            <p className="font-display text-xs font-semibold uppercase tracking-[0.35em] text-moss">Document Intelligence Platform</p>
            <h1 className="font-display text-xl font-semibold text-ink sm:text-2xl">Book Intelligence Studio</h1>
          </div>
          <nav className="flex items-center gap-3 text-sm font-medium">
            <span className="hidden rounded-full border border-moss/20 bg-moss/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.25em] text-moss sm:inline-flex">
              Live RAG
            </span>
            <Link className="rounded-full border border-black/10 px-4 py-2 transition hover:border-accent hover:text-accent" to="/">Dashboard</Link>
            <Link className="rounded-full border border-black/10 px-4 py-2 transition hover:border-accent hover:text-accent" to="/ask">Ask</Link>
          </nav>
        </div>
      </header>
      <main className="relative mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">{children}</main>
      <footer className="relative mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 pb-8 pt-2 text-xs uppercase tracking-[0.3em] text-slate-500 sm:px-6 lg:px-8">
        <span>Django REST</span>
        <span>Tailwind UI</span>
        <span>Cached RAG responses</span>
      </footer>
    </div>
  )
}

export default function App() {
  return (
    <Routes>
      <Route
        path="/"
        element={
          <Shell>
            <DashboardPage />
          </Shell>
        }
      />
      <Route
        path="/ask"
        element={
          <Shell>
            <AskPage />
          </Shell>
        }
      />
      <Route
        path="/books/:bookId"
        element={
          <Shell>
            <BookDetailPage />
          </Shell>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
