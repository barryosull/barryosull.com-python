export default function PolicyTracks({ gameState }) {
  const liberalPolicies = gameState?.liberal_policies || 0;
  const fascistPolicies = gameState?.fascist_policies || 0;
  const electionTracker = gameState?.election_tracker || 0;

  return (
    <div style={styles.container}>
      <div style={styles.track}>
        <h3 style={styles.trackTitle}>Liberal Policies</h3>
        <div style={styles.policyBoxes}>
          {[...Array(5)].map((_, i) => (
            <div
              key={i}
              style={{
                ...styles.policyBox,
                ...styles.liberalBox,
                ...(i < liberalPolicies && styles.enacted)
              }}
            >
              {i < liberalPolicies ? 'L' : ''}
            </div>
          ))}
        </div>
        <div style={styles.winCondition}>Win at 5</div>
      </div>

      <div style={styles.track}>
        <h3 style={styles.trackTitle}>Fascist Policies</h3>
        <div style={styles.policyBoxes}>
          {[...Array(6)].map((_, i) => (
            <div
              key={i}
              style={{
                ...styles.policyBox,
                ...styles.fascistBox,
                ...(i < fascistPolicies && styles.enacted)
              }}
            >
              {i < fascistPolicies ? 'F' : ''}
            </div>
          ))}
        </div>
        <div style={styles.winCondition}>Win at 6</div>
      </div>

      <div style={styles.electionTracker}>
        <h3 style={styles.trackTitle}>Failed Elections</h3>
        <div style={styles.policyBoxes}>
          {[...Array(3)].map((_, i) => (
            <div
              key={i}
              style={{
                ...styles.policyBox,
                ...styles.electionBox,
                ...(i < electionTracker && styles.enacted)
              }}
            >
              {i < electionTracker ? 'X' : ''}
            </div>
          ))}
        </div>
        <div style={styles.winCondition}>Chaos at 3</div>
      </div>
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
  track: {
    marginBottom: '20px'
  },
  trackTitle: {
    color: '#fff',
    fontSize: '16px',
    marginBottom: '10px',
    marginTop: 0
  },
  policyBoxes: {
    display: 'flex',
    gap: '10px',
    marginBottom: '8px'
  },
  policyBox: {
    width: '50px',
    height: '50px',
    border: '2px solid',
    borderRadius: '4px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '24px',
    fontWeight: 'bold',
    transition: 'all 0.3s'
  },
  liberalBox: {
    borderColor: '#2196f3',
    color: '#2196f3'
  },
  fascistBox: {
    borderColor: '#f44336',
    color: '#f44336'
  },
  electionBox: {
    borderColor: '#ff9800',
    color: '#ff9800'
  },
  enacted: {
    backgroundColor: 'currentColor',
    color: '#000'
  },
  electionTracker: {
    marginTop: '20px',
    paddingTop: '20px',
    borderTop: '1px solid #444'
  },
  winCondition: {
    color: '#888',
    fontSize: '12px'
  }
};
