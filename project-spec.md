# Secret Hitler - Project Specification

## Overview
An online implementation of the social deduction game Secret Hitler, where players are secretly divided into two teams—liberals and fascists—and must navigate deception and strategy to either elect Hitler or pass policies to win.

## Technology Stack
- **Backend**: Python with FastAPI for REST endpoints
- **Frontend**: React JS
- **Communication**: HTTP requests
- **Architecture**: Ports and Adapters (Hexagonal Architecture)
- **Design Approach**: Domain-Driven Design (DDD)

## High-Level Requirements

### Functional Requirements
1. Players can create game rooms with unique UUID identifiers
2. Players can join existing games using room IDs
3. Room creator can start the game
4. Minimum 5 players required to start a game (supports 5-10 players)
5. Game enforces Secret Hitler rules including voting, policy enactment, and special powers
6. Real-time game state updates for all players
7. Role assignment (liberals, fascists, Hitler)
8. Policy deck management (liberal and fascist policies)
9. Presidential succession and government formation
10. Special presidential powers based on board state
11. Win condition detection for both teams

### Non-Functional Requirements
1. Mobile-optimized UI with basic, clean design
2. Responsive and fast gameplay experience
3. Session persistence for active games
4. Simple, intuitive user interface
5. Clear game state visualization

## Domain Concepts

### Core Entities

#### Game Room
- **Attributes**:
  - `room_id`: UUID
  - `creator_id`: Player ID
  - `status`: WAITING | IN_PROGRESS | COMPLETED
  - `players`: Collection of Players
  - `game_state`: Game State (optional, exists when in progress)
  - `created_at`: Timestamp

#### Player
- **Attributes**:
  - `player_id`: UUID
  - `name`: String
  - `is_connected`: Boolean
  - `is_alive`: Boolean (can be killed by presidential power)

#### Game State
- **Attributes**:
  - `round_number`: Integer
  - `president`: Player reference
  - `chancellor`: Player reference
  - `previous_government`: Previous President and Chancellor
  - `policy_deck`: Policy Deck
  - `liberal_track`: Integer (0-5 policies)
  - `fascist_track`: Integer (0-6 policies)
  - `election_tracker`: Integer (0-3 failed votes)
  - `current_phase`: Phase enum
  - `role_assignments`: Map of Player to Role

#### Role (Value Object)
- **Types**:
  - Liberal (team: LIBERAL, is_hitler: false)
  - Fascist (team: FASCIST, is_hitler: false)
  - Hitler (team: FASCIST, is_hitler: true)
- **Attributes**:
  - `team`: LIBERAL | FASCIST
  - `is_hitler`: Boolean

#### Policy (Value Object)
- **Types**: LIBERAL | FASCIST

#### Policy Deck (Entity)
- **Attributes**:
  - `draw_pile`: List of Policies (6 liberal, 11 fascist)
  - `discard_pile`: List of Policies
- **Behaviors**:
  - `draw(count: int)`: Draw N policies
  - `discard(policies: List[Policy])`: Add to discard pile
  - `shuffle()`: Shuffle draw pile
  - `reshuffle_if_needed()`: If draw pile < 3, shuffle discard into draw

#### Game Phase (Enum)
- `NOMINATION`: President nominates a chancellor
- `ELECTION`: Players vote on the proposed government
- `LEGISLATIVE_PRESIDENT`: President discards one of three policies
- `LEGISLATIVE_CHANCELLOR`: Chancellor enacts one of two remaining policies
- `EXECUTIVE_ACTION`: President uses special power (if triggered)
- `GAME_OVER`: Game has ended

#### Presidential Power (Enum)
- `INVESTIGATE_LOYALTY`: Examine a player's party membership
- `CALL_SPECIAL_ELECTION`: Choose the next presidential candidate
- `POLICY_PEEK`: Examine top 3 cards of policy deck
- `EXECUTION`: Kill a player (remove from game)

### Aggregates

#### Game Aggregate (Root: Game Room)
The Game Room is the aggregate root that encapsulates the entire game lifecycle:
- Game Room
- Players in room
- Game State (when active)
- Policy Deck
- Role Assignments

### Domain Services

#### RoleAssignmentService
- Randomly assigns roles based on player count
- Ensures proper distribution (varies by player count)

#### WinConditionService
- Checks for win conditions after each policy enactment
- Liberal wins: 5 liberal policies OR Hitler assassinated
- Fascist wins: 6 fascist policies OR Hitler elected chancellor (after 3 fascist policies)

