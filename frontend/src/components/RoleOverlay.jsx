import { useState, useEffect } from 'react';
import '../../assets/styles.css';

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
    <div className="overlay">
      <div className="overlay-content">
        <h2 className="overlay-title">Your Role</h2>
        <div
          className={`role-display ${myRole.is_hitler ? 'hitler' : myRole.team === 'LIBERAL' ? 'liberal' : 'fascist'}`}
        >
        </div>
        {myRole.is_hitler && (
          <div className="role-description">
            You are Hitler! Work with the Fascists to get elected as Chancellor after 3 Fascist policies are enacted.
          </div>
        )}
        {!myRole.is_hitler && myRole.team === 'FASCIST' && (
          <div className="role-description">
            You are a Fascist! Work to enact Fascist policies and get Hitler elected as Chancellor.
          </div>
        )}
        {myRole.team === 'LIBERAL' && (
          <div className="role-description">
            You are a Liberal! Work to enact Liberal policies and prevent Hitler from being elected.
          </div>
        )}
        <button onClick={handleClose} className="close-button">
          OK
        </button>
      </div>
    </div>
  );
}
