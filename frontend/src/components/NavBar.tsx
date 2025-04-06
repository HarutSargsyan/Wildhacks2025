// src/components/Navbar.tsx
import React from "react";
import { Link, useNavigate } from "react-router";
import { useAuth } from "../context/AuthProvider";
import { FaUserCircle } from "react-icons/fa";

const Navbar: React.FC = () => {
  const { user, login, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await logout();
      navigate("/login", { replace: true });
    } catch (err) {
      console.error("Logout failed", err);
    }
  };

  return (
    <nav className="bg-white shadow">
      <div className="container mx-auto px-6 py-4 flex justify-between items-center">
        <Link to="/" className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-black rounded-full" />
          <span className="font-bold text-xl">NightSpot</span>
        </Link>

        <div className="flex items-center space-x-4">
          {user ? (
            <>
              <div className="flex items-center space-x-2">
                <FaUserCircle className="text-2xl text-gray-600" />
                <span className="text-gray-700">{user?.name}</span>
              </div>

              <button
                onClick={handleLogout}
                className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 transition"
              >
                Logout
              </button>
            </>
          ) : (
            <button
              onClick={login}
              className="px-4 py-2 bg-black text-white rounded hover:bg-gray-900 transition"
            >
              Sign In
            </button>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
