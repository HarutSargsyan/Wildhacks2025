import React, { useEffect } from "react";
import { useAuth } from "../context/AuthProvider";
import { useNavigate, useLocation } from "react-router";

export default () => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const { state } = useLocation() as { state: { from?: string } };

  useEffect(() => {
    if (isAuthenticated) {
      // redirect back to where they wanted to go
      navigate(state?.from || "/", { replace: true });
    }
  }, [isAuthenticated, navigate, state]);

  return <div>Finalizing sign‑in…</div>;
};
