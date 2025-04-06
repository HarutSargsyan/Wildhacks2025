// src/pages/CallbackPage.tsx
import { useEffect } from "react";
import { useNavigate, useLocation } from "react-router";
import { useAuth, User } from "../context/AuthProvider";

export default () => {
  const { completeLogin } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = (location.state as any)?.from || "/";

  useEffect(() => {
    // 1) Grab the raw `data` query‑param
    const params = new URLSearchParams(location.search);
    const raw = params.get("data");
    const error = params.get("error");

    if (error) {
      console.error("Login error:", error);
      navigate("/login", { replace: true });
    }

    if (!raw) {
      // no data? bounce back to login
      navigate("/login", { replace: true });
    }

    try {
      if (typeof raw !== "string") {
        throw new Error("Raw data is not a string");
      }

      const decoded = decodeURIComponent(raw);
      const payload: { user: User; token: string } = JSON.parse(decoded);

      // 3) Tell your AuthContext about it
      completeLogin(payload.user, payload.token);

      // 4) Redirect to where they were headed

      if (!payload.user.is_onboarded) {
        navigate("/onboarding", { replace: true });
      } else {
        navigate(from, { replace: true });
      }
    } catch (e) {
      console.error("Failed to parse auth payload:", e);
      navigate("/login", { replace: true });
    }
  }, []);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <p className="text-gray-600">Finalizing sign‑in…</p>
    </div>
  );
};
