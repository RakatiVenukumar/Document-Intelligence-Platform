import { Link } from 'react-router-dom'

export default function BookCard({ book }) {
  const description = book.description || book.summary || 'No description has been generated yet.'

  return (
    <article className="group flex h-full flex-col rounded-[1.75rem] border border-black/10 bg-white/90 p-6 shadow-sm transition duration-300 hover:-translate-y-1 hover:shadow-glow">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="font-display text-xs font-semibold uppercase tracking-[0.3em] text-moss">{book.genre || 'Unclassified'}</p>
          <h3 className="mt-2 line-clamp-2 font-display text-2xl font-semibold text-ink">{book.title}</h3>
        </div>
        <div className="rounded-2xl bg-ink px-3 py-2 text-right text-white">
          <p className="text-[0.65rem] uppercase tracking-[0.25em] text-sand">Rating</p>
          <p className="text-lg font-semibold">{book.rating ?? 'N/A'}</p>
        </div>
      </div>

      <p className="mt-4 text-sm font-medium text-slate-500">by {book.author}</p>

      <p className="mt-4 line-clamp-4 text-sm leading-7 text-slate-600">{description}</p>

      <div className="mt-6 flex flex-wrap gap-3 text-sm">
        <Link
          className="inline-flex items-center justify-center rounded-full bg-accent px-4 py-2 font-medium text-white transition hover:bg-accent/90"
          to={`/books/${book.id}`}
        >
          View details
        </Link>
        <a
          className="inline-flex items-center justify-center rounded-full border border-black/10 px-4 py-2 font-medium text-ink transition hover:border-accent hover:text-accent"
          href={book.url}
          target="_blank"
          rel="noreferrer"
        >
          Source link
        </a>
      </div>
    </article>
  )
}