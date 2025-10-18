import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { playerStorage, preserveParams } from '../services/storage';

export default function HomePage() {
  const [playerName, setPlayerName] = useState(() => {
    const params = new URLSearchParams(window.location.search);
    return params.get('name') || '';
  });
  const [roomCode, setRoomCode] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleCreateRoom = async (e) => {
    e.preventDefault();
    setError('');

    if (!playerName.trim()) {
      setError('Please enter your name');
      return;
    }

    setLoading(true);
    try {
      const result = await api.createRoom(playerName.trim());
      playerStorage.setPlayerId(result.player_id);
      playerStorage.setPlayerName(playerName.trim());
      navigate(preserveParams(`/room/${result.room_code}`));
    } catch (err) {
      setError("Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  const handleJoinRoom = async (e) => {
    e.preventDefault();
    setError('');

    if (!playerName.trim()) {
      setError('Please enter your name');
      return;
    }

    if (!roomCode.trim()) {
      setError('Please enter a room code');
      return;
    }

    setLoading(true);
    try {
      const result = await api.joinRoom(roomCode.trim(), playerName.trim());
      playerStorage.setPlayerId(result.player_id);
      playerStorage.setPlayerName(playerName.trim());
      navigate(preserveParams(`/room/${roomCode.trim()}`));
    } catch (err) {
      setError("Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container lobby">
      <div className="home">
        <div className="logo"></div>

        <div className="game-description">
          <p>
          Welcome to Secret Hitler! A deception game for 5 to 10 players.
          This is an online version that can be played in person or remotely.<br/>
          </p>
          <a href="https://www.secrethitler.com/assets/Secret_Hitler_Rules.pdf" target="__blank">
            Find a refresher on the rules here
          </a>
        </div>

        {error && <div className="error">{error}</div>}

        <div className="name-input">
          <h2 className="subtitle">Player Name</h2>
          <input
            type="text"
            placeholder="Your Name"
            value={playerName}
            onChange={(e) => setPlayerName(e.target.value)}
            disabled={loading}
            maxLength={10}
          />
        </div>

        <div>
          <h2 className="subtitle">Create New Game</h2>
          <button
            onClick={handleCreateRoom}
            disabled={loading}
          >
            Create Room
          </button>
        </div>

        <div className="divider">OR</div>

        <div>
          <h2 className="subtitle">Join Existing Game</h2>
          <input
            type="text"
            placeholder="Room Code"
            value={roomCode}
            onChange={(e) => setRoomCode(e.target.value)}
            disabled={loading}
          />
          <button
            onClick={handleJoinRoom}
            disabled={loading}
          >
            Join Room
          </button>
        </div>
      </div>
    </div>
  );
}
