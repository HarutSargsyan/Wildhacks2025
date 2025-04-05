// src/pages/LoginPage.tsx
import { useAuth } from "../context/AuthProvider";
import { FaGoogle } from "react-icons/fa";

export default () => {
  const { login } = useAuth();

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <button
        onClick={login}
        className="flex items-center px-6 py-3 bg-white border rounded shadow hover:bg-gray-100"
      >
        <FaGoogle className="mr-2 text-red-500" />
        Sign in with Google
      </button>
    </div>
  );
};
