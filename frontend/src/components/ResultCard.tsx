import { FaStar, FaMapMarkerAlt } from "react-icons/fa";

export default () => (
  <div className="bg-white rounded-xl shadow p-6 max-w-2xl mx-auto mt-12 flex space-x-6">
    <div className="w-32 h-32 bg-gray-200 rounded" />
    <div className="flex-1">
      <h2 className="text-xl font-semibold">The Urban Lounge</h2>
      <div className="flex items-center space-x-2 text-yellow-500 mt-1">
        <FaStar />
        <span className="text-gray-700 font-medium">4.8</span>
        <span className="text-gray-500">(234 reviews)</span>
      </div>
      <p className="text-gray-600 mt-2">
        Contemporary lounge with live jazz, craft cocktails, and outdoor
        seating.
      </p>
      <div className="flex items-center space-x-4 text-gray-500 mt-3">
        <span>$$</span>
        <span className="flex items-center space-x-1">
          <FaMapMarkerAlt /> <span>2.3 miles away</span>
        </span>
      </div>
      <button className="mt-4 px-4 py-2 bg-black text-white rounded hover:bg-gray-900">
        Book Now
      </button>
    </div>
  </div>
);
