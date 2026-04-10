import streamlit as st
import requests
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# =========================
# AUTO REFRESH (10 minutes)
# =========================
st_autorefresh(interval=600000, key="refresh")

st.title("🌍 Mozambique Climate Intelligence System")

# =========================
# API KEY
# =========================
API_KEY = "257f8a9b51420c40a035a9ec83580ed9"

# =========================
# REGIONS
# =========================
locations = ["Maputo", "Beira", "Nampula", "Tete", "Inhambane", "Quelimane"]

# =========================
# TIME
# =========================
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.success(f"Last Updated: {now}")

# =========================
# LOOP THROUGH REGIONS
# =========================
for location in locations:

    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={API_KEY}&units=metric"
    data = requests.get(url).json()

    if "main" not in data:
        st.error(f"⚠️ Failed to load data for {location}")
        continue

    # =========================
    # WEATHER DATA
    # =========================
    temp = data["main"]["temp"]
    humidity = data["main"]["humidity"]
    rainfall = data.get("rain", {}).get("1h", 0)

    # =========================
    # SOIL MOISTURE MODEL (ESTIMATED)
    # =========================
    soil_moisture = max(0, min(100, (humidity * 0.6) - (temp * 0.5) + 40))

    # =========================
    # RISK MODELS
    # =========================
    drought_score = (temp * 0.6) - (rainfall * 5) + (100 - humidity) * 0.3
    pest_score = (temp * 0.5) + (humidity * 0.5)
    disease_score = humidity + (rainfall * 10)

    # =========================
    # DROUGHT RISK
    # =========================
    if drought_score > 70:
        drought = "🔴 SEVERE DROUGHT"
    elif drought_score > 40:
        drought = "🟠 WARNING"
    else:
        drought = "🟢 SAFE"

    # =========================
    # PEST RISK
    # =========================
    if pest_score > 85:
        pests = "🔴 HIGH RISK"
    elif pest_score > 65:
        pests = "🟠 MODERATE RISK"
    else:
        pests = "🟢 LOW RISK"

    # =========================
    # DISEASE RISK
    # =========================
    if disease_score > 120:
        disease = "🔴 HIGH RISK"
    elif disease_score > 90:
        disease = "🟠 MODERATE RISK"
    else:
        disease = "🟢 LOW RISK"

    # =========================
    # OUTPUT
    # =========================
    st.divider()
    st.subheader(f"📍 {location}")

    st.metric("🌡 Temperature (°C)", temp)
    st.metric("💧 Humidity (%)", humidity)
    st.metric("🌧 Rainfall (mm)", rainfall)
    st.metric("🌱 Soil Moisture (Model)", round(soil_moisture, 1))

    st.write("🌵 Drought:", drought)
    st.write("🐛 Pests:", pests)
    st.write("🍄 Disease:", disease)

    # =========================
    # FARMER ADVICE
    # =========================
    st.subheader("📢 Farmer Advisory")

    if drought.startswith("🔴"):
        st.warning(f"{location}: Irrigation urgently required. Water stress detected.")
    elif drought.startswith("🟠"):
        st.info(f"{location}: Monitor soil moisture closely.")

    if pests.startswith("🔴"):
        st.warning(f"{location}: High pest risk. Apply control measures.")
    elif pests.startswith("🟠"):
        st.info(f"{location}: Moderate pest activity expected.")

    if disease.startswith("🔴"):
        st.warning(f"{location}: High disease risk. Improve drainage and spraying.")
    elif disease.startswith("🟠"):
        st.info(f"{location}: Moderate disease risk conditions.")