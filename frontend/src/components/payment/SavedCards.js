import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../../contexts/AuthContext';
import { getUserCards, setCardAsDefault, deleteCard } from '../../services/payment/cardService';

const SavedCards = ({ selectedCard, onCardSelect, showManage = false }) => {
  const { currentUser } = useContext(AuthContext);
  const [cards, setCards] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Only fetch cards if a user is logged in
    if (currentUser) {
      fetchUserCards();
    } else {
      setLoading(false);
      setCards([]);
    }
  }, [currentUser]);

  const fetchUserCards = async () => {
    setLoading(true);
    try {
      const response = await getUserCards(currentUser.id);
      if (response.success) {
        setCards(response.data);
        
        // If there are cards but no selection, auto-select the default card
        if (response.data.length > 0 && !selectedCard) {
          const defaultCard = response.data.find(card => card.is_default);
          if (defaultCard && onCardSelect) {
            onCardSelect(defaultCard.id.toString());
          }
        }
      } else {
        setError(response.error || 'Failed to load saved cards');
      }
    } catch (err) {
      setError('An error occurred while fetching your saved cards');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSetDefault = async (cardId) => {
    try {
      const response = await setCardAsDefault(currentUser.id, cardId);
      if (response.success) {
        // Update the local state to reflect the new default card
        setCards(prevCards => prevCards.map(card => ({
          ...card,
          is_default: card.id.toString() === cardId.toString()
        })));
      } else {
        setError(response.error || 'Failed to set card as default');
      }
    } catch (err) {
      setError('An error occurred while updating your card preferences');
      console.error(err);
    }
  };

  const handleDelete = async (cardId) => {
    if (window.confirm('Are you sure you want to delete this card?')) {
      try {
        const response = await deleteCard(currentUser.id, cardId);
        if (response.success) {
          // Remove the card from local state
          setCards(prevCards => prevCards.filter(card => card.id.toString() !== cardId.toString()));
          
          // If the deleted card was selected, clear selection or select another card
          if (selectedCard === cardId.toString() && onCardSelect) {
            const remainingCards = cards.filter(card => card.id.toString() !== cardId.toString());
            if (remainingCards.length > 0) {
              // Select the first card or the default card if available
              const defaultCard = remainingCards.find(card => card.is_default);
              onCardSelect(defaultCard ? defaultCard.id.toString() : remainingCards[0].id.toString());
            } else {
              onCardSelect('');
            }
          }
        } else {
          setError(response.error || 'Failed to delete card');
        }
      } catch (err) {
        setError('An error occurred while deleting your card');
        console.error(err);
      }
    }
  };

  if (!currentUser) {
    return null; // Don't show anything if user is not logged in
  }

  if (loading) {
    return <div className="text-center py-3">Loading your saved cards...</div>;
  }

  if (error) {
    return <div className="alert alert-danger" role="alert">{error}</div>;
  }

  if (cards.length === 0) {
    return <div className="text-muted">You don't have any saved payment methods.</div>;
  }

  return (
    <div className="saved-cards">
      {cards.map(card => (
        <div 
          key={card.id} 
          className={`card mb-2 ${selectedCard === card.id.toString() ? 'border-primary' : ''}`}
          style={{ cursor: onCardSelect ? 'pointer' : 'default' }}
          onClick={() => onCardSelect && onCardSelect(card.id.toString())}
        >
          <div className="card-body p-3">
            <div className="d-flex justify-content-between align-items-center">
              <div>
                <div className="mb-1">
                  <span className="fw-bold">{card.card_type}</span>
                </div>
                <div>**** **** **** {card.last_four}</div>
                <div className="text-muted small">
                  {card.cardholder_name} | Expires: {card.expiry_date}
                </div>
              </div>
              
              {showManage && (
                <div className="card-actions">
                  {!card.is_default && (
                    <button 
                      className="btn btn-sm btn-outline-secondary me-2"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleSetDefault(card.id);
                      }}
                    >
                      Set as Default
                    </button>
                  )}
                  <button 
                    className="btn btn-sm btn-outline-danger"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDelete(card.id);
                    }}
                  >
                    Delete
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default SavedCards;