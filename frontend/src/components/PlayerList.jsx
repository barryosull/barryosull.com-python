export default function PlayerList({ players, gameState, myPlayerId }) {
  return (
    <div style={styles.container}>
      <h3 style={styles.title}>Players</h3>
      <ul style={styles.list}>
        {players.map((player) => {
          const isPresident = gameState?.president_id === player.player_id;
          const isChancellor = gameState?.chancellor_id === player.player_id;
          const isNominated = gameState?.nominated_chancellor_id === player.player_id;
          const isDead = !player.is_alive;
          const isMe = player.player_id === myPlayerId;

          return (
            <li
              key={player.player_id}
              style={{
                ...styles.playerItem,
                ...(isDead && styles.deadPlayer)
              }}
            >
              <span style={styles.playerName}>
                {player.name}
                {isMe && <span style={styles.youBadge}>(You)</span>}
              </span>
              <div style={styles.badges}>
                {isPresident && <span style={styles.presidentBadge}>President</span>}
                {isChancellor && <span style={styles.chancellorBadge}>Chancellor</span>}
                {isNominated && <span style={styles.nominatedBadge}>Nominated</span>}
                {isDead && <span style={styles.deadBadge}>Dead</span>}
              </div>
            </li>
          );
        })}
      </ul>
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
    fontSize: '18px',
    marginBottom: '15px',
    marginTop: 0
  },
  list: {
    listStyle: 'none',
    padding: 0,
    margin: 0
  },
  playerItem: {
    color: '#fff',
    padding: '10px',
    marginBottom: '8px',
    backgroundColor: '#2a2a2a',
    borderRadius: '4px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  deadPlayer: {
    opacity: 0.5
  },
  playerName: {
    flex: 1
  },
  youBadge: {
    marginLeft: '8px',
    fontSize: '12px',
    color: '#888'
  },
  badges: {
    display: 'flex',
    gap: '8px'
  },
  presidentBadge: {
    fontSize: '12px',
    padding: '4px 8px',
    borderRadius: '4px',
    backgroundColor: '#ff9800',
    color: '#000',
    fontWeight: 'bold'
  },
  chancellorBadge: {
    fontSize: '12px',
    padding: '4px 8px',
    borderRadius: '4px',
    backgroundColor: '#4caf50',
    color: '#000',
    fontWeight: 'bold'
  },
  nominatedBadge: {
    fontSize: '12px',
    padding: '4px 8px',
    borderRadius: '4px',
    backgroundColor: '#2196f3',
    color: '#fff'
  },
  deadBadge: {
    fontSize: '12px',
    padding: '4px 8px',
    borderRadius: '4px',
    backgroundColor: '#d32f2f',
    color: '#fff'
  }
};
