# Secret Hitler - Frontend

React-based frontend for the Secret Hitler online game.

## Setup

```bash
cd frontend
npm install
```

## Development

```bash
npm run dev
```

The app will be available at http://localhost:3000

### URL Parameters

**Storage Configuration:**

By default, player state is stored in **localStorage** (persists across browser restarts).

Available storage options:

- **localStorage** (default): Persists across browser restarts, shared across all tabs
  ```
  http://localhost:3000/
  ```

- **In-memory**: Stored in JavaScript variable, lost on page refresh, fully isolated per iframe
  ```
  http://localhost:3000/?storage=local
  ```

**Note:** The `?storage=local` parameter is automatically preserved across all route changes within the app, ensuring consistent storage behavior throughout the session.

**Pre-populate Player Name:**

You can pre-fill the player name field using the `name` parameter:

```
http://localhost:3000/?name=Alice
```

**Combine parameters:**

```
http://localhost:3000/?storage=local&name=Player1
```

## Build

```bash
npm run build
```

## Features Implemented (Phase 3)

- **HomePage**: Create or join game rooms
- **Lobby**: Wait for players and start game
- **GameBoard**: Main game interface with:
  - Policy tracks (Liberal, Fascist, Election tracker)
  - Player list with roles and status
  - Phase-specific views:
    - Nomination phase
    - Voting phase
    - Policy selection (President/Chancellor)
  - Role display (your secret role)
  - Auto-refresh game state every 2 seconds

## Multi-Player Testing

For easy testing with multiple players in one browser, open `test-multi-player.html`:

```
http://localhost:3000/test-multi-player.html
```

This loads 5 iframes, each with:
- `?storage=local` (in-memory storage, fully isolated per iframe)
- `?name=Player1` through `Player5` (pre-filled names)

Perfect for testing the full game flow without opening multiple browsers!

## Mobile Optimized

The UI is responsive and works on mobile devices.
