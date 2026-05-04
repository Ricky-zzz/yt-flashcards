const API_BASE = 'http://127.0.0.1:8001/api/v1'

const parseResponse = async (response) => {
  const data = await response.json()
  if (!response.ok || !data.success) {
    const message = data?.message || 'API error'
    throw new Error(message)
  }
  return data
}

export const startSession = async (deckId, userId) => {
  const response = await fetch(`${API_BASE}/reviews/sessions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ deck_id: deckId, user_id: userId })
  })

  const data = await parseResponse(response)
  return data.data
}

export const submitAttempt = async (sessionId, cardId, userAnswer, isCorrect) => {
  const response = await fetch(`${API_BASE}/reviews/attempts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId,
      card_id: cardId,
      user_answer: userAnswer,
      is_correct: isCorrect
    })
  })

  const data = await parseResponse(response)
  return data.data
}

export const finishSession = async (sessionId, score) => {
  const response = await fetch(`${API_BASE}/reviews/sessions/${sessionId}/finish?score=${score}`, {
    method: 'POST'
  })

  const data = await parseResponse(response)
  return data.data
}

export const listSessions = async (userId, deckId) => {
  const url = new URL(`${API_BASE}/reviews/sessions`)
  if (userId != null) {
    url.searchParams.set('user_id', String(userId))
  }
  if (deckId != null) {
    url.searchParams.set('deck_id', String(deckId))
  }

  const response = await fetch(url.toString())
  const data = await parseResponse(response)
  return data.data
}

export const listAttempts = async (sessionId) => {
  const response = await fetch(`${API_BASE}/reviews/sessions/${sessionId}/attempts`)
  const data = await parseResponse(response)
  return data.data
}
