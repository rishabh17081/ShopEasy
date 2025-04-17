/**
 * Utility functions for error handling and suppression
 */

// List of paths where errors should be suppressed
const ERROR_SUPPRESSION_PATHS = ['/cart'];

/**
 * Check if errors should be suppressed based on the current path
 * @returns {boolean} True if errors should be suppressed
 */
export const shouldSuppressErrors = () => {
  const currentPath = window.location.pathname;
  return ERROR_SUPPRESSION_PATHS.some(path => currentPath.startsWith(path));
};

/**
 * Safely execute a function with error suppression if needed
 * @param {Function} fn The function to execute
 * @param {any} fallbackValue Value to return if an error occurs
 * @param {boolean} forceSuppress Force error suppression regardless of path
 * @returns {any} The result of the function or fallback value
 */
export const safeExecute = (fn, fallbackValue = null, forceSuppress = false) => {
  try {
    return fn();
  } catch (error) {
    if (shouldSuppressErrors() || forceSuppress) {
      // Silently suppress the error
      console.log('[Suppressed Error]', error);
      return fallbackValue;
    }
    // Re-throw if we're not suppressing errors
    throw error;
  }
};

/**
 * Create a global error handler for window.onerror and unhandledrejection
 * @returns {Function} Cleanup function to remove event listeners
 */
export const setupGlobalErrorSuppression = () => {
  const handleError = (event) => {
    if (shouldSuppressErrors()) {
      // Prevent the error from bubbling up
      event.preventDefault();
      event.stopPropagation();
      
      // Log it as suppressed
      console.log('[Suppressed Global Error]', 
        event.error || event.reason || event.message || 'Unknown error');
      
      return true; // Prevent default error handling
    }
    return false;
  };
  
  // Add global error handlers
  window.addEventListener('error', handleError, true);
  window.addEventListener('unhandledrejection', handleError, true);
  
  // Return cleanup function
  return () => {
    window.removeEventListener('error', handleError, true);
    window.removeEventListener('unhandledrejection', handleError, true);
  };
};

/**
 * Override console.error to suppress errors on specific paths
 * @returns {Function} Cleanup function to restore original console.error
 */
export const setupConsoleErrorSuppression = () => {
  // Save the original console.error
  const originalConsoleError = console.error;
  
  // Override console.error
  console.error = (...args) => {
    if (shouldSuppressErrors()) {
      // Log with a prefix indicating it's suppressed
      originalConsoleError('[Suppressed Error]', ...args);
    } else {
      // Normal error logging
      originalConsoleError(...args);
    }
  };
  
  // Return cleanup function
  return () => {
    console.error = originalConsoleError;
  };
};
