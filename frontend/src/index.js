import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import App from './App';
import ErrorBoundary from './components/ErrorBoundary';
import { setupGlobalErrorSuppression, setupConsoleErrorSuppression } from './utils/errorHandling';

// Set up global error handling before rendering
setupGlobalErrorSuppression();
setupConsoleErrorSuppression();

// Override the default error handler
const originalOnError = window.onerror;
window.onerror = function(message, source, lineno, colno, error) {
  // Check if we're on the cart page
  if (window.location.pathname === '/cart') {
    console.log('[Suppressed Global Error]', message);
    return true; // Prevent default error handling
  }
  
  // Otherwise use the original handler
  return originalOnError ? originalOnError(message, source, lineno, colno, error) : false;
};

// Create a custom error handler for React
class GlobalErrorHandler extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    // If we're on the cart page, don't show the error UI
    if (window.location.pathname === '/cart') {
      return { hasError: false };
    }
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // If we're on the cart page, suppress the error
    if (window.location.pathname === '/cart') {
      console.log('[Suppressed React Error]', error);
      return;
    }
    console.error('Uncaught React error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError && window.location.pathname !== '/cart') {
      return (
        <div className="error-boundary p-4 bg-light rounded">
          <h2 className="text-danger">Something went wrong.</h2>
          <p>Please try refreshing the page.</p>
        </div>
      );
    }
    return this.props.children;
  }
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <GlobalErrorHandler>
      <ErrorBoundary pathsToSuppress={['/cart']}>
        <App />
      </ErrorBoundary>
    </GlobalErrorHandler>
  </React.StrictMode>
);
