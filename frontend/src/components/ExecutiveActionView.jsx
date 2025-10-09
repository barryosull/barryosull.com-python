import { useState, useEffect } from 'react';
import { api } from '../services/api';
import { useParams } from 'react-router-dom';
import '../../assets/styles.css';

export default function ExecutiveActionView({
  gameState,
  myPlayerId,
  players,
  onUseAction,
  presidentialPower
}) {
  const { roomId } = useParams();
  const [selectedPlayerId, setSelectedPlayerId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [showingPolicies, setShowingPolicies] = useState(false);
  const [showingLoyalty, setShowingLoyalty] = useState(false);
  const [showWaitingOverlay, setShowWaitingOverlay] = useState(true);

  const isPresident = gameState.president_id === myPlayerId;
  const hasPeekedPolicies = gameState.peeked_policies && gameState.peeked_policies.length > 0;

  const handleExecute = async () => {
    if (presidentialPower === 'POLICY_PEEK' && hasPeekedPolicies && !showingPolicies) {
      setShowingPolicies(true);
      setTimeout(async () => {
        await onUseAction(null);
      }, 3000);
      return;
    }

    if (presidentialPower === 'INVESTIGATE_LOYALTY' && !showingLoyalty) {
      setLoading(true);
      try {
        const loyaltyResult = await api.investigateLoyalty(roomId, myPlayerId, selectedPlayerId);
        setResult(loyaltyResult);
        setShowingLoyalty(true);
        setLoading(false);
        setTimeout(async () => {
          await onUseAction(selectedPlayerId);
        }, 3000);
      } catch (err) {
        alert(err.message);
        setLoading(false);
      }
      return;
    }

    setLoading(true);
    try {
      const actionResult = await onUseAction(selectedPlayerId);
      setResult(actionResult);
      setSelectedPlayerId(null);
    } finally {
      setLoading(false);
    }
  };

  if (!isPresident) {
    if (!showWaitingOverlay) {
      return null;
    }

    return (
      <div className="overlay">
        <div className="overlay-content">
          <h3 className="overlay-title">Executive Action</h3>
          <div className="overlay-waiting">
            Waiting for President to use their executive power...
          </div>
          <button
            onClick={() => setShowWaitingOverlay(false)}
            className="close-button"
          >
            Close
          </button>
        </div>
      </div>
    );
  }

  const needsTarget = presidentialPower === 'INVESTIGATE_LOYALTY'
    || presidentialPower === 'EXECUTION'
    || presidentialPower === 'CALL_SPECIAL_ELECTION';

  const eligiblePlayers = needsTarget
    ? players.filter(p => {
        if (p.player_id === myPlayerId) return false;
        if (presidentialPower === 'EXECUTION' && !p.is_alive) return false;
        if (presidentialPower === 'CALL_SPECIAL_ELECTION' && !p.is_alive) return false;
        return true;
      })
    : [];

  const getPowerDescription = () => {
    switch (presidentialPower) {
      case 'INVESTIGATE_LOYALTY':
        return 'Investigate a player\'s party membership';
      case 'POLICY_PEEK':
        return 'Peek at the top 3 policies';
      case 'EXECUTION':
        return 'Execute a player';
      case 'CALL_SPECIAL_ELECTION':
        return 'Choose the next presidential candidate';
      default:
        return 'Use your executive power';
    }
  };

  return (
    <div className="overlay">
      <div className="overlay-content">
        <h3 className="overlay-title">Executive Action</h3>
        <div className="overlay-subtitle">{getPowerDescription()}</div>

        {showingPolicies && hasPeekedPolicies && (
          <div className="policy-grid">
            {gameState.peeked_policies?.map((policy, index) => (
              <span
                key={index}
                className={`policy-card ${policy.type === 'LIBERAL' ? 'liberal-card' : 'fascist-card'}`}
              ></span>
            ))}
          </div>
        )}

        {result && (
          <div className="executive-result">
            {result.team && (
              <div>
                <strong>Investigation Result:</strong> The player is a{' '}
                <span className={`investigation-result ${result.team === 'LIBERAL' ? 'liberal' : 'fascist'}`}>
                  {result.team}
                </span>
              </div>
            )}
            {result.executed_player_id && (
              <div>
                <strong>Player executed</strong>
                {result.game_over && (
                  <div className="game-over">
                    Game Over! {result.winning_team}s win!
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {needsTarget && !result && !showingPolicies && !showingLoyalty && (
          <div className="executive-player-grid">
            {eligiblePlayers.map((player) => (
              <button
                key={player.player_id}
                onClick={() => setSelectedPlayerId(player.player_id)}
                className={`player-button ${selectedPlayerId === player.player_id ? 'selected' : ''}`}
                disabled={loading}
              >
                {player.name}
              </button>
            ))}
          </div>
        )}

        {!showingPolicies && !showingLoyalty && (
          <button
            onClick={handleExecute}
            className="confirm-button"
            disabled={(needsTarget && !selectedPlayerId && !result) || loading}
          >
            {loading ? 'Using Power...' : result ? 'Continue' : hasPeekedPolicies && presidentialPower === 'POLICY_PEEK' ? 'View Policies' : 'Use Power'}
          </button>
        )}

        {(showingPolicies || showingLoyalty) && (
          <div className="overlay-subtitle">
            Auto-advancing in 3 seconds...
          </div>
        )}
      </div>
    </div>
  );
}
