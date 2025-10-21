import { useState, useEffect, useRef } from 'react';
import { api } from '../services/api';
import { playerStorage } from '../services/storage';

export function useGameState(roomCode) {
  const [gameState, setGameState] = useState(null);
  const [room, setRoom] = useState(null);
  const [myRole, setMyRole] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [notification, setNotification] = useState(null);
  const roleFetchedRef = useRef(false);
  const socketRef = useRef(null);

  const fetchGameState = async () => {

    const playerId = playerStorage.getPlayerId();

    try {
      const promises = [
        api.getRoomState(roomCode),
        api.getGameState(roomCode).catch(() => null)
      ];

      if (playerId && !roleFetchedRef.current) {
        promises.push(api.getMyRole(roomCode, playerId).catch(() => null));
      }

      const results = await Promise.all(promises);
      const roomData = results[0];
      const gameData = results[1];
      const roleData = results[2];

      setRoom(roomData);
      setGameState(gameData);
      if (roleData) {
        setMyRole(roleData);
        roleFetchedRef.current = true;
      }
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!roomCode) return;

    roleFetchedRef.current = false;
    fetchGameState();

    const wsUrl = import.meta.env.VITE_WS_URL;

    // Connect to Websocket
    const socket = new WebSocket(wsUrl + '/' + roomCode);
    socketRef.current = socket;

    socket.onmessage = function(event) {
      const message = JSON.parse(event.data);

      if (message.type === 'game_state_updated') {
        fetchGameState();
        return;
      }
      console.log(message)
      if (message.type) {
        setNotification(message);
      }
    }

    const cleanup_func = () => {
      socket.close();
    };

    return cleanup_func;
  }, [roomCode]);

  const refresh = () => {
    fetchGameState();
  };

  return {
    gameState,
    room,
    myRole,
    error,
    loading,
    refresh,
    notification,
    clearNotification: () => setNotification(null)
  };
}
