import '../../assets/styles.css';

export default function PolicyTracks({ gameState, players }) {
  const fascistPolicies = gameState?.fascist_policies || 0;
  let board = 'fascist-5-to-6';
  if (players.length >= 7) {
    board = 'fascist-7-to-8';
  }
  if (players.length >= 9) {
    board = 'fascist-9-to-10';
  }

  return (
    <div className={`policy-track ${board}`}>
      <div className="fascist-policy-boxes">
        {[...Array(6)].map((_, i) => (
          <div
            key={i}
            className="fascist-policy-card-slot"
          >
            {i < fascistPolicies && <div className="policy-card-display fascist-card"></div>}
          </div>
        ))}
      </div>
    </div>
  );
}
