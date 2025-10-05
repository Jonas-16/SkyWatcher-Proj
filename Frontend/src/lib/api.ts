// src/lib/api.ts

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export async function fetchWeatherHistory(location: string, startDate: string, endDate: string) {
  const res = await fetch(`${API_BASE_URL}/api/weather-history?location=${encodeURIComponent(location)}&start_date=${startDate}&end_date=${endDate}`);
  if (!res.ok) throw new Error('Failed to fetch weather history');
  return res.json();
}

export async function fetchProfile() {
  const res = await fetch(`${API_BASE_URL}/api/profile`);
  if (!res.ok) throw new Error('Failed to fetch profile');
  return res.json();
}

export async function fetchReports() {
  const res = await fetch(`${API_BASE_URL}/api/reports`);
  if (!res.ok) throw new Error('Failed to fetch reports');
  return res.json();
}

export async function fetchExportCSV() {
  const res = await fetch(`${API_BASE_URL}/api/export/csv`);
  if (!res.ok) throw new Error('Failed to fetch CSV export');
  return res.text();
}

export async function fetchExportJSON() {
  const res = await fetch(`${API_BASE_URL}/api/export/json`);
  if (!res.ok) throw new Error('Failed to fetch JSON export');
  return res.json();
}

export async function fetchTrips() {
  const res = await fetch(`${API_BASE_URL}/api/trips`);
  if (!res.ok) throw new Error('Failed to fetch trips');
  return res.json();
}

// Add more API functions as needed for other endpoints
