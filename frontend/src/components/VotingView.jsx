import { useState } from 'react';

export default function VotingView({ gameState, players, myPlayerId, onVote }) {
  const [hasVoted, setHasVoted] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleVote = async (vote) => {
    setLoading(true);
    try {
      await onVote(vote);
      setHasVoted(true);
    } finally {
      setLoading(false);
    }
  };

  const president = players.find((p) => p.player_id === gameState.president_id);
  const nominee = players.find(
    (p) => p.player_id === gameState.nominated_chancellor_id
  );

  const votesCount = Object.keys(gameState.votes || {}).length;
  const totalPlayers = players.filter((p) => p.is_alive).length;
  const myPlayer = players.find((p) => p.player_id === myPlayerId);
  const canVote = myPlayer && myPlayer.is_alive;
  const isPresident = myPlayerId === gameState.president_id;
  const expectedVotes = totalPlayers - 1;

  if (!canVote || isPresident || hasVoted) {
    return null;
  }

  return (
    <div style={styles.overlay}>
      <div style={styles.overlayContent}>
        <h3 style={styles.title}>Election</h3>

        <div style={styles.governmentBox}>
          <div style={styles.role}>
            <div style={styles.roleLabel}>President</div>
            <div style={styles.roleName}>{president?.name}</div>
          </div>
          <div style={styles.divider}>+</div>
          <div style={styles.role}>
            <div style={styles.roleLabel}>Chancellor Nominee</div>
            <div style={styles.roleName}>{nominee?.name}</div>
          </div>
        </div>

        <div style={styles.voteSection}>
          <div style={styles.votePrompt}>
            Vote on the proposed government:
          </div>
          <div style={styles.voteButtons}>
            <button
              onClick={() => handleVote(true)}
              style={{ ...styles.voteButton, ...styles.jaButton }}
              disabled={loading}
            >
              Ja (Yes)
            </button>
            <button
              onClick={() => handleVote(false)}
              style={{ ...styles.voteButton, ...styles.neinButton }}
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

const styles = {
  overlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.85)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000
  },
  overlayContent: {
    backgroundColor: '#2a2a2a',
    borderRadius: '12px',
    padding: '40px',
    maxWidth: '600px',
    width: '90%',
    maxHeight: '80vh',
    overflowY: 'auto',
    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.5)',
    border: '2px solid #444'
  },
  title: {
    color: '#fff',
    fontSize: '24px',
    marginBottom: '20px',
    marginTop: 0,
    textAlign: 'center'
  },
  governmentBox: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '20px',
    marginBottom: '30px',
    padding: '20px',
    backgroundColor: '#333',
    borderRadius: '8px'
  },
  role: {
    textAlign: 'center'
  },
  roleLabel: {
    color: '#888',
    fontSize: '12px',
    marginBottom: '8px',
    textTransform: 'uppercase'
  },
  roleName: {
    color: '#fff',
    fontSize: '18px',
    fontWeight: 'bold'
  },
  divider: {
    color: '#666',
    fontSize: '24px',
    fontWeight: 'bold'
  },
  voteSection: {
    textAlign: 'center'
  },
  votePrompt: {
    color: '#aaa',
    fontSize: '16px',
    marginBottom: '20px'
  },
  voteButtons: {
    display: 'flex',
    gap: '20px',
    justifyContent: 'center'
  },
  voteButton: {
    padding: '20px 40px',
    fontSize: '18px',
    borderRadius: '8px',
    border: 'none',
    color: '#fff',
    cursor: 'pointer',
    fontWeight: 'bold',
    minWidth: '150px'
  },
  jaButton: {
    backgroundColor: '#4caf50'
  },
  neinButton: {
    backgroundColor: '#f44336'
  },
  waiting: {
    textAlign: 'center',
    color: '#888',
    fontSize: '16px',
    padding: '20px'
  },
  voteCount: {
    marginTop: '10px',
    fontSize: '14px',
    color: '#666'
  }
};
