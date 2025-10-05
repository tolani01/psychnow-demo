# 🧠 PsychNow Demo - AI-Guided Psychiatric Assessment

This is a simplified demo version of PsychNow designed for clinical validation by psychiatrists and nurse practitioners.

## 🎯 Purpose

This demo focuses on the core assessment experience:
- **Conversational AI** that conducts psychiatric intake
- **Validated screening tools** (PHQ-9, GAD-7, C-SSRS, etc.)
- **Clinical report generation** with PDF download

## 🚀 Quick Start (Local Development)

### Prerequisites
- Node.js 18+ and npm
- Backend must be running (see backend setup)

### Installation

```bash
# Install dependencies
npm install

# Create environment file
cp .env.example .env.local

# Edit .env.local with your backend URL
# VITE_API_BASE_URL=http://127.0.0.1:8000

# Start development server
npm run dev
```

Visit http://localhost:3001

## 📦 Deployment to Firebase

### First-time Setup

```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login to Firebase
firebase login

# Initialize Firebase in this directory
firebase init hosting
```

When prompted:
- **Public directory**: `build`
- **Single-page app**: `Yes`
- **Overwite index.html**: `No`

### Deploy

```bash
# Build the app
npm run build

# Deploy to Firebase
firebase deploy --only hosting
```

Your demo will be live at: `https://your-project-id.web.app`

### Configure Production Backend

After deploying frontend, update backend CORS:

In Render.com dashboard, set environment variable:
```
ALLOWED_ORIGINS=https://your-project-id.web.app,https://your-project-id.firebaseapp.com
```

## 🔧 Backend Setup

The demo requires the PsychNow backend to be running.

### Option 1: Deploy to Render.com (Recommended for Demo)

1. **Push backend to GitHub** (if not already)

2. **Sign up at Render.com**
   - Visit https://render.com
   - Sign up with GitHub

3. **Create New Web Service**
   - Connect your GitHub repository
   - Select the `backend` folder
   - Use these settings:
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **Add Environment Variables** in Render dashboard:
   - `OPENAI_API_KEY` - your OpenAI key
   - `SECRET_KEY` - generate with: `openssl rand -hex 32`
   - `ALLOWED_ORIGINS` - will add after frontend deployment
   - `DATABASE_URL` - auto-populated by Render

5. **Create PostgreSQL Database**
   - Add PostgreSQL from Render dashboard
   - Connect to your web service

6. **Note your backend URL**: `https://psychnow-api.onrender.com`

7. **Update frontend .env.production**:
   ```
   VITE_API_BASE_URL=https://psychnow-api.onrender.com
   ```

### Option 2: Run Locally

```bash
cd ../backend
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # Mac/Linux

python main.py
```

Backend will run at http://localhost:8000

## 📊 Features

### Included
- ✅ AI-guided conversation (Ava)
- ✅ 30+ validated screening tools
- ✅ Real-time streaming responses
- ✅ PDF report generation
- ✅ Mobile responsive design
- ✅ Anonymous sessions (no login required)

### Removed from Full App
- ❌ Patient dashboard
- ❌ Provider portal
- ❌ Appointment scheduling
- ❌ Complex authentication
- ❌ Admin features

## 🧪 Testing

Test the complete flow:

1. Navigate to landing page
2. Click "Start Demo Assessment"
3. Complete assessment (15-20 min)
4. Verify PDF generation
5. Download and review PDF
6. Test on mobile device

## 📝 For Clinicians

This demo is designed for clinical validation. Please review:

1. **Conversation Quality**
   - Empathy and rapport building
   - Clinical appropriateness
   - Question flow and logic

2. **Assessment Completeness**
   - Screening tool administration
   - Safety assessment
   - Clinical history gathering

3. **Report Quality**
   - Structured clinical information
   - Scoring accuracy
   - Clinical utility

## 🐛 Troubleshooting

### "Failed to connect to server"
- Check that backend is running
- Verify `VITE_API_BASE_URL` in `.env.local`
- Check browser console for CORS errors

### "Backend cold start delay"
- Free tier Render services sleep after inactivity
- First request may take 30-60 seconds
- Subsequent requests are fast

### Build errors
```bash
# Clear node modules and reinstall
rm -rf node_modules package-lock.json
npm install
npm run build
```

## 💰 Cost Estimate

**For 10 Clinician Tests:**
- Firebase Hosting: Free (1GB storage, 10GB transfer)
- Render.com: Free (750 hours/month)
- PostgreSQL: Free (1GB storage)
- OpenAI API: ~$10-$20 (based on usage)

**Total: ~$10-$20**

## 📞 Support

For issues or questions:
- Check backend logs in Render dashboard
- Check browser console for frontend errors
- Review API documentation at `/api/docs`

## 🔐 Security Note

**This is a demo environment.** Do not enter real patient information.
All data is for clinical validation purposes only.

---

Built with React, TypeScript, Vite, and Tailwind CSS.
Backend: FastAPI + PostgreSQL + OpenAI GPT-4.

