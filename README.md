# 🌍 **BreathSafe**
### *Breathing Smarter, Living Better — Powered by NASA TEMPO Data*  

[🔗 **Live Demo**](https://www.tempo11.earth/)  

---

## 🫧 Introduction  

Every breath we take tells a story about our planet.  
For millions of people around the world, that story has become one of **silent danger** — the air they breathe is slowly harming their health.  

According to the **World Health Organization (WHO)**, nearly **99% of the global population** is exposed to air that exceeds safe pollution levels.  
Yet, despite the urgency, **real-time and accessible air quality information** is still lacking for most communities.  

That’s where **BreathSafe** comes in. 🌱  

---

## 💡 Why We Make the Difference  

**BreathSafe**, developed by **Team TEMPO 11**, transforms **NASA’s atmospheric science** into an intelligent, user-centered health protection system.  

By integrating **real-time data** from the **NASA TEMPO (Tropospheric Emissions: Monitoring of Pollution)** mission with **ground-based sensors**, **public health datasets**, and **AI analytics**, we help people understand, anticipate, and act upon air quality conditions that affect their lives.  

---

## 🖥️ Main Features

### 🌎 **Home Screen — Where Data Meets Action**
A dynamic interface combining real-time air quality data with personalized insights.  
![Home Screen](upload_image.22:50:22.998039)

### 🫧 **Air Quality View**
Visualizes pollutants such as **PM2.5**, **NO₂**, and **O₃** through an intuitive map, combining **NASA satellite** and **local ground sensor** data.  
![Air Quality View](upload_image.20:43:37.814369)

### 📍 **Personalized Location**
Uses **real-time geolocation** to display precise air quality information for each user’s exact position.  
![Personalized Location](upload_image.20:45:24.565860)

### 🔔 **Subscription for Alerts**
Sends **instant notifications** when pollution levels change — allowing users to plan outdoor activities safely.  
![Alerts](upload_image.22:55:28.339432)

### 🩺 **Recommendations Based on Profile**
Delivers **personalized health guidance** for groups such as children, elderly, pregnant users, and those with respiratory conditions.  
![Recommendations](upload_image.22:53:10.867016)

### 💡 **Tips**
Provides daily eco-health suggestions and protective habits based on real-time air quality.  
![Tips](upload_image.22:57:08.222013)

---

## 🛰️ Technical Approach

### 1. **Data Sources & APIs**
- **NASA TEMPO:** high-resolution air pollution data *(O₃, NO₂, CO, CH₂O, PM, Aerosol Index)*  
- **Meteomatics API:** real-time weather parameters *(temperature, humidity, wind speed, radiation, precipitation)*  
- **IPCC CIESIN SRES Dataset:** historical and projected emissions data  

### 2. **Data Processing & Integration**
- Spatial harmonization with **WGS84 / EPSG:4326**  
- **Bilinear interpolation** & **nearest neighbor sampling**  
- Data normalization with **quality flag validation**  
- Missing data recovery using **exponential decay** and **median neighborhood fill**  

### 3. **Analytical Model**
- **Mamdani-type Fuzzy Logic System** with 100+ expert rules  
- Fuzzy sets: *Low → Moderate → High → Extreme*  
- **Triangular & Gaussian membership functions**  
- **Centroid defuzzification** producing final air-quality class *(Good → Hazardous)*  

### 4. **AI & Automation Layer**
- **Qwen2.5-1.5B Transformer (Small Language Model)**  
- Generates **bilingual (EN/PT)** explanations and recommendations  
- **Low-latency reasoning (<800 ms)** for real-time insights  
- Automates environmental reports and summary generation  

### 5. **System Architecture**
- **Progressive Web App (PWA)** collecting geolocation data  
- **Serverless backend** with autoscaling & sub-second response  
- **REST API** endpoints for inference and explainability  
- **Secure infrastructure** using key vaults, containers & OpenTelemetry  

### 6. **Calibration & Validation**
- Cross-validation using **AERONET** and **urban monitoring stations**  
- Metrics: *F1 (unhealthy+)*, *macro accuracy*, *weighted kappa*, *rank correlation*  
- **Bayesian optimization** to fine-tune fuzzy thresholds  

---

## ⚡ Capabilities  

✅ Integration of **NASA satellite**, **ground**, and **weather** data  
✅ **Near real-time monitoring** and forecasting  
✅ **Validated accuracy** across multiple data sources  
✅ **Historical trends** and seasonal visualizations  
✅ **Health-based alerts** and proactive recommendations  
✅ **User-tailored insights** by health and location profile  

---

## 🔭 Future Features  

🚀 **Digital Phenotypes** — analyze human and community responses to air conditions  
🤖 **Edge AI** — local, privacy-preserving, real-time analysis  
🎯 **Hyper-Personalization** — adapt to exposure, habits, and local environments  
🧩 **Causal AI Models** — move from correlation to cause-and-effect relationships  
💬 **Explainable AI (XAI)** — transparency in why alerts and predictions are made  
🌐 **System Integrations** — future partnerships with other mobile and IoT systems  

---

## 🧠 Use of Artificial Intelligence  

We applied AI throughout the project lifecycle:  

| Application | Tools |
|--------------|--------|
| **Code generation & system logic** | ChatGPT, Manus, Claude, Gemini |
| **Text & data interpretation** | Qwen2.5 |
| **Image & video generation** | Manus, Gemini, Google Labs Flow (VEO 3 Quality) |
| **Personalized communications** | OLLAMA / Qwen2.5 |

---

## 🌎 Data & Partners  

| Source | Type | Role |
|--------|------|------|
| **NASA TEMPO / EARTHDATA / AIR QUALITY** | Satellite | Atmospheric pollutants |
| **Meteomatics** | API | Weather data |
| **IPCC CIESIN SRES** | Dataset | Emission projections |
| **WHO / EPA / AirNow / NEJM / EHP / Springer** | Validation | Health and environmental research |
| **GitHub** | Platform | Repository & version control |

---

## 👩‍🚀 NASA Space Apps Challenge — Team TEMPO 11  

- **Project:** BreathSafe  
- **Theme:** *Data for Health & Environment*  
- **Mission:** Empower communities to understand and act upon air quality conditions through real-time NASA data and AI-driven insights.  

---

## 📫 Contact  

**Team TEMPO 11 — BreathSafe Project**  
🌐 [www.tempo11.earth](https://www.tempo11.earth)  
✉️ contact@tempo11.earth  

---

> *“We don’t just monitor the air. We make it understandable, actionable, and personal.”* 🌬️  

---

