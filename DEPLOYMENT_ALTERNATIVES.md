# 🚀 PsychNow Demo - Deployment Alternatives

## ⚠️ **Firebase Permission Issue**

The automated Firebase deployment encountered permission issues. Here are alternative deployment options:

---

## 🎯 **OPTION 1: Manual Firebase Deployment (Recommended)**

### **Step 1: Create Firebase Project Manually**
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Create a project"
3. Project name: `psychnow-demo`
4. Enable Google Analytics: No (for demo)
5. Click "Create project"

### **Step 2: Enable Hosting**
1. In Firebase Console, click "Hosting" in left sidebar
2. Click "Get started"
3. Follow the setup wizard
4. Note the project ID (e.g., `psychnow-demo-abc123`)

### **Step 3: Update Configuration**
Update `.firebaserc` with your actual project ID:
```json
{
  "projects": {
    "default": "your-actual-project-id"
  }
}
```

### **Step 4: Deploy**
```bash
cd "C:\Users\gbtol\PsychNow\psychnow-demo"
firebase login
npm run build
firebase deploy --only hosting
```

---

## 🎯 **OPTION 2: Netlify Deployment (Alternative)**

### **Step 1: Build and Deploy**
```bash
cd "C:\Users\gbtol\PsychNow\psychnow-demo"
npm run build
```

### **Step 2: Deploy to Netlify**
1. Go to [Netlify](https://netlify.com)
2. Drag and drop the `build` folder
3. Your app will be live at: `https://random-name.netlify.app`

### **Step 3: Configure Environment Variables**
In Netlify dashboard:
- Site settings → Environment variables
- Add: `VITE_API_BASE_URL=https://psychnow-api.onrender.com`

---

## 🎯 **OPTION 3: Vercel Deployment (Alternative)**

### **Step 1: Install Vercel CLI**
```bash
npm install -g vercel
```

### **Step 2: Deploy**
```bash
cd "C:\Users\gbtol\PsychNow\psychnow-demo"
vercel --prod
```

### **Step 3: Configure Environment Variables**
In Vercel dashboard:
- Project settings → Environment variables
- Add: `VITE_API_BASE_URL=https://psychnow-api.onrender.com`

---

## 🎯 **OPTION 4: GitHub Pages (Free)**

### **Step 1: Create GitHub Repository**
1. Create repository: `psychnow-demo`
2. Upload frontend code

### **Step 2: Enable GitHub Pages**
1. Repository settings → Pages
2. Source: Deploy from branch
3. Branch: main
4. Folder: / (root)

### **Step 3: Deploy**
```bash
cd "C:\Users\gbtol\PsychNow\psychnow-demo"
npm run build
# Upload build contents to GitHub
```

---

## 🚀 **BACKEND DEPLOYMENT (Render.com)**

The backend deployment to Render.com should work fine. Here's the process:

### **Step 1: Create GitHub Repository**
1. Create repository: `psychnow-backend`
2. Upload backend code (including `render.yaml`)

### **Step 2: Deploy to Render**
1. Go to [render.com](https://render.com)
2. Connect GitHub repository
3. Render will auto-detect `render.yaml`
4. Set environment variables:
   ```
   OPENAI_API_KEY=your-openai-key
   ALLOWED_ORIGINS=https://your-frontend-url.com
   SMTP_USER=psychiatrynowai@gmail.com
   SMTP_PASSWORD=your-gmail-app-password
   ```

---

## 🎯 **RECOMMENDED APPROACH**

**For fastest deployment:**

1. **Frontend**: Use **Netlify** (drag & drop deployment)
2. **Backend**: Use **Render.com** (GitHub integration)

**Timeline**: 15-30 minutes total

---

## 🌐 **PRODUCTION URLs**

After deployment:
- **Frontend**: `https://your-app.netlify.app` (or chosen platform)
- **Backend**: `https://psychnow-api.onrender.com`
- **API Docs**: `https://psychnow-api.onrender.com/api/docs`

---

## 🧪 **TESTING**

Once deployed:
1. Visit frontend URL
2. Test "Start Demo" button
3. Verify API connection works
4. Test chat functionality
5. Generate PDF reports

---

## 📞 **SUPPORT**

If you need help with any of these options, let me know which one you'd prefer and I'll provide detailed step-by-step instructions!
