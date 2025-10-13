export default function PlayerList({ players, gameState, myPlayerId }) {
  return (
    <div className="player-list-container">
      <div className="player-grid">
        {players.map((player) => {
          const isPresident = gameState?.president_id === player.player_id;
          const isChancellor = gameState?.chancellor_id === player.player_id;
          const isNominated = gameState?.nominated_chancellor_id === player.player_id;
          const isDead = !player.is_alive;
          const isMe = player.player_id === myPlayerId;
          const playerVote = gameState?.votes?.[player.player_id];
          const hasVoted = playerVote !== undefined;

          const playerClasses = [
            'player-item',
            isDead && 'dead',
            hasVoted && playerVote && 'voted-yes',
            hasVoted && !playerVote && 'voted-no',
            isMe && 'you'
          ].filter(Boolean).join(' ');

          return (
            <div key={player.player_id} className={playerClasses}>
              <span className="player-name">
                {player.name.length > 10 ? player.name.slice(0, 10) + '...' : player.name}
              </span>
              <div className="player-badges">
                {isPresident && <span className="player-badge president-badge">President</span>}
                {isChancellor && <span className="player-badge chancellor-badge">Chancellor</span>}
                {isNominated && !isChancellor && <span className="player-badge nominated-badge">Nominated</span>}
                {isDead && <span className="player-badge dead-badge">Dead</span>}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
