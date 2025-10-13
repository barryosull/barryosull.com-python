import { useState, useEffect, useRef } from 'react';
import { api } from '../services/api';
import { playerStorage } from '../services/storage';

export function useGameState(roomId) {
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
        api.getRoomState(roomId),
        api.getGameState(roomId).catch(() => null)
      ];

      if (playerId && !roleFetchedRef.current) {
        promises.push(api.getMyRole(roomId, playerId).catch(() => null));
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

  const notifications = ['elected', 'policy_enacted', 'executed', 'vetoed', 'special_election', 'loyalty_investigated'];

  useEffect(() => {
    if (!roomId) return;

    roleFetchedRef.current = false;
    fetchGameState();

    // Connect to Websocket
    const socket = new WebSocket('ws://localhost:8000/api/ws/' + roomId);
    socketRef.current = socket;

    socket.onmessage = function(event) {
      const message = JSON.parse(event.data);

      if (message.type === 'game_state_updated') {
        fetchGameState();
      } 
      if (notifications.includes(message.type)) {
        setNotification(message);
      }
    }

    const cleanup_func = () => {
      socket.close();
    };

    return cleanup_func;
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
    refresh,
    notification,
    clearNotification: () => setNotification(null)
  };
}
