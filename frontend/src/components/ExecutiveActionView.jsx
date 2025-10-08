import { useState, useEffect } from 'react';
import { api } from '../services/api';
import { useParams } from 'react-router-dom';

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
      <div style={styles.overlay}>
        <div style={styles.overlayContent}>
          <h3 style={styles.title}>Executive Action</h3>
          <div style={styles.waiting}>
            Waiting for President to use their executive power...
          </div>
          <button
            onClick={() => setShowWaitingOverlay(false)}
            style={styles.closeButton}
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
    <div style={styles.overlay}>
      <div style={styles.overlayContent}>
        <h3 style={styles.title}>Executive Action</h3>
        <div style={styles.subtitle}>{getPowerDescription()}</div>

        {showingPolicies && hasPeekedPolicies && (
          <div style={styles.result}>
            <div>
              <strong>Policy Peek:</strong>
              <div style={styles.policyPeek}>
                {gameState.peeked_policies.map((policy, idx) => (
                  <div
                    key={idx}
                    style={{
                      ...styles.peekedPolicy,
                      ...(policy.type === 'LIBERAL' ? styles.liberalPeek : styles.fascistPeek)
                    }}
                  >
                    {policy.type === 'LIBERAL' ? 'L' : 'F'}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {result && (
          <div style={styles.result}>
            {result.team && (
              <div>
                <strong>Investigation Result:</strong> The player is a{' '}
                <span style={{
                  color: result.team === 'LIBERAL' ? '#2196f3' : '#f44336',
                  fontWeight: 'bold'
                }}>
                  {result.team}
                </span>
              </div>
            )}
            {result.executed_player_id && (
              <div>
                <strong>Player executed</strong>
                {result.game_over && (
                  <div style={styles.gameOver}>
                    Game Over! {result.winning_team}s win!
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {needsTarget && !result && !showingPolicies && !showingLoyalty && (
          <div style={styles.playerGrid}>
            {eligiblePlayers.map((player) => (
              <button
                key={player.player_id}
                onClick={() => setSelectedPlayerId(player.player_id)}
                style={{
                  ...styles.playerCard,
                  ...(selectedPlayerId === player.player_id && styles.selectedCard)
                }}
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
            style={{
              ...styles.confirmButton,
              ...((needsTarget && !selectedPlayerId && !result) && styles.buttonDisabled)
            }}
            disabled={(needsTarget && !selectedPlayerId && !result) || loading}
          >
            {loading ? 'Using Power...' : result ? 'Continue' : hasPeekedPolicies && presidentialPower === 'POLICY_PEEK' ? 'View Policies' : 'Use Power'}
          </button>
        )}

        {(showingPolicies || showingLoyalty) && (
          <div style={styles.autoAdvanceMessage}>
            Auto-advancing in 3 seconds...
          </div>
        )}
      </div>
    </div>
  );
}

const styles = {
  overlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.50)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000
  },
  overlayContent: {
    backgroundColor: '#FBB969',
    borderRadius: '12px',
    padding: '40px',
    maxWidth: '600px',
    width: '90%',
    maxHeight: '80vh',
    overflowY: 'auto',
    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.5)',

  },
  title: {
    color: '#83110a',
    fontSize: '24px',
    marginBottom: '10px',
    marginTop: 0,
    textAlign: 'center'
  },
  subtitle: {
    color: '#aaa',
    fontSize: '14px',
    marginBottom: '20px',
    textAlign: 'center'
  },
  waiting: {
    color: '#888',
    fontSize: '16px',
    textAlign: 'center',
    padding: '20px'
  },
  result: {
    backgroundColor: '#333',
    borderRadius: '8px',
    padding: '20px',
    marginBottom: '20px',
    color: '#fff'
  },
  policyPeek: {
    display: 'flex',
    gap: '10px',
    marginTop: '10px'
  },
  peekedPolicy: {
    width: '60px',
    height: '80px',
    borderRadius: '4px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '32px',
    fontWeight: 'bold',
    border: '2px solid'
  },
  liberalPeek: {
    borderColor: '#2196f3',
    backgroundColor: '#1a1a2e',
    color: '#2196f3'
  },
  fascistPeek: {
    borderColor: '#f44336',
    backgroundColor: '#2e1a1a',
    color: '#f44336'
  },
  gameOver: {
    marginTop: '10px',
    padding: '10px',
    backgroundColor: '#4caf50',
    borderRadius: '4px',
    fontWeight: 'bold'
  },
  playerGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
    gap: '10px',
    marginBottom: '20px'
  },
  playerCard: {
    padding: '15px',
    borderRadius: '4px',
    border: '2px solid #555',
    backgroundColor: '#333',
    color: '#fff',
    cursor: 'pointer',
    transition: 'all 0.2s'
  },
  selectedCard: {
    borderColor: '#4caf50',
    backgroundColor: '#1a2e1a',
    transform: 'scale(1.05)'
  },
  confirmButton: {
    width: '100%',
    padding: '15px',
    fontSize: '16px',
    borderRadius: '4px',
    border: 'none',
    backgroundColor: '#4caf50',
    color: '#fff',
    cursor: 'pointer',
    fontWeight: 'bold'
  },
  buttonDisabled: {
    backgroundColor: '#555',
    cursor: 'not-allowed'
  },
  autoAdvanceMessage: {
    color: '#aaa',
    fontSize: '16px',
    textAlign: 'center',
    padding: '20px',
    fontStyle: 'italic'
  },
  closeButton: {
    width: '100%',
    padding: '12px',
    fontSize: '14px',
    borderRadius: '4px',
    border: 'none',
    backgroundColor: '#666',
    color: '#fff',
    cursor: 'pointer',
    fontWeight: 'bold',
    marginTop: '10px'
  }
};
