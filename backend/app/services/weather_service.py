import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime, timedelta, time
from typing import List, Dict, Optional

from app.core.config import settings


class WeatherService:
    def __init__(self):
        # read credentials from settings (already wired in backend config)
        self.nasa_api_key = getattr(settings, 'NASA_API_KEY', None)
        self.meteomatics_username = getattr(settings, 'METEOMATICS_USERNAME', None)
        self.meteomatics_password = getattr(settings, 'METEOMATICS_PASSWORD', None)
        self.google_api_key = getattr(settings, 'GOOGLE_WEATHER_API_KEY', None)
        self.user_agent = getattr(settings, 'USER_AGENT', 'SkyWatcher/1.0 (contact@example.com)')
        self.high_wind_threshold = getattr(settings, 'HIGH_WIND_THRESHOLD', 30)

    async def analyze_weather_probability(
        self,
        location: str,
        start_date: str,
        end_date: Optional[str] = None,
        conditions_checklist: List[str] = [],
        activity_profile: Optional[str] = None
    ) -> Dict:
        """High-level wrapper: get coordinates, historical datasets, probabilities and chart."""
        # Get coordinates
        coords = await self.get_coordinates(location)
        lat, lon = coords['latitude'], coords['longitude']

        # Parse date
        date = datetime.strptime(start_date, "%Y-%m-%d")
        month_day = date.strftime("%m-%d")
        years = [date.year - i for i in range(1, 6)]

        # Fetch historical datasets (meteomatics + optional NASA)
        historical_dfs = []
        # Meteomatics
        for year in years:
            try:
                ydfs = self._get_meteomatics_for_year(lat, lon, year, month_day)
                historical_dfs.extend(ydfs)
            except Exception:
                continue

        # Combine
        df_combined = pd.concat(historical_dfs) if historical_dfs else pd.DataFrame()

        # Calculate base historical probabilities
        if not df_combined.empty:
            prob_hist = self.calculate_probabilities(df_combined)
            hourly_probs = self.calculate_hourly_probabilities(df_combined)
        else:
            prob_hist = {
                "rain_probability": 0,
                "cloudy_probability": 0,
                "sunny_probability": 0,
                "average_humidity": 0,
                "average_wind_speed": 0,
                "high_wind_probability": 0,
            }
            hourly_probs = pd.DataFrame()

        # Google live data nudge (if API key present)
        google_df = pd.DataFrame()
        if self.google_api_key:
            try:
                google_df = await self.get_google_weather(lat, lon, start_date)
            except Exception:
                google_df = pd.DataFrame()

        final_prob = self.apply_google_nudge(prob_hist, google_df, n_hist_years=len(historical_dfs))

        # Temperature summary preferences: prefer google if it has more rows
        df_final = google_df if not google_df.empty and google_df.shape[0] > df_combined.shape[0] else df_combined

        temp_stats = {
            "min": round(df_final['t_2m:C'].min(), 1) if 't_2m:C' in df_final.columns and not df_final.empty else None,
            "max": round(df_final['t_2m:C'].max(), 1) if 't_2m:C' in df_final.columns and not df_final.empty else None,
            "avg": round(df_final['t_2m:C'].mean(), 1) if 't_2m:C' in df_final.columns and not df_final.empty else None,
        }

        chart_base64 = self.generate_chart(hourly_probs, location, start_date) if not hourly_probs.empty else None

        # Format probabilities as percentages for API consumers
        formatted_probs = {
            "rain": round(final_prob.get('rain_probability', 0) * 100, 1),
            "cloudy": round(final_prob.get('cloudy_probability', 0) * 100, 1),
            "sunny": round(final_prob.get('sunny_probability', 0) * 100, 1),
            "high_wind": round(final_prob.get('high_wind_probability', 0) * 100, 1),
            "average_humidity": round(final_prob.get('average_humidity', 0), 1),
            "average_wind_speed": round(final_prob.get('average_wind_speed', 0), 1)
        }

        # Compose summary text (simple example, can be improved)
        summary_text = (
            f"On {start_date} at {location}, expected rain probability is {formatted_probs['rain']}%, "
            f"cloudy: {formatted_probs['cloudy']}%, sunny: {formatted_probs['sunny']}%. "
            f"Humidity: {formatted_probs['average_humidity']}%, wind: {formatted_probs['average_wind_speed']} km/h."
        )
        # Confidence level (simple logic: more years = higher confidence)
        confidence_level = "high" if len(historical_dfs) >= 4 else ("medium" if len(historical_dfs) >= 2 else "low")
        # Compose summary dict for API
        summary = dict(formatted_probs)
        # Hourly probabilities (convert to required schema)
        hourly_probabilities = []
        if not hourly_probs.empty:
            for row in hourly_probs.itertuples(index=False):
                hourly_probabilities.append({
                    "hour": getattr(row, "hour", 0),
                    "rain_prob": getattr(row, "rain_prob", 0.0),
                    "cloudy_prob": getattr(row, "cloudy_prob", 0.0),
                    "sunny_prob": getattr(row, "sunny_prob", 0.0),
                    "high_wind_prob": getattr(row, "high_wind_prob", 0.0),
                })
        return {
            "location": location,
            "coordinates": {"latitude": lat, "longitude": lon},
            "date": start_date,
            "summary": summary,
            "hourly_probabilities": hourly_probabilities,
            "confidence_level": confidence_level,
            "summary_text": summary_text,
            "chart_base64": chart_base64,
        }

    async def get_coordinates(self, location: str) -> Dict[str, float]:
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": location, "format": "json", "limit": 1}
        headers = {"User-Agent": self.user_agent}
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            raise ValueError(f"Place '{location}' not found")
        return {"latitude": float(data[0]["lat"]), "longitude": float(data[0]["lon"]) }

    def _get_meteomatics_for_year(self, lat: float, lon: float, year: int, month_day: str, days_range: int = 2) -> List[pd.DataFrame]:
        params = "t_2m:C,precip_1h:mm,relative_humidity_2m:p,wind_speed_FL10:kmh,total_cloud_cover:octas"
        interval = "PT1H"
        dfs: List[pd.DataFrame] = []
        target_date = datetime.strptime(f"{year}-{month_day}", "%Y-%m-%d")
        for offset in range(-days_range, days_range + 1):
            date = target_date + timedelta(days=offset)
            start = f"{date.strftime('%Y-%m-%d')}T00:00:00Z"
            end = f"{date.strftime('%Y-%m-%d')}T23:59:59Z"
            url = f"https://api.meteomatics.com/{start}--{end}:{interval}/{params}/{lat},{lon}/json"
            try:
                if self.meteomatics_username and self.meteomatics_password:
                    response = requests.get(url, auth=(self.meteomatics_username, self.meteomatics_password), timeout=15)
                else:
                    response = requests.get(url, timeout=15)
                if response.status_code != 200:
                    continue
                json_data = response.json()
            except Exception:
                continue

            all_series = {}
            for param in json_data.get("data", []):
                times, values = [], []
                for entry in param["coordinates"][0]["dates"]:
                    times.append(entry["date"])
                    values.append(entry["value"])
                all_series[param["parameter"]] = pd.Series(values, index=pd.to_datetime(times))

            if all_series:
                df = pd.DataFrame(all_series)
                # Expand single-timestamp days to full 24-hour distribution if needed
                if len(df.index.unique()) == 1:
                    single_time = df.index[0]
                    date_only = single_time.date()
                    full_day_times = pd.date_range(start=datetime.combine(date_only, time(0, 0)), periods=24, freq='1H')
                    expanded_data = {}
                    for col in df.columns:
                        base_value = df[col].iloc[0]
                        if col == 'relative_humidity_2m:p' and not np.isnan(base_value):
                            hourly_factors = np.array([1.0 + np.sin((hour - 14) * np.pi / 12) * 0.3 for hour in range(24)])
                            expanded_data[col] = np.clip(base_value * hourly_factors, 0, 100)
                        elif col == 't_2m:C' and not np.isnan(base_value):
                            hourly_variation = np.array([-np.sin((hour - 14) * np.pi / 12) * 4 for hour in range(24)])
                            expanded_data[col] = base_value + hourly_variation
                        elif col == 'precip_1h:mm' and not np.isnan(base_value):
                            if base_value > 0:
                                hourly_variation = np.array([max(0, 1 + np.sin((hour - 16) * np.pi / 8) * 0.5) for hour in range(24)])
                                expanded_data[col] = base_value * hourly_variation
                            else:
                                expanded_data[col] = [base_value] * 24
                        else:
                            expanded_data[col] = [base_value] * 24
                    df = pd.DataFrame(expanded_data, index=full_day_times)

                dfs.append(df)

        return dfs

    async def get_google_weather(self, lat: float, lon: float, target_date: str) -> pd.DataFrame:
        today = datetime.utcnow().date()
        delta_days = (pd.to_datetime(target_date).date() - today).days
        if delta_days < 0 or delta_days > 7:
            return pd.DataFrame()
        try:
            endpoint = "https://weather.googleapis.com/v1/currentConditions:lookup" if delta_days == 0 else "https://weather.googleapis.com/v1/forecast:lookup"
            params = {"key": self.google_api_key, "location.latitude": lat, "location.longitude": lon}
            resp = requests.get(endpoint, params=params, timeout=10)
            data = resp.json()
            if "currentConditions" in data:
                entry = data["currentConditions"][0]
            elif "forecast" in data:
                entry = data["forecast"]["daily"][0]
            else:
                return pd.DataFrame()
            return pd.DataFrame({
                "t_2m:C": [entry.get("temperature", np.nan)],
                "precip_1h:mm": [entry.get("precipitation", np.nan)],
                "relative_humidity_2m:p": [entry.get("humidity", np.nan)],
                "wind_speed_FL10:kmh": [entry.get("windSpeed", np.nan)],
                "total_cloud_cover:octas": [entry.get("cloudCover", np.nan)]
            })
        except Exception:
            return pd.DataFrame()

    def calculate_probabilities(self, df: pd.DataFrame) -> Dict[str, float]:
        if df.empty:
            return {"rain_probability": 0, "cloudy_probability": 0, "sunny_probability": 0, "average_humidity": 0, "average_wind_speed": 0, "high_wind_probability": 0}
        rain_prob = (df['precip_1h:mm'] > 0).mean() if 'precip_1h:mm' in df.columns else 0
        cloudy_prob = (df['relative_humidity_2m:p'] > 70).mean() if 'relative_humidity_2m:p' in df.columns else 0
        sunny_prob = ((df.get('precip_1h:mm', 0) == 0) & (df.get('relative_humidity_2m:p', 0) < 60)).mean() if 'relative_humidity_2m:p' in df.columns else 0
        avg_humidity = df['relative_humidity_2m:p'].mean() if 'relative_humidity_2m:p' in df.columns else 0
        avg_wind = df['wind_speed_FL10:kmh'].mean() if 'wind_speed_FL10:kmh' in df.columns else 0
        high_wind_prob = (df['wind_speed_FL10:kmh'] > self.high_wind_threshold).mean() if 'wind_speed_FL10:kmh' in df.columns else 0
        return {
            "rain_probability": rain_prob,
            "cloudy_probability": cloudy_prob,
            "sunny_probability": sunny_prob,
            "average_humidity": avg_humidity,
            "average_wind_speed": avg_wind,
            "high_wind_probability": high_wind_prob
        }

    def apply_google_nudge(self, probabilities: Dict[str, float], google_df: pd.DataFrame, n_hist_years: int) -> Dict[str, float]:
        nudged = probabilities.copy()
        confidence_factor = min(n_hist_years / 5, 1.0)
        if not google_df.empty:
            precip = google_df.get('precip_1h:mm', pd.Series([0])).iloc[0]
            humidity = google_df.get('relative_humidity_2m:p', pd.Series([0])).iloc[0]
            cloud = google_df.get('total_cloud_cover:octas', pd.Series([0])).iloc[0]
            wind = google_df.get('wind_speed_FL10:kmh', pd.Series([0])).iloc[0]
            if precip > 2.0:
                nudged['rain_probability'] = min(nudged.get('rain_probability', 0) + 0.1 * confidence_factor, 1.0)
            if humidity < 50:
                nudged['sunny_probability'] = min(nudged.get('sunny_probability', 0) + 0.1 * confidence_factor, 1.0)
            if humidity > 80 or cloud > 6:
                nudged['cloudy_probability'] = min(nudged.get('cloudy_probability', 0) + 0.1 * confidence_factor, 1.0)
            if wind > self.high_wind_threshold:
                nudged['high_wind_probability'] = min(nudged.get('high_wind_probability', 0) + 0.1 * confidence_factor, 1.0)
        return nudged

    def calculate_hourly_probabilities(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return pd.DataFrame(columns=['hour', 'rain_prob', 'cloudy_prob', 'sunny_prob', 'avg_wind', 'high_wind_prob'])
        df = df.copy()
        if not pd.api.types.is_datetime64_any_dtype(df.index):
            df.index = pd.to_datetime(df.index, errors='coerce')
        df = df.dropna(subset=['t_2m:C', 'precip_1h:mm', 'relative_humidity_2m:p'], how='all')
        df['hour'] = df.index.hour

        def calc_probs(group):
            rain = (group['precip_1h:mm'] > 0).mean() if 'precip_1h:mm' in group else 0
            cloudy = (group['relative_humidity_2m:p'] > 70).mean() if 'relative_humidity_2m:p' in group else 0
            sunny = ((group.get('precip_1h:mm', 0) == 0) & (group.get('relative_humidity_2m:p', 0) < 60)).mean() if 'relative_humidity_2m:p' in group else 0
            avg_wind = group['wind_speed_FL10:kmh'].mean() if 'wind_speed_FL10:kmh' in group else 0
            high_wind = (group['wind_speed_FL10:kmh'] > self.high_wind_threshold).mean() if 'wind_speed_FL10:kmh' in group else 0
            return pd.Series({
                'rain_prob': rain,
                'cloudy_prob': cloudy,
                'sunny_prob': sunny,
                'avg_wind': avg_wind,
                'high_wind_prob': high_wind
            })

        hourly_probs = df.groupby('hour').apply(calc_probs).reset_index()
        return hourly_probs

    def generate_chart(self, hourly_probs: pd.DataFrame, place: str, date: str) -> Optional[str]:
        if hourly_probs.empty:
            return None
        plt.figure(figsize=(12, 5))
        plt.plot(hourly_probs['hour'], hourly_probs['rain_prob'] * 100, label='Rain %', color='blue', marker='o')
        plt.plot(hourly_probs['hour'], hourly_probs['cloudy_prob'] * 100, label='Cloudy %', color='gray', marker='o')
        plt.plot(hourly_probs['hour'], hourly_probs['sunny_prob'] * 100, label='Sunny %', color='orange', marker='o')
        plt.plot(hourly_probs['hour'], hourly_probs['high_wind_prob'] * 100, label='High Wind %', color='red', marker='o')
        plt.title(f"Hourly Weather Probabilities for {place} on {date}")
        plt.xlabel("Hour")
        plt.ylabel("Probability (%)")
        plt.xticks(range(0, 24))
        plt.ylim(0, 100)
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.legend()
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        return img_base64
