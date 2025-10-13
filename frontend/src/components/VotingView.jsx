import { useState, useEffect } from 'react';
import '../../assets/styles.css';

export default function VotingView({ gameState, players, myPlayerId, onVote }) {
  const [loading, setLoading] = useState(false);
  const [isFadingOut, setIsFadingOut] = useState(false);
  const [shouldRender, setShouldRender] = useState(true);

  const handleVote = async (vote) => {
    setLoading(true);
    try {
      await onVote(vote);
      setIsFadingOut(true);
      setTimeout(() => {
        setShouldRender(false);
      }, 300);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setShouldRender(true);
    setIsFadingOut(false);
  }, []);

  const president = players.find((p) => p.player_id === gameState.president_id);
  const nominee = players.find(
    (p) => p.player_id === gameState.nominated_chancellor_id
  );

  const myPlayer = players.find((p) => p.player_id === myPlayerId);
  const canVote = myPlayer && myPlayer.is_alive;
  const isPresident = myPlayerId === gameState.president_id;

  if (!canVote || isPresident || !shouldRender) {
    return null;
  }

  return (
    <div className={`overlay ${isFadingOut ? 'fade-out' : 'fade-in'}`}>
      <div className="overlay-content">
        <h3 className="overlay-title">Election</h3>

        <div className="voting-government-box">
          <div className="voting-role">
            <div className="voting-role-label">President</div>
            <div className="voting-role-name">{president?.name}</div>
          </div>
          <div className="voting-divider">+</div>
          <div className="voting-role">
            <div className="voting-role-label">Chancellor Nominee</div>
            <div className="voting-role-name">{nominee?.name}</div>
          </div>
        </div>

        <div className="voting-vote-section">
          <div className="voting-vote-prompt">
            Vote on the proposed government:
          </div>
          <div className="voting-vote-buttons">
            <button
              onClick={() => handleVote(true)}
              className="voting-vote-button ja"
              disabled={loading}
            >
              Ja (Yes)
            </button>
            <button
              onClick={() => handleVote(false)}
              className="voting-vote-button nein"
              disabled={loading}
            >
              Nein (No)
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
