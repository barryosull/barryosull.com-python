import { useState, useEffect } from 'react';
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
  const [isFadingOut, setIsFadingOut] = useState(false);

  useEffect(() => {
    setIsFadingOut(false);
  }, []);

  const handleSelect = async () => {
    if (selectedPolicyIndex === null) return;

    const policies = isPresident
      ? gameState.president_policies
      : gameState.chancellor_policies;

    const selectedPolicy = policies[selectedPolicyIndex];

    setLoading(true);
    try {
      setIsFadingOut(true);
      setTimeout(async () => {
        await onSelectPolicy(selectedPolicy.type);
      }, 300);
    } finally {
      setLoading(false);
    }
  };

  const handleVeto = async (approve) => {
    setLoading(true);
    try {
      setIsFadingOut(true);
      setTimeout(async () => {
        await onVeto(approve);
      }, 300);
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
  const vetoRejected = gameState.veto_rejected;

  const isMyTurn = isPresident
    ? gameState.president_id === myPlayerId
    : gameState.chancellor_id === myPlayerId;

  if (!isMyTurn) {
    return null;
  }

  return (
    <div className={`overlay ${isFadingOut ? 'fade-out' : 'fade-in'}`}>
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
              className={`policy-card ${policy.type === 'LIBERAL' ? 'liberal-card' : 'fascist-card'} ${selectedPolicyIndex === index ? 'selected' : ''}`}
              disabled={loading}
            ></button>
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
          <>
            {!vetoRejected && (
              <button
                onClick={() => handleVeto(true)}
                className="veto-request-button"
                disabled={loading || vetoRejected}
              >
                Request Veto
              </button>
            )}
            {vetoRejected && (
              <p className="veto-rejected-message">
                Veto already rejected by President
              </p>
            )}
          </>
        )}
      </div>
    </div>
  );
}
