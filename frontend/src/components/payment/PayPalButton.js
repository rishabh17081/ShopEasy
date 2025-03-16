import React, { useEffect, useRef } from 'react';
import './PayPalButton.css';

const PayPalButton = ({ amount, onSuccess, onError }) => {
  const paypalRef = useRef();

  useEffect(() => {
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
      initializePayPalButtons();
    };

    script.onerror = (err) => {
      console.error('Error loading PayPal script:', err);
      if (onError) onError('Failed to load PayPal SDK');
    };

    document.body.appendChild(script);

    // Cleanup function
    return () => {
      // We should not remove the script when component unmounts
      // as it could be used by other components or on page navigation
    };
  }, [amount]); // Only re-run if amount changes

  const initializePayPalButtons = () => {
    try {
      if (window.paypal && paypalRef.current) {
        // Clear existing buttons (if any)
        paypalRef.current.innerHTML = '';

        window.paypal.Buttons({
          // Set up the transaction
          createOrder: (data, actions) => {
            return actions.order.create({
              purchase_units: [
                {
                  amount: {
                    value: Number(amount).toFixed(2),
                    currency_code: 'USD'
                  }
                }
              ]
            });
          },
          // Handle successful payments
          onApprove: (data, actions) => {
            return actions.order.capture().then(function(details) {
              console.log('Transaction completed!');
              if (onSuccess) onSuccess(data, details);
            });
          },
          // Handle payment errors
          onError: (err) => {
            console.error('PayPal Error:', err);
            if (onError) onError(err);
          }
        }).render(paypalRef.current);
      }
    } catch (error) {
      console.error('Error initializing PayPal buttons:', error);
      if (onError) onError(error);
    }
  };

  return (
    <div className="paypal-button-container">
      <div ref={paypalRef}></div>
    </div>
  );
};

export default PayPalButton;