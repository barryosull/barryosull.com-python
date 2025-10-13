import { useParams, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { useGameState } from '../hooks/useGameState';
import { api } from '../services/api';
import { playerStorage, preserveParams, initializeFromUrl } from '../services/storage';
import PlayerList from './PlayerList';
import PolicyTracks from './PolicyTracks';
import NominationView from './NominationView';
import VotingView from './VotingView';
import PolicySelectionView from './PolicySelectionView';
import ExecutiveActionView from './ExecutiveActionView';
import RoleOverlay from './RoleOverlay';
import '../../assets/styles.css';
import Toast from './Toast';

export default function GameBoard() {
  const { roomId } = useParams();
  const navigate = useNavigate();
  const { gameState, room, myRole, error, loading, refresh } = useGameState(roomId);
  const myPlayerId = playerStorage.getPlayerId();

  useEffect(() => {
    initializeFromUrl();
  }, []);

  if (loading) {
    return (
      <div className="container">
        <div className="loading">Loading game...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container">
        <div className="error">{error}</div>
        <button onClick={() => navigate(preserveParams('/'))} className="button">
          Return Home
        </button>
      </div>
    );
  }

  if (!gameState || !room) {
    return (
      <div className="container">
        <div className="error">Game not found</div>
        <button onClick={() => navigate(preserveParams('/'))} className="button">
          Return Home
        </button>
      </div>
    );
  }

  const handleNominate = async (chancellorId) => {
    try {
      await api.nominateChancellor(roomId, myPlayerId, chancellorId);
      refresh();
    } catch (err) {
      alert(err.message);
    }
  };

  const handleVote = async (vote) => {
    try {
      await api.castVote(roomId, myPlayerId, vote);
      refresh();
    } catch (err) {
      alert(err.message);
    }
  };

  const handleDiscardPolicy = async (policyType) => {
    try {
      await api.discardPolicy(roomId, myPlayerId, policyType);
      refresh();
    } catch (err) {
      alert(err.message);
    }
  };

  const handleEnactPolicy = async (policyType) => {
    try {
      await api.enactPolicy(roomId, myPlayerId, policyType);
      refresh();
    } catch (err) {
      alert(err.message);
    }
  };

  const handleExecutiveAction = async (targetPlayerId) => {
    try {
      const result = await api.useExecutiveAction(roomId, myPlayerId, targetPlayerId);
      refresh();
      return result;
    } catch (err) {
      alert(err.message);
      throw err;
    }
  };

  const handleVeto = async (approveVeto) => {
    try {
      await api.veto(roomId, myPlayerId, approveVeto);
      refresh();
    } catch (err) {
      alert(err.message);
    }
  };

  const renderToast = () => {
  
    const getPowerDescription = (presidentialPower) => {
      switch (presidentialPower) {
        case 'INVESTIGATE_LOYALTY':
          return 'President is investigating a player\'s party membership';
        case 'POLICY_PEEK':
          return 'President is peeking at the top 3 policies';
        case 'EXECUTION':
          return 'President is selection a player for execution';
        case 'CALL_SPECIAL_ELECTION':
          return 'President is selecting the next presidential candidate';
        default:
          return 'President is using their executive power';
      }
    };

    const phases = {
      'NOMINATION' : "Nomination Phase",
      'ELECTION' : "Voting",
      'LEGISLATIVE_PRESIDENT' : "Policy Selection",
      'LEGISLATIVE_CHANCELLOR' : "Policy Selection",
      'EXECUTIVE_ACTION' : "Executive action",
      'GAME_OVER' : "Game over",
    }

    const messages = {
      'NOMINATION' : "Waiting for president to nominate a chancellor",
      'ELECTION' : "Voting on chancellor",
      'LEGISLATIVE_PRESIDENT' : "President is select a policy to discard",
      'LEGISLATIVE_CHANCELLOR' : (gameState.veto_requested)
        ? "Chancellor has requested a veto from the president"
        : "Chancellor is selecting a policy to enact",
      'EXECUTIVE_ACTION' : getPowerDescription(gameState.presidential_power),
      'GAME_OVER' : "End of game",
    }

    const phase = phases[gameState.current_phase] ??= "Unknown phase: " + gameState.current_phase
    const message = messages[gameState.current_phase] ??= "Unknown phase, means I (the dev) missed something, whoops . . .";
    return (<Toast phase={phase} message={message}></Toast>)
  }

  const renderPhaseView = () => {
    switch (gameState.current_phase) {
      case 'NOMINATION':
        return (
          <NominationView
            players={room.players}
            gameState={gameState}
            myPlayerId={myPlayerId}
            onNominate={handleNominate}
          />
        );

      case 'ELECTION':
        return (
          <VotingView
            gameState={gameState}
            players={room.players}
            myPlayerId={myPlayerId}
            onVote={handleVote}
          />
        );

      case 'LEGISLATIVE_PRESIDENT':
        return (
          <PolicySelectionView
            gameState={gameState}
            myPlayerId={myPlayerId}
            onSelectPolicy={handleDiscardPolicy}
            onVeto={handleVeto}
            isPresident={true}
          />
        );

      case 'LEGISLATIVE_CHANCELLOR':
        return (
          <PolicySelectionView
            gameState={gameState}
            myPlayerId={myPlayerId}
            onSelectPolicy={handleEnactPolicy}
            onVeto={handleVeto}
            isPresident={false}
          />
        );

      case 'EXECUTIVE_ACTION':
        return (
          <ExecutiveActionView
            gameState={gameState}
            myPlayerId={myPlayerId}
            players={room.players}
            onUseAction={handleExecutiveAction}
            presidentialPower={gameState.presidential_power}
          />
        );

      case 'GAME_OVER':
        return (
          <div className="overlay">
            <div className = "overlay-content">
              <h2 className="overlay-title">Game Over!</h2>
              {gameState.game_over_reason && (
                <p className="overlay-subtitle">{gameState.game_over_reason}</p>
              )}
              <button onClick={() => navigate(preserveParams('/'))} className="confirm-button">
                Return to Home
              </button>
            </div>
          </div>
        );

      default:
        return (
          <div className="phase-box">
            <p>Unknown phase: {gameState.current_phase}</p>
          </div>
        );
    }
  };

  return (<>
    <div className="container">
      <div className="header">
        <h1 className="title">Secret Hitler</h1>
        <div className="room-id">Room: {roomId}</div>
      </div>
      
      <div className="players-section">
        <PlayerList
          players={room.players}
          gameState={gameState}
          myPlayerId={myPlayerId}
        />
      </div>

      <div className="main-content">
        <PolicyTracks gameState={gameState} players={room.players} />
        {renderPhaseView()}
        {renderToast()}
      </div>

      <RoleOverlay myRole={myRole} roomId={roomId} myPlayerId={myPlayerId} />
    </div>
  </>);
}