#### GovernmentFormationService
- Validates chancellor nominations (not previous government, not Hitler if restricted)
- Handles election results
- Manages failed election tracker

#### PolicyEnactmentService
- Handles policy draw and selection flow
- Manages deck reshuffling
- Triggers presidential powers based on board state

### Value Objects
- Room ID (UUID)
- Player ID (UUID)
- Policy
- Role
- Vote (JA | NEIN)

## High-Level Architecture

### Ports and Adapters Structure

```
src/
├── domain/
│   ├── entities/
│   │   ├── game_room.py
│   │   ├── player.py
│   │   ├── game_state.py
│   │   └── policy_deck.py
│   ├── value_objects/
│   │   ├── role.py
│   │   ├── policy.py
│   │   └── vote.py
│   ├── services/
│   │   ├── role_assignment_service.py
│   │   ├── win_condition_service.py
│   │   ├── government_formation_service.py
│   │   └── policy_enactment_service.py
│   └── events/
│       ├── game_started.py
│       ├── government_elected.py
│       ├── policy_enacted.py
│       └── game_ended.py
├── application/
│   ├── commands/
│   │   ├── create_room.py
│   │   ├── join_room.py
│   │   ├── start_game.py
│   │   ├── nominate_chancellor.py
│   │   ├── cast_vote.py
│   │   ├── discard_policy.py
│   │   └── use_power.py
│   ├── queries/
│   │   ├── get_room_state.py
│   │   ├── get_player_role.py
│   │   └── get_game_state.py
│   └── use_cases/
│       └── game_orchestrator.py
├── adapters/
│   ├── api/
│   │   ├── rest/
│   │   │   ├── routes.py
│   │   │   └── schemas.py
│   │   └── main.py
│   └── persistence/
│       ├── in_memory_repository.py
│       └── room_repository.py
└── ports/
    └── repository_port.py
```

### API Endpoints

#### Room Management
- `POST /rooms` - Create a new game room
- `GET /rooms/{room_id}` - Get room state
- `POST /rooms/{room_id}/join` - Join a room
- `POST /rooms/{room_id}/start` - Start the game (creator only)

#### Game Actions
- `POST /games/{room_id}/nominate` - Nominate a chancellor
- `POST /games/{room_id}/vote` - Cast a vote
- `POST /games/{room_id}/discard-policy` - President discards a policy
- `POST /games/{room_id}/enact-policy` - Chancellor enacts a policy
- `POST /games/{room_id}/use-power` - Use presidential power

#### Game State
- `GET /games/{room_id}/state` - Get current game state
- `GET /games/{room_id}/my-role` - Get the requesting player's role (private)

### Frontend Components Structure

```
src/
├── components/
│   ├── HomePage.jsx
│   ├── CreateRoom.jsx
│   ├── JoinRoom.jsx
│   ├── Lobby.jsx
│   ├── GameBoard.jsx
│   ├── PlayerList.jsx
│   ├── PolicyTracks.jsx
│   ├── NominationView.jsx
│   ├── VotingView.jsx
│   ├── PolicySelectionView.jsx
│   ├── ExecutiveActionView.jsx
│   └── GameOver.jsx
├── hooks/
│   └── useGameState.js
├── services/
│   └── api.js
└── App.jsx
```

## User Stories

### Epic 1: Room Management

**US-1.1: Create Game Room**
- As a player, I want to create a new game room so that I can host a game with my friends
- Acceptance Criteria:
  - Player can create a room from homepage
  - System generates a unique UUID for the room
  - Player receives the room ID to share
  - Player is automatically the room creator
  - Player is redirected to the lobby

**US-1.2: Join Game Room**
- As a player, I want to join an existing game room using a room ID
- Acceptance Criteria:
  - Player can enter a room ID on homepage
  - System validates the room exists
  - System validates the game hasn't started
  - Player joins the lobby
  - All players in lobby see the new player

**US-1.3: View Lobby**
- As a player in a lobby, I want to see all connected players
- Acceptance Criteria:
  - Display list of all players in the room
  - Show total player count
  - Show minimum player requirement (5)
  - Show room ID prominently for sharing
  - Creator sees a "Start Game" button
  - Non-creators see waiting message

### Epic 2: Game Start

**US-2.1: Start Game**
- As a room creator, I want to start the game when enough players have joined
- Acceptance Criteria:
  - Start button only enabled when 5+ players present
  - Start button only visible to creator
  - System randomly assigns roles
  - System creates policy deck
  - System selects first president (randomly)
  - All players transition to game board

