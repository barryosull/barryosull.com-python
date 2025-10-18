const API_BASE = 'http://127.0.0.1:8000/api';

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
  if (response.status === 204) {
    return {}
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

  async joinRoom(roomCode, playerName) {
    const response = await fetch(`${API_BASE}/rooms/${roomCode}/join`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_name: playerName })
    });
    return handleResponse(response);
  },

  async getRoomState(roomCode) {
    const response = await fetch(`${API_BASE}/rooms/${roomCode}`);
    return handleResponse(response);
  },

  async startGame(roomCode, playerId) {
    const response = await fetch(`${API_BASE}/rooms/${roomCode}/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_id: playerId })
    });
    return handleResponse(response);
  },

  async reorderPlayers(roomCode, playerId, playerIds) {
    const response = await fetch(`${API_BASE}/rooms/${roomCode}/reorder-players`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        player_id: playerId,
        player_ids: playerIds
      })
    });
    return handleResponse(response);
  },

  async nominateChancellor(roomCode, playerId, chancellorId) {
    const response = await fetch(`${API_BASE}/games/${roomCode}/nominate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        player_id: playerId,
        chancellor_id: chancellorId
      })
    });
    return handleResponse(response);
  },

  async castVote(roomCode, playerId, vote) {
    const response = await fetch(`${API_BASE}/games/${roomCode}/vote`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_id: playerId, vote })
    });
    return handleResponse(response);
  },

  async discardPolicy(roomCode, playerId, policyType) {
    const response = await fetch(`${API_BASE}/games/${roomCode}/discard-policy`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_id: playerId, policy_type: policyType })
    });
    return handleResponse(response);
  },

  async enactPolicy(roomCode, playerId, policyType) {
    const response = await fetch(`${API_BASE}/games/${roomCode}/enact-policy`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_id: playerId, policy_type: policyType })
    });
    return handleResponse(response);
  },

  async getGameState(roomCode) {
    const response = await fetch(`${API_BASE}/games/${roomCode}/state`);
    return handleResponse(response);
  },

  async getMyRole(roomCode, playerId) {
    const response = await fetch(`${API_BASE}/games/${roomCode}/my-role?player_id=${playerId}`);
    return handleResponse(response);
  },

  async investigateLoyalty(roomCode, playerId, targetPlayerId) {
    const response = await fetch(
      `${API_BASE}/games/${roomCode}/investigate-loyalty?player_id=${playerId}&target_player_id=${targetPlayerId}`
    );
    return handleResponse(response);
  },

  async useExecutiveAction(roomCode, playerId, targetPlayerId = null) {
    const response = await fetch(`${API_BASE}/games/${roomCode}/use-power`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        player_id: playerId,
        target_player_id: targetPlayerId
      })
    });
    return handleResponse(response);
  },

  async veto(roomCode, playerId, approveVeto) {
    const response = await fetch(`${API_BASE}/games/${roomCode}/veto`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        player_id: playerId,
        approve_veto: approveVeto
      })
    });
    if (response.status === 204) {
      return null;
    }
    return handleResponse(response);
  }
};
