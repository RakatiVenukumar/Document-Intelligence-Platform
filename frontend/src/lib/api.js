const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/$/, '')

export async function fetchBooks() {
  const response = await fetch(`${API_BASE_URL}/api/books/`)

  if (!response.ok) {
    throw new Error(`Failed to load books (${response.status})`)
  }

  return response.json()
}

export async function fetchBook(bookId) {
  const response = await fetch(`${API_BASE_URL}/api/books/${bookId}/`)

  if (!response.ok) {
    throw new Error(`Failed to load book ${bookId} (${response.status})`)
  }

  return response.json()
}