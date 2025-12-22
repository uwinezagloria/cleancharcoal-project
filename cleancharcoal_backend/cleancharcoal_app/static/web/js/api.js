const API = "/api/";

async function apiPost(endpoint, data) {
  const res = await fetch(API + endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  let payload = {};
  try { payload = await res.json(); } catch (e) {}

  if (!res.ok) {
    throw new Error(payload.detail || payload.error || "Request failed");
  }
  return payload;
}
