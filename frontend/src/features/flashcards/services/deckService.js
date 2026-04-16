const API_BASE = 'http://127.0.0.1:8001/api/v1'

const parseResponse = async (response) => {
  const data = await response.json()
  if (!response.ok || !data.success) {
    const message = data?.message || 'Request failed'
    throw new Error(message)
  }
  return data
}

export const listDecks = async (userId) => {
  const url = new URL(`${API_BASE}/decks`)
  if (userId != null) {
    url.searchParams.set('user_id', String(userId))
  }

  const response = await fetch(url.toString())
  const data = await parseResponse(response)
  return data.data
}

export const createDeck = async ({ title, userId, sourceUrl }) => {
  const response = await fetch(`${API_BASE}/decks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      title,
      user_id: userId,
      source_url: sourceUrl || null
    })
  })

  const data = await parseResponse(response)
  return data.data
}

export const updateDeck = async (deckId, payload) => {
  const response = await fetch(`${API_BASE}/decks/${deckId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })

  const data = await parseResponse(response)
  return data.data
}

export const deleteDeck = async (deckId) => {
  const response = await fetch(`${API_BASE}/decks/${deckId}`, {
    method: 'DELETE'
  })

  const data = await parseResponse(response)
  return data.data
}

export const listCards = async (deckId) => {
  const response = await fetch(`${API_BASE}/decks/${deckId}/cards`)
  const data = await parseResponse(response)
  return data.data
}

export const createCard = async (deckId, payload) => {
  const response = await fetch(`${API_BASE}/decks/${deckId}/cards`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })

  const data = await parseResponse(response)
  return data.data
}

export const updateCard = async (cardId, payload) => {
  const response = await fetch(`${API_BASE}/cards/${cardId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })

  const data = await parseResponse(response)
  return data.data
}

export const deleteCard = async (cardId) => {
  const response = await fetch(`${API_BASE}/cards/${cardId}`, {
    method: 'DELETE'
  })

  const data = await parseResponse(response)
  return data.data
}
