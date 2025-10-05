# 📁 PsychNow Demo - Project Structure

## Overview

```
psychnow-demo/
├── 📄 Configuration Files
│   ├── package.json           ← Dependencies & scripts
│   ├── vite.config.ts         ← Build configuration
│   ├── tsconfig.json          ← TypeScript settings
│   ├── tailwind.config.js     ← Styling framework
│   ├── postcss.config.js      ← CSS processing
│   ├── firebase.json          ← Hosting configuration
│   ├── .firebaserc            ← Firebase project link
│   ├── .env.example           ← Environment template
│   └── .gitignore             ← Git ignore rules
│
├── 📄 Documentation
│   ├── README.md              ← Technical documentation
│   ├── QUICK_START.md         ← Fast deployment guide ⭐
│   ├── PROJECT_STRUCTURE.md   ← You are here
│   └── ...
│
├── 🎨 Source Code (src/)
│   ├── main.tsx               ← Application entry point
│   ├── App.tsx                ← Router & routes (3 routes)
│   ├── index.css              ← Global styles
│   │
│   ├── 🧩 components/
│   │   ├── DemoLanding.tsx           ← Landing page for clinicians
│   │   ├── PatientIntake.tsx         ← Assessment chatbox (Ava)
│   │   ├── AssessmentComplete.tsx    ← Success page
│   │   │
│   │   └── foundation/
│   │       ├── Button.tsx            ← Reusable button component
│   │       ├── Input.tsx             ← Reusable input component
│   │       └── ChatBubble.tsx        ← Chat message bubbles
│   │
│   └── 🛠️ lib/
│       └── utils.ts           ← Utility functions (cn)
│
├── 🌐 Public Assets
│   └── index.html             ← HTML template
│
└── 📦 Build Output (after npm run build)
    └── build/                 ← Production files for deployment
```

---

## 🎯 Key Files Explained

### Configuration

**package.json**
- Lists all dependencies (React, Router, Tailwind, etc.)
- Defines scripts: `dev`, `build`, `deploy`
- No need to modify

**firebase.json**
- Tells Firebase to serve `build/` folder
- Single-page app routing configured
- Caching headers for assets

**.env.example → .env.local** (you create this)
```
VITE_API_BASE_URL=http://127.0.0.1:8000
```
For local development

**.env.production** (you create this)
```
VITE_API_BASE_URL=https://your-backend.onrender.com
```
For production deployment

---

## 🧩 Components Deep Dive

### 1. DemoLanding.tsx (Landing Page)

**Purpose:** First page clinicians see

**Features:**
- Professional hero section
- "What You'll Experience" cards
- Testing instructions
- Feedback expectations
- Privacy notice
- "Start Demo Assessment" CTA button

**Routes to:** `/assessment`

**Customization Points:**
- Line ~259: Your contact email
- Optional: Add your logo
- Optional: Change colors/branding

---

### 2. PatientIntake.tsx (Main Assessment)

**Purpose:** The actual AI-guided assessment

**Features:**
- Session initialization
- Streaming SSE responses from backend
- Chat interface (messages back and forth)
- Option buttons (when Ava offers choices)
- PDF report download
- Retry mechanism if report fails
- Mobile responsive

**Flow:**
1. Mounts → `initSession()` → Creates session token
2. `getInitialGreeting()` → Ava says hello
3. User types → `sendMessage()` → Backend processes
4. Ava responds → Streams back character by character
5. Continue until `:finish` or assessment complete
6. Backend generates PDF → Base64 returned
7. Download button appears → User downloads report

**Key State:**
- `messages[]` - Chat history
- `sessionId` - Current session identifier  
- `busy` - Whether Ava is "thinking"
- `finished` - Assessment complete flag

**Backend Integration:**
```typescript
const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

// Start session
POST ${apiBase}/api/v1/intake/start

// Chat endpoint (SSE streaming)
POST ${apiBase}/api/v1/intake/chat
```

---

### 3. AssessmentComplete.tsx

**Purpose:** Success page after finishing

**Features:**
- Celebration message
- Review checklist
- Return to home button

