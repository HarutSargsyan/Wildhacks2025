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
} from "react-icons/fa";

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
  { label: "Party" as FormState["mood"], icon: <FaCocktail /> },
  { label: "Dining" as FormState["mood"], icon: <FaUtensils /> },
  { label: "Live Music" as FormState["mood"], icon: <FaMusic /> },
  { label: "Chill" as FormState["mood"], icon: <FaCoffee /> },
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

export default () => {
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

  return (
    <div className="max-w-lg mx-auto p-6 bg-white rounded-xl shadow space-y-6">
      {/* Mood */}
      <div>
        <p className="mb-2 font-medium text-gray-700">What’s your mood?</p>
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

      {/* Submit Button */}
      <button
        type="button"
        onClick={() => console.log(formState)}
        className="w-full py-3 bg-black text-white rounded hover:bg-gray-900 transition"
      >
        Find My Spot
      </button>

      {/* Debug: show current state */}
      <pre className="mt-4 p-2 bg-gray-100 rounded text-sm">
        {JSON.stringify(formState, null, 2)}
      </pre>
    </div>
  );
};
