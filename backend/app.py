from flask import Flask, abort, request, redirect, session, jsonify
from flask_cors import CORS
import json
import urllib
from authlib.integrations.flask_client import OAuth
from pymongo import MongoClient
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import uuid
from google import genai
import itertools
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from icalendar import Calendar, Event as CalendarEvent
import pytz
from bson import ObjectId
from flask.json import JSONEncoder

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')
CORS(
    app,
    supports_credentials=True,
    resources={r"/*": {"origins": "*"}}
)


# MongoDB setup
client = MongoClient(os.getenv('MONGO_URL'))
db = client["NightSpot"]
dbs = client.NightSpot
collection = dbs["users"]

# OAuth setup
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid email profile',
                   'token_endpoint_auth_method': 'client_secret_post',
                   'token_placement': 'header'},
    jwks_uri='https://www.googleapis.com/oauth2/v3/certs'

)

# Add these environment variables at the top with other env vars
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')

class MongoJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

app.json_encoder = MongoJSONEncoder

@app.route('/auth/google')
def auth_google():
    """
    Endpoint to initiate Google OAuth flow
    """
    # Generate a state token to prevent CSRF
    state = str(uuid.uuid4())
    session['oauth_state'] = state

    # Get the redirect URL from the frontend
    redirect_url = request.args.get('redirect_url', os.getenv('FRONTEND_URL'))
    session['redirect_url'] = redirect_url

    # Redirect to Google OAuth
    redirect_uri = f"{request.url_root}auth-callback"
    return google.authorize_redirect(redirect_uri, state=state)


@app.route('/auth-callback')
def auth_callback():
    """
    Callback endpoint for Google OAuth
    """
    try:
        # Verify state token to prevent CSRF
        if request.args.get('state') != session.get('oauth_state'):
            return jsonify({'error': 'Invalid state parameter'}), 400

        # Get token from Google
        token = google.authorize_access_token()

        # Get user info from Google
        user_info = google.get('userinfo').json()
        # Check if user exists in database
        existing_user = db.users.find_one({'email': user_info['email']})

        if existing_user:
            # Update existing user data
            db.users.update_one(
                {'email': user_info['email']},
                {'$set': {
                    'last_login': datetime.utcnow(),
                    'name': user_info.get('name'),
                    'picture': user_info.get('picture')
                }}
            )
            user_id = str(existing_user['_id'])
            is_onboarded = existing_user.get('is_onboarded', False)
        else:
            # Create new user
            new_user = {
                'email': user_info['email'],
                'name': user_info.get('name'),
                'picture': user_info.get('picture'),
                'created_at': datetime.utcnow(),
                'last_login': datetime.utcnow(),
                'is_onboarded': False
            }
            result = db.users.insert_one(new_user)
            user_id = str(result.inserted_id)
            is_onboarded = False

        # Prepare user info for session
        user_session_data = {
            'id': user_id,
            'email': user_info['email'],
            'name': user_info.get('name'),
            'picture': user_info.get('picture'),
            'is_onboarded': is_onboarded
        }

        # Set session data
        session['user_info'] = user_session_data
        session['token'] = token['access_token']
        session.permanent = True  # Make the session permanent

        # Prepare response data
        response_data = {
            'token': token['access_token'],
            'user': user_session_data
        }

        # Serialize + URL‑encode
        raw = json.dumps(response_data, separators=(",", ":"))
        encoded = urllib.parse.quote(raw, safe="")

        # Redirect back to React
        frontend_url = session.get('redirect_url', os.getenv('FRONTEND_URL'))
        return redirect(f"{frontend_url}/auth-callback?data={encoded}")

    except Exception as e:
        print(f"Error in callback: {str(e)}")
        # Redirect to frontend with error
        frontend_url = session.get('redirect_url', os.getenv('FRONTEND_URL'))
        return redirect(f"{frontend_url}/auth-callback?error=Authentication failed")


