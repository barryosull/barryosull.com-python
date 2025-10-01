# Secret Hitler

Write a project spec for an online version of the game secret hitler. Outline the requirements, the high level design and the domain concepts that should be implemented. 

Write a spec that Claude AI can use to the build the app step by step. 

Outline user stories as well, with high level details. 

Write the output to "project-spec.md".

## Technology:
- Python backend with fast API for endpoints
- React JS frontend
- Use HTTP for messaging back and forth

## Behaviour:
Players will hit the homepage and have the option to either create a game room or join an existing game via the ID

Game room IDs should be UUIDs.

The creator of the room can start the game at any point.

A minimum of 5 players are needed to start a game.

## Design
The game should follow the ports and adapters pattern. It should be playable via the browser.

Build it using domain driven design concepts.

## UI
Make the UI very basic. It should be optimised for mobile.

Game rules can be found here: https://www.secrethitler.com/assets/Secret_Hitler_Rules.pdf