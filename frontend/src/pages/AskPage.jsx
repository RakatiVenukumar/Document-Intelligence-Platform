export default function AskPage() {
  return (
    <section className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
      <div className="rounded-[2rem] border border-black/10 bg-white/80 p-8 shadow-glow backdrop-blur-xl">
        <p className="font-display text-xs font-semibold uppercase tracking-[0.35em] text-accent">Q&A</p>
        <h2 className="mt-3 font-display text-3xl font-semibold sm:text-4xl">Ask questions over indexed books</h2>
        <p className="mt-4 max-w-2xl text-sm leading-7 text-slate-600 sm:text-base">
          The input form and answer stream will be added in the next UI step, using the RAG backend that is already in
          place.
        </p>
      </div>
      <div className="rounded-[2rem] border border-black/10 bg-ink p-8 text-white shadow-glow">
        <p className="font-display text-xs font-semibold uppercase tracking-[0.35em] text-sand">Preview</p>
        <div className="mt-6 space-y-4 text-sm leading-7 text-slate-200">
          <p>Questions will show citations, source chunks, and AI-generated answers.</p>
          <p>The panel is sized and styled to become the live response stream in Step 16.</p>
        </div>
      </div>
    </section>
  )
}
