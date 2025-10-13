import { useEffect, useState } from 'react';
import '../../assets/styles.css';

export default function ElectionOverlay({ electionData, players, onClose }) {
  const [isVisible, setIsVisible] = useState(false);
  const [isFadingOut, setIsFadingOut] = useState(false);

  useEffect(() => {
    if (electionData) {
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
  }, [electionData, onClose]);

  if (!electionData || !isVisible) return null;

  const president = players.find(p => p.player_id === electionData.president_id);
  const chancellor = players.find(p => p.player_id === electionData.chancellor_id);

  return (
    <div className={`overlay ${isFadingOut ? 'fade-out' : 'fade-in'}`}>
      <div className="overlay-content">
        <h2 className="overlay-title">Government Formed!</h2>
        <div className="election-announcement">
          <div className="elected-role">
            <div className="role-label">President</div>
            <div className="role-player">{president?.name}</div>
          </div>
          <div className="election-divider">+</div>
          <div className="elected-role">
            <div className="role-label">Chancellor</div>
            <div className="role-player">{chancellor?.name}</div>
          </div>
        </div>
      </div>
    </div>
  );
}
