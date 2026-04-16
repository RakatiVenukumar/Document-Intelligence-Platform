import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'

import { fetchBook } from '../lib/api'

function InfoTile({ label, value }) {
  return (
    <div className="rounded-3xl border border-black/10 bg-canvas/70 p-4">
      <p className="text-[0.65rem] uppercase tracking-[0.3em] text-slate-500">{label}</p>
      <p className="mt-2 text-base font-semibold text-ink">{value}</p>
    </div>
  )
}

export default function BookDetailPage() {
  const { bookId } = useParams()
  const [book, setBook] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [refreshKey, setRefreshKey] = useState(0)

  useEffect(() => {
    let active = true

    async function loadBook() {
      try {
        const data = await fetchBook(bookId)
        if (active) {
          setBook(data)
        }
      } catch (loadError) {
        if (active) {
          setError(loadError.message || 'Failed to load book details.')
        }
      } finally {
        if (active) {
          setLoading(false)
        }
      }
    }

    loadBook()

    return () => {
      active = false
    }
  }, [bookId, refreshKey])

  function handleRetry() {
    setError('')
    setLoading(true)
    setRefreshKey((value) => value + 1)
  }

  if (loading) {
    return (
      <section className="overflow-hidden rounded-[2rem] border border-black/10 bg-white/80 shadow-glow backdrop-blur-xl">
        <div className="grid gap-0 lg:grid-cols-[1.2fr_0.8fr]">
          <div className="space-y-5 p-8 sm:p-10">
            <div className="h-3 w-24 animate-pulse rounded-full bg-slate-200" />
            <div className="h-10 w-2/3 animate-pulse rounded-full bg-slate-200" />
            <div className="h-4 w-40 animate-pulse rounded-full bg-slate-200" />
            <div className="mt-6 flex gap-3">
              <div className="h-9 w-28 animate-pulse rounded-full bg-slate-200" />
              <div className="h-9 w-28 animate-pulse rounded-full bg-slate-200" />
            </div>
            <div className="space-y-3 pt-6">
              <div className="h-4 animate-pulse rounded-full bg-slate-200" />
              <div className="h-4 animate-pulse rounded-full bg-slate-200" />
              <div className="h-4 w-5/6 animate-pulse rounded-full bg-slate-200" />
            </div>
          </div>
          <aside className="space-y-4 border-t border-black/10 bg-ink p-8 lg:border-l lg:border-t-0">
            {Array.from({ length: 4 }).map((_, index) => (
              <div key={index} className="h-20 animate-pulse rounded-3xl bg-white/10" />
            ))}
          </aside>
        </div>
      </section>
    )
  }

  if (error) {
    return (
      <section className="rounded-[2rem] border border-red-200 bg-red-50 p-8 text-sm text-red-700">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <p>{error}</p>
          <button
            className="inline-flex items-center justify-center rounded-full bg-red-600 px-4 py-2 font-medium text-white transition hover:bg-red-500"
            type="button"
            onClick={handleRetry}
          >
            Retry
          </button>
        </div>
      </section>
    )
  }

  if (!book) {
    return null
  }

  const summary = book.summary || 'AI-generated summary will appear here once the book has been processed.'
  const description = book.description || 'No description has been provided for this book yet.'

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4">
        <Link className="text-sm font-medium text-slate-500 transition hover:text-accent" to="/">
          ← Back to dashboard
        </Link>
        <Link
          className="rounded-full border border-black/10 bg-white px-4 py-2 text-sm font-medium text-ink transition hover:border-accent hover:text-accent"
          to={`/ask?bookId=${book.id}`}
        >
          Ask about this book
        </Link>
      </div>

      <section className="overflow-hidden rounded-[2rem] border border-black/10 bg-white/80 shadow-glow backdrop-blur-xl">
        <div className="grid gap-0 lg:grid-cols-[1.2fr_0.8fr]">
          <div className="p-8 sm:p-10">
            <p className="font-display text-xs font-semibold uppercase tracking-[0.35em] text-accent">Book Detail</p>
            <h2 className="mt-3 font-display text-3xl font-semibold sm:text-5xl">{book.title}</h2>
            <p className="mt-3 text-base text-slate-600">by {book.author}</p>

            <div className="mt-6 flex flex-wrap gap-3 text-sm">
              <span className="rounded-full bg-ink px-4 py-2 font-medium text-white">{book.genre || 'Unclassified'}</span>
              <span className="rounded-full border border-black/10 bg-canvas px-4 py-2 font-medium text-ink">
                Rating: {book.rating ?? 'N/A'}
              </span>
            </div>

            <div className="mt-8 space-y-4">
              <div>
                <p className="text-xs uppercase tracking-[0.25em] text-slate-500">Summary</p>
                <p className="mt-2 max-w-3xl text-sm leading-7 text-slate-600 sm:text-base">{summary}</p>
              </div>
              <div>
                <p className="text-xs uppercase tracking-[0.25em] text-slate-500">Description</p>
                <p className="mt-2 max-w-3xl text-sm leading-7 text-slate-600 sm:text-base">{description}</p>
              </div>
            </div>
          </div>

          <aside className="border-t border-black/10 bg-ink p-8 text-white lg:border-l lg:border-t-0">
            <p className="font-display text-xs font-semibold uppercase tracking-[0.35em] text-sand">Quick Facts</p>
            <div className="mt-6 grid gap-4">
              <InfoTile label="Author" value={book.author} />
              <InfoTile label="Genre" value={book.genre || 'Unclassified'} />
              <InfoTile label="Rating" value={book.rating ?? 'N/A'} />
              <InfoTile label="Source URL" value={book.url} />
            </div>
          </aside>
        </div>
      </section>
    </div>
  )
}
