import { FaTwitter, FaInstagram, FaFacebook } from "react-icons/fa";

export default () => (
  <footer className="bg-white border-t">
    <div className="container mx-auto px-6 py-4 flex flex-col md:flex-row justify-between items-center">
      <p className="text-gray-500 text-sm">
        © 2025 NightSpot. All rights reserved.
      </p>
      <div className="flex space-x-4 mt-2 md:mt-0 text-gray-500">
        <a href="#">
          <FaTwitter />
        </a>
        <a href="#">
          <FaInstagram />
        </a>
        <a href="#">
          <FaFacebook />
        </a>
      </div>
    </div>
  </footer>
);