**US-2.2: Receive Role Assignment**
- As a player, I want to know my secret role when the game starts
- Acceptance Criteria:
  - Player sees their role privately
  - Liberals see they are liberal (no other info)
  - Fascists see other fascists and Hitler (in larger games)
  - Hitler sees other fascists only in games with 6 or fewer players
  - Role information is clearly displayed and persistent

### Epic 3: Government Formation

**US-3.1: Nominate Chancellor**
- As the president, I want to nominate a chancellor candidate
- Acceptance Criteria:
  - President sees list of eligible players (not self, not previous government)
  - President selects one player
  - All players see the nominated government
  - Game transitions to voting phase
  - Clear indication of who is president and who is nominated

**US-3.2: Vote on Government**
- As a player, I want to vote on the proposed government
- Acceptance Criteria:
  - Player sees who is nominated
  - Player can vote "Ja" (yes) or "Nein" (no)
  - Vote is secret until all votes cast
  - Cannot change vote once submitted
  - Game shows waiting state for remaining votes

**US-3.3: View Election Results**
- As a player, I want to see the results of the election
- Acceptance Criteria:
  - All votes revealed simultaneously
  - Clear display of each player's vote
  - Show if government elected (>50% yes votes)
  - If elected, proceed to legislative session
  - If rejected, increment failed election tracker
  - Presidential rotation happens if rejected

### Epic 4: Legislative Session

**US-4.1: President Discards Policy**
- As the president in an elected government, I want to choose which policy to discard
- Acceptance Criteria:
  - President sees 3 policies drawn from deck
  - President selects 1 to discard
  - Discarded policy goes to discard pile (hidden)
  - Remaining 2 policies passed to chancellor
  - Clear timer or waiting indicator

**US-4.2: Chancellor Enacts Policy**
- As the chancellor, I want to choose which policy to enact
- Acceptance Criteria:
  - Chancellor sees 2 policies from president
  - Chancellor selects 1 to enact
  - Enacted policy placed on appropriate track
  - Other policy goes to discard pile
  - All players see which policy was enacted
  - Board state updates visibly

**US-4.3: View Board State**
- As a player, I want to see the current state of both policy tracks
- Acceptance Criteria:
  - Liberal track shows 0-5 policies
  - Fascist track shows 0-6 policies
  - Election tracker shows failed elections (0-3)
  - Current president and chancellor clearly marked
  - Previous government indicated

### Epic 5: Executive Actions

