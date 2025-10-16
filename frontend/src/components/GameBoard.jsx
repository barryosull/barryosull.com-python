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
import VetoConfirm from './VetoConfirm';
import ExecutiveActionView from './ExecutiveActionView';
import RoleOverlay from './RoleOverlay';
import NotificationOverlay from './NotificationOverlay';
import '../../assets/styles.css';
import Toast from './Toast';

export default function GameBoard() {
  const { roomId } = useParams();
  const navigate = useNavigate();
  const { gameState, room, myRole, error, loading, refresh, notification, clearNotification } = useGameState(roomId);
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
        if (gameState.veto_requested) {
          return (
            <VetoConfirm
              gameState={gameState}
              myPlayerId={myPlayerId}
              onVeto={handleVeto}
            />
          );
        }

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
          <div className="overlay fade-in">
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
      
      <div class="game-board">
        <div className="players-section">
          <PlayerList
            players={room.players}
            gameState={gameState}
            myPlayerId={myPlayerId}
          />
        </div>

        <div className="main-content">
          <PolicyTracks gameState={gameState} players={room.players} />
        </div>
      </div>

      {!notification && renderPhaseView()}

      <Toast gameState={gameState} />
  
      <NotificationOverlay
        notification={notification}
        players={room?.players || []}
        onClose={clearNotification}
      />

      <RoleOverlay myRole={myRole} roomId={roomId} myPlayerId={myPlayerId} />
    </div>
  </>);
}
