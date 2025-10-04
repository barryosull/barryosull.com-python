function getStorageType() {
  const params = new URLSearchParams(window.location.search);
  const storageParam = params.get('storage');

  if (storageParam === 'session') {
    return sessionStorage;
  }

  return localStorage;
}

const storage = getStorageType();

export const playerStorage = {
  setPlayerId(playerId) {
    storage.setItem('playerId', playerId);
  },

  getPlayerId() {
    return storage.getItem('playerId');
  },

  setPlayerName(playerName) {
    storage.setItem('playerName', playerName);
  },

  getPlayerName() {
    return storage.getItem('playerName');
  },

  clear() {
    storage.removeItem('playerId');
    storage.removeItem('playerName');
  }
};
