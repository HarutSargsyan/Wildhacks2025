import React from "react";
import { useLocation, useNavigate } from "react-router";
import { FaMapMarkerAlt, FaClock, FaUsers } from "react-icons/fa";

interface MatchState {
  event: {
    event_id: string;
    users: Array<{
      id: string;
      name: string;
    }>;
    meeting_time: string;
    location: {
      name: string;
      address: string;
      type: string;
      description: string;
    };
  };
}

export default () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { event } = location.state as MatchState;

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full p-8 bg-white rounded-xl shadow-lg">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-2">🎉 Match Found! 🎉</h1>
          <p className="text-gray-600">You've been matched with an awesome group!</p>
        </div>

        <div className="space-y-6">
          {/* Location */}
          <div className="flex items-start space-x-3 p-4 bg-gray-50 rounded-lg">
            <FaMapMarkerAlt className="text-2xl text-black mt-1" />
            <div>
              <h3 className="font-medium">{event.location.name}</h3>
              <p className="text-gray-600">{event.location.address}</p>
              <p className="text-sm text-gray-500 mt-1">{event.location.description}</p>
            </div>
          </div>

          {/* Time */}
          <div className="flex items-center space-x-3 p-4 bg-gray-50 rounded-lg">
            <FaClock className="text-2xl text-black" />
            <div>
              <h3 className="font-medium">Meeting Time</h3>
              <p className="text-gray-600">
                {new Date(event.meeting_time).toLocaleString()}
              </p>
            </div>
          </div>

          {/* Group Members */}
          <div className="p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center space-x-3 mb-3">
              <FaUsers className="text-2xl text-black" />
              <h3 className="font-medium">Your Group</h3>
            </div>
            <ul className="space-y-2">
              {event.users.map((user) => (
                <li
                  key={user.id}
                  className="flex items-center space-x-3 p-2 bg-white rounded"
                >
                  <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">
                    {user.name.charAt(0)}
                  </div>
                  <span>{user.name}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Action Buttons */}
          <div className="flex space-x-4 mt-6">
            <button
              onClick={() => navigate("/")}
              className="flex-1 py-3 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition"
            >
              Back to Home
            </button>
            <button
              onClick={() => {
                // Here you could add functionality to share the event details
                window.alert("Sharing functionality coming soon!");
              }}
              className="flex-1 py-3 bg-black text-white rounded hover:bg-gray-900 transition"
            >
              Share with Group
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}; 