# 🌐 **Frontend Integration Guide - Connect React to FastAPI**

## 🎯 **Current Status**

- ✅ **Backend**: 100% Complete (30 screeners, all APIs ready)
- ✅ **Frontend**: Exists but needs updates for new backend
- ⏳ **Connection**: Needs minor updates

---

## 📋 **INTEGRATION STEPS**

### **Step 1: Update API Base URL (Already Good!)**

The frontend is currently pointing to `http://localhost:8000/chat/`, which needs to be updated to the new versioned API.

**File**: `pychnow design/src/components/PatientIntake.tsx`

**Current (line ~1004)**:
```typescript
fetch('http://localhost:8000/chat/', {
```

**Change to**:
```typescript
fetch('http://localhost:8000/api/v1/intake/chat', {
```

---

### **Step 2: Add Authentication Token Support**

**Current**: Frontend doesn't send auth tokens  
**Needed**: Backend expects JWT tokens for authenticated endpoints

**Add before fetch (around line ~992)**:
```typescript
const sendMessage = async (prompt: string) => {
  if (loading) return;
  setBusy(true);

  // Get token from localStorage
  const token = localStorage.getItem('access_token');
  
  const form = new FormData();
  form.append('prompt', prompt);
  if (sessionRef.current) form.append('session_id', sessionRef.current);

  const controller = new AbortController();
  // ... rest stays the same

  try {
    const res = await fetch('http://localhost:8000/api/v1/intake/chat', {
      method: 'POST',
      headers: {
        // Add Authorization header if token exists
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
      },
      body: form,
      signal: controller.signal,
    });
    // ... rest stays the same
```

---

### **Step 3: Create Login/Register Pages**

The backend has authentication endpoints that need frontend pages:

**Create**: `pychnow design/src/components/PatientLogin.tsx`

```typescript
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { CustomButton } from './foundation/Button';
import { CustomInput } from './foundation/Input';

export default function PatientLogin() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const res = await fetch('http://localhost:8000/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || 'Login failed');
      }

      const data = await res.json();
      
      // Save token and user info
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('user_id', data.user.id);
      localStorage.setItem('user_role', data.user.role);
      localStorage.setItem('user_email', data.user.email);
      
      // Redirect to intake
      navigate('/patient-intake');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 px-4">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-xl p-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Welcome Back</h1>
        <p className="text-gray-600 mb-6">Sign in to continue your mental health journey</p>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-red-700 text-sm">
              {error}
            </div>
          )}
          
          <CustomInput
            type="email"
            placeholder="Email address"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          
          <CustomInput
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          
          <CustomButton
            type="submit"
            variant="primary"
            disabled={loading}
            className="w-full"
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </CustomButton>
        </form>
        
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600">
            Don't have an account?{' '}
            <button
              onClick={() => navigate('/patient-signup')}
              className="text-blue-600 hover:underline font-medium"
            >
              Sign up
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}
```

---

### **Step 4: Create Registration Page**

**Create**: `pychnow design/src/components/PatientRegister.tsx`

```typescript
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { CustomButton } from './foundation/Button';
import { CustomInput } from './foundation/Input';

export default function PatientRegister() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    firstName: '',
    lastName: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    try {
      const res = await fetch('http://localhost:8000/api/v1/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password,
          role: 'patient',  // Default role
        }),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || 'Registration failed');
      }

      const data = await res.json();
      
      // Save token and redirect
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('user_id', data.user.id);
      localStorage.setItem('user_role', 'patient');
      
      navigate('/patient-intake');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 px-4">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-xl p-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Create Account</h1>
        <p className="text-gray-600 mb-6">Join PsychNow for comprehensive mental health care</p>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-red-700 text-sm">
              {error}
            </div>
          )}
          
          <CustomInput
            type="email"
            placeholder="Email address"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            required
          />
          
          <CustomInput
            type="password"
            placeholder="Password (min 8 characters)"
            value={formData.password}
            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
            required
            minLength={8}
          />
          
          <CustomInput
            type="password"
            placeholder="Confirm password"
            value={formData.confirmPassword}
            onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
            required
          />
          
          <CustomButton
            type="submit"
            variant="primary"
            disabled={loading}
            className="w-full"
          >
            {loading ? 'Creating account...' : 'Create Account'}
          </CustomButton>
        </form>
        
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600">
            Already have an account?{' '}
            <button
              onClick={() => navigate('/patient-signin')}
              className="text-blue-600 hover:underline font-medium"
            >
              Sign in
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}
```

---

### **Step 5: Update Router with Auth Routes**

**File**: `pychnow design/src/App.tsx`

