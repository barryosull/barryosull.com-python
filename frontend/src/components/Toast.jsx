import { useState, useEffect, useRef } from 'react';
import '../../assets/styles.css';

export default function Toast({ phase, message }) {
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