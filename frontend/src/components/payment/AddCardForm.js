import React, { useState } from 'react';
import { saveCard } from '../../services/payment/cardService';

const AddCardForm = ({ userId, onCardAdded, onCancel }) => {
  const [formData, setFormData] = useState({
    cardNumber: '',
    expiryDate: '',
    cvv: '',
    cardholderName: '',
    isDefault: false
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState(null);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
    
    // Clear error when field is edited
    if (errors[name]) {
      setErrors({
        ...errors,
        [name]: null
      });
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    // Card number validation (basic check for length and format)
    if (!formData.cardNumber.trim()) {
      newErrors.cardNumber = 'Card number is required';
    } else if (!/^\d{13,19}$/.test(formData.cardNumber.replace(/\s/g, ''))) {
      newErrors.cardNumber = 'Invalid card number format';
    }
    
    // Expiry date validation (MM/YY or MM/YYYY format)
    if (!formData.expiryDate.trim()) {
      newErrors.expiryDate = 'Expiry date is required';
    } else if (!/^(0[1-9]|1[0-2])\/(\d{2}|\d{4})$/.test(formData.expiryDate)) {
      newErrors.expiryDate = 'Invalid expiry date format (MM/YY or MM/YYYY)';
    } else {
      // Check if card is expired
      const [month, year] = formData.expiryDate.split('/');
      const expYear = year.length === 2 ? '20' + year : year;
      const expDate = new Date(parseInt(expYear), parseInt(month) - 1, 1);
      const today = new Date();
      
      if (expDate < today) {
        newErrors.expiryDate = 'Card has expired';
      }
    }
    
    // CVV validation (3-4 digits)
    if (!formData.cvv.trim()) {
      newErrors.cvv = 'CVV is required';
    } else if (!/^\d{3,4}$/.test(formData.cvv)) {
      newErrors.cvv = 'CVV should be 3-4 digits';
    }
    
    // Cardholder name validation
    if (!formData.cardholderName.trim()) {
      newErrors.cardholderName = 'Cardholder name is required';
    } else if (formData.cardholderName.trim().length < 3) {
      newErrors.cardholderName = 'Cardholder name is too short';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setLoading(true);
    setApiError(null);
    
    try {
      const response = await saveCard(userId, formData);
      
      if (response.success) {
        // Reset form
        setFormData({
          cardNumber: '',
          expiryDate: '',
          cvv: '',
          cardholderName: '',
          isDefault: false
        });
        
        // Notify parent component
        if (onCardAdded) {
          onCardAdded(response.data);
        }
      } else {
        setApiError(response.error || 'Failed to save card. Please try again.');
      }
    } catch (error) {
      console.error('Error saving card:', error);
      setApiError('An unexpected error occurred. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const formatCardNumber = (value) => {
    // Remove all spaces
    const v = value.replace(/\s+/g, '');
    // Add a space after every 4 characters
    const formatted = v.replace(/(\d{4})/g, '$1 ').trim();
    return formatted;
  };

  return (
    <div className="add-card-form">
      {apiError && (
        <div className="alert alert-danger mb-3" role="alert">
          {apiError}
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <div className="mb-3">
          <label htmlFor="cardNumber" className="form-label">Card Number</label>
          <input
            type="text"
            className={`form-control ${errors.cardNumber ? 'is-invalid' : ''}`}
            id="cardNumber"
            name="cardNumber"
            value={formData.cardNumber}
            onChange={(e) => {
              const formatted = formatCardNumber(e.target.value);
              setFormData({ ...formData, cardNumber: formatted });
            }}
            placeholder="1234 5678 9012 3456"
            maxLength="19"
            required
          />
          {errors.cardNumber && (
            <div className="invalid-feedback">{errors.cardNumber}</div>
          )}
        </div>
        
        <div className="row mb-3">
          <div className="col">
            <label htmlFor="expiryDate" className="form-label">Expiry Date</label>
            <input
              type="text"
              className={`form-control ${errors.expiryDate ? 'is-invalid' : ''}`}
              id="expiryDate"
              name="expiryDate"
              value={formData.expiryDate}
              onChange={handleChange}
              placeholder="MM/YY"
              maxLength="7"
              required
            />
            {errors.expiryDate && (
              <div className="invalid-feedback">{errors.expiryDate}</div>
            )}
          </div>
          
          <div className="col">
            <label htmlFor="cvv" className="form-label">CVV</label>
            <input
              type="password"
              className={`form-control ${errors.cvv ? 'is-invalid' : ''}`}
              id="cvv"
              name="cvv"
              value={formData.cvv}
              onChange={handleChange}
              placeholder="123"
              maxLength="4"
              required
            />
            {errors.cvv && (
              <div className="invalid-feedback">{errors.cvv}</div>
            )}
          </div>
        </div>
        
        <div className="mb-3">
          <label htmlFor="cardholderName" className="form-label">Cardholder Name</label>
          <input
            type="text"
            className={`form-control ${errors.cardholderName ? 'is-invalid' : ''}`}
            id="cardholderName"
            name="cardholderName"
            value={formData.cardholderName}
            onChange={handleChange}
            placeholder="John Doe"
            required
          />
          {errors.cardholderName && (
            <div className="invalid-feedback">{errors.cardholderName}</div>
          )}
        </div>
        
        <div className="mb-3 form-check">
          <input
            type="checkbox"
            className="form-check-input"
            id="isDefault"
            name="isDefault"
            checked={formData.isDefault}
            onChange={handleChange}
          />
          <label className="form-check-label" htmlFor="isDefault">
            Set as default payment method
          </label>
        </div>
        
        <div className="d-flex justify-content-end">
          {onCancel && (
            <button
              type="button"
              className="btn btn-outline-secondary me-2"
              onClick={onCancel}
              disabled={loading}
            >
              Cancel
            </button>
          )}
          
          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                Saving...
              </>
            ) : (
              'Save Card'
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default AddCardForm;