import axios from 'axios';
import api from '../../services/api';

// Use the API URL from environment variables or default to relative path
const API_URL = 'http://192.0.0.2:5001/api';

// Get all payment cards for the current user
export const getUserCards = async (userId) => {
  try {
    // Make a real API call to the backend to fetch user's cards
    console.log('Fetching cards for user:', userId);
    
    // Use the api instance to make the authenticated request
    const response = await api.get(`${API_URL}/user/cards`);
    
    console.log('Cards API response:', response.data);
    
    // Return the data in the expected format
    return {
      success: true,
      data: response.data
    };
  } catch (error) {
    console.error('Error fetching user cards:', error);
    console.error('Error details:', error.response ? error.response.data : 'No response data');
    
    // Return a graceful error response instead of throwing
    return {
      success: false,
      data: [],
      error: error.message || 'Failed to fetch cards'
    };
  }
};

// Save a new payment card
export const saveCard = async (userId, cardData) => {
  try {
    console.log('Saving card for user:', userId, cardData);
    
    // Format the data for the API
    const apiCardData = {
      card_number: cardData.cardNumber,
      expiry_date: cardData.expiryDate,
      cvv: cardData.cvv,
      cardholder_name: cardData.cardholderName,
      is_default: cardData.isDefault || false
    };
    
    // Make the API call to save the card
    const response = await api.post(`${API_URL}/user/cards`, apiCardData);
    console.log('Save card response:', response.data);
    
    return {
      success: true,
      message: 'Card saved successfully',
      data: response.data
    };
  } catch (error) {
    console.error('Error saving card:', error);
    throw error;
  }
};

// Set a card as the default payment method
export const setCardAsDefault = async (userId, cardId) => {
  try {
    console.log('Setting card as default:', userId, cardId);
    
    // Make the API call to set the card as default
    const response = await api.put(`${API_URL}/user/cards/${cardId}/default`);
    console.log('Set default card response:', response.data);
    
    return {
      success: true,
      message: 'Card set as default successfully'
    };
  } catch (error) {
    console.error('Error setting card as default:', error);
    throw error;
  }
};

// Delete a payment card
export const deleteCard = async (userId, cardId) => {
  try {
    console.log('Deleting card:', userId, cardId);
    
    // Make the API call to delete the card
    const response = await api.delete(`${API_URL}/user/cards/${cardId}`);
    console.log('Delete card response:', response.data);
    
    return {
      success: true,
      message: 'Card deleted successfully'
    };
  } catch (error) {
    console.error('Error deleting card:', error);
    throw error;
  }
};

// Update a payment card
export const updateCard = async (userId, cardId, cardData) => {
  try {
    console.log('Updating card:', userId, cardId, cardData);
    
    // Format the data for the API
    const apiCardData = {};
    
    // Only include fields that are provided
    if (cardData.expiryDate) {
      apiCardData.expiry_date = cardData.expiryDate;
    }
    
    if (cardData.cardholderName) {
      apiCardData.cardholder_name = cardData.cardholderName;
    }
    
    if (cardData.isDefault !== undefined) {
      apiCardData.is_default = cardData.isDefault;
    }
    
    // Make the API call to update the card
    const response = await api.put(`${API_URL}/user/cards/${cardId}`, apiCardData);
    console.log('Update card response:', response.data);
    
    return {
      success: true,
      message: 'Card updated successfully',
      data: response.data
    };
  } catch (error) {
    console.error('Error updating card:', error);
    throw error;
  }
};
