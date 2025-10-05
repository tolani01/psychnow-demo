# 🚀 PsychNow Demo - Final Deployment Steps

## ✅ **DEPLOYMENT PREPARATION COMPLETE**

All code has been prepared and is ready for production deployment. Here are the final steps to get your app live:

---

## 🎯 **STEP-BY-STEP DEPLOYMENT**

### **PHASE 1: Backend Deployment (Render.com)**

#### **Step 1: Create GitHub Repository**
1. Go to [GitHub](https://github.com) and create a new repository
2. Name it: `psychnow-demo`
3. Upload the contents of the `backend/` folder to the repository
4. Make sure `render.yaml` is in the root directory

#### **Step 2: Deploy to Render**
1. Go to [render.com](https://render.com) and sign up/login
2. Click "New +" → "Blueprint"
3. Connect your GitHub repository
4. Render will automatically detect the `render.yaml` configuration
5. Click "Apply" to create the services

#### **Step 3: Configure Environment Variables**
In the Render dashboard, set these environment variables:

```
OPENAI_API_KEY=sk-proj-your-openai-api-key-here
ALLOWED_ORIGINS=https://psychnow-demo.web.app,https://psychnow-demo.firebaseapp.com
SMTP_USER=psychiatrynowai@gmail.com
SMTP_PASSWORD=your-gmail-app-password
```

**Note**: The database and other variables are automatically configured by `render.yaml`

---

### **PHASE 2: Frontend Deployment (Firebase)**

#### **Step 1: Authenticate Firebase**
Open PowerShell/Command Prompt and run:
```bash
cd "C:\Users\gbtol\PsychNow\psychnow-demo"
firebase login
```
Follow the browser authentication process.

#### **Step 2: Initialize Firebase Project**
```bash
firebase init hosting
```
- Select "Use an existing project"
- Choose project ID: `psychnow-demo` (or create new)
- Set public directory: `build`
- Configure as SPA: Yes
- Don't overwrite index.html: No

#### **Step 3: Deploy**
```bash
npm run build
firebase deploy --only hosting
```

**OR** use the provided script:
```bash
.\deploy.ps1
```

---

## 🌐 **PRODUCTION URLs**

After successful deployment:
- **Frontend**: `https://psychnow-demo.web.app`
- **Backend**: `https://psychnow-api.onrender.com`
- **API Documentation**: `https://psychnow-api.onrender.com/api/docs`

---

## 🧪 **TESTING CHECKLIST**

Once deployed, verify:

### **Backend Health**
- [ ] Visit: `https://psychnow-api.onrender.com/health`
- [ ] Should return: `{"status": "healthy", "app": "PsychNow", ...}`

### **Frontend**
- [ ] Visit: `https://psychnow-demo.web.app`
- [ ] Landing page loads correctly
- [ ] "Start Demo" button works

### **Integration**
- [ ] Start an assessment
- [ ] Chat with Ava works
- [ ] API calls succeed
- [ ] PDF generation works
- [ ] Email notifications sent

---

## 🔧 **TROUBLESHOOTING**

### **Backend Issues**
- Check Render logs for errors
- Verify environment variables are set
- Ensure database is connected

### **Frontend Issues**
- Check browser console for errors
- Verify API base URL is correct
- Check CORS settings

### **Integration Issues**
- Verify CORS allows your frontend domain
- Check API endpoints are accessible
- Test with browser developer tools

---

## 📞 **SUPPORT**

- **Admin Email**: `gb.tolani@gmail.com`
- **Technical Issues**: Check Render/Firebase logs
- **Documentation**: See other `.md` files in project

---

## 🎉 **SUCCESS!**

Once deployed and tested, your PsychNow demo will be ready for:
- ✅ Clinical validation by psychiatrists
- ✅ Professional presentation
- ✅ Feedback collection
- ✅ Integration discussions

**Estimated Time**: 30-60 minutes for complete deployment

**Timeline**: Ready for clinical testing within 2 hours! 🚀
