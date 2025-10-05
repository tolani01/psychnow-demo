# 🚀 Complete Deployment Guide - PsychNow Demo

This guide will get your demo live and accessible to clinicians **TODAY**.

## ⏱️ Total Time Estimate: 2-3 Hours

- Backend Deployment: 45-60 min
- Frontend Deployment: 30-45 min  
- Testing: 30 min
- Email Preparation: 15 min

---

## PART 1: BACKEND DEPLOYMENT (Render.com)

### Step 1: Prepare Backend for Deployment (5 min)

1. **Ensure .gitignore is correct** (backend directory):
   ```bash
   cd backend
   cat .gitignore
   ```

   Should include:
   ```
   __pycache__/
   *.py[cod]
   venv/
   .env
   *.db
   uploads/
   pdfs/
   ```

2. **Test locally one more time**:
   ```powershell
   .\venv\Scripts\Activate.ps1
   python main.py
   ```
   
   Visit http://localhost:8000/health - should return OK

### Step 2: Push Backend to GitHub (10 min)

If not already in GitHub:

```bash
cd C:\Users\gbtol\PsychNow

# Initialize if needed
git init
git add backend/
git commit -m "Add backend for deployment"

# Create repository on GitHub (via web interface)
# Then:
git remote add origin https://github.com/your-username/psychnow.git
git branch -M main
git push -u origin main
```

### Step 3: Deploy to Render.com (30 min)

1. **Sign up at Render.com**
   - Visit https://render.com
   - Click "Get Started for Free"
   - Sign up with GitHub account

2. **Create PostgreSQL Database First**
   - Dashboard → New → PostgreSQL
   - **Name**: `psychnow-db`
   - **Database**: `psychnow`
   - **User**: `psychnow`
   - **Region**: Ohio (US East)
   - **Plan**: Free
   - Click "Create Database"
   - **⚠️ IMPORTANT**: Copy the "Internal Database URL" - you'll need it

3. **Create Web Service**
   - Dashboard → New → Web Service
   - Connect your GitHub repository
   - Select the repository
   - **Root Directory**: `backend` (IMPORTANT!)
   - **Name**: `psychnow-api`
   - **Region**: Ohio (US East)
   - **Branch**: `main`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free

4. **Add Environment Variables**
   
   In the web service settings, add these:

   | Variable | Value | Source |
   |----------|-------|--------|
   | `PYTHON_VERSION` | `3.11.0` | Type manually |
   | `ENVIRONMENT` | `production` | Type manually |
   | `DEBUG` | `false` | Type manually |
   | `DATABASE_URL` | [paste from Step 2] | From PostgreSQL |
   | `OPENAI_API_KEY` | `sk-...` | **From your .env file** |
   | `SECRET_KEY` | [generate below] | Generate new |
   | `ALGORITHM` | `HS256` | Type manually |
   | `OPENAI_MODEL` | `gpt-4o-mini` | Type manually |
   | `ALLOWED_ORIGINS` | `*` | Temporary - will update |

   **Generate SECRET_KEY:**
   ```powershell
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

5. **Deploy**
   - Click "Create Web Service"
   - Wait 5-10 minutes for first deploy
   - Watch the logs for any errors

6. **Verify Backend is Live**
   
   Your backend URL will be: `https://psychnow-api.onrender.com`
   
   Test it:
   ```
   https://psychnow-api.onrender.com/health
   ```
   
   Should return: `{"status":"healthy"}`

   Also check API docs:
   ```
   https://psychnow-api.onrender.com/api/docs
   ```

---

## PART 2: FRONTEND DEPLOYMENT (Firebase)

### Step 1: Install Firebase CLI (5 min)

```powershell
# Install Firebase Tools globally
npm install -g firebase-tools

# Login to Firebase
firebase login
```

This will open your browser - login with your Google account.

### Step 2: Create Firebase Project (5 min)

1. **Via Firebase Console:**
   - Visit https://console.firebase.google.com
   - Click "Add Project"
   - **Project Name**: `psychnow-demo` (or your choice)
   - Disable Google Analytics (not needed for demo)
   - Click "Create Project"

2. **Note your Project ID** (shown in settings)

### Step 3: Configure Demo for Deployment (10 min)

```powershell
cd C:\Users\gbtol\PsychNow\psychnow-demo

# Install dependencies
npm install

# Initialize Firebase
firebase init hosting
```

When prompted:
- **Select project**: Choose the project you just created
- **Public directory**: Enter `build`
- **Single-page app**: `Yes`
- **Set up automatic builds**: `No`
- **Overwrite build/index.html**: `No`

### Step 4: Configure Production Environment (5 min)

Create `.env.production`:

```powershell
# Create production environment file
echo VITE_API_BASE_URL=https://psychnow-api.onrender.com > .env.production
```

**⚠️ Replace `psychnow-api` with YOUR actual Render service name!**

### Step 5: Build and Deploy (10 min)

```powershell
# Build the production app
npm run build

# Deploy to Firebase
firebase deploy --only hosting
```

Wait 2-3 minutes...

You'll get output like:
```
✔  Deploy complete!

Project Console: https://console.firebase.google.com/project/psychnow-demo
Hosting URL: https://psychnow-demo.web.app
```

**🎉 Your demo is now LIVE!**

### Step 6: Update Backend CORS (5 min)

Now that you have your frontend URL, update backend:

1. Go to Render.com dashboard
2. Select your `psychnow-api` service
3. Environment tab
4. Edit `ALLOWED_ORIGINS`:
   ```
   https://psychnow-demo.web.app,https://psychnow-demo.firebaseapp.com
   ```
5. Save and wait for automatic redeploy (~2 min)

---

## PART 3: TESTING (30 min)

