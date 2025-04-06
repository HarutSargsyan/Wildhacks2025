// src/components/PersonalInfoForm.tsx
import React, { useState, ChangeEvent, FormEvent, useEffect } from "react";
import { FaEdit, FaSave } from "react-icons/fa";
import { useAuth } from "../context/AuthProvider";
import axios from "../axi/axios";
import { useNavigate } from "react-router";

type Gender = "Male" | "Female" | "Non‑binary" | "Other" | "";
type Race =
  | "Asian"
  | "Black"
  | "Hispanic"
  | "White"
  | "Native American"
  | "Other"
  | "";

interface PersonalInfo {
  age: string;
  gender: Gender;
  race: Race;
  hometown: string;
  questions: [string, string][]; // Array of [question, answer] pairs
}

const genderOptions: Gender[] = ["", "Male", "Female", "Non‑binary", "Other"];
const raceOptions: Race[] = [
  "",
  "Asian",
  "Black",
  "Hispanic",
  "White",
  "Native American",
  "Other",
];

const PersonalInfo = () => {
  const [formState, setFormState] = useState<PersonalInfo>({
    age: "",
    gender: "",
    race: "",
    hometown: "",
    questions: [
      ['What are your hobbies?', ''],
      ['What is your ideal hangout?', ''],
      ['How do you feel about last minute plans?', '']
    ]
  });
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { setUser, user } = useAuth();

  useEffect(() => {
    console.log("user ", user?.is_onboarded);
  }, [user]);

  const navigate = useNavigate();

  const handleChange = (key: keyof PersonalInfo) => (e: ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    if (key === 'questions') {
      const index = parseInt(e.target.name);
      const value = e.target.value;
      setFormState(prev => ({
        ...prev,
        questions: prev.questions.map((q, i) => i === index ? [q[0], value] : q)
      }));
    } else {
      setFormState(prev => ({ ...prev, [key]: e.target.value }));
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      if (!user?.email) {
        throw new Error('No authenticated user found');
      }

      const response = await fetch(`http://localhost:5001/users/${user.email}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formState),
        credentials: 'include'
      });

      if (!response.ok) {
        throw new Error('Failed to update profile');
      }

      const data = await response.json();
      console.log('Profile updated:', data);
      setUser(data.data);
      navigate("/");
      setIsEditing(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-start justify-center p-6">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-md bg-white rounded-xl shadow p-8 space-y-6"
      >
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">Personal Information</h2>
          <img
            src={user?.picture}
            alt="User avatar"
            className="w-10 h-10 rounded-full"
          />
        </div>

        {/* Age */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Age
          </label>
          <input
            type="number"
            value={formState.age}
            onChange={handleChange("age")}
            disabled={!isEditing}
            className={`w-full border rounded px-3 py-2 focus:outline-none focus:ring ${
              isEditing
                ? "focus:border-blue-500"
                : "bg-gray-100 cursor-not-allowed"
            }`}
            placeholder="Enter your age"
          />
        </div>

        {/* Gender */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Gender
          </label>
          <select
            value={formState.gender}
            onChange={handleChange("gender")}
            disabled={!isEditing}
            className={`w-full border rounded px-3 py-2 focus:outline-none focus:ring ${
              isEditing
                ? "focus:border-blue-500"
                : "bg-gray-100 cursor-not-allowed"
            }`}
          >
            {genderOptions.map((g) => (
              <option key={g} value={g}>
                {g === "" ? "Select gender" : g}
              </option>
            ))}
          </select>
        </div>

        {/* Race
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Race
          </label>
          <select
            value={formState.race}
            onChange={handleChange("race")}
            disabled={!isEditing}
            className={`w-full border rounded px-3 py-2 focus:outline-none focus:ring ${
              isEditing
                ? "focus:border-blue-500"
                : "bg-gray-100 cursor-not-allowed"
            }`}
          >
            {raceOptions.map((r) => (
              <option key={r} value={r}>
                {r === "" ? "Select race" : r}
              </option>
            ))}
          </select>
        </div> */}

        {/* Hometown */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Hometown
          </label>
          <input
            type="text"
            value={formState.hometown}
            onChange={handleChange("hometown")}
            disabled={!isEditing}
            className={`w-full border rounded px-3 py-2 focus:outline-none focus:ring ${
              isEditing
                ? "focus:border-blue-500"
                : "bg-gray-100 cursor-not-allowed"
            }`}
            placeholder="Enter your hometown"
          />
        </div>

        {/* Questions */}
        <div className="space-y-4">
          {formState.questions.map(([question, answer], index) => (
            <div key={index} className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">
                {question}
              </label>
              <textarea
                name={index.toString()}
                value={answer}
                onChange={handleChange("questions")}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                rows={4}
                disabled={!isEditing}
                placeholder={`Enter your answer for: ${question}`}
              />
            </div>
          ))}
        </div>

        <div className="flex justify-end space-x-4">
          {!isEditing ? (
            <button
              type="button"
              onClick={() => setIsEditing(true)}
              className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Edit
            </button>
          ) : (
            <>
              <button
                type="button"
                onClick={() => setIsEditing(false)}
                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isLoading}
                className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
              >
                {isLoading ? 'Saving...' : 'Save Changes'}
              </button>
            </>
          )}
        </div>
      </form>
    </div>
  );
};

export default PersonalInfo;
