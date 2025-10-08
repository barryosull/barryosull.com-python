export default function PolicyTracks({ gameState }) {
  const liberalPolicies = gameState?.liberal_policies || 0;
  const fascistPolicies = gameState?.fascist_policies || 0;
  const electionTracker = gameState?.election_tracker || 0;

  return (
    <div style={styles.container}>
      <div style={styles.track}>
        <div style={styles.explanation}>Win at 5</div>
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
        
      </div>

      <div style={styles.track}>
        <div style={styles.explanation}>Win at 6</div>
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
        
      </div>

      <div style={styles.electionTracker}>
        <div style={styles.explanation}>Chaos at 3</div>
        <h3 style={styles.trackTitle}>
          Failed Elections
          {[...Array(3)].map((_, i) => (
            <div
              key={i}
              style={{
                ...styles.electionBox,
                ...(i < electionTracker && styles.enacted)
              }}
            >
              {i < electionTracker ? 'X' : ''}
            </div>
          ))}
        </h3>
        <div style={{}}>
          
        </div>
        
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
    border: '1px solid #ff9800',
    color: '#ff9800',
    width: '16px',
    height: '16px',
    borderRadius: '8px',
    display: 'inline-block',
    marginTop: '2px',
    marginLeft: '10px',
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
  explanation: {
    color: '#888',
    fontSize: '12px',
    float: 'right',
  }
};
