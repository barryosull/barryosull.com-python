# Secret Hitler - Frontend

React-based frontend for the Secret Hitler online game.

## Quick Start (Docker)

The easiest way to run the entire application (frontend + backend) is using Docker Compose from the project root:

```bash
# From project root
docker-compose up -d
```

The app will be available at http://localhost:8080

## Local Development

For frontend development with hot-reload:

### Setup

```bash
cd frontend
npm install
```

### Development Server

```bash
npm run dev
```

The development server will be available at http://localhost:3000

**Note:** Make sure the backend is running (either via Docker or locally) for the app to function.

### URL Parameters

**Storage Configuration:**

By default, player state is stored in **localStorage** (persists across browser restarts).

Available storage options:

- **localStorage** (default): Persists across browser restarts, shared across all tabs
  ```
  http://localhost:8080/
  ```

- **In-memory**: Stored in JavaScript variable, lost on page refresh, fully isolated per iframe
  ```
  http://localhost:8080/?storage=local
  ```

**Note:** The `?storage=local` parameter is automatically preserved across all route changes within the app, ensuring consistent storage behavior throughout the session.

**Pre-populate Player Name:**

You can pre-fill the player name field using the `name` parameter:

```
http://localhost:8080/?name=Alice
```

**Combine parameters:**

```
http://localhost:8080/?storage=local&name=Player1
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

For easy testing with multiple players in one browser, use the test page:

**With Docker:**
```
http://localhost:8080/test/multi-player
```

**With Dev Server:**
```
http://localhost:3000/test/multi-player
```

This loads 5 iframes, each with:
- `?storage=local` (in-memory storage, fully isolated per iframe)
- `?name=Player1` through `Player5` (pre-filled names)

Perfect for testing the full game flow without opening multiple browsers!

**Booting into a known state**
There is a play-test script that will boot a game into a known state and print a link to said game for play-testing.

There are two args to the script:
1. Number of players
2. Rounds to play (always enacts fascist policies)

Here is how this looks with docker:
```bash
docker-compose exec app python src/scripts/playtest.py 6 1
```

## Mobile Optimized

The UI is responsive and works on mobile devices.
