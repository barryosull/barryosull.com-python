import { useState } from 'react';
import '../../assets/styles.css';

export default function Toast({ phase, message }) {
  return (
    <div className="toast">
      <div className="toast-content">
        <h3 className="toast-title">{phase}</h3>
        <div className="toast-waiting">
          {message}
        </div>
      </div>
    </div>
  );
}