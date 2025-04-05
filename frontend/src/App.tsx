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

export default () => {
  const { isAuthenticated } = useAuth();

  function PrivateRoute({ children }: { children: React.ReactElement }) {
    const location = useLocation();

    if (!isAuthenticated) {
      return (
        <Navigate to="/login" state={{ from: location.pathname }} replace />
      );
    }
    return children;
  }
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route
          path="/login"
          element={isAuthenticated ? <Navigate to="/" /> : <Login />}
        />
        <Route path="/callback" element={<CallbackPage />} />
        <Route
          path="/"
          element={
            <PrivateRoute>
              <RequestForm />
            </PrivateRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
};
