import { BrowserRouter, Routes, Route } from 'react-router-dom';
import HomePage from './components/HomePage';
import Lobby from './components/Lobby';
import GameBoard from './components/GameBoard';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/room/:roomId" element={<Lobby />} />
        <Route path="/game/:roomId" element={<GameBoard />} />
      </Routes>
    </BrowserRouter>
  );
}
