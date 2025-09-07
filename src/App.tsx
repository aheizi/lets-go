import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Login from './pages/Login';
import PlanCreate from './pages/PlanCreate';
import PlanDetail from './pages/PlanDetail';
import PlanEdit from './pages/PlanEdit';
import PlanList from './pages/PlanList';
import Collaborate from './pages/Collaborate';
import Profile from './pages/Profile';
import ProfileSettings from './pages/ProfileSettings';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/plans" element={<PlanList />} />
          <Route path="/create" element={<PlanCreate />} />
          <Route path="/plan/create" element={<PlanCreate />} />
          <Route path="/plan/:id" element={<PlanDetail />} />
          <Route path="/edit-plan/:id" element={<PlanEdit />} />
          <Route path="/collaborate/:id" element={<Collaborate />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/profile/settings" element={<ProfileSettings />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
