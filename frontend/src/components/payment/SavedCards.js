import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../../contexts/AuthContext';
import { getUserCards, setCardAsDefault, deleteCard } from '../../services/payment/cardService';

const SavedCards = ({ selectedCard, onCardSelect, showManage = false }) => {
  const { currentUser } = useContext(AuthContext);
  const [cards, setCards] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Function to check if a card is expired
  const isCardExpired = (expiryDate) => {
    // Parse the expiry date (format: MM/YYYY)
    const [month, year] = expiryDate.split('/');
    
    // Create a date object for the expiry date (last day of the month)
    const expiryDateObj = new Date(parseInt(year), parseInt(month) - 1, 1);
    expiryDateObj.setMonth(expiryDateObj.getMonth() + 1, 0); // Last day of the month
    
    // Create a date object for the cutoff date (07/2025)
    const cutoffDate = new Date(2025, 10, 31); // July 31, 2025
    
    // Compare the dates
    return expiryDateObj < cutoffDate;
  };

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
        
        // If there are cards but no selection, auto-select the default card or a non-expired card
        if (response.data.length > 0 && !selectedCard && onCardSelect) {
          // First try to find a non-expired default card
          const defaultNonExpiredCard = response.data.find(card => 
            card.is_default && !isCardExpired(card.expiry_date)
          );
          
          if (defaultNonExpiredCard) {
            // Prefer non-expired default card
            onCardSelect(defaultNonExpiredCard.id.toString());
          } else {
            // If no non-expired default card, try to find any non-expired card
            const nonExpiredCard = response.data.find(card => 
              !isCardExpired(card.expiry_date)
            );
            
            if (nonExpiredCard) {
              // Use any non-expired card
              onCardSelect(nonExpiredCard.id.toString());
            } else {
              // If all cards are expired, fall back to the default card
              const defaultCard = response.data.find(card => card.is_default);
              if (defaultCard) {
                onCardSelect(defaultCard.id.toString());
              } else {
                // Last resort: use the first card
                onCardSelect(response.data[0].id.toString());
              }
            }
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
              // First try to find a non-expired default card
              const defaultNonExpiredCard = remainingCards.find(card => 
                card.is_default && !isCardExpired(card.expiry_date)
              );
              
              if (defaultNonExpiredCard) {
                // Prefer non-expired default card
                onCardSelect(defaultNonExpiredCard.id.toString());
              } else {
                // If no non-expired default card, try to find any non-expired card
                const nonExpiredCard = remainingCards.find(card => 
                  !isCardExpired(card.expiry_date)
                );
                
                if (nonExpiredCard) {
                  // Use any non-expired card
                  onCardSelect(nonExpiredCard.id.toString());
                } else {
                  // If all cards are expired, fall back to the default card
                  const defaultCard = remainingCards.find(card => card.is_default);
                  if (defaultCard) {
                    onCardSelect(defaultCard.id.toString());
                  } else {
                    // Last resort: use the first card
                    onCardSelect(remainingCards[0].id.toString());
                  }
                }
              }
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
          onClick={() => {
            if (onCardSelect) {
              // If the card is expired, show a warning before selecting
              if (isCardExpired(card.expiry_date)) {
                if (window.confirm('This card has expired. Are you sure you want to use it?')) {
                  onCardSelect(card.id.toString());
                }
              } else {
                onCardSelect(card.id.toString());
              }
            }
          }}
        >
          <div className={`card-body p-3 ${isCardExpired(card.expiry_date) ? 'bg-light' : ''}`}>
            <div className="d-flex justify-content-between align-items-center">
              <div>
                <div className="mb-1">
                  <span className="fw-bold">{card.card_type}</span>
                  {isCardExpired(card.expiry_date) && (
                    <span className="badge bg-danger ms-2">Expired</span>
                  )}
                </div>
                <div>**** **** **** {card.last_four}</div>
                <div className={`small ${isCardExpired(card.expiry_date) ? 'text-danger' : 'text-muted'}`}>
                  {card.cardholder_name} | Expires: {card.expiry_date}
                  {isCardExpired(card.expiry_date) && ' (Card needs to be updated)'}
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
