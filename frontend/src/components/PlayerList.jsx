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

          return (
            <div
              key={player.player_id}
              style={{
                ...styles.playerItem,
                ...(isDead && styles.deadPlayer)
              }}
            >
              <span style={styles.playerName}>
                {player.name.length > 10 ? player.name.slice(0, 10) + '...' : player.name}
                {isMe && <span style={styles.youBadge}>(You)</span>}
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
    backgroundColor: '#2a2a2a',
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
  youBadge: {
    marginLeft: '8px',
    fontSize: '12px',
    color: '#888'
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
    padding: '3px 6px',
    margin: '0px 3px',
    borderRadius: '3px',
    color: '#000',
    fontWeight: 'bold',
    display: 'inline-block',
  },
  presidentBadge: {
    backgroundColor: '#ff9800',
  },
  chancellorBadge: {
    fontSize: '10px',
    padding: '3px 6px',
    borderRadius: '3px',
    backgroundColor: '#4caf50',
    color: '#000',
    fontWeight: 'bold'
  },
  nominatedBadge: {
    fontSize: '10px',
    padding: '3px 6px',
    borderRadius: '3px',
    backgroundColor: '#2196f3',
    color: '#fff'
  },
  deadBadge: {
    fontSize: '10px',
    padding: '3px 3px',
    borderRadius: '3px',
    backgroundColor: '#d32f2f',
    color: '#fff'
  }
};
