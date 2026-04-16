import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'

import { askQuestion } from '../lib/api'

export default function AskPage() {
  const [searchParams] = useSearchParams()
  const [question, setQuestion] = useState('What is this book about?')
  const [bookId, setBookId] = useState('')
  const [topK, setTopK] = useState('5')
  const [answer, setAnswer] = useState('')
  const [sourceChunks, setSourceChunks] = useState([])
  const [usedLlm, setUsedLlm] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    const bookIdFromUrl = searchParams.get('bookId')
    if (bookIdFromUrl) {
      setBookId(bookIdFromUrl)
    }
  }, [searchParams])

  async function handleSubmit(event) {
    event.preventDefault()
    setLoading(true)
    setError('')

    try {
      const result = await askQuestion({
        question,
        bookId: bookId || null,
        topK: Number(topK),
      })
      setAnswer(result.answer)
      setSourceChunks(result.source_chunks || [])
      setUsedLlm(Boolean(result.used_llm))
    } catch (submitError) {
      setError(submitError.message || 'Unable to submit the question.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="grid gap-6 lg:grid-cols-[1.05fr_0.95fr]">
      <div className="rounded-[2rem] border border-black/10 bg-white/80 p-8 shadow-glow backdrop-blur-xl">
        <p className="font-display text-xs font-semibold uppercase tracking-[0.35em] text-accent">Q&A</p>
        <h2 className="mt-3 font-display text-3xl font-semibold sm:text-4xl">Ask questions over indexed books</h2>
        <p className="mt-4 max-w-2xl text-sm leading-7 text-slate-600 sm:text-base">
          Submit a question against the RAG pipeline, optionally scoped to a specific book, and get back an answer
          with citations to the relevant source chunks.
        </p>

        <form className="mt-8 space-y-4" onSubmit={handleSubmit}>
          <label className="block space-y-2">
            <span className="text-xs font-semibold uppercase tracking-[0.25em] text-slate-500">Question</span>
            <textarea
              className="min-h-36 w-full rounded-3xl border border-black/10 bg-white px-4 py-3 text-sm text-ink outline-none transition placeholder:text-slate-400 focus:border-accent"
              placeholder="Ask about themes, summary, recommendations, or a specific detail from the book."
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
            />
          </label>

          <div className="grid gap-4 sm:grid-cols-2">
            <label className="block space-y-2">
              <span className="text-xs font-semibold uppercase tracking-[0.25em] text-slate-500">Book ID</span>
              <input
                className="w-full rounded-3xl border border-black/10 bg-white px-4 py-3 text-sm text-ink outline-none transition placeholder:text-slate-400 focus:border-accent"
                placeholder="Leave blank for all books"
                value={bookId}
                onChange={(event) => setBookId(event.target.value)}
              />
            </label>
            <label className="block space-y-2">
              <span className="text-xs font-semibold uppercase tracking-[0.25em] text-slate-500">Top results</span>
              <input
                className="w-full rounded-3xl border border-black/10 bg-white px-4 py-3 text-sm text-ink outline-none transition placeholder:text-slate-400 focus:border-accent"
                type="number"
                min="1"
                max="10"
                value={topK}
                onChange={(event) => setTopK(event.target.value)}
              />
            </label>
          </div>

          <button
            className="inline-flex items-center justify-center rounded-full bg-accent px-6 py-3 text-sm font-semibold text-white transition hover:bg-accent/90 disabled:cursor-not-allowed disabled:opacity-60"
            type="submit"
            disabled={loading || !question.trim()}
          >
            {loading ? 'Searching...' : 'Ask the assistant'}
          </button>
        </form>

        {error ? (
          <p className="mt-6 rounded-3xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</p>
        ) : null}
      </div>

      <div className="rounded-[2rem] border border-black/10 bg-ink p-8 text-white shadow-glow">
        <p className="font-display text-xs font-semibold uppercase tracking-[0.35em] text-sand">Answer</p>
        {answer ? (
          <div className="mt-6 space-y-6">
            <div className="rounded-[1.5rem] border border-white/10 bg-white/5 p-6">
              <div className="flex flex-wrap items-center gap-3">
                <span className="rounded-full bg-white px-3 py-1 text-xs font-semibold uppercase tracking-[0.25em] text-ink">
                  {usedLlm ? 'LLM generated' : 'Fallback response'}
                </span>
              </div>
              <p className="mt-4 text-sm leading-7 text-slate-100">{answer}</p>
            </div>

            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.25em] text-sand">Source chunks</p>
              <div className="mt-4 space-y-3">
                {sourceChunks.map((chunk) => (
                  <article key={`${chunk.citation_id}-${chunk.chunk_id}`} className="rounded-3xl border border-white/10 bg-white/5 p-4 text-sm text-slate-200">
                    <p className="text-xs font-semibold uppercase tracking-[0.25em] text-sand">
                      [{chunk.citation_id}] {chunk.metadata?.book_title || 'Unknown Book'}
                    </p>
                    <p className="mt-3 leading-7">{chunk.text}</p>
                  </article>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="mt-6 rounded-[1.5rem] border border-dashed border-white/20 p-6 text-sm leading-7 text-slate-200">
            Ask a question to see the generated answer and the evidence used to produce it.
          </div>
        )}
      </div>
    </section>
  )
}
