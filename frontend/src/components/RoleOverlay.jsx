import { useState, useEffect } from 'react';

const shownRoles = {};

export default function RoleOverlay({ myRole, roomId, myPlayerId }) {
  const [showOverlay, setShowOverlay] = useState(false);

  useEffect(() => {
    if (myRole && roomId && myPlayerId) {
      const urlParams = new URLSearchParams(window.location.search);
      const hideOverlay = urlParams.get('hide_overlay') === '1';

      if (hideOverlay) {
        return;
      }

      const roleShownKey = `${roomId}_${myPlayerId}`;
      if (!shownRoles[roleShownKey]) {
        setShowOverlay(true);
      }
    }
  }, [myRole, roomId, myPlayerId]);

  const handleClose = () => {
    const roleShownKey = `${roomId}_${myPlayerId}`;
    shownRoles[roleShownKey] = true;
    setShowOverlay(false);
  };

  if (!showOverlay || !myRole) {
    return null;
  }

  return (
    <div style={styles.overlay}>
      <div style={styles.overlayContent}>
        <h2 style={styles.overlayTitle}>Your Role</h2>
        <div
          style={{
            ...styles.overlayRole,
            ...(myRole.team === 'LIBERAL'
              ? styles.overlayRoleLiberal
              : styles.overlayRoleFascist)
          }}
        >
          {myRole.is_hitler ? 'Hitler' : myRole.team}
        </div>
        {myRole.is_hitler && (
          <div style={styles.overlayDescription}>
            You are Hitler! Work with the Fascists to get elected as Chancellor after 3 Fascist policies are enacted.
          </div>
        )}
        {!myRole.is_hitler && myRole.team === 'FASCIST' && (
          <div style={styles.overlayDescription}>
            You are a Fascist! Work to enact Fascist policies and get Hitler elected as Chancellor.
          </div>
        )}
        {myRole.team === 'LIBERAL' && (
          <div style={styles.overlayDescription}>
            You are a Liberal! Work to enact Liberal policies and prevent Hitler from being elected.
          </div>
        )}
        <button onClick={handleClose} style={styles.overlayButton}>
          OK
        </button>
      </div>
    </div>
  );
}

const styles = {
  overlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.50)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000
  },
  overlayContent: {
    backgroundColor: '#FBB969',
    borderRadius: '12px',
    padding: '40px',
    maxWidth: '500px',
    textAlign: 'center',
    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.5)',
  },
  overlayTitle: {
    color: '#fff',
    fontSize: '28px',
    marginBottom: '20px',
    marginTop: 0
  },
  overlayRole: {
    fontSize: '48px',
    fontWeight: 'bold',
    padding: '30px',
    borderRadius: '8px',
    marginBottom: '20px',
    textTransform: 'uppercase',
    letterSpacing: '2px'
  },
  overlayRoleLiberal: {
    color: '#2196f3',
    backgroundColor: '#0d1f2e',
    border: '3px solid #2196f3'
  },
  overlayRoleFascist: {
    color: '#f44336',
    backgroundColor: '#2e0d0d',
    border: '3px solid #f44336'
  },
  overlayDescription: {
    color: '#aaa',
    fontSize: '16px',
    lineHeight: '1.6',
    marginBottom: '30px'
  },
  overlayButton: {
    padding: '15px 40px',
    fontSize: '18px',
    borderRadius: '8px',
    border: 'none',
    backgroundColor: '#4caf50',
    color: '#fff',
    cursor: 'pointer',
    fontWeight: 'bold',
    minWidth: '150px'
  }
};
