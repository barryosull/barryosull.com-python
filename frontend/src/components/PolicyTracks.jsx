export default function PolicyTracks({ gameState }) {
  const liberalPolicies = gameState?.liberal_policies || 0;
  const fascistPolicies = gameState?.fascist_policies || 0;
  const electionTracker = gameState?.election_tracker || 0;

  return (<>
    <div style={{...styles.board, ...styles.liberal}}>
      <div style={styles.liberalPolicyBoxes}>
        {[...Array(5)].map((_, i) => (
          <div
            key={i}
            style={styles.liberalPolicyCardSlot}
          >
            {i < liberalPolicies && <div style={{...styles.policyCard, ...styles.policyCardLiberal}}></div>}
          </div>
        ))}
      </div>
      <div style={styles.electionTracker}>
        <div style={styles.electionBox}>
          <div style={styles.electionCheck}></div>
        </div>
        {[...Array(3)].map((_, i) => (
            <div
              key={i}
              style={styles.electionBox}
            >
              {i < electionTracker && <div style={styles.electionCheck}></div>}
            </div>
          ))}
      </div>
    </div>

    <div style={{...styles.board, ...styles.fascist5To6}}>
      <div style={styles.fascistPolicyBoxes}>
        {[...Array(6)].map((_, i) => (
          <div
            key={i}
            style={styles.fascistPolicyCardSlot}
          >
            {i < fascistPolicies && <div style={{...styles.policyCard, ...styles.policyCardFascist}}></div>}
          </div>
        ))}
      </div>
    </div>
  </>);
}

const styles = {
  board: {
    backgroundSize: 'cover',
    backgroundRepeat: 'none',
    width: '100%',
    aspectRatio: '2921/1025',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    position: 'relative',
  },
  liberal: {
    backgroundImage: 'url("/assets/images/liberal-board.png"',
  },
  fascist5To6: {
     backgroundImage: 'url("/assets/images/fascist-board-5-to-6-players.png"',
  },
  fascist7To8: {
     backgroundImage: 'url("/assets/images/fascist-board-7-to-8-players.png"',
  },
  fascist9To10: {
     backgroundImage: 'url("/assets/images/fascist-board-9-to-10-players.png"',
  },
  liberalPolicyBoxes: {
    width: '70%',
    height: '55%',
    margin: 'auto'
  },
  fascistPolicyBoxes: {
    width: '85%',
    height: '55%',
    margin: 'auto',
  },
  liberalPolicyCardSlot: {
    marginTop: "0.5%",
    width: '20%',
    height: '100%',
    display: 'inline-block',
  },
  fascistPolicyCardSlot: {
    marginTop: "1%",
    width: '16.6%',
    height: '100%',
    display: 'inline-block',
  },
  policyCard: {
    margin: '5% 10%',
    height: '90%',
    width: '80%',
  },
  policyCardLiberal: {
    backgroundImage: 'url("/assets/images/policy-liberal.png"',
    backgroundSize: 'cover',
    backgroundRepeat: 'none',
  },
  policyCardFascist: {
    backgroundImage: 'url("/assets/images/policy-fascist.png"',
    backgroundSize: 'cover',
    backgroundRepeat: 'none',
  },
  electionTracker: {
    position: 'absolute',
    bottom: '10%',
    height: '11%',
    width: '38%',
    margin: '0px auto',
  },
  electionBox: {
    width: '25%',
    height: '100%',
    float: 'left',
    position: 'relative',
    left: "-1%",
  },
  electionCheck: {
    width: '37%',
    height: '90%',
    margin: '5% auto',
    backgroundColor: '#000',
    borderRadius: '50%',
  },
};
