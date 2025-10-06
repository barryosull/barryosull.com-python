import { useParams, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { useGameState } from '../hooks/useGameState';
import { api } from '../services/api';
import { playerStorage, preserveParams, initializeFromUrl } from '../services/storage';
import PlayerList from './PlayerList';
import PolicyTracks from './PolicyTracks';
import NominationView from './NominationView';
import VotingView from './VotingView';
import PolicySelectionView from './PolicySelectionView';
import ExecutiveActionView from './ExecutiveActionView';

export default function GameBoard() {
  const { roomId } = useParams();
  const navigate = useNavigate();
  const { gameState, room, myRole, error, loading, refresh } = useGameState(roomId);
  const myPlayerId = playerStorage.getPlayerId();
  const [roleVisible, setRoleVisible] = useState(false);

  useEffect(() => {
    initializeFromUrl();
  }, []);

  if (loading) {
    return (
      <div style={styles.container}>
        <div style={styles.loading}>Loading game...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={styles.container}>
        <div style={styles.error}>{error}</div>
        <button onClick={() => navigate(preserveParams('/'))} style={styles.button}>
          Return Home
        </button>
      </div>
    );
  }

  if (!gameState || !room) {
    return (
      <div style={styles.container}>
        <div style={styles.error}>Game not found</div>
        <button onClick={() => navigate(preserveParams('/'))} style={styles.button}>
          Return Home
        </button>
      </div>
    );
  }

  const handleNominate = async (chancellorId) => {
    try {
      await api.nominateChancellor(roomId, myPlayerId, chancellorId);
      refresh();
    } catch (err) {
      alert(err.message);
    }
  };

  const handleVote = async (vote) => {
    try {
      await api.castVote(roomId, myPlayerId, vote);
      refresh();
    } catch (err) {
      alert(err.message);
    }
  };

  const handleDiscardPolicy = async (policyType) => {
    try {
      await api.discardPolicy(roomId, myPlayerId, policyType);
      refresh();
    } catch (err) {
      alert(err.message);
    }
  };

  const handleEnactPolicy = async (policyType) => {
    try {
      await api.enactPolicy(roomId, myPlayerId, policyType);
      refresh();
    } catch (err) {
      alert(err.message);
    }
  };

  const handleExecutiveAction = async (targetPlayerId) => {
    try {
      const result = await api.useExecutiveAction(roomId, myPlayerId, targetPlayerId);
      refresh();
      return result;
    } catch (err) {
      alert(err.message);
      throw err;
    }
  };

  const handleVeto = async (approveVeto) => {
    try {
      await api.veto(roomId, myPlayerId, approveVeto);
      refresh();
    } catch (err) {
      alert(err.message);
    }
  };

  const getPresidentialPower = () => {
    const playerCount = room.player_count;
    const fascistPolicies = gameState.fascist_policies;

    if (playerCount <= 6) {
      const powerMap = {
        3: 'POLICY_PEEK',
        4: 'EXECUTION',
        5: 'EXECUTION'
      };
      return powerMap[fascistPolicies];
    } else if (playerCount <= 8) {
      const powerMap = {
        1: 'INVESTIGATE_LOYALTY',
        2: 'CALL_SPECIAL_ELECTION',
        3: 'POLICY_PEEK',
        4: 'EXECUTION',
        5: 'EXECUTION'
      };
      return powerMap[fascistPolicies];
    } else {
      const powerMap = {
        1: 'INVESTIGATE_LOYALTY',
        2: 'INVESTIGATE_LOYALTY',
        3: 'CALL_SPECIAL_ELECTION',
        4: 'EXECUTION',
        5: 'EXECUTION'
      };
      return powerMap[fascistPolicies];
    }
  };

  const renderPhaseView = () => {
    switch (gameState.current_phase) {
      case 'NOMINATION':
        return (
          <NominationView
            players={room.players}
            gameState={gameState}
            myPlayerId={myPlayerId}
            onNominate={handleNominate}
          />
        );

      case 'ELECTION':
        return (
          <VotingView
            gameState={gameState}
            players={room.players}
            myPlayerId={myPlayerId}
            onVote={handleVote}
          />
        );

      case 'LEGISLATIVE_PRESIDENT':
        return (
          <PolicySelectionView
            gameState={gameState}
            myPlayerId={myPlayerId}
            onSelectPolicy={handleDiscardPolicy}
            onVeto={handleVeto}
            isPresident={true}
          />
        );

      case 'LEGISLATIVE_CHANCELLOR':
        return (
          <PolicySelectionView
            gameState={gameState}
            myPlayerId={myPlayerId}
            onSelectPolicy={handleEnactPolicy}
            onVeto={handleVeto}
            isPresident={false}
          />
        );

      case 'EXECUTIVE_ACTION':
        return (
          <ExecutiveActionView
            gameState={gameState}
            myPlayerId={myPlayerId}
            players={room.players}
            onUseAction={handleExecutiveAction}
            presidentialPower={getPresidentialPower()}
          />
        );

      case 'GAME_OVER':
        return (
          <div style={styles.phaseBox}>
            <h2 style={styles.gameOver}>Game Over!</h2>
            {gameState.game_over_reason && (
              <p style={styles.gameOverReason}>{gameState.game_over_reason}</p>
            )}
            <button onClick={() => navigate(preserveParams('/'))} style={styles.button}>
              Return to Home
            </button>
          </div>
        );

      default:
        return (
          <div style={styles.phaseBox}>
            <p>Unknown phase: {gameState.current_phase}</p>
          </div>
        );
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>Secret Hitler</h1>
        <div style={styles.roomId}>Room: {roomId}</div>
      </div>

      {myRole && (
        <div
          style={styles.roleBox}
          onClick={() => setRoleVisible(!roleVisible)}
        >
          <div style={styles.roleLabel}>Your Role: {roleVisible ? '' : '(click to reveal)'}</div>
          {roleVisible && (
            <div
              style={{
                ...styles.roleValue,
                ...(myRole.team === 'LIBERAL'
                  ? styles.liberal
                  : styles.fascist)
              }}
            >
              {myRole.is_hitler ? 'Hitler' : myRole.team}
            </div>
          )}
        </div>
      )}

      <div style={styles.mainContent}>
        <div style={styles.leftColumn}>
          <PolicyTracks gameState={gameState} />
          <PlayerList
            players={room.players}
            gameState={gameState}
            myPlayerId={myPlayerId}
          />
        </div>

        <div style={styles.rightColumn}>{renderPhaseView()}</div>
      </div>
    </div>
  );
}

const styles = {
  container: {
    minHeight: '100vh',
    backgroundColor: '#1a1a1a',
    padding: '20px'
  },
  header: {
    textAlign: 'center',
    marginBottom: '20px'
  },
  title: {
    color: '#fff',
    fontSize: '32px',
    marginBottom: '10px'
  },
  roomId: {
    color: '#888',
    fontSize: '14px',
    fontFamily: 'monospace'
  },
  roleBox: {
    backgroundColor: '#333',
    borderRadius: '8px',
    padding: '15px',
    marginBottom: '20px',
    textAlign: 'center',
    maxWidth: '400px',
    margin: '0 auto 20px',
    cursor: 'pointer',
    userSelect: 'none'
  },
  roleLabel: {
    color: '#888',
    fontSize: '12px',
    marginBottom: '8px',
    textTransform: 'uppercase'
  },
  roleValue: {
    fontSize: '24px',
    fontWeight: 'bold'
  },
  liberal: {
    color: '#2196f3'
  },
  fascist: {
    color: '#f44336'
  },
  mainContent: {
    display: 'grid',
    gridTemplateColumns: '1fr 2fr',
    gap: '20px',
    maxWidth: '1400px',
    margin: '0 auto'
  },
  leftColumn: {
    minWidth: 0
  },
  rightColumn: {
    minWidth: 0
  },
  phaseBox: {
    backgroundColor: '#333',
    borderRadius: '8px',
    padding: '40px',
    textAlign: 'center',
    color: '#fff'
  },
  gameOver: {
    fontSize: '36px',
    marginBottom: '20px'
  },
  gameOverReason: {
    fontSize: '18px',
    marginBottom: '30px',
    color: '#ddd'
  },
  button: {
    padding: '12px 24px',
    fontSize: '16px',
    borderRadius: '4px',
    border: 'none',
    backgroundColor: '#0066cc',
    color: '#fff',
    cursor: 'pointer',
    fontWeight: 'bold'
  },
  loading: {
    color: '#fff',
    fontSize: '20px',
    textAlign: 'center',
    padding: '40px'
  },
  error: {
    backgroundColor: '#d32f2f',
    color: '#fff',
    padding: '20px',
    borderRadius: '8px',
    marginBottom: '20px',
    textAlign: 'center'
  }
};
