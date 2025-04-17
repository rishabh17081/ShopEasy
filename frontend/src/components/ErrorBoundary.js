import React, { Component } from 'react';

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { 
      hasError: false,
      error: null,
      errorInfo: null,
      suppressErrors: props.suppressErrors || false,
      pathsToSuppress: props.pathsToSuppress || []
    };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    // You can log the error to an error reporting service
    this.setState({ errorInfo });
    
    // Check if we should suppress this error based on current path
    const currentPath = window.location.pathname;
    const shouldSuppress = this.state.suppressErrors || 
      this.state.pathsToSuppress.some(path => currentPath.startsWith(path));
    
    if (!shouldSuppress) {
      console.error("Error caught by ErrorBoundary:", error, errorInfo);
    } else {
      // Log suppressed error with a prefix
      console.log("[Suppressed Error]", error);
    }
  }

  render() {
    // Check if we should suppress this error based on current path
    const currentPath = window.location.pathname;
    const shouldSuppress = this.state.suppressErrors || 
      this.state.pathsToSuppress.some(path => currentPath.startsWith(path));
    
    if (this.state.hasError) {
      // If we should suppress errors on this path, just render children normally
      if (shouldSuppress) {
        return this.props.children;
      }
      
      // Otherwise show the fallback UI
      return (
        <div className="error-boundary p-4 bg-light rounded">
          <h2 className="text-danger">Something went wrong.</h2>
          <p>Please try refreshing the page or contact support if the problem persists.</p>
          {this.props.fallback}
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
