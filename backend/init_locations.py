from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Connect to MongoDB
client = MongoClient(os.getenv('MONGO_URL'))
db = client.NightSpot  # Changed to match the database name in app.py
locations_collection = db.locations

# Sample locations in Evanston
locations = [
    {
        "name": "The Barn Steakhouse",
        "address": "1016 Church St, Evanston, IL 60201",
        "type": "restaurant",
        "description": "Upscale steakhouse in a converted barn"
    },
    {
        "name": "Bat 17",
        "address": "1709 Benson Ave, Evanston, IL 60201",
        "type": "restaurant",
        "description": "Popular sandwich spot and sports bar"
    },
    {
        "name": "World of Beer",
        "address": "1601 Sherman Ave, Evanston, IL 60201",
        "type": "bar",
        "description": "Casual bar with extensive beer selection"
    },
    {
        "name": "Celtic Knot Public House",
        "address": "626 Church St, Evanston, IL 60201",
        "type": "pub",
        "description": "Traditional Irish pub with live music"
    },
    {
        "name": "La Principal",
        "address": "700 Main St, Evanston, IL 60202",
        "type": "restaurant",
        "description": "Mexican restaurant and bar"
    },
    {
        "name": "Found Kitchen & Social House",
        "address": "1631 Chicago Ave, Evanston, IL 60201",
        "type": "restaurant",
        "description": "Farm-to-table American cuisine"
    },
    {
        "name": "Prairie Moon",
        "address": "1635 Chicago Ave, Evanston, IL 60201",
        "type": "restaurant",
        "description": "American restaurant and bar"
    },
    {
        "name": "Tapville Social",
        "address": "810 Grove St, Evanston, IL 60201",
        "type": "bar",
        "description": "Self-pour tap wall and social house"
    }
]

# Clear existing locations
locations_collection.delete_many({})

# Insert new locations
locations_collection.insert_many(locations)

print(f"Added {len(locations)} locations to the database") 