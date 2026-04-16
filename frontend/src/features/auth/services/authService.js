const API_BASE = 'http://127.0.0.1:8001/api/v1'
const USER_STORAGE_KEY = 'yt_flashcard_user_v1'

const parseResponse = async (response) => {
  const data = await response.json()
  if (!response.ok || !data.success) {
    const message = data?.message || 'Request failed'
    throw new Error(message)
  }
  return data
}

export const getStoredUser = () => {
  const raw = localStorage.getItem(USER_STORAGE_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw)
  } catch {
    localStorage.removeItem(USER_STORAGE_KEY)
    return null
  }
}

export const setStoredUser = (user) => {
  if (!user) return
  localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user))
}

export const clearStoredUser = () => {
  localStorage.removeItem(USER_STORAGE_KEY)
}

export const registerUser = async ({ email, password, fullName }) => {
  const response = await fetch(`${API_BASE}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email,
      password,
      full_name: fullName || null
    })
  })

  const data = await parseResponse(response)
  setStoredUser(data?.data?.user)
  return data
}

export const loginUser = async ({ email, password }) => {
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  })

  const data = await parseResponse(response)
  setStoredUser(data?.data?.user)
  return data
}
