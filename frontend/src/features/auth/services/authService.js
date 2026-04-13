const API_BASE = 'http://127.0.0.1:8001/api/v1'

const parseResponse = async (response) => {
  const data = await response.json()
  if (!response.ok || !data.success) {
    const message = data?.message || 'Request failed'
    throw new Error(message)
  }
  return data
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

  return parseResponse(response)
}

export const loginUser = async ({ email, password }) => {
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  })

  return parseResponse(response)
}
