import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import DemoLanding from './components/DemoLanding';
import PatientIntake from './components/PatientIntake';
import AssessmentComplete from './components/AssessmentComplete';

export default function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50 flex flex-col">
        <div className="flex-1">
          <Routes>
            <Route path="/" element={<DemoLanding />} />
            <Route path="/assessment" element={<PatientIntake />} />
            <Route path="/complete" element={<AssessmentComplete />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
        
        {/* Footer */}
        <footer className="bg-white border-t border-gray-200 py-4">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center text-sm text-gray-600">
              <p className="mb-1">PsychNow Demo Version - For Clinical Validation Only</p>
              <p>
                Questions? Contact:{' '}
                <a 
                  href="mailto:psychiatrynowai@gmail.com" 
                  className="text-blue-600 hover:text-blue-800 underline"
                >
                  psychiatrynowai@gmail.com
                </a>
              </p>
            </div>
          </div>
        </footer>
      </div>
    </Router>
  );
}

