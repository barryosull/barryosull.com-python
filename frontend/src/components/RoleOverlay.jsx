import { useState, useEffect } from 'react';
import '../../assets/styles.css';

const shownRoles = {};

export default function RoleOverlay({ myRole, roomCode, myPlayerId, forceShow = false, onClose }) {
  const [showOverlay, setShowOverlay] = useState(false);
  const [isFadingOut, setIsFadingOut] = useState(false);

  useEffect(() => {
    if (forceShow) {
      setShowOverlay(true);
      setIsFadingOut(false);
    }
  }, [forceShow]);

  useEffect(() => {
    if (myRole && roomCode && myPlayerId) {
      const urlParams = new URLSearchParams(window.location.search);
      const hideOverlay = urlParams.get('hide_overlay') === '1';

      if (hideOverlay) {
        return;
      }

      const roleShownKey = `${roomCode}_${myPlayerId}`;
      if (!shownRoles[roleShownKey]) {
        setShowOverlay(true);
        setIsFadingOut(false);
      }
    }
  }, [myRole, roomCode, myPlayerId]);

  const handleClose = () => {
    const roleShownKey = `${roomCode}_${myPlayerId}`;
    shownRoles[roleShownKey] = true;
    setIsFadingOut(true);
    setTimeout(() => {
      setShowOverlay(false);
      if (onClose) {
        onClose();
      }
    }, 300);
  };

  if (!showOverlay || !myRole) {
    return null;
  }

  return (
    <div className={`overlay ${isFadingOut ? 'fade-out' : 'fade-in'}`}>
      <div className="overlay-content">
        <h2 className="overlay-title">Your Role</h2>
        <div
          className={`role-display ${myRole.is_hitler ? 'hitler' : myRole.team === 'LIBERAL' ? 'liberal' : 'fascist'}`}
        >
        </div>
        <div className="role-description">
          {myRole.is_hitler && (
            <span>
              You are Hitler! Work with the Fascists to get elected as Chancellor after 3 Fascist policies are enacted.
            </span>
          )}
          {!myRole.is_hitler && myRole.team === 'FASCIST' && (
            <span>
              You are a Fascist! Work to enact Fascist policies and get Hitler elected as Chancellor.
            </span>
          )}
          {myRole.team === 'LIBERAL' && (
            <span>
              You are a Liberal! Work to enact Liberal policies and prevent Hitler from being elected.
            </span>
          )}
        </div>
        {myRole.teammates && myRole.teammates.length > 0 && (
          <div className="role-description">
            <span>
              {myRole.teammates.length === 1 ? 'Your Teammate:' : 'Your Teammates:'}
            </span>
            <div className="team-mates">
            {myRole.teammates.map((teammate) => (
              <div className={teammate.is_hitler ? 'hitler' : 'fascist'} key={teammate.player_id}>
                {teammate.name} {teammate.is_hitler ? '(Hitler)' : '(Fascist)'}
              </div>
            ))}
            </div>
          </div>
        )}
        <button onClick={handleClose} className="close-button">
          OK
        </button>
      </div>
    </div>
  );
}
