import { useState } from 'react';
import '../../assets/styles.css';

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
  const [showWaitingOverlay, setShowWaitingOverlay] = useState(true);

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
    if (!showWaitingOverlay) {
      return null;
    }

    return (
      <div className="overlay">
        <div className="overlay-content">
          <h3 className="overlay-title">Legislative Session</h3>
          <div className="overlay-waiting">
            Waiting for {roleText} to {actionText.toLowerCase()} a policy...
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

  if (vetoRequested && isPresident) {
    return (
      <div className="overlay">
        <div className="overlay-content">
          <h3 className="overlay-title">Veto Request</h3>
          <div className="overlay-subtitle">
            The Chancellor has requested to veto the agenda. Do you approve?
          </div>

          <div className="veto-buttons">
            <button
              onClick={() => handleVeto(true)}
              className="veto-button approve"
              disabled={loading}
            >
              Approve Veto
            </button>
            <button
              onClick={() => handleVeto(false)}
              className="veto-button reject"
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
    <div className="overlay">
      <div className="overlay-content">
        <h3 className="overlay-title">Legislative Session</h3>
        <div className="overlay-subtitle">
          You are the {roleText}. {actionText} one policy.
        </div>

        <div className="policy-grid">
          {policies?.map((policy, index) => (
            <button
              key={index}
              onClick={() => setSelectedPolicyIndex(index)}
              className={`policy-card ${policy.type === 'LIBERAL' ? 'liberal' : 'fascist'} ${selectedPolicyIndex === index ? 'selected' : ''}`}
              disabled={loading}
            >
              <div className="policy-type">
                {policy.type === 'LIBERAL' ? 'Liberal' : 'Fascist'}
              </div>
              <div className="policy-icon">
                {policy.type === 'LIBERAL' ? 'L' : 'F'}
              </div>
            </button>
          ))}
        </div>

        <button
          onClick={handleSelect}
          className="confirm-button"
          disabled={selectedPolicyIndex === null || loading}
        >
          {loading ? `${actionText}ing...` : `${actionText} Policy`}
        </button>

        {vetoAvailable && !isPresident && (
          <button
            onClick={() => setVetoRequested(true)}
            className="veto-request-button"
            disabled={loading}
          >
            Request Veto
          </button>
        )}
      </div>
    </div>
  );
}
