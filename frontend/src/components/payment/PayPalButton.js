import React, { useEffect, useRef } from 'react';
import './PayPalButton.css';

const PayPalButton = ({ amount, onSuccess, onError }) => {
  const paypalRef = useRef();

  useEffect(() => {
    // Load the PayPal JS SDK script
    const script = document.createElement('script');
    script.src = 'https://www.paypal.com/sdk/js?client-id=AdlchHuRCMtJU8TEV1808gahBAlgSLZJULcVEl5-sOgIwLNbIGqK6L4PvBW3v-eE8zLn9LYaLtWsIZP3&currency=USD&components=buttons&enable-funding=venmo,paylater,card';
    script.setAttribute('data-sdk-integration-source', 'button-factory');
    script.async = true;

    script.onload = () => {
      // Initialize PayPal buttons after script loads
      if (window.paypal) {
        window.paypal.Buttons({
          // Set up the transaction
          createOrder: (data, actions) => {
            return actions.order.create({
              purchase_units: [
                {
                  amount: {
                    value: amount.toString(),
                    currency_code: 'USD'
                  }
                }
              ]
            });
          },
          // Handle successful payments
          onApprove: (data, actions) => {
            return actions.order.capture().then(function(details) {
              console.log('Transaction completed by ' + details.payer.name.given_name + '!');
              console.log('Transaction ID: ' + data.orderID);
              onSuccess(data, details);
            });
          },
          // Handle payment errors
          onError: (err) => {
            console.error('PayPal Error:', err);
            onError(err);
          }
        }).render(paypalRef.current);
      }
    };

    document.body.appendChild(script);

    return () => {
      // Clean up - remove the script when component unmounts
      if (document.body.contains(script)) {
        document.body.removeChild(script);
      }
    };
  }, [amount, onSuccess, onError]);

  return (
    <div className="paypal-button-container">
      <div ref={paypalRef}></div>
    </div>
  );
};

export default PayPalButton;
