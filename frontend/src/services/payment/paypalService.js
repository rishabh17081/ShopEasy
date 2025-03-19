import axios from 'axios';
import { getAuthToken } from '../api';

const BASE_URL = '/api/cards';

export const PayPalService = {
  /**
   * Update the PayPal subscription ID for a specific card
   * @param {number} cardId - The ID of the card
   * @param {string} subscriptionId - The PayPal subscription ID
   * @returns {Promise} - Resolves with the updated card information
   */
  updateCardSubscription: async (cardId, subscriptionId) => {
    try {
      const response = await axios.post(
        `${BASE_URL}/update_subscription`, 
        { card_id: cardId, subscription_id: subscriptionId },
        {
          headers: {
            'Authorization': `Bearer ${getAuthToken()}`,
            'Content-Type': 'application/json'
          }
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error updating card subscription:', error);
      throw error;
    }
  },

  /**
   * Retrieve the subscription ID for a specific card
   * @param {number} cardId - The ID of the card
   * @returns {Promise} - Resolves with the card's subscription ID
   */
  getCardSubscription: async (cardId) => {
    try {
      const response = await axios.get(
        `${BASE_URL}/subscription`, 
        {
          params: { card_id: cardId },
          headers: {
            'Authorization': `Bearer ${getAuthToken()}`,
            'Content-Type': 'application/json'
          }
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error retrieving card subscription:', error);
      throw error;
    }
  },

  /**
   * Create a PayPal subscription for a card
   * @param {string} pan - Primary Account Number (card number)
   * @param {string} expiryDate - Card expiry date in YYYY-MM format
   * @returns {Promise} - Resolves with the subscription details
   */
  createCardSubscription: async (pan, expiryDate) => {
    try {
      const response = await axios.post(
        '/api/paypal/create_subscription', 
        { pan, expiry_date: expiryDate },
        {
          headers: {
            'Authorization': `Bearer ${getAuthToken()}`,
            'Content-Type': 'application/json'
          }
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error creating card subscription:', error);
      throw error;
    }
  }
};
