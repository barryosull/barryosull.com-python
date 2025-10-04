const API_BASE = '/api';

class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

async function handleResponse(response) {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new ApiError(error.detail || 'Request failed', response.status);
  }
  return response.json();
}

export const api = {
  async createRoom(playerName) {
    const response = await fetch(`${API_BASE}/rooms`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_name: playerName })
    });
    return handleResponse(response);
  },

  async joinRoom(roomId, playerName) {
    const response = await fetch(`${API_BASE}/rooms/${roomId}/join`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_name: playerName })
    });
    return handleResponse(response);
  },

  async getRoomState(roomId) {
    const response = await fetch(`${API_BASE}/rooms/${roomId}`);
    return handleResponse(response);
  },

  async startGame(roomId, playerId) {
    const response = await fetch(`${API_BASE}/rooms/${roomId}/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_id: playerId })
    });
    return handleResponse(response);
  },

  async nominateChancellor(roomId, playerId, chancellorId) {
    const response = await fetch(`${API_BASE}/games/${roomId}/nominate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        player_id: playerId,
        chancellor_id: chancellorId
      })
    });
    return handleResponse(response);
  },

  async castVote(roomId, playerId, vote) {
    const response = await fetch(`${API_BASE}/games/${roomId}/vote`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_id: playerId, vote })
    });
    return handleResponse(response);
  },

  async discardPolicy(roomId, playerId, policyType) {
    const response = await fetch(`${API_BASE}/games/${roomId}/discard-policy`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_id: playerId, policy_type: policyType })
    });
    return handleResponse(response);
  },

  async enactPolicy(roomId, playerId, policyType) {
    const response = await fetch(`${API_BASE}/games/${roomId}/enact-policy`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_id: playerId, policy_type: policyType })
    });
    return handleResponse(response);
  },

  async getGameState(roomId) {
    const response = await fetch(`${API_BASE}/games/${roomId}/state`);
    return handleResponse(response);
  },

  async getMyRole(roomId, playerId) {
    const response = await fetch(`${API_BASE}/games/${roomId}/my-role?player_id=${playerId}`);
    return handleResponse(response);
  }
};