**Add routes**:
```typescript
import PatientLogin from './components/PatientLogin';
import PatientRegister from './components/PatientRegister';

function App() {
  return (
    <Routes>
      {/* Landing */}
      <Route path="/" element={<LandingPage />} />
      
      {/* Auth */}
      <Route path="/patient-signin" element={<PatientLogin />} />
      <Route path="/patient-signup" element={<PatientRegister />} />
      
      {/* Patient Flow */}
      <Route path="/patient-intake" element={<PatientIntake />} />
      <Route path="/patient-summary" element={<PatientIntakeSummary />} />
      
      {/* ... other routes ... */}
    </Routes>
  );
}
```

---

### **Step 6: Protect Intake Route**

Add auth check to `PatientIntake.tsx`:

```typescript
export default function PatientIntake() {
  const navigate = useNavigate();
  
  // Check auth on mount
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      navigate('/patient-signin');
    }
  }, [navigate]);
  
  // ... rest of component
}
```

---

### **Step 7: Start Initial Session with Backend**

**Update**: `PatientIntake.tsx` - Add session initialization

**Add after component state (around line ~970)**:
```typescript
// Initialize session on mount
useEffect(() => {
  const initSession = async () => {
    const token = localStorage.getItem('access_token');
    const userId = localStorage.getItem('user_id');
    
    if (!token || !userId) {
      navigate('/patient-signin');
      return;
    }
    
    try {
      const res = await fetch('http://localhost:8000/api/v1/intake/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ patient_id: userId }),
      });
      
      const data = await res.json();
      sessionRef.current = data.session_token;
      setSessionId(data.session_token.slice(0, 8));
      
      // Push initial greeting
      pushSys(data.greeting, new Date().toISOString());
      
    } catch (err) {
      console.error('Failed to start session:', err);
      pushSys('⚠️ Failed to start session. Please refresh.', new Date().toISOString());
    }
  };
  
  initSession();
}, [navigate]);
```

---

## 🧪 **TESTING THE CONNECTION**

### **Step 1: Start Backend**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload
```

**Expected**: Server running at `http://localhost:8000`

---

### **Step 2: Start Frontend**
```powershell
cd "pychnow design"
npm install  # If first time
npm run dev
```

**Expected**: Frontend running at `http://localhost:5173`

---

### **Step 3: Test Flow**

1. ✅ Navigate to `http://localhost:5173`
2. ✅ Click "Sign Up" → Create account
3. ✅ Verify redirect to intake page
4. ✅ See Ava's greeting message
5. ✅ Type a message about symptoms
6. ✅ See streaming response
7. ✅ Complete screeners
8. ✅ Type `:finish`
9. ✅ View report summary

---

## 🚨 **COMMON ISSUES & FIXES**

### **Issue #1: CORS Error**
**Error**: "Access to fetch blocked by CORS policy"

**Fix**: Backend already configured for CORS, but verify in `backend/.env`:
```
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

---

### **Issue #2: 401 Unauthorized**
**Error**: "401 Unauthorized" on `/intake/chat`

**Fix**: Check auth token is being sent:
```typescript
// In PatientIntake.tsx sendMessage function
console.log('Token:', localStorage.getItem('access_token'));

headers: {
  'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
}
```

---

### **Issue #3: Session Not Found**
**Error**: "Session not found" errors

**Fix**: Ensure session is initialized with `/intake/start` before calling `/intake/chat`

---

## 📊 **INTEGRATION CHECKLIST**

- [ ] Update API URL to `/api/v1/intake/chat`
- [ ] Add Authorization header with JWT token
- [ ] Create PatientLogin.tsx
- [ ] Create PatientRegister.tsx
- [ ] Update App.tsx routes
- [ ] Add auth check to PatientIntake
- [ ] Add session initialization
- [ ] Test full flow end-to-end
- [ ] Verify streaming responses work
- [ ] Verify report generation works
- [ ] Verify all 30 screeners are accessible

---

## 🎯 **ESTIMATED TIME**

- **Code changes**: 30-45 minutes
- **Testing**: 15-30 minutes
- **Bug fixes**: 15-30 minutes
- **Total**: **1-2 hours**

---

## 🎉 **RESULT**

After completing these steps, you'll have:

✅ Full authentication flow  
✅ Protected intake route  
✅ Backend-connected AI conversation  
✅ Access to all 30 screeners  
✅ Report generation working  
✅ End-to-end patient journey functional  

**Status**: **PILOT-READY** 🚀

---

*Integration guide created: October 2, 2025*  
*Backend: ✅ Ready | Frontend: ⏳ Needs 1-2 hours of integration*

