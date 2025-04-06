// src/context/AuthContext.tsx
import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import axios from "axios";
import { Navigate, useNavigate } from "react-router";

export interface User {
  id: string;
  email: string;
  name: string;
  picture?: string;
  is_onboarded?: boolean;
  extroversion?: number;
  openness?: number;
  spontaneity?: number;
  energy_level?: number;
}

export interface AuthContextType {
  user: User | null;
  is_onboarded: boolean | undefined;
  token: string | null;
  login: () => void;
  logout: () => Promise<void>;
  completeLogin: (user: User, token: string) => void;
  setUser: (user: User) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  // On mount, check if already logged in via session cookie
  useEffect(() => {
    axios
      .get<{ user: User; token: string }>("http://localhost:5001/auth/me", {
        withCredentials: true,
      })
      .then((res) => {
        setUser(res.data.user);
        console.log("user after update ", res.data.user);
        setToken(res.data.token);

        if (!res.data.user.is_onboarded) {
          navigate("/onboarding");
        }
      })
      .catch((error) => {
        // If we get a 401, clear the session and redirect to login
        if (error.response?.status === 401) {
          setUser(null);
          setToken(null);
          navigate("/login");
        } else {
          console.error("Error checking auth status:", error);
        }
      })
      .finally(() => setLoading(false));
  }, [navigate]);

  const login = () => {
    window.location.href =
      "http://localhost:5001/auth/google?redirect=http://localhost:5173/auth-callback";
  };

  const logout = async () => {
    try {
      await axios.post(
        "http://localhost:5001/auth/logout",
        {},
        {
          withCredentials: true,
        }
      );
      setUser(null);
      setToken(null);
      navigate("/");
    } catch (err) {
      console.error("Logout failed", err);
    }
  };

  /**
   * Called by CallbackPage after parsing the ?data= payload
   * from your Flask redirect.
   */
  const completeLogin = (loggedInUser: User, authToken: string) => {
    setUser(loggedInUser);
    setToken(authToken);
    // Optionally persist token in localStorage:
    // localStorage.setItem("token", authToken);
  };

  if (loading) {
    return <div>Loading authentication…</div>;
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        login,
        logout,
        completeLogin,
        setUser: setUser,
        is_onboarded: user?.is_onboarded,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export function useAuth(): AuthContextType {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
