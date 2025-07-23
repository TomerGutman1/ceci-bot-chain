import React, { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';

interface AnalysisLoadingModalProps {
  isOpen: boolean;
}

const ANALYSIS_MESSAGES = [
  'הטיוטה התקבלה. מתחילים בניתוח.',
  'בודקים את מבנה הטיוטה ותקינות הנתונים.',
  'מזהים קריטריונים רלוונטיים לציון.',
  'מחשבים מדדי הערכה לפי מתודולוגיית המשרד.',
  'מכינים דו״ח מסכם להצגה.',
  'עוד רגע – מבצעים אימות סופי.'
];

export function AnalysisLoadingModal({ isOpen }: AnalysisLoadingModalProps) {
  const [currentMessageIndex, setCurrentMessageIndex] = useState(0);

  console.log('AnalysisLoadingModal - isOpen:', isOpen); // Debug log

  useEffect(() => {
    console.log('AnalysisLoadingModal useEffect - isOpen:', isOpen); // Debug log
    if (!isOpen) {
      setCurrentMessageIndex(0);
      return;
    }

    // Set up interval to rotate messages
    const interval = setInterval(() => {
      setCurrentMessageIndex((prevIndex) => {
        if (prevIndex >= ANALYSIS_MESSAGES.length - 1) {
          return 1; // Loop back to message 2
        }
        return prevIndex + 1;
      });
    }, 8000); // 8 seconds

    return () => clearInterval(interval);
  }, [isOpen]);

  if (!isOpen) return null;

  return createPortal(
    <div className="fixed inset-0 z-[9999] flex items-center justify-center">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/50" />
      
      {/* Modal Content */}
      <div className="relative bg-white rounded-lg shadow-2xl max-w-md w-full mx-4 p-8">
        <div className="flex justify-center mb-6">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-600 border-t-transparent"></div>
        </div>
        <h3 className="text-xl font-medium text-center mb-4">מנתח את ההחלטה</h3>
        <div className="bg-blue-50 rounded-lg p-4">
          <p className="text-center text-blue-900 font-medium">{ANALYSIS_MESSAGES[currentMessageIndex]}</p>
        </div>
        <div className="mt-4 flex justify-center">
          <div className="flex gap-1">
            {[0, 1, 2].map((i) => (
              <div
                key={i}
                className={`h-2 w-2 rounded-full bg-blue-600 ${
                  i === currentMessageIndex % 3 ? 'opacity-100' : 'opacity-30'
                } transition-opacity`}
              />
            ))}
          </div>
        </div>
      </div>
    </div>,
    document.body
  );
}