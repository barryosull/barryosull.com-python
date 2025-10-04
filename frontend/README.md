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

### Storage Configuration

By default, player state is stored in **localStorage** (persists across browser restarts).

To use **sessionStorage** instead (isolates each tab, useful for testing multiple players):

```
http://localhost:3000/?storage=session
```

This allows you to open multiple tabs and play as different players in the same browser.

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

## Mobile Optimized

The UI is responsive and works on mobile devices.
