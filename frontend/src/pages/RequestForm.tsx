// SearchForm.tsx
import React, { useState, ChangeEvent, ReactElement } from "react";
import {
  FaCocktail,
  FaUtensils,
  FaMusic,
  FaCoffee,
  FaMapMarkerAlt,
  FaUtensils as FaFood,
  FaMusic as FaLive,
  FaTree,
  FaPaw,
  FaClock,
} from "react-icons/fa";
import { useAuth } from "../context/AuthProvider";
import { useNavigate } from "react-router-dom";

interface Preferences {
  liveMusic: boolean;
  foodAvailable: boolean;
  outdoorSeating: boolean;
  petFriendly: boolean;
}

interface FormState {
  mood: "Party" | "Dining" | "Live Music" | "Chill" | "";
  budget: number;
  location: string;
  preferences: Preferences;
}

const moodOptions = [
  { label: "Party" as const, icon: <FaCocktail /> },
  { label: "Dining" as const, icon: <FaUtensils /> },
  { label: "Live Music" as const, icon: <FaMusic /> },
  { label: "Chill" as const, icon: <FaCoffee /> },
];

const preferenceOptions: {
  key: keyof Preferences;
  label: string;
  icon: ReactElement;
}[] = [
  { key: "liveMusic", label: "Live Music", icon: <FaLive /> },
  { key: "foodAvailable", label: "Food Available", icon: <FaFood /> },
  { key: "outdoorSeating", label: "Outdoor Seating", icon: <FaTree /> },
  { key: "petFriendly", label: "Pet Friendly", icon: <FaPaw /> },
];

const RequestForm = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [selectedTime, setSelectedTime] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formState, setFormState] = useState<FormState>({
    mood: "",
    budget: 3,
    location: "",
    preferences: {
      liveMusic: false,
      foodAvailable: false,
      outdoorSeating: false,
      petFriendly: false,
    },
  });

  const handleMoodSelect = (mood: FormState["mood"]) => {
    setFormState((prev) => ({ ...prev, mood }));
  };

  const handleBudgetChange = (e: ChangeEvent<HTMLInputElement>) => {
    setFormState((prev) => ({ ...prev, budget: Number(e.target.value) }));
  };

  const handleLocationChange = (e: ChangeEvent<HTMLInputElement>) => {
    setFormState((prev) => ({ ...prev, location: e.target.value }));
  };

  const handlePrefToggle = (key: keyof Preferences) => {
    setFormState((prev) => ({
      ...prev,
      preferences: {
        ...prev.preferences,
        [key]: !prev.preferences[key],
      },
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    if (!user) {
      setError('You must be logged in to join the queue');
      setIsLoading(false);
      return;
    }

    if (!selectedTime) {
      setError('Please select a meeting time');
      setIsLoading(false);
      return;
    }

    try {
      // Format the datetime string from YYYY-MM-DDThh:mm to YYYY-MM-DD HH:MM
      const formattedTime = selectedTime.replace('T', ' ');

      const response = await fetch('http://localhost:5001/join', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          name: user.name,
          email: user.email,
          meeting_time: formattedTime,
          extroversion: user.extroversion || 0,
          openness: user.openness || 0,
          spontaneity: user.spontaneity || 0,
          energy_level: user.energy_level || 0
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to join queue');
      }

      // If we got an event back, we were matched immediately
      if (data.event) {
        navigate('/match', { state: { event: data.event } });
      } else {
        // Otherwise we're waiting for a match
        navigate('/waiting', { state: { meeting_time: formattedTime } });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="m-10 max-w-lg mx-auto p-6 bg-white rounded-xl shadow space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Find Your Group</h2>
        <img
          src={user?.picture}
          alt="User avatar"
          className="w-10 h-10 rounded-full"
        />
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Mood */}
        <div>
          <p className="mb-2 font-medium text-gray-700">What's your mood?</p>
          <div className="grid grid-cols-2 gap-4">
            {moodOptions.map(({ label, icon }) => {
              const selected = formState.mood === label;
              return (
                <button
                  key={label}
                  type="button"
                  onClick={() => handleMoodSelect(label)}
                  className={`
                    flex flex-col items-center justify-center py-6 border rounded-lg transition
                    ${
                      selected
                        ? "bg-black text-white border-black"
                        : "bg-white text-gray-700 hover:bg-gray-100"
                    }
                  `}
                >
                  <span className="text-2xl mb-2">{icon}</span>
                  <span>{label}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Time Selector */}
        <div>
          <p className="mb-2 font-medium text-gray-700">Meeting Time</p>
          <div className="relative">
            <FaClock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="datetime-local"
              value={selectedTime}
              onChange={(e) => setSelectedTime(e.target.value)}
              className="w-full border rounded pl-10 pr-4 py-2 focus:outline-none focus:ring"
              min={new Date().toISOString().slice(0, 16)}
              required
            />
          </div>
        </div>

        {/* Budget */}
        <div>
          <p className="mb-2 font-medium text-gray-700">Budget Range</p>
          <div className="flex items-center space-x-4">
            <span className="text-gray-500">$</span>
            <input
              type="range"
              min={1}
              max={5}
              value={formState.budget}
              onChange={handleBudgetChange}
              className="flex-1"
            />
            <span className="text-gray-500">{"$".repeat(formState.budget)}</span>
          </div>
        </div>

        {/* Location */}
        <div>
          <p className="mb-2 font-medium text-gray-700">Preferred Location</p>
          <div className="relative">
            <FaMapMarkerAlt className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              value={formState.location}
              onChange={handleLocationChange}
              placeholder="Enter your location"
              className="w-full border rounded pl-10 pr-4 py-2 focus:outline-none focus:ring"
            />
          </div>
        </div>

        {/* Preferences */}
        <div>
          <p className="mb-2 font-medium text-gray-700">Additional Preferences</p>
          <div className="grid grid-cols-2 gap-4">
            {preferenceOptions.map(({ key, label, icon }) => (
              <label
                key={key}
                className="flex items-center space-x-2 cursor-pointer select-none"
              >
                <input
                  type="checkbox"
                  checked={formState.preferences[key]}
                  onChange={() => handlePrefToggle(key)}
                  className="form-checkbox h-5 w-5 text-black"
                />
                <span className="flex items-center space-x-1 text-gray-700">
                  {icon}
                  <span>{label}</span>
                </span>
              </label>
            ))}
          </div>
        </div>

        {error && (
          <div className="p-4 rounded bg-red-100 text-red-700">
            {error}
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isLoading || !selectedTime}
          className={`w-full py-3 rounded transition ${
            isLoading || !selectedTime
              ? "bg-gray-400 cursor-not-allowed"
              : "bg-black text-white hover:bg-gray-900"
          }`}
        >
          {isLoading ? "Finding Group..." : "Find My Group"}
        </button>
      </form>
    </div>
  );
};

export default RequestForm;
