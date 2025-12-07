// simple wrapper for API calls
const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000/api";

export function authHeaders(token) {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function postJSON(path, body, token) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders(token) },
    body: JSON.stringify(body),
  });
  return res.json();
}

export async function putJSON(path, body, token) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json", ...authHeaders(token) },
    body: JSON.stringify(body),
  });
  return res.json();
}

export async function getJSON(path, token) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "GET",
    headers: authHeaders(token),
  });
  return res.json();
}

// DELETE helper
export async function deleteJSON(path, token) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "DELETE",
    headers: authHeaders(token),
  });
  return res.json();
}

// file upload (FormData)
export async function postFormData(path, formData, token) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: authHeaders(token), // do NOT set Content-Type
    body: formData,
  });
  return res.json();
}
