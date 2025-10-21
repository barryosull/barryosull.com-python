import { useParams, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { useGameState } from '../hooks/useGameState';
import { api } from '../services/api';
import { playerStorage, preserveParams, initializeFromUrl } from '../services/storage';
import PlayerList from './PlayerList';
import LiberalTrack from './LiberalTrack';
import FascistTrack from './FascistTrack';
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
  const { roomCode } = useParams();
  const navigate = useNavigate();
  const { gameState, room, myRole, error, loading, refresh, notification, clearNotification } = useGameState(roomCode);
  const myPlayerId = playerStorage.getPlayerId();
  const [showRoleOverlay, setShowRoleOverlay] = useState(false);
  const [autoCloseNotifications, setAutoCloseNotifications] = useState(
    new URLSearchParams(window.location.search).get('auto_close_notifications') === '1'
  );

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
      await api.nominateChancellor(roomCode, myPlayerId, chancellorId);
      refresh();
    } catch (err) {
      console.error(err.message)
    }
  };

  const handleVote = async (vote) => {
    try {
      await api.castVote(roomCode, myPlayerId, vote);
      refresh();
    } catch (err) {
      console.error(err)
    }
  };

  const handleDiscardPolicy = async (policyType) => {
    try {
      await api.discardPolicy(roomCode, myPlayerId, policyType);
      refresh();
    } catch (err) {
      console.error(err.message)
    }
  };

  const handleEnactPolicy = async (policyType) => {
    try {
      await api.enactPolicy(roomCode, myPlayerId, policyType);
      refresh();
    } catch (err) {
      console.error(err.message)
    }
  };

  const handleExecutiveAction = async (targetPlayerId) => {
    try {
      const result = await api.useExecutiveAction(roomCode, myPlayerId, targetPlayerId);
      refresh();
      return result;
    } catch (err) {
      console.error(err.message)
      throw err;
    }
  };

  const handleVeto = async (approveVeto) => {
    try {
      await api.veto(roomCode, myPlayerId, approveVeto);
      refresh();
    } catch (err) {
      console.error(err.message)
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
              <div
                className={`role-display ${gameState.game_over_reason.toUpperCase().includes('LIBERAL') ? 'liberal' : 'fascist'}`}
              ></div>
              {gameState.game_over_reason && (
                <h3 className="overlay-subtitle">{gameState.game_over_reason}</h3>
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
      </div>

      <div className="game-board">
        <PlayerList
            players={room.players}
            gameState={gameState}
            myPlayerId={myPlayerId}
          />
        <LiberalTrack gameState={gameState} />
        <FascistTrack gameState={gameState} players={room.players} />
        <div className="controls">
          <button
            id="display-role"
            onClick={() => setShowRoleOverlay(true)}
            className="button"
          >
            View My Role
          </button>
          <div className="toggle-control">
            <label htmlFor="auto-close-toggle" className="toggle-label">
              Auto close notifications
            </label>
            <label className="toggle-switch">
              <input
                type="checkbox"
                id="auto-close-toggle"
                checked={autoCloseNotifications}
                onChange={(e) => setAutoCloseNotifications(e.target.checked)}
              />
              <span className="toggle-slider"></span>
            </label>
          </div>
        </div>   
      </div>

      {!notification && renderPhaseView()}

      <Toast gameState={gameState} />
  
      <NotificationOverlay
        notification={notification}
        players={room?.players || []}
        onClose={clearNotification}
        autoClose={autoCloseNotifications}
      />

      <RoleOverlay
        myRole={myRole}
        roomCode={roomCode}
        myPlayerId={myPlayerId}
        forceShow={showRoleOverlay}
        onClose={() => setShowRoleOverlay(false)}
      />
    </div>
  </>);
}
