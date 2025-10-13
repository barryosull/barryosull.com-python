import { useEffect, useState } from 'react';
import '../../assets/styles.css';

export default function NotificationOverlay({ notification, players, onClose }) {
  const [isVisible, setIsVisible] = useState(false);
  const [isFadingOut, setIsFadingOut] = useState(false);

  useEffect(() => {
    if (notification) {
      setIsVisible(true);
      setIsFadingOut(false);
      const timer = setTimeout(() => {
        setIsFadingOut(true);
        setTimeout(() => {
          setIsVisible(false);
          onClose();
        }, 300);
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [notification, onClose]);

  if (!notification || !isVisible) return null;

  const notificationTitle = {
    'elected': "Government Formed!",
    'policy_enacted': "Policy Enacted!",
    'executed': "Player Executed!",
    'vetoed': "Election Vetoed!",
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
              className={`policy-card ${notification.policy_type === 'LIBERAL' ? 'liberal-card' : 'fascist-card'}`}
          ></span>
        </div>
      )
    }
    
    return (<div>Something happened, I dunno, asked the dev!</div>);
  };

  return (
    <div className={`overlay ${isFadingOut ? 'fade-out' : 'fade-in'}`}>
      <div className="overlay-content">
        <h2 className="overlay-title">{title}</h2>
        {notificationBody()}
      </div>
    </div>
  )
};
