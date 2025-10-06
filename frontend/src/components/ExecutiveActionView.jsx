import { useState } from 'react';

export default function ExecutiveActionView({
  gameState,
  myPlayerId,
  players,
  onUseAction,
  presidentialPower
}) {
  const [selectedPlayerId, setSelectedPlayerId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const isPresident = gameState.president_id === myPlayerId;

  const handleExecute = async () => {
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
    return (
      <div style={styles.container}>
        <h3 style={styles.title}>Executive Action</h3>
        <div style={styles.waiting}>
          Waiting for President to use their executive power...
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
    <div style={styles.container}>
      <h3 style={styles.title}>Executive Action</h3>
      <div style={styles.subtitle}>{getPowerDescription()}</div>

      {result && (
        <div style={styles.result}>
          {result.party_membership && (
            <div>
              <strong>Investigation Result:</strong> The player is a{' '}
              <span style={{
                color: result.party_membership === 'LIBERAL' ? '#2196f3' : '#f44336',
                fontWeight: 'bold'
              }}>
                {result.party_membership}
              </span>
            </div>
          )}
          {result.policies && (
            <div>
              <strong>Policy Peek:</strong>
              <div style={styles.policyPeek}>
                {result.policies.map((policy, idx) => (
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

      {needsTarget && !result && (
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

      <button
        onClick={handleExecute}
        style={{
          ...styles.confirmButton,
          ...((needsTarget && !selectedPlayerId && !result) && styles.buttonDisabled)
        }}
        disabled={(needsTarget && !selectedPlayerId && !result) || loading}
      >
        {loading ? 'Using Power...' : result ? 'Continue' : 'Use Power'}
      </button>
    </div>
  );
}

const styles = {
  container: {
    backgroundColor: '#333',
    borderRadius: '8px',
    padding: '20px',
    marginBottom: '20px'
  },
  title: {
    color: '#fff',
    fontSize: '20px',
    marginBottom: '10px',
    marginTop: 0
  },
  subtitle: {
    color: '#aaa',
    fontSize: '14px',
    marginBottom: '20px'
  },
  waiting: {
    color: '#888',
    fontSize: '16px',
    textAlign: 'center',
    padding: '20px'
  },
  result: {
    backgroundColor: '#2a2a2a',
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
    backgroundColor: '#2a2a2a',
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
  }
};
