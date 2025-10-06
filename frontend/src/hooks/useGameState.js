import { useState, useEffect } from 'react';
import { api } from '../services/api';
import { playerStorage } from '../services/storage';

export function useGameState(roomId) {
  const [gameState, setGameState] = useState(null);
  const [room, setRoom] = useState(null);
  const [myRole, setMyRole] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchGameState = async () => {
    
    const playerId = playerStorage.getPlayerId();
    
    try {
      const [roomData, gameData, roleData] = await Promise.all([
        api.getRoomState(roomId),
        api.getGameState(roomId).catch(() => null),
        playerId ? api.getMyRole(roomId, playerId).catch(() => null) : null
      ]);

      setRoom(roomData);
      setGameState(gameData);
      setMyRole(roleData);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!roomId) return;

    fetchGameState();
    const interval = setInterval(fetchGameState, 2000);

    return () => clearInterval(interval);
  }, [roomId]);

  const refresh = () => {
    fetchGameState();
  };

  return {
    gameState,
    room,
    myRole,
    error,
    loading,
    refresh
  };
}
