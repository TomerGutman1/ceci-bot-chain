/**
 * Test Entry Point for Macro Filter View Dashboard
 * Run this to test the dashboard components standalone
 */

import React from 'react';
import { createRoot } from 'react-dom/client';
import TestApp from './TestApp';
import '../test.css';

// Error boundary for testing
class TestErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error?: Error }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('[TestErrorBoundary] Error caught:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-red-50">
          <div className="text-center p-8 bg-white rounded-lg shadow-lg max-w-md mx-4">
            <div className="text-red-500 text-6xl mb-4">❌</div>
            <h1 className="text-xl font-bold text-red-900 mb-2">שגיאה בטעינת הרכיבים</h1>
            <p className="text-red-700 mb-4">
              {this.state.error?.message || 'שגיאה לא ידועה'}
            </p>
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
            >
              טען מחדש
            </button>
            <details className="mt-4 text-left">
              <summary className="cursor-pointer text-sm text-red-600">פרטים טכניים</summary>
              <pre className="mt-2 text-xs bg-red-100 p-2 rounded overflow-auto">
                {this.state.error?.stack}
              </pre>
            </details>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

// Mount the test app
const container = document.getElementById('test-root');
if (!container) {
  // Create container if it doesn't exist
  const root = document.createElement('div');
  root.id = 'test-root';
  document.body.appendChild(root);
  
  const reactRoot = createRoot(root);
  reactRoot.render(
    <React.StrictMode>
      <TestErrorBoundary>
        <TestApp />
      </TestErrorBoundary>
    </React.StrictMode>
  );
} else {
  const reactRoot = createRoot(container);
  reactRoot.render(
    <React.StrictMode>
      <TestErrorBoundary>
        <TestApp />
      </TestErrorBoundary>
    </React.StrictMode>
  );
}

// Console welcome message
console.log(`
🧪 MACRO FILTER VIEW - TEST ENVIRONMENT
=====================================
✅ React ${React.version} loaded
✅ TypeScript enabled  
✅ Hebrew RTL support
✅ All dashboard components available

📋 Available Test Tabs:
• סקירה כללית (Overview)
• מיטוב נתונים (Data Optimizer) 
• השוואת ממשלות (Government Comparison)
• התראות חכמות (Smart Alerts)
• שיתוף דוחות (Report Sharing)
• סביבת עבודה (Personal Workspace)

🔧 Development Mode: Mock data is being used
🚀 Ready for testing!
`);