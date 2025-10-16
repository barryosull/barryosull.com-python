import '../../assets/styles.css';

export default function PolicyTracks({ gameState }) {
  const liberalPolicies = gameState?.liberal_policies || 0;
  const electionTracker = gameState?.election_tracker || 0;

  return (
    <div className="policy-track liberal">
      <div className="liberal-policy-boxes">
        {[...Array(5)].map((_, i) => (
          <div
            key={i}
            className="liberal-policy-card-slot"
          >
            {i < liberalPolicies && <div className="policy-card-display liberal-card"></div>}
          </div>
        ))}
      </div>
      <div className="election-tracker">
        <div className="election-box">
          <div className="election-check"></div>
        </div>
        {[...Array(3)].map((_, i) => (
            <div
              key={i}
              className="election-box"
            >
              {i < electionTracker && <div className="election-check"></div>}
            </div>
          ))}
      </div>
    </div>
  );
}
