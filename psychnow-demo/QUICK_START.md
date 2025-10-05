# ⚡ QUICK START - Get Demo Live in 2 Hours

Follow these steps **in order**. Don't skip ahead!

## ✅ STEP 1: Install Dependencies (5 min)

```powershell
# Navigate to demo folder
cd "C:\Users\gbtol\PsychNow\psychnow-demo"

# Install all dependencies
npm install
```

Wait for install to complete (~2-3 minutes).

---

## ✅ STEP 2: Test Locally (10 min)

```powershell
# Create local environment file
cp .env.example .env.local

# The default should work (backend at localhost:8000)
```

**In one terminal - Start Backend:**
```powershell
cd "C:\Users\gbtol\PsychNow\backend"
.\venv\Scripts\Activate.ps1
python main.py
```

**In another terminal - Start Frontend:**
```powershell
cd "C:\Users\gbtol\PsychNow\psychnow-demo"
npm run dev
```

Visit http://localhost:3001

Test:
1. Click "Start Demo Assessment"
2. Type a message
3. Verify Ava responds
4. **If it works, you're ready to deploy!**

Press `Ctrl+C` to stop both servers.

---

## ✅ STEP 3: Deploy Backend to Render (45 min)

### 3A: Push to GitHub (if not already)

```powershell
cd "C:\Users\gbtol\PsychNow"

# Add backend to git
git add backend/
git add backend/render.yaml
git commit -m "Add backend for Render deployment"
git push
```

### 3B: Deploy on Render.com

1. Go to https://render.com
2. Sign up with GitHub
3. Click "New +" → "Web Service"
4. Connect your repository
5. Settings:
   - **Root Directory**: `backend`
   - **Build**: `pip install -r requirements.txt`
   - **Start**: `alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free

6. Add environment variables:
   ```
   OPENAI_API_KEY=sk-... (get from your backend/.env file)
   SECRET_KEY=generate_new_one (run: python -c "import secrets; print(secrets.token_urlsafe(32))")
   ALLOWED_ORIGINS=* (will update after frontend deploy)
   DATABASE_URL=will_auto_populate
   ENVIRONMENT=production
   DEBUG=false
   OPENAI_MODEL=gpt-4o-mini
   ```

7. Click "Create Web Service"
8. Wait 5-10 minutes
9. **Your backend URL**: `https://YOUR-SERVICE-NAME.onrender.com`
10. Test: Visit `https://YOUR-SERVICE-NAME.onrender.com/health`

---

## ✅ STEP 4: Deploy Frontend to Firebase (30 min)

### 4A: Install Firebase CLI

```powershell
npm install -g firebase-tools
firebase login
```

This opens your browser - login with Google.

### 4B: Create Firebase Project

1. Visit https://console.firebase.google.com
2. Click "Add Project"
3. Name: `psychnow-demo`
4. Disable Analytics
5. Click "Create Project"

### 4C: Initialize Firebase

```powershell
cd "C:\Users\gbtol\PsychNow\psychnow-demo"

firebase init hosting
```

When asked:
- **Project**: Select the one you just created
- **Public directory**: `build`
- **Single-page app**: `Yes`
- **Overwrite**: `No`

### 4D: Configure Production Backend URL

```powershell
# Create production env file
echo VITE_API_BASE_URL=https://YOUR-SERVICE-NAME.onrender.com > .env.production
```

**⚠️ REPLACE `YOUR-SERVICE-NAME` with YOUR actual Render URL!**

### 4E: Build and Deploy

```powershell
npm run build
firebase deploy --only hosting
```

Wait 2-3 minutes...

**🎉 You'll get your live URL**: `https://psychnow-demo.web.app`

---

## ✅ STEP 5: Update Backend CORS (5 min)

1. Go back to Render.com dashboard
2. Select your web service
3. Environment tab
4. Edit `ALLOWED_ORIGINS`:
   ```
   https://psychnow-demo.web.app,https://psychnow-demo.firebaseapp.com
   ```
5. Save (auto-redeploys in ~2 min)

---

## ✅ STEP 6: Test Production (15 min)

Visit your demo: `https://psychnow-demo.web.app`

**Complete Test:**
1. ✅ Landing page loads
2. ✅ Click "Start Demo Assessment"
3. ✅ Ava greets you
4. ✅ Send a message
5. ✅ Ava responds
6. ✅ Continue conversation
7. ✅ Complete assessment (or type `:finish`)
8. ✅ PDF generates
9. ✅ Download PDF
10. ✅ Test on phone

**If all works → You're READY!**

---

## ✅ STEP 7: Send to Clinicians (30 min)

### Prepare Email

1. Open `CLINICIAN_EMAIL_TEMPLATE.md`
2. Replace `[YOUR-DEMO-URL]` with your actual URL
3. Add your contact info
4. Customize for each clinician

### Create Tracking Sheet

Google Sheets with columns:
- Clinician Name
- Email
- Sent Date
- Completed?
- Feedback Date
- Rating
- Key Notes

### Optional: Google Form

Create at forms.google.com:
- Name and specialty
- Conversation flow rating (1-5)
- Report quality rating (1-5)
- What you liked
- What concerns you have
- Would you use this? (Yes/No/Maybe)
- Comments

### Send Emails

**Best time**: 8-9 AM on a weekday

**Include**:
- Demo URL
- Time estimate (15-20 min)
- What you're looking for
- Deadline (if any)
- Feedback form link

---

## 🎯 YOUR CHECKLIST

Before sending to clinicians:

- [ ] Backend deployed and responding at `/health`
- [ ] Frontend deployed and accessible
- [ ] Can complete full assessment
- [ ] PDF downloads successfully
- [ ] Tested on mobile device
- [ ] CORS configured correctly
- [ ] Email template personalized
- [ ] Tracking system set up
- [ ] Contact info is correct

---

## 🆘 HELP!

### Backend won't deploy
- Check Render logs
- Verify environment variables
- Make sure `backend` is root directory

### Frontend shows "Can't connect"
- Check browser console (F12)
- Verify `.env.production` has correct backend URL
- Check CORS in Render
- Wait 30 seconds (free tier cold start)

### PDF not generating
- Check OpenAI API key in Render
- Check OpenAI account has credits
- View Render logs for errors

### Still stuck?
- Check `DEPLOYMENT_GUIDE.md` for detailed troubleshooting
- Review Render logs
- Check browser console for errors

---

## 🚀 TIMELINE SUMMARY

| Step | Time | What |
|------|------|------|
| 1 | 5 min | Install dependencies |
| 2 | 10 min | Test locally |
| 3 | 45 min | Deploy backend |
| 4 | 30 min | Deploy frontend |
| 5 | 5 min | Configure CORS |
| 6 | 15 min | Test production |
| 7 | 30 min | Email preparation |
| **TOTAL** | **~2.5 hours** | **Demo is LIVE!** |

---

## 🎉 NEXT STEPS

Once emails are sent:

1. **Monitor**: Check Render logs for usage
2. **Track**: Update your spreadsheet as feedback comes in
3. **Follow up**: Send reminder after 3 days
4. **Analyze**: Compile feedback for improvements
5. **Iterate**: Make changes based on clinical input

Good luck! 🚀

