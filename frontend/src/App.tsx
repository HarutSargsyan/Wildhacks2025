// src/App.tsx
import React from "react";
import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
  useLocation,
} from "react-router";
import { useAuth } from "./context/AuthProvider";
import Login from "./pages/Login";
import CallbackPage from "./pages/Callback";
import RequestForm from "./pages/RequestForm"; // your protected UI
import Navbar from "./components/NavBar";
import PersonalInfo from "./pages/PersonalInfo";
import WaitingPage from "./pages/WaitingPage";
import MatchPage from "./pages/MatchPage";

export default () => {
  const { user } = useAuth();

  function PrivateRoute({ children }: { children: React.ReactElement }) {
    const location = useLocation();

    if (!user) {
      return (
        <Navigate to="/login" state={{ from: location.pathname }} replace />
      );
    }
    return children;
  }
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/login" element={user ? <Navigate to="/" /> : <Login />} />
        <Route path="/auth-callback" element={<CallbackPage />} />
        <Route
          path="/onboarding"
          element={
            <PrivateRoute>
              <PersonalInfo />
            </PrivateRoute>
          }
        />
        <Route
          path="/"
          element={
            <PrivateRoute>
              {user?.is_onboarded ? (
                <RequestForm />
              ) : (
                <Navigate to="/onboarding" />
              )}
            </PrivateRoute>
          }
        />
        <Route
          path="/waiting"
          element={
            <PrivateRoute>
              <WaitingPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/match"
          element={
            <PrivateRoute>
              <MatchPage />
            </PrivateRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  );
};
