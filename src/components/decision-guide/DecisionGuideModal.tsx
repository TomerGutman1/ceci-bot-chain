import React, { useState, useCallback, useRef, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { useDropzone } from 'react-dropzone';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Upload, FileText, AlertCircle } from 'lucide-react';
import { analyzeDecisionDraft } from '@/services/decisionGuide.service';
import { AnalysisResults } from './AnalysisResults';
import { toast } from '@/components/ui/use-toast';

interface DecisionGuideModalProps {
  isOpen: boolean;
  onClose: () => void;
}

// Analysis status messages
const ANALYSIS_MESSAGES = [
  'הטיוטה התקבלה. מתחילים בניתוח.',
  'בודקים את מבנה הטיוטה ותקינות הנתונים.',
  'מזהים קריטריונים רלוונטיים לציון.',
  'מחשבים מדדי הערכה לפי מתודולוגיית המשרד.',
  'מכינים דו״ח מסכם להצגה.',
  'עוד רגע – מבצעים אימות סופי.'
];

export function DecisionGuideModal({ isOpen, onClose }: DecisionGuideModalProps) {
  const [mode, setMode] = useState<'upload' | 'paste'>('upload');
  const [textContent, setTextContent] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResults, setAnalysisResults] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [currentMessageIndex, setCurrentMessageIndex] = useState(0);
  const [viewState, setViewState] = useState<'input' | 'loading' | 'results'>('input');

  // Rotate messages effect
  useEffect(() => {
    if (viewState !== 'loading') {
      setCurrentMessageIndex(0);
      return;
    }

    const interval = setInterval(() => {
      setCurrentMessageIndex((prev) => (prev + 1) % ANALYSIS_MESSAGES.length);
    }, 8000);

    return () => clearInterval(interval);
  }, [viewState]);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const uploadedFile = acceptedFiles[0];
    if (uploadedFile) {
      // Validate file type
      const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
      if (!validTypes.includes(uploadedFile.type)) {
        setError('סוג קובץ לא נתמך. אנא העלה קובץ PDF, DOCX או TXT.');
        return;
      }
      
      // Validate file size (8MB)
      if (uploadedFile.size > 8 * 1024 * 1024) {
        setError('הקובץ גדול מדי. הגודל המקסימלי הוא 8MB.');
        return;
      }
      
      setFile(uploadedFile);
      setError(null);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive, open } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt']
    },
    maxFiles: 1,
    maxSize: 8 * 1024 * 1024, // 8MB
    noClick: false, // Ensure clicking is enabled
    noKeyboard: false,
  });

  const handleAnalyze = async () => {
    console.log('handleAnalyze called!');
    if (!file && !textContent.trim()) {
      setError('אנא העלה קובץ או הדבק טקסט לניתוח.');
      return;
    }

    console.log('Setting viewState to loading...');
    setViewState('loading');
    setIsAnalyzing(true);
    setError(null);
    
    // Force a small delay to ensure the loading state is shown
    await new Promise(resolve => setTimeout(resolve, 100));

    try {
      
      // Ensure minimum display time for loading modal
      const startTime = Date.now();
      const results = await analyzeDecisionDraft(file, textContent);
      const elapsedTime = Date.now() - startTime;
      
      // If the request was too fast, wait a bit to show the loading state
      if (elapsedTime < 3000) {
        await new Promise(resolve => setTimeout(resolve, 3000 - elapsedTime));
      }
      
      setAnalysisResults(results);
      setViewState('results');
      
      // Show toast if misuse detected
      if (results.misuse_detected) {
        toast({
          title: "שימוש לא תקין",
          description: results.misuse_message,
          variant: "destructive",
        });
        onClose();
        return;
      }
    } catch (err) {
      setError('אירעה שגיאה זמנית. מומלץ לנסות שוב בעוד כמה דקות.');
      console.error('Analysis error:', err);
      setViewState('input');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleReset = () => {
    setAnalysisResults(null);
    setFile(null);
    setTextContent('');
    setError(null);
    setViewState('input');
  };

  const handleBackToChat = () => {
    onClose();
  };

  console.log('DecisionGuideModal render - viewState:', viewState, 'isAnalyzing:', isAnalyzing);

  return (
    <>
      <Dialog open={isOpen} onOpenChange={(open) => {
        // Don't allow closing during analysis
        if (!isAnalyzing && !open) {
          onClose();
        }
      }}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        {viewState === 'results' && analysisResults ? (
          <>
            <DialogHeader>
              <DialogTitle className="text-2xl text-center">תוצאות ניתוח ההחלטה</DialogTitle>
            </DialogHeader>
            
            <AnalysisResults
              results={analysisResults}
              onReset={handleReset}
              onBackToChat={handleBackToChat}
            />
          </>
        ) : (
          <>
            <DialogHeader>
              <DialogTitle className="text-2xl text-center">שיפור ניסוח ישימות החלטת ממשלה</DialogTitle>
              <DialogDescription className="text-center text-lg">
                העלה קובץ PDF של החלטת ממשלה או הדבק נוסח – וקבל פידבק מיידי לשיפור
              </DialogDescription>
            </DialogHeader>

            <div className="mt-6">
              {/* Mode Toggle */}
              <div className="flex justify-center gap-4 mb-6">
                  <Button
                    variant={mode === 'upload' ? 'default' : 'outline'}
                    onClick={() => setMode('upload')}
                  >
                    <Upload className="ml-2 h-4 w-4" />
                    העלאת קובץ
                  </Button>
                  <Button
                    variant={mode === 'paste' ? 'default' : 'outline'}
                    onClick={() => setMode('paste')}
                  >
                    <FileText className="ml-2 h-4 w-4" />
                    הדבקת טקסט
                  </Button>
                </div>

              {/* Upload Mode */}
              {mode === 'upload' && (
                <div
                  {...getRootProps()}
                  className={`
                    border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
                    transition-colors duration-200
                    ${isDragActive ? 'border-primary bg-primary/10' : 'border-gray-300 hover:border-gray-400'}
                    ${file ? 'bg-green-50 border-green-300' : ''}
                  `}
                >
                  <input {...getInputProps()} />
                  {file ? (
                    <div className="space-y-2">
                      <FileText className="mx-auto h-12 w-12 text-green-600" />
                      <p className="text-lg font-medium">{file.name}</p>
                      <p className="text-sm text-gray-600">
                        גודל: {(file.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          setFile(null);
                        }}
                      >
                        החלף קובץ
                      </Button>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      <Upload className="mx-auto h-12 w-12 text-gray-400" />
                      <p className="text-lg">
                        {isDragActive ? 'שחרר כאן...' : (
                          <>
                            גרור קובץ לכאן או{' '}
                            <span 
                              className="text-primary underline cursor-pointer hover:text-primary/80"
                              onClick={(e) => {
                                e.stopPropagation();
                                open();
                              }}
                            >
                              לחץ כאן לבחירה
                            </span>
                          </>
                        )}
                      </p>
                      <p className="text-sm text-gray-600">
                        PDF, DOCX או TXT עד 8MB
                      </p>
                    </div>
                  )}
                </div>
              )}

              {/* Paste Mode */}
              {mode === 'paste' && (
                <div className="space-y-4">
                  <Textarea
                    placeholder="הדבק כאן את טקסט טיוטת ההחלטה..."
                    value={textContent}
                    onChange={(e) => setTextContent(e.target.value)}
                    className="min-h-[300px] text-right"
                    dir="rtl"
                  />
                  <p className="text-sm text-gray-600 text-right">
                    {textContent.length} תווים
                  </p>
                </div>
              )}

              {/* Error Message */}
              {error && (
                <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
                  <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
                  <p className="text-red-800">{error}</p>
                </div>
              )}

              {/* Action Buttons */}
              <div className="mt-6 flex justify-between">
                <Button variant="outline" onClick={onClose}>
                  ביטול
                </Button>
                <Button
                  onClick={handleAnalyze}
                  disabled={(!file && !textContent.trim())}
                >
                  שלח לניתוח
                </Button>
              </div>
            </div>
          </>
        )}
      </DialogContent>
    </Dialog>
    
    {/* Loading Overlay */}
    {viewState === 'loading' && createPortal(
      <div className="fixed inset-0 flex items-center justify-center animate-fadeIn" style={{ zIndex: 99999 }}>
        <div className="absolute inset-0 bg-black/60 animate-fadeIn" />
        <div className="relative bg-white rounded-xl shadow-2xl p-8 max-w-md w-full mx-4 animate-scaleIn">
          <div className="flex justify-center mb-6">
            <div className="animate-spin rounded-full h-20 w-20 border-4 border-blue-600 border-t-transparent"></div>
          </div>
          <h3 className="text-2xl font-semibold text-center mb-4 text-gray-900">מנתח את ההחלטה</h3>
          <div className="bg-blue-50 rounded-lg p-4 mb-6">
            <p className="text-center text-blue-900 font-medium text-lg">{ANALYSIS_MESSAGES[currentMessageIndex]}</p>
          </div>
          <div className="flex justify-center gap-2">
            {ANALYSIS_MESSAGES.map((_, i) => (
              <div
                key={i}
                className={`h-2 rounded-full transition-all duration-300 ${
                  i === currentMessageIndex ? 'bg-blue-600 w-8' : 'bg-blue-300 w-2'
                }`}
              />
            ))}
          </div>
        </div>
      </div>,
      document.body
    )}
    </>
  );
}