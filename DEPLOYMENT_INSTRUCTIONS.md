# 🚀 PsychNow Deployment Instructions

## Backend Deployment to Render.com

### Step 1: Create GitHub Repository
1. Go to GitHub and create a new repository named `psychnow-demo`
2. Upload the backend code to the repository
3. Make sure the `render.yaml` file is in the root of the backend directory

### Step 2: Deploy to Render
1. Go to [render.com](https://render.com) and sign up/login
2. Click "New +" → "Blueprint"
3. Connect your GitHub repository
4. Render will automatically detect the `render.yaml` configuration
5. Set the following environment variables in Render dashboard:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `ALLOWED_ORIGINS`: `https://psychnow-demo.web.app,https://psychnow-demo.firebaseapp.com`
   - `SMTP_USER`: `psychiatrynowai@gmail.com`
   - `SMTP_PASSWORD`: Your Gmail app password
   - `ADMIN_EMAIL`: `gb.tolani@gmail.com`

### Step 3: Deploy Frontend to Firebase
1. Install Firebase CLI: `npm install -g firebase-tools`
2. Login to Firebase: `firebase login`
3. Initialize project: `firebase init hosting`
4. Set project ID: `psychnow-demo`
5. Set public directory: `build`
6. Configure as SPA: Yes
7. Build and deploy: `npm run build && firebase deploy`

## Production URLs
- **Frontend**: https://psychnow-demo.web.app
- **Backend**: https://psychnow-api.onrender.com
- **API Docs**: https://psychnow-api.onrender.com/api/docs

## Environment Variables Needed

### Backend (Render)
```
OPENAI_API_KEY=sk-proj-...
ALLOWED_ORIGINS=https://psychnow-demo.web.app,https://psychnow-demo.firebaseapp.com
SMTP_USER=psychiatrynowai@gmail.com
SMTP_PASSWORD=your-gmail-app-password
ADMIN_EMAIL=gb.tolani@gmail.com
```

### Frontend (Firebase)
```
VITE_API_BASE_URL=https://psychnow-api.onrender.com
```

## Testing Checklist
- [ ] Backend health check: https://psychnow-api.onrender.com/health
- [ ] Frontend loads: https://psychnow-demo.web.app
- [ ] API connection works
- [ ] Chat functionality operational
- [ ] PDF generation working
- [ ] Email notifications working
