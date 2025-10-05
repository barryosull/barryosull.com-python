// In-memory storage for when storage=local is used
const memoryStorage = {
  playerId: null,
  playerName: null
};

function getStorageType() {
  const params = new URLSearchParams(window.location.search);
  const storageParam = params.get('storage');

  if (storageParam === 'local') {
    return {
      setItem(key, value) {
        memoryStorage[key] = value;
      },
      getItem(key) {
        return memoryStorage[key];
      },
      removeItem(key) {
        memoryStorage[key] = null;
      }
    };
  }

  return localStorage;
}

const storage = getStorageType();

function isUsingMemoryStorage() {
  const params = new URLSearchParams(window.location.search);
  return params.get('storage') === 'local';
}

export function initializeFromUrl() {
  if (!isUsingMemoryStorage()) {
    return;
  }

  const params = new URLSearchParams(window.location.search);
  const playerIdParam = params.get('playerId');

  if (playerIdParam && !memoryStorage.playerId) {
    memoryStorage.playerId = playerIdParam;
  }
}

export function preserveParams(path) {
  const params = new URLSearchParams(window.location.search);
  const storageParam = params.get('storage');

  if (storageParam === 'local') {
    const separator = path.includes('?') ? '&' : '?';
    return `${path}${separator}storage=local`;
  }

  return path;
}

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
