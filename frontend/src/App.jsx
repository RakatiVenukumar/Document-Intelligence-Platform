import { Link, Navigate, Route, Routes } from 'react-router-dom'

import AskPage from './pages/AskPage'
import BookDetailPage from './pages/BookDetailPage'
import DashboardPage from './pages/DashboardPage'

function Shell({ children }) {
  return (
    <div className="min-h-screen bg-hero-grid text-ink">
      <header className="sticky top-0 z-20 border-b border-black/5 bg-white/75 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
          <div>
            <p className="font-display text-xs font-semibold uppercase tracking-[0.35em] text-moss">Document Intelligence Platform</p>
            <h1 className="font-display text-xl font-semibold text-ink sm:text-2xl">Book Intelligence Studio</h1>
          </div>
          <nav className="flex items-center gap-3 text-sm font-medium">
            <Link className="rounded-full border border-black/10 px-4 py-2 transition hover:border-accent hover:text-accent" to="/">Dashboard</Link>
            <Link className="rounded-full border border-black/10 px-4 py-2 transition hover:border-accent hover:text-accent" to="/ask">Ask</Link>
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">{children}</main>
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
