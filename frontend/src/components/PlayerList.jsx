export default function PlayerList({ players, gameState, myPlayerId }) {
  return (
    <div style={styles.container}>
      <div style={styles.playerGrid}>
        {players.map((player) => {
          const isPresident = gameState?.president_id === player.player_id;
          const isChancellor = gameState?.chancellor_id === player.player_id;
          const isNominated = gameState?.nominated_chancellor_id === player.player_id;
          const isDead = !player.is_alive;
          const isMe = player.player_id === myPlayerId;
          const playerVote = gameState?.votes?.[player.player_id];
          const hasVoted = playerVote !== undefined;

          return (
            <div
              key={player.player_id}
              style={{
                ...styles.playerItem,
                ...(isDead && styles.deadPlayer),
                ...(hasVoted && playerVote && styles.votedYes),
                ...(hasVoted && !playerVote && styles.votedNo),
                ...(isMe && styles.you)
              }}
            >
              <span style={styles.playerName}>
                {player.name.length > 10 ? player.name.slice(0, 10) + '...' : player.name}
              </span>
              <div style={styles.badges}>
                {isPresident && <span style={{...styles.badge, ...styles.presidentBadge}}>President</span>}
                {isChancellor && <span style={{...styles.badge, ...styles.chancellorBadge}}>Chancellor</span>}
                {isNominated && !isChancellor && <span style={{...styles.badge, ...styles.nominatedBadge}}>Nominated</span>}
                {isDead && <span style={{...styles.badge, ...styles.deadBadge}}>Dead</span>}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

const styles = {
  container: {
    padding: '0px',
    marginBottom: '20px'
  },
  playerGrid: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '10px'
  },
  playerItem: {
    color: '#fff',
    padding: '12px',
    backgroundColor: '#cb6849',
    borderRadius: '4px',
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
    flex: '1 1 calc(20% - 10px)',
    minWidth: '90px',
    maxWidth: 'calc(20% - 10px)',
    position: 'relative',
  },
  deadPlayer: {
    opacity: 0.5
  },
  playerName: {
    flex: 1,
    textAlign: 'center',
    fontSize: '12px',  
  },
  you: {
    border: '1px solid #fff',
  },
  badges: {
    position: 'absolute',
    top: '-10px',
    left: '0px',
    width: '100%',
    textAlign: 'center',
  },
  badge: {
    fontSize: '10px',
    padding: '2px 4px',
    margin: '0px 2px',
    borderRadius: '2px',
    color: '#000',
    fontWeight: 'bold',
    display: 'inline-block',
  },
  presidentBadge: {
    backgroundColor: '#ff9800',
  },
  chancellorBadge: {
    backgroundColor: '#ff9800',
  },
  nominatedBadge: {
    backgroundColor: '#ff9800',
  },
  deadBadge: {
    backgroundColor: '#d32f2f',
  },
  votedYes: {
    backgroundColor: '#4caf50'
  },
  votedNo: {
    backgroundColor: '#df3c30ff'
  }
};
