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
  who: string;
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

export default () => {
  const [formState, setFormState] = useState<PersonalInfo>({
    age: "",
    gender: "",
    race: "",
    hometown: "",
    who: "",
  });

  const [isEditing, setIsEditing] = useState(false);

  const { setUser, user } = useAuth();

  useEffect(() => {
    console.log("user ", user?.is_onboarded);
  }, [user]);

  const navigate = useNavigate();
  const handleChange =
    (key: keyof PersonalInfo) =>
    (
      e: ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
    ) => {
      setFormState((prev) => ({ ...prev, [key]: e.target.value }));
    };

  const handleEditToggle = () => setIsEditing((prev) => !prev);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    const res = await axios.put(
      `http://localhost:5001/users/${user?.email}`,
      formState
    );
    if (res.status === 200) {
      console.log("res", res);
      setUser(res.data.data);
      navigate("/");
    } else {
      console.error("Failed to update personal info");
    }
    setIsEditing(false);
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

        {/* Race */}
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
        </div>

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
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            How do you feel about last minute plans?
          </label>
          <textarea
            value={formState.who}
            onChange={handleChange("who")}
            disabled={!isEditing}
            className={`w-full border rounded px-3 py-2 focus:outline-none focus:ring ${
              isEditing
                ? "focus:border-blue-500"
                : "bg-gray-100 cursor-not-allowed"
            }`}
            placeholder="Enter Field 3"
            rows={3}
          />
        </div>
        {/* Actions */}
        <div className="flex justify-end space-x-3">
          <button
            type="button"
            onClick={handleEditToggle}
            className="flex items-center px-4 py-2 border rounded hover:bg-gray-100 transition"
          >
            <FaEdit className="mr-2" /> {isEditing ? "Cancel" : "Edit"}
          </button>
          {isEditing && (
            <button
              type="submit"
              onClick={handleSubmit}
              className="flex items-center px-4 py-2 bg-black text-white rounded hover:bg-gray-900 transition"
            >
              <FaSave className="mr-2" /> Save Changes
            </button>
          )}
        </div>
      </form>
    </div>
  );
};
