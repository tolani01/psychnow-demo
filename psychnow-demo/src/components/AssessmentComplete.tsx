import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { CheckCircle, Home, FileText, Star, Send, AlertCircle } from 'lucide-react';

interface LocationState {
  sessionId: string;
  patientPdf: string;
  clinicianPdf: string;
}

export default function AssessmentComplete() {
  const navigate = useNavigate();
  const location = useLocation();
  const state = location.state as LocationState;
  const apiBase = (import.meta as any).env?.VITE_API_BASE_URL || (window.location.hostname === 'localhost' ? 'http://127.0.0.1:8000' : 'https://psychnow-api.onrender.com');
  const effectiveSessionId = state?.sessionId || (typeof window !== 'undefined' ? (new URLSearchParams(window.location.search).get('sessionId') || localStorage.getItem('psychnow_session_id') || '') : '');
  
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [fallbackPatientPdf, setFallbackPatientPdf] = useState<string>('');
  const [fallbackClinicianPdf, setFallbackClinicianPdf] = useState<string>('');
  const [downloadingPatient, setDownloadingPatient] = useState(false);
  const [downloadingClinician, setDownloadingClinician] = useState(false);
  
  // Feedback form state
  const [conversationRating, setConversationRating] = useState(0);
  const [patientReportRating, setPatientReportRating] = useState(0);
  const [clinicianReportRating, setClinicianReportRating] = useState(0);
  const [wouldUse, setWouldUse] = useState('');
  const [strength, setStrength] = useState('');
  const [concern, setConcern] = useState('');
  const [missingPatient, setMissingPatient] = useState('');
  const [missingClinician, setMissingClinician] = useState('');
  const [additionalComments, setAdditionalComments] = useState('');
  const [testerEmail, setTesterEmail] = useState('');
  const [testerName, setTesterName] = useState('');

  const downloadPDF = (pdfBase64: string, reportType: 'patient' | 'clinician') => {
    try {
      const byteCharacters = atob(pdfBase64);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: 'application/pdf' });
      
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `PsychNow_${reportType}_Report_${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading PDF:', error);
    }
  };

  // Auto-fetch PDFs and email if missing/needed
  useEffect(() => {
    if (!effectiveSessionId) return;
    fetch(`${apiBase}/api/v1/intake/session/${encodeURIComponent(effectiveSessionId)}/reports?email=true`)
      .then(async (r) => {
        if (!r.ok) return;
        const data = await r.json();
        if (!state?.patientPdf && data?.patient_pdf) setFallbackPatientPdf(data.patient_pdf);
        if (!state?.clinicianPdf && data?.clinician_pdf) setFallbackClinicianPdf(data.clinician_pdf);
      })
      .catch(() => {});
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchReports = async (): Promise<{ patient_pdf?: string; clinician_pdf?: string }> => {
    if (!effectiveSessionId) return {};
    try {
      const r = await fetch(`${apiBase}/api/v1/intake/session/${encodeURIComponent(effectiveSessionId)}/reports`);
      if (!r.ok) return {};
      const data = await r.json();
      if (data?.patient_pdf && !fallbackPatientPdf) setFallbackPatientPdf(data.patient_pdf);
      if (data?.clinician_pdf && !fallbackClinicianPdf) setFallbackClinicianPdf(data.clinician_pdf);
      return data;
    } catch {
      return {};
    }
  };

  const handleDownload = async (reportType: 'patient' | 'clinician') => {
    if (reportType === 'patient') {
      const base64 = state?.patientPdf || fallbackPatientPdf;
      if (base64) {
        downloadPDF(base64, 'patient');
        return;
      }
      setDownloadingPatient(true);
      const data = await fetchReports();
      if (data?.patient_pdf) downloadPDF(data.patient_pdf, 'patient');
      setDownloadingPatient(false);
    } else {
      const base64 = state?.clinicianPdf || fallbackClinicianPdf;
      if (base64) {
        downloadPDF(base64, 'clinician');
        return;
      }
      setDownloadingClinician(true);
      const data = await fetchReports();
      if (data?.clinician_pdf) downloadPDF(data.clinician_pdf, 'clinician');
      setDownloadingClinician(false);
    }
  };

  const handleSubmitFeedback = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    // Validation
    if (!conversationRating || !patientReportRating || !clinicianReportRating) {
      setError('Please provide all star ratings');
      return;
    }
    
    if (!wouldUse) {
      setError('Please indicate whether you would use this in practice');
      return;
    }
    
    setSubmitting(true);
    
    try {
      const apiBase = (import.meta as any).env?.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
      const response = await fetch(`${apiBase}/api/v1/feedback/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: state?.sessionId,
          conversation_rating: conversationRating,
          patient_report_rating: patientReportRating,
          clinician_report_rating: clinicianReportRating,
          would_use: wouldUse,
          strength: strength || null,
          concern: concern || null,
          missing_patient: missingPatient || null,
          missing_clinician: missingClinician || null,
          additional_comments: additionalComments || null,
          tester_email: testerEmail || null,
          tester_name: testerName || null,
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to submit feedback');
      }
      
      setFeedbackSubmitted(true);
      setSubmitting(false);
    } catch (err) {
      console.error('Failed to submit feedback:', err);
      setError('Failed to submit feedback. Please try again or contact us via email.');
      setSubmitting(false);
    }
  };

  const StarRating = ({ value, onChange, label }: { value: number; onChange: (rating: number) => void; label: string }) => (
    <div className="mb-6">
      <label className="block text-sm font-semibold text-gray-900 mb-2">{label}</label>
      <div className="flex items-center space-x-2">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            type="button"
            onClick={() => onChange(star)}
            className="focus:outline-none transition-transform hover:scale-110"
          >
            <Star
              className={`w-10 h-10 ${
                star <= value
                  ? 'fill-yellow-400 text-yellow-400'
                  : 'fill-gray-200 text-gray-300'
              }`}
            />
          </button>
        ))}
        <span className="ml-4 text-sm font-medium text-gray-700">
          {value > 0 ? `${value}/5` : 'Not rated'}
        </span>
      </div>
    </div>
  );

  if (!effectiveSessionId) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md text-center">
          <AlertCircle className="w-16 h-16 text-orange-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Session Not Found</h2>
          <p className="text-gray-600 mb-6">Please complete an assessment first.</p>
          <button
            onClick={() => navigate('/')}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold"
          >
            Return to Home
          </button>
        </div>
      </div>
    );
  }

  if (feedbackSubmitted) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-green-50 to-white flex items-center justify-center p-4">
        <div className="max-w-2xl w-full bg-white rounded-2xl shadow-xl border border-gray-200 p-8">
          <div className="text-center">
            <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <CheckCircle className="w-12 h-12 text-green-600" />
            </div>
            
            <h1 className="text-3xl font-bold text-gray-900 mb-4">
              Thank You! 🎉
            </h1>
            
            <p className="text-lg text-gray-600 mb-8">
              Your feedback has been submitted successfully. Your insights are invaluable and will directly influence the development of PsychNow.
            </p>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
              <p className="text-sm text-blue-900">
                <strong>What happens next?</strong><br />
                We'll review your feedback along with input from other clinicians and use it to improve the assessment flow and report quality. You may hear from us with questions or updates.
              </p>
            </div>

            <div className="bg-green-50 border border-green-200 rounded-lg p-6 mb-8">
              <p className="text-sm text-green-900">
                <strong>Interested in integrating PsychNow Platform into your clinic?</strong><br />
                If you or any provider is interested in integrating this tool into your clinic, contact us at{' '}
                <a 
                  href="mailto:psychiatrynowai@gmail.com" 
                  className="text-green-700 underline hover:text-green-800 font-medium"
                >
                  psychiatrynowai@gmail.com
                </a>
                . We'd love to discuss how PsychNow Platform can enhance your practice.
              </p>
            </div>

            <button
              onClick={() => navigate('/')}
              className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
            >
              <Home className="w-5 h-5" />
              Return to Home
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Success Header */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-8 mb-8">
          <div className="text-center mb-6">
            <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="w-12 h-12 text-green-600" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Assessment Complete!
            </h1>
            <p className="text-lg text-gray-600">
              Thank you for testing the PsychNow assessment system.
            </p>
          </div>

          {/* Dual Report Downloads */}
          <div className="grid md:grid-cols-2 gap-4 mb-6">
            {/* Patient Report */}
            <div className="bg-blue-50 border-2 border-blue-300 rounded-lg p-6">
              <h3 className="font-bold text-lg text-blue-900 mb-2 flex items-center">
                <span className="text-2xl mr-2">📋</span>
                Patient Report
              </h3>
              <p className="text-sm text-blue-800 mb-4">
                Compassionate, patient-friendly summary with accessible language
              </p>
              <button
                onClick={() => handleDownload('patient')}
                disabled={downloadingPatient}
                className="w-full px-4 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white rounded-lg font-semibold transition-colors flex items-center justify-center gap-2"
              >
                {downloadingPatient ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    Preparing PDF...
                  </>
                ) : (
                  <>
                    <FileText className="w-5 h-5" />
                    Download Patient Report
                  </>
                )}
              </button>
            </div>

            {/* Clinician Report */}
            <div className="bg-indigo-50 border-2 border-indigo-300 rounded-lg p-6">
              <h3 className="font-bold text-lg text-indigo-900 mb-2 flex items-center">
                <span className="text-2xl mr-2">🩺</span>
                Clinician Report
              </h3>
              <p className="text-sm text-indigo-800 mb-4">
                Comprehensive clinical assessment with diagnostic reasoning
              </p>
              <button
                onClick={() => handleDownload('clinician')}
                disabled={downloadingClinician}
                className="w-full px-4 py-3 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-300 text-white rounded-lg font-semibold transition-colors flex items-center justify-center gap-2"
              >
                {downloadingClinician ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    Preparing PDF...
                  </>
                ) : (
                  <>
                    <FileText className="w-5 h-5" />
                    Download Clinician Report
                  </>
                )}
              </button>
            </div>
          </div>

          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <p className="text-sm text-yellow-900 text-center">
              💡 Please download and review <strong>both reports</strong> before providing feedback below
            </p>
          </div>
        </div>

        {/* Feedback Form */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-2 flex items-center">
            <span className="text-3xl mr-2">💬</span>
            Clinical Feedback (2 minutes)
          </h2>
          <p className="text-gray-600 mb-6">
            Your expert input will directly shape this platform. Please share your honest assessment.
          </p>

          <form onSubmit={handleSubmitFeedback} className="space-y-6">
            {/* Star Ratings */}
            <div className="bg-gray-50 rounded-lg p-6">
              <h3 className="font-bold text-gray-900 mb-4">⭐ Rate Your Experience</h3>
              
              <StarRating 
                value={conversationRating}
                onChange={setConversationRating}
                label="1. How would you rate the conversation flow and quality?"
              />
              
              <StarRating 
                value={patientReportRating}
                onChange={setPatientReportRating}
                label="2. How would you rate the Patient Report quality?"
              />
              
              <StarRating 
                value={clinicianReportRating}
                onChange={setClinicianReportRating}
                label="3. How would you rate the Clinician Report quality?"
              />
            </div>

            {/* Would Use in Practice */}
            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-3">
                4. Would you use this tool in your practice? *
              </label>
              <div className="space-y-2">
                {[
                  { value: 'yes_definitely', label: '✅ Yes, definitely', color: 'green' },
                  { value: 'yes_probably', label: '👍 Yes, probably', color: 'blue' },
                  { value: 'maybe', label: '🤔 Maybe, with some changes', color: 'yellow' },
                  { value: 'probably_not', label: '👎 Probably not', color: 'orange' },
                  { value: 'no', label: '❌ No', color: 'red' },
                ].map((option) => (
                  <label
                    key={option.value}
                    className={`flex items-center p-4 border-2 rounded-lg cursor-pointer transition-all ${
                      wouldUse === option.value
                        ? `border-${option.color}-500 bg-${option.color}-50`
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <input
                      type="radio"
                      name="wouldUse"
                      value={option.value}
                      checked={wouldUse === option.value}
                      onChange={(e) => setWouldUse(e.target.value)}
                      className="mr-3 w-5 h-5"
                    />
                    <span className="font-medium text-gray-900">{option.label}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Open-Ended Feedback */}
            <div className="space-y-4">
              <h3 className="font-bold text-gray-900">💭 Your Insights</h3>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  5. What was the <span className="text-green-600 font-semibold">biggest strength</span> of this assessment?
                </label>
                <textarea
                  value={strength}
                  onChange={(e) => setStrength(e.target.value)}
                  rows={3}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  placeholder="What did you like most about the conversation, flow, or reports?"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  6. What was your <span className="text-red-600 font-semibold">biggest concern</span>?
                </label>
                <textarea
                  value={concern}
                  onChange={(e) => setConcern(e.target.value)}
                  rows={3}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  placeholder="Any red flags, clinical issues, or areas that need improvement?"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  7. What's missing from the <span className="text-blue-600 font-semibold">Patient Report</span>?
                </label>
                <textarea
                  value={missingPatient}
                  onChange={(e) => setMissingPatient(e.target.value)}
                  rows={2}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  placeholder="What information would be helpful for patients that wasn't included?"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  8. What's missing from the <span className="text-indigo-600 font-semibold">Clinician Report</span>?
                </label>
                <textarea
                  value={missingClinician}
                  onChange={(e) => setMissingClinician(e.target.value)}
                  rows={2}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  placeholder="What clinical information or decision support would you want to see?"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  9. Additional comments or suggestions
                </label>
                <textarea
                  value={additionalComments}
                  onChange={(e) => setAdditionalComments(e.target.value)}
                  rows={4}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  placeholder="Any other feedback, suggestions, or observations?"
                />
              </div>
            </div>

            {/* Optional Tester Info */}
            <div className="bg-gray-50 rounded-lg p-6">
              <h3 className="font-bold text-gray-900 mb-4">📧 Optional: Contact Information</h3>
              <p className="text-sm text-gray-600 mb-4">
                If you're willing to be contacted for follow-up questions:
              </p>
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Your Name
                  </label>
                  <input
                    type="text"
                    value={testerName}
                    onChange={(e) => setTesterName(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Dr. Jane Smith"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Your Email
                  </label>
                  <input
                    type="email"
                    value={testerEmail}
                    onChange={(e) => setTesterEmail(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="dr.smith@hospital.com"
                  />
                </div>
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-sm text-red-800 flex items-center gap-2">
                  <AlertCircle className="w-5 h-5" />
                  {error}
                </p>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={submitting}
              className="w-full bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 disabled:from-gray-400 disabled:to-gray-400 text-white font-bold py-4 px-8 rounded-lg text-lg transition-all shadow-lg hover:shadow-xl flex items-center justify-center gap-2"
            >
              {submitting ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  Submitting...
                </>
              ) : (
                <>
                  <Send className="w-5 h-5" />
                  Submit Feedback
                </>
              )}
            </button>

            <p className="text-xs text-gray-500 text-center mt-4">
              Your feedback will be sent to the development team and used to improve PsychNow
            </p>
          </form>
        </div>

        {/* Return Home */}
        <div className="mt-8 text-center">
          <button
            onClick={() => navigate('/')}
            className="text-gray-600 hover:text-gray-900 underline flex items-center gap-2 mx-auto"
          >
            <Home className="w-4 h-4" />
            Return to Home
          </button>
        </div>
      </div>
    </div>
  );
}
