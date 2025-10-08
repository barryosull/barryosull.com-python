import { useState } from 'react';

export default function PolicySelectionView({
  gameState,
  myPlayerId,
  onSelectPolicy,
  isPresident,
  onVeto
}) {
  const [selectedPolicyIndex, setSelectedPolicyIndex] = useState(null);
  const [loading, setLoading] = useState(false);
  const [vetoRequested, setVetoRequested] = useState(false);

  const handleSelect = async () => {
    if (selectedPolicyIndex === null) return;

    const policies = isPresident
      ? gameState.president_policies
      : gameState.chancellor_policies;

    const selectedPolicy = policies[selectedPolicyIndex];

    setLoading(true);
    try {
      await onSelectPolicy(selectedPolicy.type);
    } finally {
      setLoading(false);
    }
  };

  const handleVeto = async (approve) => {
    setLoading(true);
    try {
      await onVeto(approve);
    } finally {
      setLoading(false);
    }
  };

  const policies = isPresident
    ? gameState.president_policies
    : gameState.chancellor_policies;

  const actionText = isPresident ? 'Discard' : 'Enact';
  const roleText = isPresident ? 'President' : 'Chancellor';
  const vetoAvailable = gameState.fascist_policies >= 5;

  const isMyTurn = isPresident
    ? gameState.president_id === myPlayerId
    : gameState.chancellor_id === myPlayerId;

  if (!isMyTurn) {
    return (
      <div style={styles.overlay}>
        <div style={styles.overlayContent}>
          <h3 style={styles.title}>Legislative Session</h3>
          <div style={styles.waiting}>
            Waiting for {roleText} to {actionText.toLowerCase()} a policy...
          </div>
        </div>
      </div>
    );
  }

  if (vetoRequested && isPresident) {
    return (
      <div style={styles.overlay}>
        <div style={styles.overlayContent}>
          <h3 style={styles.title}>Veto Request</h3>
          <div style={styles.subtitle}>
            The Chancellor has requested to veto the agenda. Do you approve?
          </div>

          <div style={styles.vetoButtons}>
            <button
              onClick={() => handleVeto(true)}
              style={{ ...styles.vetoButton, ...styles.approveButton }}
              disabled={loading}
            >
              Approve Veto
            </button>
            <button
              onClick={() => handleVeto(false)}
              style={{ ...styles.vetoButton, ...styles.rejectButton }}
              disabled={loading}
            >
              Reject Veto
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.overlay}>
      <div style={styles.overlayContent}>
        <h3 style={styles.title}>Legislative Session</h3>
        <div style={styles.subtitle}>
          You are the {roleText}. {actionText} one policy.
        </div>

        <div style={styles.policyGrid}>
          {policies?.map((policy, index) => (
            <button
              key={index}
              onClick={() => setSelectedPolicyIndex(index)}
              style={{
                ...styles.policyCard,
                ...(policy.type === 'LIBERAL'
                  ? styles.liberalCard
                  : styles.fascistCard),
                ...(selectedPolicyIndex === index && styles.selectedCard)
              }}
              disabled={loading}
            >
              <div style={styles.policyType}>
                {policy.type === 'LIBERAL' ? 'Liberal' : 'Fascist'}
              </div>
              <div style={styles.policyIcon}>
                {policy.type === 'LIBERAL' ? 'L' : 'F'}
              </div>
            </button>
          ))}
        </div>

        <button
          onClick={handleSelect}
          style={{
            ...styles.confirmButton,
            ...(selectedPolicyIndex === null && styles.buttonDisabled)
          }}
          disabled={selectedPolicyIndex === null || loading}
        >
          {loading ? `${actionText}ing...` : `${actionText} Policy`}
        </button>

        {vetoAvailable && !isPresident && (
          <button
            onClick={() => setVetoRequested(true)}
            style={styles.vetoRequestButton}
            disabled={loading}
          >
            Request Veto
          </button>
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
    color: '#fff',
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
  policyGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
    gap: '15px',
    marginBottom: '20px'
  },
  policyCard: {
    padding: '30px 20px',
    borderRadius: '8px',
    border: '3px solid',
    cursor: 'pointer',
    transition: 'all 0.2s',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '10px'
  },
  liberalCard: {
    borderColor: '#2196f3',
    backgroundColor: '#1a1a2e',
    color: '#2196f3'
  },
  fascistCard: {
    borderColor: '#f44336',
    backgroundColor: '#2e1a1a',
    color: '#f44336'
  },
  selectedCard: {
    transform: 'scale(1.05)',
    boxShadow: '0 0 20px currentColor'
  },
  policyType: {
    fontSize: '14px',
    fontWeight: 'bold',
    textTransform: 'uppercase'
  },
  policyIcon: {
    fontSize: '48px',
    fontWeight: 'bold'
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
  vetoRequestButton: {
    width: '100%',
    padding: '12px',
    fontSize: '14px',
    borderRadius: '4px',
    border: 'none',
    backgroundColor: '#ff9800',
    color: '#fff',
    cursor: 'pointer',
    fontWeight: 'bold',
    marginTop: '10px'
  },
  vetoButtons: {
    display: 'flex',
    gap: '10px',
    marginTop: '20px'
  },
  vetoButton: {
    flex: 1,
    padding: '15px',
    fontSize: '16px',
    borderRadius: '4px',
    border: 'none',
    color: '#fff',
    cursor: 'pointer',
    fontWeight: 'bold'
  },
  approveButton: {
    backgroundColor: '#4caf50'
  },
  rejectButton: {
    backgroundColor: '#f44336'
  }
};