**Currently:** Minimal implementation (can be enhanced later)

---

### 4. Foundation Components

**Button.tsx**
```typescript
<CustomButton 
  variant="primary" // or "secondary"
  onClick={handleClick}
  disabled={isDisabled}
>
  Click Me
</CustomButton>
```

**Input.tsx**
```typescript
<CustomInput 
  value={text}
  onChange={handleChange}
  placeholder="Type here..."
  disabled={busy}
/>
```

**ChatBubble.tsx**
```typescript
<ChatBubble type="system"> // or "patient"
  Message content here
</ChatBubble>
```

---

## 🔄 Application Flow

```
User visits site
       ↓
┌──────────────────┐
│  DemoLanding     │  Landing page explains demo
│  (Route: /)     │  Shows "Start Assessment" button
└────────┬─────────┘
         ↓ [User clicks "Start"]
         ↓
┌──────────────────┐
│  PatientIntake   │  1. Creates session
│  (Route:         │  2. Ava greets user
│   /assessment)   │  3. Conversation begins
│                  │  4. User answers questions
│                  │  5. Screening tools administered
│                  │  6. Assessment completes
│                  │  7. PDF generated
└────────┬─────────┘
         ↓ [Assessment finished]
         ↓
┌──────────────────┐
│ AssessmentComp.  │  Success message
│ (Route:          │  PDF download reminder
│  /complete)      │  Return home option
└──────────────────┘
```

---

## 🌐 Backend Integration

### API Endpoints Used

**1. Start Session**
```
POST /api/v1/intake/start
Body: { patient_id: "demo_xxx", user_name: null }
Response: { session_token: "xyz123..." }
```

**2. Chat (Streaming)**
```
POST /api/v1/intake/chat
Body: { session_token: "xyz123...", prompt: "User message" }
Response: Server-Sent Events (SSE) stream

data: {"content": "Hello", "options": null, "done": false}
data: {"content": " there", "options": null, "done": false}
data: {"content": "!", "done": true, "pdf_report": "base64..."}
```

### Backend Requirements

Your backend MUST:
- ✅ Be running and accessible
- ✅ Have OPENAI_API_KEY configured
- ✅ Have CORS configured for your frontend domain
- ✅ Support `/api/v1/intake/start` endpoint
- ✅ Support `/api/v1/intake/chat` endpoint with SSE streaming
- ✅ Generate PDF reports

**Good news:** Your existing backend already does all this! ✅

---

## 🎨 Styling

### Tailwind CSS

All styling uses Tailwind utility classes:

```typescript
// Example from DemoLanding.tsx
<button className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 
  hover:from-blue-700 hover:to-indigo-700 text-white font-semibold 
  py-4 px-8 rounded-lg">
  Start Demo
</button>
```

### Colors Used

- **Primary Blue**: `blue-600` (buttons, accents)
- **Secondary**: `indigo-600` (gradients)
- **Success**: `green-600` (PDF download)
- **Warning**: `orange-600` (retry button)
- **Background**: `gray-50` (page backgrounds)
- **Text**: `gray-900` (primary text)

### Responsive Design

- Mobile-first approach
- Breakpoints: `sm:`, `md:`, `lg:`
- Chat bubbles adapt to screen size
- Tested on phones, tablets, desktop

---

## 📦 Build Process

### Development Mode

```bash
npm run dev
```

- Runs on http://localhost:3001
- Hot module reload (instant updates)
- Source maps for debugging
- `.env.local` used for environment variables

### Production Build

```bash
npm run build
```

**What happens:**
1. TypeScript compiled to JavaScript
2. Tailwind CSS purged (removes unused styles)
3. Code bundled and minified
4. Assets hashed for cache-busting
5. Output to `build/` directory

**Build output:**
```
build/
├── index.html (entry point)
├── assets/
│   ├── index-[hash].js    (JavaScript bundle)
│   ├── index-[hash].css   (Styles)
│   └── ...
└── vite.svg
```

### Deployment

```bash
firebase deploy --only hosting
```

- Uploads `build/` folder to Firebase
- Deploys to: `https://your-project.web.app`
- Takes 2-3 minutes
- SSL automatically enabled

