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
  const [shouldRender, setShouldRender] = useState(true);

  useEffect(() => {
    setShouldRender(true);
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
        setShouldRender(false);
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
        setShouldRender(false);
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

  const isMyTurn = isPresident
    ? gameState.president_id === myPlayerId
    : gameState.chancellor_id === myPlayerId;

  // Check for veto state first, before isMyTurn check
  if (gameState.veto_requested) {
    const isPresidentPlayer = gameState.president_id === myPlayerId;
    const isChancellorPlayer = gameState.chancellor_id === myPlayerId;

    if (isPresidentPlayer && shouldRender) {
      return (
        <div className={`overlay ${isFadingOut ? 'fade-out' : 'fade-in'}`}>
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
    } else {
      // Other players
      return null;
    }
  }

  if (!isMyTurn || !shouldRender) {
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
          <button
            onClick={() => handleVeto(true)}
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
