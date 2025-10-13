import { useState } from 'react';
import '../../assets/styles.css';

export default function NominationView({ players, gameState, myPlayerId, onNominate }) {
  const [selectedChancellor, setSelectedChancellor] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showWaitingOverlay, setShowWaitingOverlay] = useState(true);

  const isPresident = gameState.president_id === myPlayerId;

  const handleNominate = async () => {
    if (!selectedChancellor) return;

    setLoading(true);
    try {
      await onNominate(selectedChancellor);
    } finally {
      setLoading(false);
    }
  };

  const eligiblePlayerIds = gameState.eligible_chancellor_nominees || [];
  const eligiblePlayers = players.filter((p) =>
    eligiblePlayerIds.includes(p.player_id)
  );

  if (!isPresident) {
    if (!showWaitingOverlay) {
      return null;
    }

    return (
      <div className="toast">
        <div className="toast-content">
          <h3 className="toast-title">Nomination Phase</h3>
          <div className="toast-waiting">
            Waiting for President to nominate a Chancellor...
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="overlay">
      <div className="overlay-content">
        <h3 className="overlay-title">Nominate a Chancellor</h3>
        <div className="overlay-subtitle">
          You are the President. Choose a player to nominate as Chancellor.
        </div>

        <div className="executive-player-grid">
          {eligiblePlayers.map((player) => (
            <button
              key={player.player_id}
              onClick={() => setSelectedChancellor(player.player_id)}
              className={`player-button ${selectedChancellor === player.player_id ? 'selected' : ''}`}
              disabled={loading}
            >
              {player.name}
            </button>
          ))}
        </div>

        <button
          onClick={handleNominate}
          className="confirm-button"
          disabled={!selectedChancellor || loading}
        >
          {loading ? 'Nominating...' : 'Confirm Nomination'}
        </button>
      </div>
    </div>
  );
}