**US-5.1: Investigate Loyalty**
- As the president after triggering this power, I want to investigate a player's loyalty
- Acceptance Criteria:
  - President selects a player to investigate
  - President privately sees if player is Liberal or Fascist (not if they're Hitler)
  - Other players see who was investigated but not the result
  - President cannot investigate same player twice
  - Game continues with next round

**US-5.2: Call Special Election**
- As the president after triggering this power, I want to choose the next president
- Acceptance Criteria:
  - President selects any player (including self)
  - Selected player becomes next president
  - After their term, presidency returns to normal rotation
  - All players informed of special election

**US-5.3: Policy Peek**
- As the president after triggering this power, I want to peek at the top 3 policies
- Acceptance Criteria:
  - President privately sees top 3 policies
  - Policies remain in deck in same order
  - Other players informed president peeked
  - No mechanical effect on game

**US-5.4: Execution**
- As the president after triggering this power, I want to execute a player
- Acceptance Criteria:
  - President selects a player to execute
  - Selected player is killed (removed from game)
  - Player's role is NOT revealed
  - If Hitler executed, liberals win immediately
  - Dead players cannot vote or be nominated
  - All players see who was executed

### Epic 6: Game End

**US-6.1: Liberal Victory**
- As a player, I want to be notified when liberals win
- Acceptance Criteria:
  - Game ends when 5 liberal policies enacted
  - Game ends when Hitler is executed
  - All player roles revealed
  - Clear victory message displayed
  - Option to return to homepage

**US-6.2: Fascist Victory**
- As a player, I want to be notified when fascists win
- Acceptance Criteria:
  - Game ends when 6 fascist policies enacted
  - Game ends when Hitler elected chancellor after 3 fascist policies
  - All player roles revealed
  - Clear victory message displayed
  - Option to return to homepage

### Epic 7: Edge Cases & Game Rules

**US-7.1: Failed Election Chaos**
- As a player, I want the game to handle failed elections properly
- Acceptance Criteria:
  - Failed election tracker increments after each failed vote
  - After 3 failed elections, top policy auto-enacted
  - Election tracker resets after chaos
  - If Hitler elected chancellor during chaos after 3 fascist policies, game ends (fascists win)

**US-7.2: Deck Reshuffling**
- As a player, I want the deck to be managed properly
- Acceptance Criteria:
  - When fewer than 3 cards remain, discard pile shuffled into deck
  - Reshuffle happens before president draws
  - All players notified of reshuffle

**US-7.3: Veto Power**
- As chancellor or president (after 5 fascist policies), I want the option to veto
- Acceptance Criteria:
  - Veto only available after 5 fascist policies enacted
  - Chancellor can propose veto
  - President must agree for veto to succeed
  - If vetoed, both policies discarded, election tracker increments
  - If veto rejected, chancellor must enact a policy

## Game Rules Summary

### Setup
- 5-10 players required
- Role distribution varies by player count:
  - 5 players: 3 liberals, 1 fascist, 1 Hitler
  - 6 players: 4 liberals, 1 fascist, 1 Hitler
  - 7 players: 4 liberals, 2 fascists, 1 Hitler
  - 8 players: 5 liberals, 2 fascists, 1 Hitler
  - 9 players: 5 liberals, 3 fascists, 1 Hitler
  - 10 players: 6 liberals, 3 fascists, 1 Hitler
- Policy deck: 6 liberal, 11 fascist policies

### Win Conditions
**Liberals win if:**
- 5 liberal policies are enacted, OR
- Hitler is assassinated (executed)

**Fascists win if:**
- 6 fascist policies are enacted, OR
- Hitler is elected chancellor after 3 fascist policies are on the board

### Game Flow
1. **Nomination Phase**: President nominates a chancellor
2. **Election Phase**: All players vote on the government
3. **Legislative Phase**: If elected, president draws 3 policies, discards 1, chancellor enacts 1 of remaining 2
4. **Executive Action Phase**: If triggered, president uses power
5. Presidential rotation to next player

### Presidential Powers (triggered by fascist policy position)
- Position 1 (5-6 players): None
- Position 1 (7-10 players): Investigate Loyalty
- Position 2 (7-10 players): Investigate Loyalty (or Special Election for 9-10)
- Position 3: Policy Peek (or Special Election for 7-8 players)
- Position 4: Execution
- Position 5: Execution
- Position 6: N/A (game ends)

### Key Rules
- Cannot nominate previous president or chancellor as chancellor (except if 5 or fewer alive players)
- Cannot nominate Hitler as chancellor if 3+ fascist policies enacted (he can still be elected)
- After 3 failed elections, top policy auto-enacted (chaos)
- Veto power unlocked after 5 fascist policies (chancellor proposes, president must agree)

## Implementation Phases

### Phase 1: Foundation (MVP Backend)
- Domain entities and value objects
- Repository implementation (in-memory)
- Room creation and joining
- Basic game state management

### Phase 2: Core Game Loop
- Role assignment
- Government formation
- Policy enactment
- Basic win conditions

### Phase 3: Frontend MVP
- Homepage (create/join)
- Lobby view
- Basic game board
- Voting and policy selection UI

### Phase 4: Advanced Features
- Executive actions
- Veto power
- Failed election handling
- Deck reshuffling

### Phase 5: Polish
- Mobile optimization
- Error handling and edge cases
- UI/UX improvements
- Game state persistence

## Testing Strategy

### Unit Tests
- Domain logic (role assignment, win conditions, policy deck mechanics)
- Business rules validation
- Value object behavior

### Integration Tests
- API endpoints
- Command and query handlers
- Repository interactions

### E2E Tests
- Complete game flow from room creation to victory
- All executive actions
- Edge cases (chaos, veto, reshuffling)

## Open Questions
1. Should there be a time limit for votes/policy selection?
  - No time limit
2. Should players be able to reconnect if they lose connection?
  1. Yes they should
3. Should there be a chat feature for discussion phases?
  - No chat feature
4. Should game history be persisted beyond active sessions?
  - No, feel free to delete the game once completed
5. Should there be authentication, or just anonymous play with display names?
  - Anonymous play is fine

## Future Enhancements
- Player authentication and profiles
- Game history and statistics
- Spectator mode
- Custom game rules/variants
- Voice chat integration
- Improved animations and transitions
- Tutorial/practice mode
