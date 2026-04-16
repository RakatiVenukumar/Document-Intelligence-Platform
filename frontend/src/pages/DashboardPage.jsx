import { useEffect, useMemo, useState } from 'react'

import BookCard from '../components/BookCard'
import { fetchBooks } from '../lib/api'

export default function DashboardPage() {
  const [books, setBooks] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true

    async function loadBooks() {
      try {
        const data = await fetchBooks()
        if (!active) {
          return
        }
        setBooks(Array.isArray(data) ? data : data.results || [])
      } catch (loadError) {
        if (active) {
          setError(loadError.message || 'Failed to load books.')
        }
      } finally {
        if (active) {
          setLoading(false)
        }
      }
    }

    loadBooks()

    return () => {
      active = false
    }
  }, [])

  const averageRating = useMemo(() => {
    const numericRatings = books
      .map((book) => Number(book.rating))
      .filter((rating) => Number.isFinite(rating))

    if (!numericRatings.length) {
      return '0.0'
    }

    return (numericRatings.reduce((sum, rating) => sum + rating, 0) / numericRatings.length).toFixed(1)
  }, [books])

  return (
    <div className="space-y-8">
      <section className="rounded-[2rem] border border-black/10 bg-white/80 p-8 shadow-glow backdrop-blur-xl">
        <p className="font-display text-xs font-semibold uppercase tracking-[0.35em] text-accent">Dashboard</p>
        <div className="mt-4 flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <h2 className="font-display text-3xl font-semibold sm:text-4xl">Book catalog and intelligence workspace</h2>
            <p className="mt-4 max-w-2xl text-sm leading-7 text-slate-600 sm:text-base">
              Browse uploaded books, review generated insights, and jump into question answering from one curated
              surface.
            </p>
          </div>
          <div className="grid grid-cols-2 gap-4 text-sm sm:min-w-[20rem]">
            <div className="rounded-3xl border border-black/10 bg-canvas/70 p-4">
              <p className="text-xs uppercase tracking-[0.25em] text-slate-500">Books loaded</p>
              <p className="mt-2 font-display text-3xl font-semibold text-ink">{books.length}</p>
            </div>
            <div className="rounded-3xl border border-black/10 bg-canvas/70 p-4">
              <p className="text-xs uppercase tracking-[0.25em] text-slate-500">Avg. rating</p>
              <p className="mt-2 font-display text-3xl font-semibold text-ink">{averageRating}</p>
            </div>
          </div>
        </div>
      </section>

      {loading ? (
        <section className="rounded-[2rem] border border-dashed border-black/15 bg-white/60 p-10 text-center text-sm text-slate-500">
          Loading books from the backend...
        </section>
      ) : error ? (
        <section className="rounded-[2rem] border border-red-200 bg-red-50 p-8 text-sm text-red-700">
          {error}
        </section>
      ) : books.length === 0 ? (
        <section className="rounded-[2rem] border border-dashed border-black/15 bg-white/60 p-10 text-center text-sm text-slate-500">
          No books are available yet. Upload or scrape books to populate the dashboard.
        </section>
      ) : (
        <section className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
          {books.map((book) => (
            <BookCard key={book.id} book={book} />
          ))}
        </section>
      )}
    </div>
  )
}
