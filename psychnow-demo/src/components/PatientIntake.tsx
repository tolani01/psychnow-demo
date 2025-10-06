import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChatBubble } from './foundation/ChatBubble';
import { CustomButton } from './foundation/Button';
import { CustomInput } from './foundation/Input';
import { Home } from 'lucide-react';

interface ChatMessage {
  type: 'patient' | 'system';
  content: string;
  timestamp: string;
  options?: Array<{label: string; value: string}>;
  pdf_report?: string;  // Legacy
  patient_pdf?: string;  // Patient version
  clinician_pdf?: string;  // Clinician version
}

export default function PatientIntake() {
  const navigate = useNavigate();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [busy, setBusy] = useState(false);
  const [sessionId, setSessionId] = useState<string>('');
  const [finished, setFinished] = useState(false);
  const [reportGenerationFailed, setReportGenerationFailed] = useState(false);
  const [patientPdfBase64, setPatientPdfBase64] = useState<string>('');
  const [clinicianPdfBase64, setClinicianPdfBase64] = useState<string>('');
  
  const sessionRef = useRef<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const checkAndRecoverSession = async () => {
      // Check if there's a session ID in URL params or localStorage
      const urlParams = new URLSearchParams(window.location.search);
      const urlSessionId = urlParams.get('sessionId');
      const storedSessionId = localStorage.getItem('psychnow_session_id');
      
      if (urlSessionId || storedSessionId) {
        const sessionToUse = urlSessionId || storedSessionId;
        setSessionId(sessionToUse.slice(0, 8)); // Display version
        sessionRef.current = sessionToUse; // Full token for API calls
        
        // Try to recover the session
        try {
          const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/v1/intake/session/${sessionToUse}/recover`);
          
          if (response.ok) {
            const data = await response.json();
            pushSys(`✅ Welcome back! Resuming your assessment from where you left off...`, new Date().toISOString());
            
            // Restore conversation history
            if (data.conversation_history && data.conversation_history.length > 0) {
              setMessages(data.conversation_history);
            }
          } else {
            // Recovery failed, start new session
            initSession();
          }
        } catch (error) {
          console.error('Recovery error:', error);
          // Recovery failed, start new session
          initSession();
        }
      } else {
        // Start new session
        initSession();
      }
    };
    
    checkAndRecoverSession();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Keep backend alive - ping every 10 minutes to prevent Render timeout
  useEffect(() => {
    const pingBackend = async () => {
      try {
        const apiBase = window.location.hostname === 'localhost' ? 'http://127.0.0.1:8002' : 'https://psychnow-api.onrender.com';
        await fetch(`${apiBase}/health`);
        console.log('✅ Backend ping successful - keeping alive');
      } catch (error) {
        console.warn('⚠️ Backend ping failed:', error);
      }
    };

    // Ping immediately, then every 10 minutes
    pingBackend();
    const pingInterval = setInterval(pingBackend, 10 * 60 * 1000); // 10 minutes

    return () => clearInterval(pingInterval);
  }, []);

  const getInitialGreeting = async () => {
    if (!sessionRef.current) return;
    
    try {
      const apiBase = window.location.hostname === 'localhost' ? 'http://127.0.0.1:8002' : 'https://psychnow-api.onrender.com';
      const res = await fetch(`${apiBase}/api/v1/intake/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_token: sessionRef.current,
          prompt: '',
        }),
      });

      if (!res.ok) {
        throw new Error('Failed to get initial greeting');
      }

      const reader = res.body?.getReader();
      if (!reader) return;

      let fullResponse = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = new TextDecoder().decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.content) {
                fullResponse += data.content;
                setMessages(prev => {
                  const newMessages = [...prev];
                  const lastMessage = newMessages[newMessages.length - 1];
                  if (lastMessage && lastMessage.type === 'system') {
                    lastMessage.content = fullResponse;
                  } else {
                    newMessages.push({
                      type: 'system',
                      content: fullResponse,
                      timestamp: new Date().toISOString(),
                    });
                  }
                  return newMessages;
                });
              }
            } catch (e) {
              console.warn('Error parsing SSE data:', e);
            }
          }
        }
      }
    } catch (error) {
      console.error('Error getting initial greeting:', error);
      pushSys('⚠️ Failed to connect to server. Please check your connection and try again.', new Date().toISOString());
    }
  };

  const initSession = async () => {
    const userId = `demo_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    try {
      const apiBase = window.location.hostname === 'localhost' ? 'http://127.0.0.1:8002' : 'https://psychnow-api.onrender.com';
      const res = await fetch(`${apiBase}/api/v1/intake/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          patient_id: userId,
          user_name: null
        }),
      });
      
      if (!res.ok) {
        throw new Error('Failed to start session');
      }
      
      const data = await res.json();
      sessionRef.current = data.session_token;
      setSessionId(data.session_token.slice(0, 8));
      
      // Store session ID for recovery
      localStorage.setItem('psychnow_session_id', data.session_token);
      
      await getInitialGreeting();
      
    } catch (err) {
      console.error('Failed to start session:', err);
      pushSys('⚠️ Failed to start session. Please refresh the page and try again.', new Date().toISOString());
    }
  };

  const pushSys = (content: string, timestamp: string) => {
    setMessages(prev => [...prev, {
      type: 'system',
      content,
      timestamp,
    }]);
  };

  const pushPatient = (content: string) => {
    setMessages(prev => [...prev, {
      type: 'patient',
      content,
      timestamp: new Date().toISOString(),
    }]);
  };

  const sendMessage = async (prompt: string) => {
    if (!prompt.trim() || busy) return;
    
    if (prompt.trim() !== ":finish") {
      pushPatient(prompt);
    }
    
    setBusy(true);
    await sendMessageToBackend(prompt);
  };

  const sendMessageWithoutAddingUser = async (prompt: string) => {
    if (!prompt.trim() || busy) return;
    
    setBusy(true);
    await sendMessageToBackend(prompt);
  };

  const handleFinish = async () => {
    if (busy) return;
    
    setBusy(true);
    await sendMessageToBackend(":finish");
  };

  const handleResumeSession = async () => {
    if (!sessionRef.current) return;
    
    try {
      setBusy(true);
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/v1/intake/session/${sessionRef.current}/recover`);
      
      if (response.ok) {
        const data = await response.json();
        pushSys(`✅ Session recovered! Continuing from where we left off...`, new Date().toISOString());
        
        // Restore conversation history
        if (data.conversation_history && data.conversation_history.length > 0) {
          setMessages(data.conversation_history);
        } else {
          // If no conversation history, start fresh but keep the session
          pushSys(`ℹ️ No previous conversation found. Starting fresh with existing session.`, new Date().toISOString());
        }
      } else {
        pushSys(`❌ Could not recover session. Please start a new assessment.`, new Date().toISOString());
      }
    } catch (error) {
      console.error('Recovery error:', error);
      pushSys(`❌ Recovery failed. Please start a new assessment.`, new Date().toISOString());
    } finally {
      setBusy(false);
    }
  };

  const sendMessageToBackend = async (prompt: string) => {
    try {
      const apiBase = window.location.hostname === 'localhost' ? 'http://127.0.0.1:8002' : 'https://psychnow-api.onrender.com';
      const res = await fetch(`${apiBase}/api/v1/intake/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_token: sessionRef.current,
          prompt: prompt
        })
      });
      
      if (res.status === 429) {
        pushSys('⏱️ Please slow down a bit. Wait a few seconds and try again.', new Date().toISOString());
        setBusy(false);
        return;
      }
      
      if (!res.ok) {
        throw new Error('Backend request failed');
      }

      const reader = res.body?.getReader();
      if (reader) {
        let fullResponse = '';
        let isFirstChunk = true;

        while (true) {
          const { done, value } = await reader.read();
          if (done) {
            setBusy(false);
            break;
          }

          const chunk = new TextDecoder().decode(value);
          const lines = chunk.split('\n');
          
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                if (data.content) {
                  fullResponse += data.content;
                  
                  if (isFirstChunk) {
                    setMessages(prev => [...prev, {
                      type: 'system',
                      content: data.content,
                      timestamp: new Date().toISOString(),
                    }]);
                    isFirstChunk = false;
                  } else {
                    setMessages(prev => {
                      const newMessages = [...prev];
                      const lastMessage = newMessages[newMessages.length - 1];
                      if (lastMessage && lastMessage.type === 'system') {
                        lastMessage.content = fullResponse;
                      }
                      return newMessages;
                    });
                  }
                }
                
                if (data.options) {
                  setMessages(prev => {
                    const newMessages = [...prev];
                    const lastMessage = newMessages[newMessages.length - 1];
                    if (lastMessage && lastMessage.type === 'system') {
                      lastMessage.options = data.options;
                    }
                    return newMessages;
                  });
                }
                
                // Handle PDFs (both patient and clinician versions)
                if (data.patient_pdf) {
                  console.log('📄 Patient PDF received');
                  setPatientPdfBase64(data.patient_pdf);
                  setMessages(prev => {
                    const newMessages = [...prev];
                    const lastMessage = newMessages[newMessages.length - 1];
                    if (lastMessage && lastMessage.type === 'system') {
                      lastMessage.patient_pdf = data.patient_pdf;
                    }
                    return newMessages;
                  });
                }
                
                if (data.clinician_pdf) {
                  console.log('🩺 Clinician PDF received');
                  setClinicianPdfBase64(data.clinician_pdf);
                  setMessages(prev => {
                    const newMessages = [...prev];
                    const lastMessage = newMessages[newMessages.length - 1];
                    if (lastMessage && lastMessage.type === 'system') {
                      lastMessage.clinician_pdf = data.clinician_pdf;
                    }
                    return newMessages;
                  });
                }
                
                // Legacy support for single PDF
                if (data.pdf_report && !data.patient_pdf) {
                  console.log('📄 PDF report received (legacy)');
                  setPatientPdfBase64(data.pdf_report);
                  setMessages(prev => {
                    const newMessages = [...prev];
                    const lastMessage = newMessages[newMessages.length - 1];
                    if (lastMessage && lastMessage.type === 'system') {
                      lastMessage.pdf_report = data.pdf_report;
                    }
                    return newMessages;
                  });
                }
                
                if (data.done) {
                  setBusy(false);
                  
                  if (fullResponse.includes('Assessment complete') || fullResponse.includes('Assessment Summary')) {
                    setFinished(true);
                    
                    // Navigate to feedback page after a short delay (with or without PDFs)
                    setTimeout(() => {
                      if (sessionRef.current) {
                        navigate('/complete', {
                          state: {
                            sessionId: sessionRef.current,
                            patientPdf: data.patient_pdf || patientPdfBase64 || null,
                            clinicianPdf: data.clinician_pdf || clinicianPdfBase64 || null
                          }
                        });
                      }
                    }, 1500);
                  }
                  
                  if (fullResponse.includes('error while generating your report') || 
                      fullResponse.includes('Error generating report')) {
                    setReportGenerationFailed(true);
                  }
                }
              } catch (e) {
                // Ignore parsing errors
              }
            }
          }
        }
      }
    } catch (error) {
      console.error('Backend error:', error);
      
      // Enhanced error handling with recovery options
      const errorMessage = `⚠️ I encountered an error processing your message. 

Don't worry - your conversation is saved and you can continue where you left off.

Your progress is safe and won't be lost.`;
      
      pushSys(errorMessage, new Date().toISOString());
      
      // Add recovery options
      setTimeout(() => {
        pushSys(`🔄 **Recovery Options:**

• **Try Again:** Simply retype your message and send it
• **Continue:** I'll ask you a different question to keep the assessment moving
• **Resume:** If you refresh the page, you can resume exactly where you left off

Your session ID is: \`${sessionId}\` (save this if you need to resume later)`, new Date().toISOString());
      }, 1000);
      
      setBusy(false);
    }
  };

  const downloadPDF = (pdfBase64: string) => {
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
      link.download = `PsychNow_Assessment_Demo_${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading PDF:', error);
    }
  };

  const retryReportGeneration = () => {
    setReportGenerationFailed(false);
    sendMessageWithoutAddingUser(':finish');
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !busy) {
      sendMessage(input);
      setInput('');
    }
  };

  const handleOptionClick = (option: string) => {
    if (!busy) {
      if (option !== ":finish") {
        setMessages(prev => [...prev, {
          type: 'patient',
          content: option,
          timestamp: new Date().toISOString(),
        }]);
      } else {
        setMessages(prev => [...prev, {
          type: 'patient',
          content: "Complete Assessment",
          timestamp: new Date().toISOString(),
        }]);
      }
      
      sendMessageWithoutAddingUser(option);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <div className="sticky top-0 z-50 bg-white shadow-sm border-b px-3 md:px-6 py-3 md:py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2 md:space-x-3 min-w-0 flex-1">
            <div className="w-8 h-8 md:w-10 md:h-10 bg-blue-600 rounded-full flex items-center justify-center flex-shrink-0">
              <span className="text-white font-semibold text-sm md:text-base">A</span>
            </div>
            <div className="min-w-0">
              <h1 className="text-sm md:text-lg font-semibold text-gray-900 truncate">Ava - Mental Health Assessment</h1>
              <p className="text-xs md:text-sm text-gray-500 truncate">Demo Session {sessionId}</p>
            </div>
          </div>
          <CustomButton
            onClick={() => navigate('/')}
            variant="secondary"
            className="text-xs md:text-sm px-3 md:px-4 py-2 font-medium flex items-center gap-2"
          >
            <Home className="w-4 h-4" />
            <span className="hidden sm:inline">Home</span>
          </CustomButton>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 overflow-hidden flex flex-col">
        <div className="flex-1 overflow-y-auto p-3 md:p-6 flex flex-col gap-3 md:gap-4">
          {messages.map((msg, idx) => (
            <div key={idx} className="flex">
              <div className={msg.type === 'patient' ? 'max-w-[95%] md:max-w-[85%] ml-auto mr-2 md:mr-4' : 'max-w-[95%] md:max-w-[85%] ml-2 md:ml-4'}>
                <ChatBubble type={msg.type}>
                  <div className="whitespace-pre-wrap">{msg.content}</div>
                  {msg.options && msg.type === 'system' && (
                    <div className="mt-3 space-y-2">
                      {msg.options.map((option: any, optionIdx: number) => (
                        <button
                          key={optionIdx}
                          onClick={() => handleOptionClick(option.value)}
                          className="w-full text-left px-4 py-2 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg text-blue-800 font-medium transition-colors"
                        >
                          {option.label}
                        </button>
                      ))}
                    </div>
                  )}
                  {msg.pdf_report && (
                    <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                      <div className="flex items-center justify-between flex-wrap gap-3">
                        <div>
                          <h4 className="font-semibold text-green-800">📄 Assessment Report Generated</h4>
                          <p className="text-sm text-green-600 mt-1">Your comprehensive clinical report is ready</p>
                        </div>
                        <button
                          onClick={() => downloadPDF(msg.pdf_report!)}
                          className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition-colors"
                        >
                          Download PDF
                        </button>
                      </div>
                    </div>
                  )}
                  {msg.timestamp && (
                    <div className="text-xs text-gray-400 mt-1">
                      {new Date(msg.timestamp).toLocaleTimeString()}
                    </div>
                  )}
                </ChatBubble>
              </div>
            </div>
          ))}
          {busy && (
            <div>
              <ChatBubble type="system">
                <div className="flex items-center space-x-2">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                  <span className="text-sm text-gray-500">Ava is thinking...</span>
                </div>
              </ChatBubble>
            </div>
          )}
          
          {reportGenerationFailed && !busy && (
            <div className="flex justify-center my-4">
              <CustomButton
                onClick={retryReportGeneration}
                variant="primary"
                className="bg-orange-600 hover:bg-orange-700 text-white px-6 py-3 rounded-lg shadow-lg"
              >
                🔄 Retry Report Generation
              </CustomButton>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="border-t bg-white p-3 md:p-4">
          {!finished ? (
            <div className="space-y-3">
              <form onSubmit={handleSubmit} className="flex flex-row gap-2 md:gap-3 items-center">
                <CustomInput
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type your response here..."
                  disabled={busy}
                  className="flex-1 text-base md:text-lg h-[48px] md:h-[50px] px-4"
                />
                <CustomButton
                  type="submit"
                  variant="primary"
                  disabled={!input.trim() || busy}
                  className="flex-shrink-0 w-auto min-w-[80px] md:min-w-[100px] h-[48px] md:h-[50px] px-4 md:px-6 text-base md:text-lg font-medium"
                >
                  Send
                </CustomButton>
              </form>
              
              {/* Action Buttons - Separated from Send to prevent accidental clicks */}
              <div className="flex justify-center gap-3">
                <CustomButton
                  type="button"
                  onClick={() => handleFinish()}
                  variant="secondary"
                  disabled={busy}
                  className="px-6 py-2 text-sm font-medium border-orange-300 text-orange-700 hover:bg-orange-50 bg-orange-25"
                >
                  🏁 Complete Assessment Early
                </CustomButton>
                
                {/* Resume Session Button - appears if there's an error */}
                {messages.some(msg => msg.content.includes('encountered an error')) && (
                  <CustomButton
                    type="button"
                    onClick={handleResumeSession}
                    variant="secondary"
                    disabled={busy}
                    className="px-6 py-2 text-sm font-medium border-green-300 text-green-700 hover:bg-green-50 bg-green-25"
                  >
                    🔄 Resume Session
                  </CustomButton>
                )}
              </div>
            </div>
          ) : (
            <div className="text-center py-4">
              <p className="text-gray-700 font-medium mb-2">✅ Assessment completed!</p>
              <p className="text-sm text-gray-500">Thank you for testing the PsychNow demo.</p>
            </div>
          )}
          <div className="text-xs text-gray-400 mt-2 text-center">
            {!finished ? "Ava will guide you through the assessment • Use 'Complete Assessment Early' button below to finish anytime" : "Assessment complete - Please review the report"}
          </div>
        </div>
      </div>
    </div>
  );
}

