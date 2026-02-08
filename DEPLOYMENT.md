# 🚀 Deployment Guide

This project is set up to be deployed for free using **Render** (Backend) and **Vercel** (Frontend).

## 1. Deploy Backend (Render)

1. Create a [Render account](https://render.com/).
2. Click **New +** -> **Web Service**.
3. Connect your GitHub repository.
4. Select the repository `ElectronicsHotDeals`.
5. Configure the service:
   - **Name:** `electronics-hot-deals-backend`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
6. Click **Create Web Service**.
7. Wait for deployment to finish. Copy your backend URL (e.g., `https://electronics-hot-deals-backend.onrender.com`).

## 2. Deploy Frontend (Vercel)

1. Create a [Vercel account](https://vercel.com/).
2. Click **Add New...** -> **Project**.
3. Import your GitHub repository `ElectronicsHotDeals`.
4. Configure the project:
   - **Framework Preset:** `Vite`
   - **Root Directory:** `frontend` (Important! Click Edit)
5. **Environment Variables:**
   - Add a new variable: `VITE_API_URL`
   - Value: Your Render Backend URL (e.g., `https://electronics-hot-deals-backend.onrender.com`)
6. Click **Deploy**.

## 3. Post-Deployment Setup

1. **Update Backend CORS (Optional but Recommended):**
   - Go to your Render dashboard -> Environment Variables.
   - Add `ALLOWED_ORIGINS` with your Vercel URL (e.g., `https://electronics-hot-deals.vercel.app`).
   - (Note: The current configuration allows all origins `*` for simplicity).

2. **Verify Integration:**
   - Open your Vercel URL.
   - Check if products load correctly from the backend.

## ⚠️ Free Tier Limitations

- **Render Free Tier:** Spins down after inactivity. The first request might take 30-50 seconds to wake up.
- **Ephemeral Storage:** Scraped data updates will be lost when the Render instance restarts. Only the initial `jumia_products_clean.csv` from the repo will persist. To fix this, you would need external storage (e.g., AWS S3, Google Cloud Storage) or a database (PostgreSQL provided by Render).

## 🐋 Alternative: Docker Deployment (Self-Hosting)

You can also deploy the entire stack using Docker if you have a VPS (e.g., DigitalOcean, Hetzner).

```bash
# Build and run
docker-compose up --build -d
```
