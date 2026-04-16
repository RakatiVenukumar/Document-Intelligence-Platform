import { useParams } from 'react-router-dom'

export default function BookDetailPage() {
  const { bookId } = useParams()

  return (
    <section className="rounded-[2rem] border border-black/10 bg-white/80 p-8 shadow-glow backdrop-blur-xl">
      <p className="font-display text-xs font-semibold uppercase tracking-[0.35em] text-moss">Book Detail</p>
      <h2 className="mt-3 font-display text-3xl font-semibold sm:text-4xl">Book #{bookId}</h2>
      <p className="mt-4 max-w-2xl text-sm leading-7 text-slate-600 sm:text-base">
        The detail view will expand this scaffold with metadata, AI summaries, recommendations, and RAG answers.
      </p>
    </section>
  )
}
