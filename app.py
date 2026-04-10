import streamlit as st
import requests
import pandas as pd
import os
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# =========================
# PAGE CONFIG (MINISTRY UI)
# =========================
st.set_page_config(page_title="Ministry Climate Dashboard", layout="wide")

st.title("🏛️ Mozambique Climate Early Warning Dashboard")
st.caption("Real-time national climate intelligence for decision-making")

# =========================
# AUTO REFRESH
# =========================
st_autorefresh(interval=600000, key="refresh")

# =========================
# API KEY
# =========================
API_KEY = "257f8a9b51420c40a035a9ec83580ed9"

# =========================
# TIME
# =========================
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.success(f"Last Updated: {now}")

# =========================
# USER INPUT
# =========================
location = st.text_input("Enter Region / City Name", "Maputo")
future_days = st.slider("Select future outlook (days)", 1, 30, 7)
days_past = st.slider("Select past days to view", 1, 30, 7)

# =========================
# FUNCTIONS
# =========================
def get_weather(location):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={API_KEY}&units=metric"
    return requests.get(url).json()

def get_forecast(location):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={location}&appid={API_KEY}&units=metric"
    return requests.get(url).json()

# =========================
# MAIN SYSTEM
# =========================
if location:

    data = get_weather(location)

    if "main" not in data:
        st.error("⚠️ Location not found. Try another name.")
    else:

        # =========================
        # CURRENT WEATHER
        # =========================
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        rainfall = data.get("rain", {}).get("1h", 0)

        soil_moisture = max(0, min(100, (humidity * 0.6) - (temp * 0.5) + 40))

        # =========================
        # SAVE HISTORY
        # =========================
        file = "climate_history.csv"

        new_data = pd.DataFrame([{
            "date": now,
            "location": location,
            "temp": temp,
            "humidity": humidity,
            "rainfall": rainfall,
            "soil_moisture": soil_moisture
        }])

        if os.path.exists(file):
            new_data.to_csv(file, mode='a', header=False, index=False)
        else:
            new_data.to_csv(file, index=False)

        # =========================
        # RISK ENGINE
        # =========================
        drought_score = (temp * 0.6) - (rainfall * 5) + (100 - humidity) * 0.3
        pest_score = (temp * 0.5) + (humidity * 0.5)
        disease_score = humidity + (rainfall * 10)

        drought = "🟢 SAFE"
        if drought_score > 70:
            drought = "🔴 SEVERE DROUGHT"
        elif drought_score > 40:
            drought = "🟠 WARNING"

        pests = "🟢 LOW RISK"
        if pest_score > 85:
            pests = "🔴 HIGH RISK"
        elif pest_score > 65:
            pests = "🟠 MODERATE RISK"

        disease = "🟢 LOW RISK"
        if disease_score > 120:
            disease = "🔴 HIGH RISK"
        elif disease_score > 90:
            disease = "🟠 MODERATE RISK"

        # =========================
        # MINISTRY DASHBOARD CARDS
        # =========================
        st.subheader(f"📍 {location} - Live Climate Overview")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("🌡 Temperature", f"{temp} °C")
        col2.metric("💧 Humidity", f"{humidity} %")
        col3.metric("🌧 Rainfall", f"{rainfall} mm")
        col4.metric("🌱 Soil Moisture", f"{round(soil_moisture,1)}")

        # =========================
        # RISK STATUS PANEL
        # =========================
        st.subheader("🚨 National Risk Status")

        if drought.startswith("🔴"):
            st.error(f"{location}: Severe drought detected")

        if pests.startswith("🔴"):
            st.warning(f"{location}: Pest outbreak risk")

        if disease.startswith("🔴"):
            st.warning(f"{location}: Disease risk detected")

        st.write("🌵 Drought:", drought)
        st.write("🐛 Pests:", pests)
        st.write("🍄 Disease:", disease)

        # =========================
        # MINISTRY DECISION PANEL
        # =========================
        st.subheader("📌 Ministry Advisory Summary")

        if drought.startswith("🔴"):
            st.error("⚠️ ACTION: Immediate irrigation + drought response activation")

        elif pests.startswith("🟠"):
            st.warning("⚠️ ACTION: Pest surveillance recommended")

        elif disease.startswith("🟠"):
            st.warning("⚠️ ACTION: Preventive disease control needed")

        else:
            st.success("✅ CONDITIONS STABLE ACROSS MONITORED REGION")

        # =========================
        # FORECAST
        # =========================
        forecast_data = get_forecast(location)

        st.subheader("📊 Future Climate Outlook")

        temps, humidity_list, rain_list = [], [], []

        if "list" in forecast_data:
            for item in forecast_data["list"]:
                temps.append(item["main"]["temp"])
                humidity_list.append(item["main"]["humidity"])
                rain_list.append(item.get("rain", {}).get("3h", 0))

            avg_temp = sum(temps) / len(temps)
            avg_humidity = sum(humidity_list) / len(humidity_list)
            total_rain = sum(rain_list)

            trend_temp = avg_temp + (future_days * 0.2)
            trend_humidity = avg_humidity
            trend_rain = total_rain * (future_days / 5)

            st.write(f"🌡 Projected Temp: {round(trend_temp,1)} °C")
            st.write(f"💧 Projected Humidity: {round(trend_humidity,1)} %")
            st.write(f"🌧 Projected Rainfall: {round(trend_rain,1)} mm")

        # =========================
        # PAST TREND
        # =========================
        st.subheader("📊 National Climate Trend Monitoring")

        if os.path.exists("climate_history.csv"):
            df = pd.read_csv("climate_history.csv")
            df_filtered = df[df["location"] == location]
            df_filtered = df_filtered.tail(days_past)

            st.line_chart(df_filtered[["temp", "humidity", "soil_moisture"]])
        else:
            st.info("No historical data yet.")
