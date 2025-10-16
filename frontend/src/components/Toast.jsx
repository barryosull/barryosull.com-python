import { useState, useEffect, useRef } from 'react';
import '../../assets/styles.css';

export default function Toast({ gameState }) {
  const getPowerDescription = (presidentialPower) => {
    switch (presidentialPower) {
      case 'INVESTIGATE_LOYALTY':
        return 'President is investigating a player\'s party membership';
      case 'POLICY_PEEK':
        return 'President is peeking at the top 3 policies';
      case 'EXECUTION':
        return 'President is selection a player for execution';
      case 'CALL_SPECIAL_ELECTION':
        return 'President is selecting the next presidential candidate';
      default:
        return 'President is using their executive power';
    }
  };

  const phases = {
    'NOMINATION': "Nomination Phase",
    'ELECTION': "Voting",
    'LEGISLATIVE_PRESIDENT': "Policy Selection",
    'LEGISLATIVE_CHANCELLOR': "Policy Selection",
    'EXECUTIVE_ACTION': "Executive action",
    'GAME_OVER': "Game over",
  };

  const messages = {
    'NOMINATION': "Waiting for president to nominate a chancellor",
    'ELECTION': "Voting on chancellor",
    'LEGISLATIVE_PRESIDENT': "President is selecting a policy to discard",
    'LEGISLATIVE_CHANCELLOR': (gameState.veto_requested)
      ? "Chancellor has requested a veto from the president"
      : "Chancellor is selecting a policy to enact",
    'EXECUTIVE_ACTION': getPowerDescription(gameState.presidential_power),
    'GAME_OVER': "End of game",
  };

  const phase = phases[gameState.current_phase] ?? "Unknown phase: " + gameState.current_phase;
  const message = messages[gameState.current_phase] ?? "Unknown phase, means I (the dev) missed something, whoops . . .";

  const [current, setCurrent] = useState({ phase, message, key: 0 });
  const [previous, setPrevious] = useState(null);
  const isFirstRender = useRef(true);

  useEffect(() => {
    setPrevious(current);
    setCurrent({ phase, message, key: current.key + 1 });

    const timer = setTimeout(() => {
      isFirstRender.current = false;
      setPrevious(null);
    }, 500);

    return () => clearTimeout(timer);
  }, [phase, message]);

  return (
    <>
      {previous && (
        <div key={previous.key} className="toast toast-previous">
          <div className="toast-content slide-out">
            <h3 className="toast-title">{previous.phase}</h3>
            <div className="toast-waiting">
              {previous.message}
            </div>
          </div>
        </div>
      )}
      <div key={current.key} className="toast">
        <div className={`toast-content ${!isFirstRender.current ? 'slide-in' : ''}`}>
          <h3 className="toast-title">{current.phase}</h3>
          <div className="toast-waiting">
            {current.message}
          </div>
        </div>
      </div>
    </>
  );
}