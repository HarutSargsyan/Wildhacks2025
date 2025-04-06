import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import { FaSpinner } from "react-icons/fa";
import axios from "axios";

interface QueueStatus {
  status: "waiting" | "matched";
  event?: {
    event_id: string;
    users: Array<{
      id: string;
      name: string;
    }>;
    meeting_time: string;
  };
}

export default () => {
  const navigate = useNavigate();
  const [status, setStatus] = useState<QueueStatus>({ status: "waiting" });
  const [location, setLocation] = useState<string>("");

  // List of possible locations (for now, randomly selected)
  const locations = [
    "The Violet Hour",
    "Three Dots and a Dash",
    "The Aviary",
    "Lost Lake",
    "The Whistler",
    "Scofflaw",
    "The Office",
    "The Drifter",
    "The Berkshire Room",
    "The Broken Shaker"
  ];

  useEffect(() => {
    // Start polling for updates
    const pollInterval = setInterval(async () => {
      try {
        const response = await axios.get("http://localhost:5001/queue");
        const userInEvent = response.data.find((user: any) => user.event_id);
        
        if (userInEvent) {
          setStatus({
            status: "matched",
            event: {
              event_id: userInEvent.event_id,
              users: userInEvent.users,
              meeting_time: userInEvent.meeting_time
            }
          });
          // Select a random location
          setLocation(locations[Math.floor(Math.random() * locations.length)]);
          clearInterval(pollInterval);
          // Wait a moment before redirecting to show the match
          setTimeout(() => {
            navigate("/match", {
              state: {
                event: userInEvent,
                location
              }
            });
          }, 2000);
        }
      } catch (error) {
        console.error("Error polling queue:", error);
      }
    }, 5000); // Poll every 5 seconds

    return () => clearInterval(pollInterval);
  }, [navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full p-8 bg-white rounded-xl shadow-lg text-center">
        <div className="mb-8">
          <FaSpinner className="w-16 h-16 mx-auto animate-spin text-black" />
        </div>
        <h1 className="text-2xl font-bold mb-4">Finding Your Perfect Group</h1>
        <p className="text-gray-600 mb-6">
          We're matching you with people who share your interests and preferences.
          This might take a few minutes...
        </p>
        <div className="space-y-4">
          <div className="flex items-center justify-center space-x-2">
            <div className="w-3 h-3 bg-black rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
            <div className="w-3 h-3 bg-black rounded-full animate-bounce" style={{ animationDelay: "200ms" }} />
            <div className="w-3 h-3 bg-black rounded-full animate-bounce" style={{ animationDelay: "400ms" }} />
          </div>
          {status.status === "matched" && (
            <div className="mt-4 p-4 bg-green-100 text-green-700 rounded-lg">
              <p>Match found! Redirecting you to your group...</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}; 