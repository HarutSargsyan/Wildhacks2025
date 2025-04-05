// src/context/AuthContext.tsx
import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import axios from "axios";

export interface User {
  sub: string; // Auth0 user ID
  name: string;
  email: string;
  picture?: string;
  // …any other metadata
}

export interface AuthContextType {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
  login: () => void;
  logout: () => void;
}

// Create context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Provider
export const AuthProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  // On mount, fetch session
  useEffect(() => {
    axios
      .get<{ user: User; token: string }>("/auth/me", { withCredentials: true })
      .then((res) => {
        setUser(res.data.user);
        setToken(res.data.token);
      })
      .catch(() => {
        setUser(null);
        setToken(null);
      })
      .finally(() => setLoading(false));
  }, []);

  const login = () => {
    // Redirect browser to backend OAuth start
    window.location.href = "/auth/google";
  };

  const logout = () => {
    axios
      .post("/auth/logout", {}, { withCredentials: true })
      .then(() => {
        setUser(null);
        setToken(null);
      })
      .catch(console.error);
  };

  // While we’re loading session, don’t render children
  if (loading) {
    return <div>Loading authentication…</div>;
  }

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated: !!user,
        user,
        token,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook
export function useAuth(): AuthContextType {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
}
