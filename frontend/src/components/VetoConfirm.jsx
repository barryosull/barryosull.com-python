import { useState, useEffect } from 'react';
import '../../assets/styles.css';

export default function VetoConfirm({
  gameState,
  myPlayerId,
  onVeto
}) {
  const [loading, setLoading] = useState(false);
  const [isFadingOut, setIsFadingOut] = useState(false);
  
  useEffect(() => {
    setIsFadingOut(false);
  }, []);

  const handleVeto = async (approve) => {
    setLoading(true);
    try {
      setIsFadingOut(true);
      setTimeout(async () => {
        await onVeto(approve);
      }, 300);
    } finally {
      setLoading(false);
    }
  };

  // Check for veto state first, before isMyTurn check
  if (!gameState.veto_requested) {
    return null;
  }
  
  const isPresidentPlayer = gameState.president_id === myPlayerId;
  if (!isPresidentPlayer) {
    return null;   
  }  

  return (
    <div className={`overlay ${isFadingOut ? 'fade-out' : 'fade-in'}`}>
      <div className="overlay-content">
        <h3 className="overlay-title">Veto Request</h3>
        <div className="overlay-subtitle">
          The Chancellor has requested to veto the agenda. Do you approve?
        </div>

        <div className="veto-buttons">
          <button
            onClick={() => handleVeto(true)}
            className="veto-button approve"
            disabled={loading}
          >
            Approve Veto
          </button>
          <button
            onClick={() => handleVeto(false)}
            className="veto-button reject"
            disabled={loading}
          >
            Reject Veto
          </button>
        </div>
      </div>
    </div>
  );
}