---

## 🔧 Environment Variables

### Development (.env.local)

```
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Used when running `npm run dev`

### Production (.env.production)

```
VITE_API_BASE_URL=https://psychnow-api.onrender.com
```

Used when running `npm run build`

**IMPORTANT:** 
- Variables MUST start with `VITE_`
- Accessed in code as `import.meta.env.VITE_API_BASE_URL`
- Not sensitive (bundled into frontend code)

---

## 📊 Dependencies

### Core

- **react** & **react-dom** - UI framework
- **react-router-dom** - Routing (3 routes)
- **typescript** - Type safety

### Styling

- **tailwindcss** - Utility-first CSS
- **clsx** & **tailwind-merge** - Dynamic classNames
- **lucide-react** - Icons (Brain, Home, etc.)

### Build Tools

- **vite** - Fast build tool
- **@vitejs/plugin-react-swc** - React with SWC compiler

### Total Size

- `node_modules/`: ~200-300 MB
- Production build: ~200-500 KB (minified + gzipped)
- Loads in < 2 seconds on good connection

---

## 🚀 Scripts

Defined in `package.json`:

```json
{
  "dev": "vite",                          // Start dev server
  "build": "vite build",                  // Build for production
  "preview": "vite preview",              // Preview production build locally
  "deploy": "npm run build && firebase deploy --only hosting"  // One-command deploy
}
```

---

## 🔍 What's Different from Full App?

### Removed

- ❌ Patient dashboard & portal
- ❌ Provider dashboard & portal  
- ❌ Admin panels
- ❌ Appointment scheduling
- ❌ Health records
- ❌ Telemedicine
- ❌ Complex authentication
- ❌ User profiles
- ❌ Staff management
- ❌ Multi-role routing

### Kept (Core Demo)

- ✅ Landing page (simplified)
- ✅ Assessment chatbox (PatientIntake)
- ✅ AI conversation
- ✅ PDF generation
- ✅ Streaming responses
- ✅ Anonymous sessions

**Result:** ~90% smaller codebase, focused on single use case

---

## 📝 Adding Features Later

If you want to add something:

### New Page

1. Create component in `src/components/NewPage.tsx`
2. Add route in `src/App.tsx`:
   ```typescript
   <Route path="/new-page" element={<NewPage />} />
   ```
3. Link to it:
   ```typescript
   <Link to="/new-page">Go to New Page</Link>
   ```

### New Component

1. Create in `src/components/MyComponent.tsx`
2. Export it:
   ```typescript
   export default function MyComponent() { ... }
   ```
3. Import where needed:
   ```typescript
   import MyComponent from './components/MyComponent';
   ```

### Style Changes

Edit Tailwind classes directly in components (no separate CSS files needed)

---

## 🧪 Testing Locally

```bash
# Terminal 1: Backend
cd C:\Users\gbtol\PsychNow\backend
.\venv\Scripts\Activate.ps1
python main.py

# Terminal 2: Frontend
cd C:\Users\gbtol\PsychNow\psychnow-demo
npm run dev
```

Visit http://localhost:3001

**Test:**
1. Landing page loads
2. Click "Start Demo"
3. Ava greets you
4. Send message
5. Ava responds
6. Complete assessment

---

## 📚 Further Reading

- **React Docs**: https://react.dev
- **React Router**: https://reactrouter.com
- **Tailwind CSS**: https://tailwindcss.com
- **Vite**: https://vitejs.dev
- **Firebase Hosting**: https://firebase.google.com/docs/hosting

---

## ⚡ Quick Commands Reference

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Deploy to Firebase (after build)
firebase deploy --only hosting

# Or use the combined script
npm run deploy
```

---

## 🎯 Next Steps

1. **Test locally** - Make sure everything works
2. **Deploy** - Follow `QUICK_START.md`
3. **Send to clinicians** - Use `CLINICIAN_EMAIL_TEMPLATE.md`
4. **Collect feedback** - Use `FEEDBACK_FORM_TEMPLATE.md`
5. **Iterate** - Make improvements based on feedback

You're all set! 🚀