@app.route('/api/user/profile')
def get_user_profile():
    """
    Protected endpoint to get user profile
    """
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'No token provided'}), 401

    try:
        # Verify token and get user info
        user_info = google.parse_id_token(token)
        user = db.users.find_one({'email': user_info['email']})

        if not user:   
            return jsonify({'error': 'User not found'}), 404

        return jsonify({
            'id': str(user['_id']),
            'email': user['email'],
            'name': user.get('name'),
            'picture': user.get('picture')
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 401


@app.route('/auth/me')
def auth_me():
    user_session = session.get('user_info')
    if not user_session:
        return jsonify({'error': 'Not authenticated'}), 401
        
    user = collection.find_one({"email": user_session['email']})
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    user["id"] = str(user.pop("_id"))
    token = session.get('token')
    if not token:
        return jsonify({'error': 'No token found'}), 401

    return jsonify({
        'user': user,
        'token': token
    })


@app.route('/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "Logged out"})
    return redirect('/')


@app.route('/users/<user_email>', methods=['PUT'])
def update_user(user_email):
    data = request.get_json()
    if not data:
        abort(400, description="No update data provided")

    try:
        # Extract features from questions
        questions = data.get('questions', [])
        total_extroversion = 0
        total_openness = 0
        total_spontaneity = 0
        total_energy_level = 0
        count = 0

        for question, answer in questions:
            if answer:  # Only process non-empty answers
                response = extract_features(question, answer)
                lines = response.strip().splitlines()
                feature_scores = {}
                for line in lines:
                    if ':' in line:
                        category, value = line.split(':', 1)
                        try:
                            feature_scores[category.strip()] = float(value.strip())
                        except ValueError:
                            feature_scores[category.strip()] = 0.0
                
                total_extroversion += feature_scores.get('extroversion', 0.0)
                total_openness += feature_scores.get('openness', 0.0)
                total_spontaneity += feature_scores.get('spontaneity', 0.0)
                total_energy_level += feature_scores.get('energy_level', 0.0)
                count += 1

        # Compute average scores if at least one question was answered
        if count > 0:
            avg_extroversion = total_extroversion / count
            avg_openness = total_openness / count
            avg_spontaneity = total_spontaneity / count
            avg_energy_level = total_energy_level / count
        else:
            avg_extroversion = avg_openness = avg_spontaneity = avg_energy_level = 0.0

        # Update user data
        update_data = {
            "age": data.get('age'),
            "gender": data.get('gender'),
            "race": data.get('race'),
            "hometown": data.get('hometown'),
            "extroversion": avg_extroversion,
            "openness": avg_openness,
            "spontaneity": avg_spontaneity,
            "energy_level": avg_energy_level,
            "is_onboarded": True
        }

        result = collection.update_one(
            {"email": user_email}, 
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            abort(404, description="User not found")

        updated_user = collection.find_one({"email": user_email})
        if not updated_user:
            abort(500, description="Error fetching updated user")

        updated_user["id"] = str(updated_user.pop("_id"))
        return jsonify({"data": updated_user}), 200

    except Exception as e:
        print("Error updating user:", e)
        abort(500, description="User update failed")


@app.get('/users/<user_email>')
def get_user(user_email):
    user = collection.find_one({"email": user_email})
    if not user:
        abort(404, description="User not found")
    user["id"] = str(user.pop("_id"))
    return jsonify({"data": user}), 200

# MongoDB connection details
MONGO_URL = os.getenv("MONGO_URL")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = MongoClient(MONGO_URL)
db = client['NightSpot']
waiting_users_collection = db['waiting_users']
events_collection = db['events']
locations_collection = db['locations']  # Add locations collection


def serialize_doc(doc):
    """
    Convert MongoDB ObjectId in a document to string.
    """
    if doc is None:
        return None
    # Convert the Mongo-generated _id field if it exists.
    if '_id' in doc:
        doc['_id'] = str(doc['_id'])
    return doc

def serialize_docs(docs):
    """
    Serialize a list of documents.
    """
    return [serialize_doc(doc) for doc in docs]


def extract_features(question, answer):
    client = genai.Client(api_key = GEMINI_API_KEY)
    
    prompt_text = f"""You are a specialist in the human psyche and you can determine someone personality from short responses.
    The way you evaluate the change is writing a report scoring from 0 to 5 the response in four categories: extroversion, openness, spontaneity and energy_level.
    0 means the absolute lowest level of the category possible. A 0 extroversion person absolutely despises being with other people.
    5 means the absolute peak of the category. A 5 openness person would be open to essentially anything.
    Don't be afraid of giving scores that end with values other than .5 and .0
    You should only output the name of the category, a colon, a space, and the score. 

    The formatting of the response should be the following (example with dummy values):
    extroversion: 2.2
    openness: 4.6
    spontaneity: 0.0
    energy_level: 5.0

    A client of yours was tasked to respond to the following question:
    {question}

    And they gave the following answer:
    {answer}

    Give your response in the specified format. 
    """

    return client.models.generate_content(
    model="gemini-2.0-flash", contents=prompt_text
    ).text

def fetch_waiting_users_by_meeting_time(meeting_time):
    """
    Fetch all waiting users for a given meeting time.
    """
    users = list(waiting_users_collection.find({"meeting_time": meeting_time}))
    return users

def is_similar_group(group, threshold=2.5):
    """
    Check if a group of users is similar based on the features:
    dummy1, dummy2, dummy3, dummy4.
    
    A group is considered similar if for each dummy feature, the difference 
    between the maximum and minimum values does not exceed the threshold.
    """
    features = ["dummy1", "dummy2", "dummy3", "dummy4"]
    for feature in features:
        values = [user.get(feature, 0) for user in group]
        if max(values) - min(values) > threshold:
            return False
    return True

def find_eligible_group(users, group_size=5, threshold=1.0):
    """
    Find any group of `group_size` users (from a given meeting time queue) 
    that are similar enough based on the dummy features.
    
    This function uses itertools.combinations to try every group of 5 users.
    """
    for group in itertools.combinations(users, group_size):
        if is_similar_group(group, threshold):
            return list(group)
    return None

def get_random_location():
    """Get a random location from the locations collection"""
    try:
        # Use MongoDB's aggregation pipeline to get a random document
        pipeline = [{"$sample": {"size": 1}}]
        location = list(locations_collection.aggregate(pipeline))
        if location:
            return location[0]
        return {"name": "Evanston", "address": "1501 Maple Ave, Evanston, IL 60201"}  # Default fallback
    except Exception as e:
        print(f"Error getting random location: {str(e)}")
        return {"name": "Evanston", "address": "1501 Maple Ave, Evanston, IL 60201"}  # Default fallback

def create_calendar_invite(meeting_time, group_members, location):
    """Create a calendar invite for the event"""
    cal = Calendar()
    cal.add('prodid', '-//NightSpot Event//nightspot.com//')
    cal.add('version', '2.0')
    
    event = CalendarEvent()
    event.add('summary', 'NightSpot Group Meetup')
    
    # Convert meeting_time string to datetime
    start_time = datetime.strptime(meeting_time, "%Y-%m-%d %H:%M")
    end_time = start_time + timedelta(hours=2)  # Default 2-hour event
    
    # Add timezone information
    tz = pytz.timezone('America/Chicago')
    start_time = tz.localize(start_time)
    end_time = tz.localize(end_time)
    
    event.add('dtstart', start_time)
    event.add('dtend', end_time)
    
    # Add description with group members and location
    description = "Your NightSpot group meetup!\n\nLocation:\n"
    description += f"{location['name']}\n{location['address']}\n\nGroup Members:\n"
    for member in group_members:
        description += f"- {member['name']}\n"
    event.add('description', description)
    
    # Add location
    event.add('location', f"{location['name']} - {location['address']}")
    
    cal.add_component(event)
    return cal.to_ical()

def send_group_emails(group, meeting_time, event_id):
    """Send emails to all group members with calendar invite"""
    try:
        # Get a random location for the meetup
        location = get_random_location()
        
        # Create calendar invite with location
        calendar_invite = create_calendar_invite(meeting_time, group, location)
        
        # Connect to SMTP server
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        
        for user in group:
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = SMTP_USERNAME
            msg['To'] = user['email']
            msg['Subject'] = 'Your NightSpot Group has been Matched!'
            
            # Email body
            body = f"""Hi {user['name']},

Great news! We've found your perfect group for a night out!

Meeting Location:
{location['name']}
{location['address']}

Your group is scheduled to meet at {meeting_time}.

Your group members are:
"""
            for member in group:
                if member['email'] != user['email']:
                    body += f"- {member['name']}\n"
            
            body += "\nWe've attached a calendar invite for your convenience. Looking forward to your amazing night out!"
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach calendar invite
            cal_attachment = MIMEApplication(calendar_invite, _subtype='ics')
            cal_attachment.add_header('Content-Disposition', 'attachment', filename='nightspot_event.ics')
            msg.attach(cal_attachment)
            
            # Send email
            server.send_message(msg)
        
        server.quit()
        return True, location
    except Exception as e:
        print(f"Error sending emails: {str(e)}")
        return False, None

@app.route('/join', methods=['POST'])
def join_queue():
    """
    Endpoint for a user to join the event planning queue.
    """
    data = request.json
    name = data.get('name')
    email = data.get('email')
    meeting_time = data.get('meeting_time')
    extroversion = data.get('extroversion')
    openness = data.get('openness')
    spontaneity = data.get('spontaneity')
    energy_level = data.get('energy_level')
    
    # Validate required fields
    if None in [name, email, meeting_time, extroversion, openness, spontaneity, energy_level]:
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        # Create a new user record
        new_user = {
            "id": str(uuid.uuid4()),
            "name": name,
            "email": email,
            "meeting_time": meeting_time,
            "extroversion": float(extroversion),
            "openness": float(openness),
            "spontaneity": float(spontaneity),
            "energy_level": float(energy_level)
        }
        waiting_users_collection.insert_one(new_user)
        
        # Fetch only the waiting users for this meeting time
        users_for_time = fetch_waiting_users_by_meeting_time(meeting_time)
        
        # Try to find an eligible group of 5 similar users in the same meeting time queue
        eligible_group = find_eligible_group(users_for_time)
        
        if eligible_group:
            # Remove the eligible users from the waiting collection
            eligible_ids = [user['id'] for user in eligible_group]
            waiting_users_collection.delete_many({"id": {"$in": eligible_ids}})
            
            # Send emails to all group members and get the location
            email_sent, location = send_group_emails(eligible_group, meeting_time, str(uuid.uuid4()))
            
            # Create and store an event document
            event_doc = {
                "event_id": str(uuid.uuid4()),
                "users": eligible_group,
                "meeting_time": meeting_time,
                "location": location
            }
            events_collection.insert_one(event_doc)
            
            return jsonify({
                "event": event_doc, 
                "detail": "Event created with similar users for the specified meeting time!",
                "emails_sent": email_sent
            })
        else:
            return jsonify({"event": None, "detail": "Added to queue for meeting time, waiting for more users."})
            
    except Exception as e:
        print(f"Error in join_queue: {str(e)}")
        return jsonify({"error": "Failed to process request"}), 500

@app.route('/queue', methods=['GET'])
def get_queue():
    """
    Returns the list of all waiting users across meeting times.
    """
    users = list(waiting_users_collection.find())
    users = serialize_docs(users)
    return jsonify(users)

@app.route('/queue', methods=['DELETE'])
def clear_queue():
    """
    Clears all users from the waiting queue. Useful for testing or administrative purposes.
    """
    waiting_users_collection.delete_many({})
    return jsonify({"detail": "Queue cleared."})

@app.route('/get_features', methods=['POST'])
def get_features():
    data = request.json
    questions = data['questions']
    total_extroversion = 0
    total_openness = 0
    total_spontaneity = 0
    total_energy_level = 0

    count = 0

    for question, answer in questions:
        response = extract_features(question, answer)
        lines = response.strip().splitlines()
        feature_scores = {}
        for line in lines:
            if ':' in line:
                category, value = line.split(':', 1)
                try:
                    feature_scores[category.strip()] = float(value.strip())
                except ValueError:
                    feature_scores[category.strip()] = 0.0
        
        total_extroversion += feature_scores.get('extroversion', 0.0)
        total_openness += feature_scores.get('openness', 0.0)
        total_spontaneity += feature_scores.get('spontaneity', 0.0)
        total_energy_level += feature_scores.get('energy_level', 0.0)
        count += 1

    # Compute average scores if at least one question was provided
    if count > 0:
        avg_extroversion = total_extroversion / count
        avg_openness = total_openness / count
        avg_spontaneity = total_spontaneity / count
        avg_energy_level = total_energy_level / count
    else:
        avg_extroversion = avg_openness = avg_spontaneity = avg_energy_level = 0.0

    return jsonify({
        "extroversion": avg_extroversion,
        "openness": avg_openness,
        "spontaneity": avg_spontaneity,
        "energy_level": avg_energy_level
    })
    

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    app.run(debug=True, host='0.0.0.0', port=port)