### Test Checklist

Visit your demo URL: `https://your-project.web.app`

- [ ] Landing page loads correctly
- [ ] Click "Start Demo Assessment"  
- [ ] Assessment starts (Ava greets you)
- [ ] Type a response and send
- [ ] Ava responds (streaming works)
- [ ] Continue conversation for 2-3 exchanges
- [ ] Test option buttons if presented
- [ ] Complete assessment (or type `:finish` to skip)
- [ ] PDF generates successfully
- [ ] Download PDF and verify it opens
- [ ] Test on mobile device (use phone browser)

### If Issues:

**Backend not responding:**
- Check Render logs: Dashboard → psychnow-api → Logs
- Verify environment variables are set
- Check that DATABASE_URL is correct

**CORS errors:**
- Check browser console (F12)
- Verify ALLOWED_ORIGINS in Render
- Make sure to include both .web.app and .firebaseapp.com

**Frontend not loading:**
- Check browser console for errors
- Verify build succeeded: `ls build/`
- Redeploy: `npm run build && firebase deploy --only hosting`

**Cold start delays:**
- Free tier Render services sleep after inactivity
- First request after sleep takes 30-60 seconds
- This is normal for free tier

---

## PART 4: PREPARE CLINICIAN EMAIL (15 min)

### Step 1: Customize Email Template

1. Open `CLINICIAN_EMAIL_TEMPLATE.md`
2. Replace `[YOUR-DEMO-URL.web.app]` with your actual URL
3. Add your contact information
4. Personalize for each clinician

### Step 2: Create Spreadsheet for Tracking

Create a Google Sheet:

| Clinician Name | Specialty | Email | Sent Date | Completed | Feedback Date | Rating | Notes |
|----------------|-----------|-------|-----------|-----------|--------------|--------|-------|
| Dr. Smith | Psychiatrist | ... | 10/4 | ✓ | 10/5 | 4/5 | Loved flow |
| ... | ... | ... | ... | ... | ... | ... | ... |

### Step 3: Optional - Create Google Form

Quick feedback form:

1. Go to forms.google.com
2. Create new form: "PsychNow Demo Feedback"
3. Add questions:
   - Your name and specialty
   - How would you rate the conversation flow? (1-5)
   - How would you rate the report quality? (1-5)
   - What did you like most?
   - What concerns do you have?
   - What's missing?
   - Would you use this in practice? (Yes/No/Maybe)
   - Additional comments

4. Get shareable link
5. Add to email template

---

## PART 5: SEND TO CLINICIANS

### Timing Strategy

**Option A: Send All at Once** (Tomorrow morning)
- 8-9 AM on a weekday
- Include deadline: "Feedback by Friday helpful"

**Option B: Staggered**
- Send to 3-4 clinicians first
- Get initial feedback
- Make quick fixes
- Send to remaining 6-7

**Recommended: Option A** (you need feedback quickly)

### Email Tips

1. **Subject Line Matters**
   - ✅ "Quick favor: 15 min demo feedback needed"
   - ✅ "PsychNow Demo - Your clinical input needed"
   - ❌ "Check out my new app"

2. **Keep It Short**
   - Busy clinicians skim emails
   - Put the link early
   - Be specific about time (15-20 min)

3. **Follow-Up Plan**
   - Wait 3 days
   - Send friendly reminder
   - Offer to schedule a call

---

## 🎯 QUICK REFERENCE

### Your URLs

**Demo Frontend:**  
`https://[your-project-id].web.app`

**Backend API:**  
`https://psychnow-api.onrender.com`

**API Docs:**  
`https://psychnow-api.onrender.com/api/docs`

**Firebase Console:**  
`https://console.firebase.google.com/project/[your-project-id]`

**Render Dashboard:**  
`https://dashboard.render.com`

### Quick Commands

**Redeploy Frontend:**
```powershell
cd C:\Users\gbtol\PsychNow\psychnow-demo
npm run build
firebase deploy --only hosting
```

**View Backend Logs:**
```
Render Dashboard → psychnow-api → Logs
```

**Update Backend Env Var:**
```
Render Dashboard → psychnow-api → Environment → Edit
```

---

## 🐛 Common Issues & Fixes

### "Backend is taking forever to respond"
- Free tier has cold starts (30-60 sec first request)
- Keep it warm: https://cron-job.org/en/ (ping every 10 min)
- Or upgrade to $7/month Render plan

### "CORS policy error"
- Check ALLOWED_ORIGINS includes your exact frontend URL
- Include both .web.app AND .firebaseapp.com
- Wait 2 min for Render to redeploy after changing

### "PDF not generating"
- Check OpenAI API key is correct
- Check OpenAI account has credits
- Check Render logs for errors

### "Can't deploy to Firebase"
- Run `firebase login` again
- Check you selected correct project: `firebase use [project-id]`
- Make sure `build` directory exists: `npm run build`

---

## 💰 Cost Monitoring

**Monitor OpenAI Usage:**
- https://platform.openai.com/usage
- Set billing alert at $20

**Expected Costs:**
- 10 assessments: ~$10-15
- Backend/DB: $0 (free tier)
- Firebase: $0 (free tier)

---

## ✅ Pre-Launch Checklist

Before sending to clinicians:

- [ ] Demo loads at your-url.web.app
- [ ] Can complete full assessment
- [ ] PDF generates and downloads
- [ ] Tested on mobile
- [ ] Backend CORS configured
- [ ] Email template customized
- [ ] Tracking spreadsheet ready
- [ ] Contact info in demo is correct
- [ ] Optional: Google Form created

---

## 🎉 YOU'RE READY!

Your demo is live and ready for clinician validation. Good luck! 🚀

