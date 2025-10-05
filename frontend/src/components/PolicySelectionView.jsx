import { useState } from 'react';

export default function PolicySelectionView({
  gameState,
  myPlayerId,
  onSelectPolicy,
  isPresident
}) {
  const [selectedPolicyIndex, setSelectedPolicyIndex] = useState(null);
  const [loading, setLoading] = useState(false);

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

  const policies = isPresident
    ? gameState.president_policies
    : gameState.chancellor_policies;

  const actionText = isPresident ? 'Discard' : 'Enact';
  const roleText = isPresident ? 'President' : 'Chancellor';

  const isMyTurn = isPresident
    ? gameState.president_id === myPlayerId
    : gameState.chancellor_id === myPlayerId;

  if (!isMyTurn) {
    return (
      <div style={styles.container}>
        <h3 style={styles.title}>Legislative Session</h3>
        <div style={styles.waiting}>
          Waiting for {roleText} to {actionText.toLowerCase()} a policy...
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
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
  }
};
