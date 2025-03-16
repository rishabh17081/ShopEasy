import React from 'react';

const CardForm = ({ 
  formData, 
  onChange, 
  saveCard = false, 
  showSaveOption = false,
  required = true, 
  className = ''
}) => {
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    onChange(name, type === 'checkbox' ? checked : value);
  };

  // Format card number with spaces
  const formatCardNumber = (e) => {
    const input = e.target;
    let value = input.value.replace(/\D/g, ''); // Remove non-digits
    
    if (value.length > 16) {
      value = value.slice(0, 16); // Limit to 16 digits
    }
    
    // Format with spaces after every 4 digits
    const cardNumber = value.replace(/(\d{4})(?=\d)/g, '$1 ');
    
    onChange('cardNumber', cardNumber);
  };

  // Format expiry date with slash
  const formatExpiryDate = (e) => {
    const input = e.target;
    let value = input.value.replace(/\D/g, ''); // Remove non-digits
    
    if (value.length > 4) {
      value = value.slice(0, 4); // Limit to 4 digits (MM/YY)
    }
    
    // Format with slash between month and year
    if (value.length > 2) {
      value = value.slice(0, 2) + '/' + value.slice(2);
    }
    
    onChange('expiryDate', value);
  };

  // Format CVV to be numeric only and limited to 3-4 digits
  const formatCVV = (e) => {
    const input = e.target;
    let value = input.value.replace(/\D/g, ''); // Remove non-digits
    
    if (value.length > 4) {
      value = value.slice(0, 4); // Limit to 4 digits max
    }
    
    onChange('cvv', value);
  };

  return (
    <div className={`card-form ${className}`}>
      <div className="mb-3">
        <label htmlFor="cardNumber" className="form-label">Card Number</label>
        <input
          type="text"
          className="form-control"
          id="cardNumber"
          name="cardNumber"
          value={formData.cardNumber || ''}
          onChange={formatCardNumber}
          placeholder="1234 5678 9012 3456"
          required={required}
          maxLength={19} // 16 digits + 3 spaces
        />
      </div>
      
      <div className="row mb-3">
        <div className="col">
          <label htmlFor="expiryDate" className="form-label">Expiry Date</label>
          <input
            type="text"
            className="form-control"
            id="expiryDate"
            name="expiryDate"
            value={formData.expiryDate || ''}
            onChange={formatExpiryDate}
            placeholder="MM/YY"
            required={required}
            maxLength={5} // MM/YY
          />
        </div>
        <div className="col">
          <label htmlFor="cvv" className="form-label">CVV</label>
          <input
            type="text"
            className="form-control"
            id="cvv"
            name="cvv"
            value={formData.cvv || ''}
            onChange={formatCVV}
            placeholder="123"
            required={required}
            maxLength={4}
          />
        </div>
      </div>

      <div className="mb-3">
        <label htmlFor="cardholderName" className="form-label">Cardholder Name</label>
        <input
          type="text"
          className="form-control"
          id="cardholderName"
          name="cardholderName"
          value={formData.cardholderName || ''}
          onChange={(e) => handleChange(e)}
          placeholder="Name as it appears on card"
          required={required}
        />
      </div>

      {showSaveOption && (
        <div className="mb-3 form-check">
          <input
            type="checkbox"
            className="form-check-input"
            id="saveCardInfo"
            name="saveCardInfo"
            checked={saveCard}
            onChange={(e) => handleChange(e)}
          />
          <label className="form-check-label" htmlFor="saveCardInfo">
            Save this card for future purchases
          </label>
        </div>
      )}
    </div>
  );
};

export default CardForm;