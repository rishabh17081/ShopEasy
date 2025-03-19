import React, { useEffect, useRef, useState } from 'react';
import './PayPalButton.css';

const PayPalButton = ({ amount, onSuccess, onError }) => {
  const paypalRef = useRef();
  const [errorHandled, setErrorHandled] = useState(false);
  
  // Wrap the onError callback to ensure errors are always handled
  const safeOnError = (err) => {
    // Mark that we've handled an error
    setErrorHandled(true);
    
    // Prevent the error from propagating
    try {
      if (onError && typeof onError === 'function') {
        onError(err);
      }
    } catch (callbackError) {
      // Silently suppress any errors from the error handler itself
      console.log('[Suppressed] Error in error handler');
    }
  };

  useEffect(() => {
    try {
      // Check if the script is already loaded to prevent duplicate loading
      if (document.querySelector('script[src*="paypal.com/sdk/js"]')) {
        initializePayPalButtons();
        return;
      }
  
      // Load the PayPal JS SDK script
      const script = document.createElement('script');
      script.src = 'https://www.paypal.com/sdk/js?client-id=AYPClqv81q430Lb3nz1Ld0dMKzgIGe6n5jIOZDJMAWpZKkS3wM6R9l2wv-tmb2_O9JMbas5aiEEAwtqC&currency=USD';
      script.async = true;
  
      script.onload = () => {
        try {
          initializePayPalButtons();
        } catch (initError) {
          safeOnError(initError);
        }
      };
  
      script.onerror = (err) => {
        // Silently handle script loading errors
        safeOnError('Failed to load PayPal SDK');
      };
  
      document.body.appendChild(script);
  
      // Cleanup function
      return () => {
        // We should not remove the script when component unmounts
        // as it could be used by other components or on page navigation
      };
    } catch (error) {
      // Catch any errors in the effect itself
      safeOnError(error);
    }
  }, [amount]); // Only re-run if amount changes

  const initializePayPalButtons = () => {
    try {
      if (!window.paypal) {
        // If PayPal SDK is not available, fail silently
        return;
      }
      
      if (!paypalRef.current) {
        // If the ref is not available, fail silently
        return;
      }
      
      // Clear existing buttons (if any)
      paypalRef.current.innerHTML = '';

      // Safely handle amount
      let safeAmount = '0.00';
      try {
        const numAmount = Number(amount);
        safeAmount = !isNaN(numAmount) ? numAmount.toFixed(2) : '0.00';
      } catch (e) {
        // Silently handle amount parsing errors
        safeAmount = '0.00';
      }

      try {
        window.paypal.Buttons({
          // Set up the transaction
          createOrder: (data, actions) => {
            try {
              return actions.order.create({
                purchase_units: [
                  {
                    amount: {
                      value: safeAmount,
                      currency_code: 'USD'
                    }
                  }
                ]
              });
            } catch (createOrderError) {
              // Silently handle createOrder errors
              safeOnError(createOrderError);
              return Promise.reject();
            }
          },
          // Handle successful payments
          onApprove: (data, actions) => {
            try {
              return actions.order.capture().then(function(details) {
                try {
                  if (onSuccess && typeof onSuccess === 'function') {
                    onSuccess(data, details);
                  }
                } catch (successCallbackError) {
                  // Silently handle success callback errors
                  safeOnError(successCallbackError);
                }
              }).catch(captureError => {
                // Silently handle capture errors
                safeOnError(captureError);
              });
            } catch (approveError) {
              // Silently handle onApprove errors
              safeOnError(approveError);
              return Promise.resolve();
            }
          },
          // Handle payment errors
          onError: (err) => {
            // Use our safe error handler
            safeOnError(err);
          }
        }).render(paypalRef.current).catch(renderError => {
          // Silently handle render errors
          safeOnError(renderError);
        });
      } catch (buttonsError) {
        // Silently handle Buttons creation errors
        safeOnError(buttonsError);
      }
    } catch (error) {
      // Silently handle any other errors
      safeOnError(error);
    }
  };

  return (
    <div className="paypal-button-container">
      <div ref={paypalRef}></div>
    </div>
  );
};

export default PayPalButton;
