// 🧭 GitHub Copilot Full-Stack Integration Instructions
// See DEVELOPER_GUIDE.md for full context and rules.
// This file provides a complete, modular API client for all backend endpoints.
// ✅ Do not delete existing code. Only append or extend functions as needed.

const BASE_URL = import.meta.env.VITE_API_BASE_URL;

// Helper for fetch with error handling and JWT support
function getAuthHeaders() {
  const token = localStorage.getItem("token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function fetchJson(url, options = {}) {
  const headers = {
    ...(options.headers || {}),
    ...getAuthHeaders(),
  };
  const res = await fetch(url, { ...options, headers });
  if (!res.ok) {
    if (res.status === 401) {
      localStorage.removeItem("token");
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }
    const msg = await res.text();
    throw new Error(`API error: ${res.status} ${res.statusText} - ${msg}`);
  }
  return res.json();
}

const api = {
  // --- Weather Analysis ---
  async getWeatherProbability(payload) {
    return fetchJson(`${BASE_URL}/api/weather-probability`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  },

  async getWeatherHistory(location, dateRange) {
    const query = new URLSearchParams({ location, ...dateRange }).toString();
    return fetchJson(`${BASE_URL}/api/weather-history?${query}`);
  },

  async searchLocations(query) {
    return fetchJson(`${BASE_URL}/api/locations/search?q=${encodeURIComponent(query)}`);
  },

  // --- Trip Management ---
  async getTrips() {
    return fetchJson(`${BASE_URL}/api/trips`);
  },

  async createTrip(payload) {
    // Map frontend camelCase to backend snake_case and ensure ISO datetime format
    function toIsoDateString(dateStr) {
      // If already has T, return as is
      if (dateStr.includes('T')) return dateStr;
      // If only date, add T00:00:00
      return dateStr ? `${dateStr}T00:00:00` : undefined;
    }
    const mapped = {
      ...payload,
      start_date: toIsoDateString(payload.startDate),
      end_date: toIsoDateString(payload.endDate),
    };
    delete mapped.startDate;
    delete mapped.endDate;
    return fetchJson(`${BASE_URL}/api/trips`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(mapped),
    });
  },

  async getTrip(id) {
    return fetchJson(`${BASE_URL}/api/trips/${id}`);
  },

  async updateTrip(id, payload) {
    return fetchJson(`${BASE_URL}/api/trips/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  },

  async deleteTrip(id) {
    return fetchJson(`${BASE_URL}/api/trips/${id}`, {
      method: "DELETE",
    });
  },

  // --- AI Recommendations ---
  async getRecommendations(payload) {
    return fetchJson(`${BASE_URL}/api/recommendations`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  },

  // --- Reports ---
  async getReports() {
    return fetchJson(`${BASE_URL}/api/reports`);
  },

  async createReport(payload) {
    return fetchJson(`${BASE_URL}/api/reports`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  },

  async updateReport(id, payload) {
    return fetchJson(`${BASE_URL}/api/reports/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  },

  async deleteReport(id) {
    return fetchJson(`${BASE_URL}/api/reports/${id}`, {
      method: "DELETE",
    });
  },

  async uploadReportPhoto(id, file) {
    const formData = new FormData();
    formData.append("photo", file);
    const res = await fetch(`${BASE_URL}/api/reports/${id}/photos`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) throw new Error("Failed to upload photo");
    return res.json();
  },

  // --- Profile Management ---
  async getProfile() {
    return fetchJson(`${BASE_URL}/api/profile`);
  },

  async updateProfile(payload) {
    return fetchJson(`${BASE_URL}/api/profile`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  },

  async updateProfilePreferences(payload) {
    return fetchJson(`${BASE_URL}/api/profile/preferences`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  },

  // --- Export / Calendar ---
  async exportCsv() {
    const res = await fetch(`${BASE_URL}/api/export/csv`);
    if (!res.ok) throw new Error("Failed to export CSV");
    return res.blob();
  },

  async exportJson() {
    return fetchJson(`${BASE_URL}/api/export/json`);
  },

  async createCalendarEvent(payload) {
    return fetchJson(`${BASE_URL}/api/calendar/event`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  },

  // --- Auth ---
  async signup(payload) {
    // Ensure username is sent for backend
    if (!payload.username) throw new Error("Username is required");
    return fetchJson(`${BASE_URL}/auth/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  },

  async login({ username, password }) {
    // FastAPI expects form data, not JSON, for OAuth2PasswordRequestForm
    const form = new URLSearchParams();
    form.append("username", username);
    form.append("password", password);
    return fetchJson(`${BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: form.toString(),
    });
  },

  async logout() {
    return fetchJson(`${BASE_URL}/auth/logout`, {
      method: "POST",
    });
  },

  async getCurrentUser() {
    return fetchJson(`${BASE_URL}/auth/user`);
  },
};

// Export the API client
export default api;

// --- End of Copilot Integration API Layer ---
