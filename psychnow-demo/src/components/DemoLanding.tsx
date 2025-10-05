import { useNavigate } from 'react-router-dom';
import { Brain, CheckCircle, FileText, MessageCircle, Clock, Shield } from 'lucide-react';

export default function DemoLanding() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">PsychNow</h1>
                <p className="text-xs text-gray-500">Clinical Demo Version</p>
              </div>
            </div>
            <div className="hidden sm:block">
              <span className="px-4 py-2 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                ✓ For Clinical Review
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-12">
          <div className="inline-flex items-center px-4 py-2 bg-blue-100 text-blue-800 rounded-full text-sm font-medium mb-6">
            🩺 For Psychiatrists & Nurse Practitioners
          </div>
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            AI-Guided Psychiatric<br />Intake Assessment
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Experience our conversational AI system that conducts comprehensive mental health assessments 
            and generates clinical reports. Your feedback will shape the future of this platform.
          </p>
        </div>

        {/* What to Try Card */}
        <div className="bg-white rounded-2xl shadow-xl border border-gray-200 p-8 mb-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
            <MessageCircle className="w-6 h-6 mr-2 text-blue-600" />
            What You'll Experience
          </h3>
          
          <div className="grid md:grid-cols-2 gap-6 mb-8">
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                <CheckCircle className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <h4 className="font-semibold text-gray-900 mb-1">Conversational Flow</h4>
                <p className="text-sm text-gray-600">Natural, empathetic AI conversation that adapts to patient responses</p>
              </div>
            </div>

            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0 w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                <FileText className="w-5 h-5 text-green-600" />
              </div>
              <div>
                <h4 className="font-semibold text-gray-900 mb-1">Validated Screening Tools</h4>
                <p className="text-sm text-gray-600">PHQ-9, GAD-7, C-SSRS, ASRS, PCL-5, and 25+ other screeners</p>
              </div>
            </div>

            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0 w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
                <Brain className="w-5 h-5 text-purple-600" />
              </div>
              <div>
                <h4 className="font-semibold text-gray-900 mb-1">Comprehensive Assessment</h4>
                <p className="text-sm text-gray-600">Complete psychiatric history, safety screening, and clinical context</p>
              </div>
            </div>

            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0 w-8 h-8 bg-orange-100 rounded-lg flex items-center justify-center">
                <FileText className="w-5 h-5 text-orange-600" />
              </div>
              <div>
                <h4 className="font-semibold text-gray-900 mb-1">Clinical Report</h4>
                <p className="text-sm text-gray-600">Structured PDF report with scores, interpretations, and recommendations</p>
              </div>
            </div>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <div className="flex items-start space-x-3">
              <Clock className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm text-blue-900">
                  <strong>Time Commitment:</strong> 15-20 minutes for complete assessment
                </p>
              </div>
            </div>
          </div>

          <button
            onClick={() => navigate('/assessment')}
            className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold py-4 px-8 rounded-lg text-lg transition-all shadow-lg hover:shadow-xl"
          >
            Start Demo Assessment →
          </button>
        </div>

        {/* Dual Report Explanation */}
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl border-2 border-blue-200 p-8 mb-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
            <FileText className="w-6 h-6 mr-2 text-blue-600" />
            Two Report Versions for Your Review
          </h3>
          <p className="text-gray-700 mb-6">
            After completing the assessment, you'll receive <strong>two distinct reports</strong> to evaluate both patient communication and clinical utility:
          </p>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg p-6 border-2 border-blue-300 shadow-sm">
              <h4 className="font-bold text-lg text-blue-900 mb-2 flex items-center">
                <span className="text-2xl mr-2">📋</span> Patient Report
              </h4>
              <p className="text-gray-700 text-sm mb-3">
                Compassionate, accessible summary designed for patients:
              </p>
              <ul className="text-sm text-gray-600 space-y-1.5">
                <li>• Plain language explanations</li>
                <li>• Validation and hope-focused</li>
                <li>• Self-care resources</li>
                <li>• Clear next steps</li>
              </ul>
            </div>
            
            <div className="bg-white rounded-lg p-6 border-2 border-indigo-300 shadow-sm">
              <h4 className="font-bold text-lg text-indigo-900 mb-2 flex items-center">
                <span className="text-2xl mr-2">🩺</span> Clinician Report
              </h4>
              <p className="text-gray-700 text-sm mb-3">
                Comprehensive clinical assessment for providers:
              </p>
              <ul className="text-sm text-gray-600 space-y-1.5">
                <li>• Full diagnostic reasoning</li>
                <li>• Treatment recommendations</li>
                <li>• Risk stratification details</li>
                <li>• Clinical decision support</li>
              </ul>
            </div>
          </div>
          <div className="mt-6 bg-blue-100 border border-blue-300 rounded-lg p-4">
            <p className="text-sm text-blue-900 text-center">
              <strong>💡 Why Two Reports?</strong> By reviewing both versions, you can evaluate patient communication quality <strong>and</strong> assess whether the clinical report supports your workflow and decision-making.
            </p>
          </div>
        </div>

        {/* Instructions Card */}
        <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-2xl border border-indigo-200 p-8 mb-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-4">📋 Testing Instructions</h3>
          <ol className="space-y-3 text-gray-700">
            <li className="flex items-start space-x-3">
              <span className="flex-shrink-0 w-6 h-6 bg-indigo-600 text-white rounded-full flex items-center justify-center text-sm font-bold">1</span>
              <span><strong>Complete the assessment</strong> as if you were a patient seeking care</span>
            </li>
            <li className="flex items-start space-x-3">
              <span className="flex-shrink-0 w-6 h-6 bg-indigo-600 text-white rounded-full flex items-center justify-center text-sm font-bold">2</span>
              <span><strong>Evaluate the conversation quality</strong> - Is it empathetic? Clinically appropriate?</span>
            </li>
            <li className="flex items-start space-x-3">
              <span className="flex-shrink-0 w-6 h-6 bg-indigo-600 text-white rounded-full flex items-center justify-center text-sm font-bold">3</span>
              <span><strong>Review the generated report</strong> - Is it comprehensive? Clinically useful?</span>
            </li>
            <li className="flex items-start space-x-3">
              <span className="flex-shrink-0 w-6 h-6 bg-indigo-600 text-white rounded-full flex items-center justify-center text-sm font-bold">4</span>
              <span><strong>Download the PDF</strong> and assess report quality and formatting</span>
            </li>
          </ol>
        </div>

        {/* Feedback Section */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-4">💬 Your Feedback is Critical</h3>
          <p className="text-gray-600 mb-4">
            As a clinical expert, your input will directly shape this platform. After completing the assessment, you'll be asked to provide quick feedback (2 minutes) on:
          </p>
          <ul className="space-y-2 text-gray-700 mb-6">
            <li className="flex items-start space-x-2">
              <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
              <span><strong>Conversation Quality:</strong> Natural flow, clinical appropriateness, empathy</span>
            </li>
            <li className="flex items-start space-x-2">
              <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
              <span><strong>Patient Report:</strong> Clarity, helpfulness, appropriateness for patients</span>
            </li>
            <li className="flex items-start space-x-2">
              <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
              <span><strong>Clinician Report:</strong> Clinical utility, completeness, decision support value</span>
            </li>
            <li className="flex items-start space-x-2">
              <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
              <span><strong>Practice Integration:</strong> Whether you would use this in your workflow</span>
            </li>
          </ul>
          <div className="bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-300 rounded-lg p-4">
            <p className="text-sm text-green-900 text-center font-medium">
              ✅ Built-in feedback form appears immediately after assessment completion - takes only 2 minutes!
            </p>
          </div>
        </div>

        {/* Privacy Notice */}
        <div className="mt-8 bg-gray-50 border border-gray-200 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <Shield className="w-5 h-5 text-gray-600 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-gray-600">
              <strong>Privacy Note:</strong> This is a demo environment. Please do not enter real patient information. 
              All data entered during this demo will be used solely for product development and clinical validation.
            </div>
          </div>
        </div>
      </div>

    </div>
  );
}

