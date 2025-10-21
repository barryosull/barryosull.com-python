import { useEffect, useState } from 'react';
import '../../assets/styles.css';

export default function NotificationOverlay({ notification, players, onClose, autoClose = true }) {
  const [isVisible, setIsVisible] = useState(false);
  const [isFadingOut, setIsFadingOut] = useState(false);

  useEffect(() => {
    if (notification) {
      setIsVisible(true);
      setIsFadingOut(false);
      if (autoClose) {
        const timer = setTimeout(() => {
          setIsFadingOut(true);
          setTimeout(() => {
            setIsVisible(false);
            onClose();
          }, 300);
        }, 3000);
        return () => clearTimeout(timer);
      }
    }
  }, [notification, onClose, autoClose]);

  const handleClose = () => {
    setIsFadingOut(true);
    setTimeout(() => {
      setIsVisible(false);
      onClose();
    }, 300);
  };

  if (!notification || !isVisible) return null;

  const notificationTitle = {
    'elected': "Government Formed!",
    'policy_enacted': "Policy Enacted!",
    'executed': "Player Executed!",
    'vetoed': "Election Vetoed!",
    'special_election': "Special Election!",
    'loyalty_investigated' : "Loyalty Investigated!",
    'failed_election': "Election failed!",
    'chaos': "Chaos!",
    'veto_rejected': "Veto Rejected!"
  }

  const title = notificationTitle[notification.type] ?? notification.type;

  const notificationBody = () => {
    if (notification.type === 'elected') {
      const chancellor = players.find(p => p.player_id === notification.chancellor_id);

      return (
        <div className="election-announcement">
            <div className="elected-role">
              <div className="role-label">Chancellor</div>
              <div className="role-player">{chancellor?.name}</div>
            </div>
          </div>
      );
    }
    if (notification.type === 'policy_enacted') {
      return (
        <div className="policy-grid">
          <span
              className={`policy-enacted idle-wobble ${notification.policy_type === 'LIBERAL' ? 'liberal-card' : 'fascist-card'}`}
          ></span>
        </div>
      )
    }

    if (notification.type === 'failed_election') {
      return (<>
        <h3>"Nein" votes cast by:</h3>
        <div className="player-grid">
          {players.map((player) => {
            const noVote = notification?.no_votes?.includes(player.player_id);
            if (!noVote) {
              return;
            }
            
            return (
              <div key={player.player_id} className="player-item voted-no">
                <span className="player-name">
                  {player.name.length > 10 ? player.name.slice(0, 10) + '...' : player.name}
                </span>
              </div>
            )
          })}
        </div>
        {notification?.policy_type && (
          <div className="policy-grid">
            <h3>3 failed governments, chaos enacted!</h3>
            <span
                className={`policy-enacted idle-wobble ${notification.policy_type === 'LIBERAL' ? 'liberal-card' : 'fascist-card'}`}
            ></span>
          </div>
        )}
      </>);
    }

    if (notification.type === 'executed') {
      const executed = players.find(p => p.player_id === notification.player_id);
      return (  
        <h3>{executed?.name} was executed by the president</h3>
      );
    }

    if (notification.type === 'vetoed') {
      return (<>
        <h3>Election was vetoed by the president and chancellor, advancing election tracker</h3>
        {notification?.policy_type && (
          <div className="policy-grid">
          <h3>3 failed governments, chaos enacted!</h3>
          <span
              className={`policy-enacted idle-wobble ${notification.policy_type === 'LIBERAL' ? 'liberal-card' : 'fascist-card'}`}
          ></span>
        </div>
        )}
      </>);
    }

    if (notification.type === 'veto_rejected') {
      return (  
        <h3>President has rejected veto, chancellor must select a policy</h3>
      );
    }

    if (notification.type === 'special_election') {
      const president = players.find(p => p.player_id === notification.player_id);
      return (  
        <h3>{president.name} was elected president</h3>
      );
    }

    if (notification.type === 'loyalty_investigated') {
      const investigated = players.find(p => p.player_id === notification.player_id);
      return (  
        <h3>{investigated.name}'s loyalty was investigated</h3>
      );
    }
    
    return (<div>Something happened, I dunno, asked the dev!</div>);
  };

  return (
    <div className={`overlay ${isFadingOut ? 'fade-out' : 'fade-in'}`}>
      <div className="overlay-content">
        <h2 className="overlay-title">{title}</h2>
        {notificationBody()}
        {!autoClose && (
          <button onClick={handleClose} className="confirm-button">
            Close
          </button>
        )}
      </div>
    </div>
  )
};
