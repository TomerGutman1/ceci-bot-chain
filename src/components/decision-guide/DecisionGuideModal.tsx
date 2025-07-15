import React, { useState, useCallback, useRef } from 'react';
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

export function DecisionGuideModal({ isOpen, onClose }: DecisionGuideModalProps) {
  const [mode, setMode] = useState<'upload' | 'paste'>('upload');
  const [textContent, setTextContent] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResults, setAnalysisResults] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

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
    if (!file && !textContent.trim()) {
      setError('אנא העלה קובץ או הדבק טקסט לניתוח.');
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    try {
      const results = await analyzeDecisionDraft(file, textContent);
      setAnalysisResults(results);
      
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
      setError('אירעה שגיאה בניתוח. אנא נסה שוב.');
      console.error('Analysis error:', err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleReset = () => {
    setAnalysisResults(null);
    setFile(null);
    setTextContent('');
    setError(null);
  };

  const handleBackToChat = () => {
    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        {!analysisResults ? (
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
                  disabled={(!file && !textContent.trim()) || isAnalyzing}
                >
                  {isAnalyzing ? 'מנתח...' : 'שלח לניתוח'}
                </Button>
              </div>
            </div>
          </>
        ) : (
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
        )}
      </DialogContent>
    </Dialog>
  );
}