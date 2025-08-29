#!/usr/bin/env python3
import requests
import json
import sys
import os
import argparse
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

def authenticate(email, password):
    """
    Authenticate with Google Identity Toolkit and get an ID token
    
    Args:
        email: User email
        password: User password
        
    Returns:
        dict: Authentication response with idToken
    """
    url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
    api_key = "AIzaSyBOfBEli4wu5Ly7ts1JLCG8lF1JUvtbPo8"
    
    payload = {
        "returnSecureToken": True,
        "email": email,
        "password": password,
        "clientType": "CLIENT_TYPE_WEB"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(f"{url}?key={api_key}", json=payload, headers=headers)
        response.raise_for_status()
        
        auth_data = response.json()
        print(f"✓ Successfully authenticated as {auth_data.get('displayName', email)}")
        return auth_data
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Authentication failed: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        sys.exit(1)

def update_golfer_preferences(start_time, end_time, date, players, courses, id_token):
    """
    Update golfer preferences via PUT request to teetimealerts API
    
    Args:
        start_time: Start time hour (e.g., 5 for 5 AM)
        end_time: End time hour (e.g., 12 for 12 PM)
        date: Date in YYYY-MM-DD format
        players: Number of players (e.g., "2", "3", "4")
        courses: List of course_name values to track
        id_token: Authentication token from login
    """
    url = "https://api.teetimealerts.io/api/golfer/preferences/add"
    
    payload = {
        "uuid": "thouv0sZQpfu6vUMzET6Hu696yx1",
        "preferences": {
            "courses": courses,
            "start_times": [int(start_time)],
            "end_times": [int(end_time)],
            "players": [players],
            "dates": [date],
            "preferences_id": 56865685699492,
            "alerts_sent": 0
        },
        "golfer_ignore_in_analytics": 2241
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {id_token}"
    }
    
    try:
        response = requests.put(url, json=payload, headers=headers)
        response.raise_for_status()
        
        print(f"\n✓ Successfully updated preferences")
        print(f"  Start time: {start_time}:00")
        print(f"  End time: {end_time}:00")
        print(f"  Date: {date}")
        print(f"  Players: {players}")
        print(f"  Courses: {len(courses)} selected")
        print(f"\nResponse status: {response.status_code}")
        
        if response.text:
            try:
                print(f"Response data: {json.dumps(response.json(), indent=2)}")
            except json.JSONDecodeError:
                print(f"Response text: {response.text}")
                
    except requests.exceptions.RequestException as e:
        print(f"✗ Error updating preferences: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        sys.exit(1)

def validate_date(date_string):
    """Validate date format YYYY-MM-DD"""
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def get_config_path():
    """Get the path to the user's config file"""
    config_dir = Path.home() / '.teetimealerts'
    config_dir.mkdir(exist_ok=True)
    return config_dir / 'config.json'

def load_config():
    """Load user configuration from file"""
    config_path = get_config_path()
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}

def save_config(config):
    """Save user configuration to file"""
    config_path = get_config_path()
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

def search_courses_by_zip(zipcode, radius=50):
    """
    Search for golf courses by ZIP code
    
    Args:
        zipcode: ZIP code to search
        radius: Search radius in miles (default 50)
        
    Returns:
        list: List of courses with their details
    """
    url = "https://api.teetimealerts.io/api/course/search/zipcode"
    
    payload = {
        "zipCode": zipcode,
        "radius": radius
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        return data.get('courses', [])
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Error searching courses: {e}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return []

def select_courses(courses):
    """
    Interactive course selection from search results
    
    Args:
        courses: List of courses from search
        
    Returns:
        list: List of selected course_name values
    """
    if not courses:
        print("No courses found in your area.")
        return []
    
    print("\n=== Available Golf Courses ===")
    for i, course in enumerate(courses, 1):
        distance = course.get('course_distance', 0)
        print(f"{i:2}. {course['course_fullname']} ({course['course_city']}) - {distance:.1f} miles")
    
    print("\nEnter the numbers of courses you want to track (comma-separated)")
    print("Example: 1,3,5,7")
    print("Or type 'all' to select all courses: ", end='')
    
    selection = input().strip().lower()
    
    if selection == 'all':
        return [course['course_name'] for course in courses]
    
    try:
        indices = [int(x.strip()) - 1 for x in selection.split(',')]
        selected = []
        for idx in indices:
            if 0 <= idx < len(courses):
                selected.append(courses[idx]['course_name'])
        return selected
    except (ValueError, IndexError):
        print("Invalid selection. Please try again.")
        return select_courses(courses)

def get_or_set_default_courses():
    """
    Get default courses from config or prompt user to set them
    
    Returns:
        list: List of course_name values to use
    """
    config = load_config()
    
    if 'default_courses' in config and config['default_courses']:
        print(f"\n✓ Using saved default courses ({len(config['default_courses'])} courses)")
        print("Courses:", ', '.join(config['default_courses'][:5]), 
              '...' if len(config['default_courses']) > 5 else '')
        
        response = input("\nUse these courses? (y/n) or 'reset' to choose new ones: ").strip().lower()
        
        if response == 'y' or response == 'yes' or response == '':
            return config['default_courses']
        elif response != 'reset' and response != 'n' and response != 'no':
            return config['default_courses']
    
    print("\n=== Setting Up Default Courses ===")
    zipcode = input("Enter your ZIP code: ").strip()
    
    if not zipcode:
        print("✗ ZIP code is required")
        sys.exit(1)
    
    print(f"\nSearching for courses near {zipcode}...")
    courses = search_courses_by_zip(zipcode)
    
    if not courses:
        print("✗ No courses found. Please check your ZIP code and try again.")
        sys.exit(1)
    
    selected = select_courses(courses)
    
    if not selected:
        print("✗ No courses selected.")
        sys.exit(1)
    
    config['default_courses'] = selected
    config['zipcode'] = zipcode
    save_config(config)
    
    print(f"\n✓ Saved {len(selected)} courses as defaults")
    return selected

def main():
    parser = argparse.ArgumentParser(
        description='Update golf tee time preferences via TeeTimeAlerts API',
        epilog='Note: Requires .env file with EMAIL and PASSWORD variables'
    )
    
    parser.add_argument('--start_time', 
                        type=int, 
                        required=True,
                        help='Start time hour in 24hr format (0-23)')
    
    parser.add_argument('--end_time', 
                        type=int, 
                        required=True,
                        help='End time hour in 24hr format (0-23)')
    
    parser.add_argument('--date', 
                        type=str, 
                        required=True,
                        help='Date in YYYY-MM-DD format')
    
    parser.add_argument('--num_players', 
                        type=int, 
                        required=True,
                        help='Number of players (1-4)')
    
    args = parser.parse_args()
    
    start_time = args.start_time
    end_time = args.end_time
    date = args.date
    players = str(args.num_players)
    
    try:
        if not (0 <= start_time <= 23):
            raise ValueError("Start time must be between 0 and 23")
        if not (0 <= end_time <= 23):
            raise ValueError("End time must be between 0 and 23")
        if start_time >= end_time:
            raise ValueError("Start time must be before end time")
        if not (1 <= args.num_players <= 4):
            raise ValueError("Number of players must be between 1 and 4")
            
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    if not validate_date(date):
        print(f"Error: Invalid date format. Please use YYYY-MM-DD")
        sys.exit(1)
    
    # Load environment variables
    load_dotenv()
    
    email = os.getenv('EMAIL')
    password = os.getenv('PASSWORD')
    
    if not email or not password:
        print("Error: EMAIL and PASSWORD must be set in .env file")
        print("Please create a .env file with:")
        print("  EMAIL=your_email@example.com")
        print("  PASSWORD=your_password")
        sys.exit(1)
    
    # Get or set default courses
    courses = get_or_set_default_courses()
    
    if not courses:
        print("Error: No courses selected")
        sys.exit(1)
    
    # Authenticate and get token
    print("\nAuthenticating...")
    auth_response = authenticate(email, password)
    id_token = auth_response.get('idToken')
    
    if not id_token:
        print("Error: Failed to get authentication token")
        sys.exit(1)
    
    # Update preferences with authentication
    update_golfer_preferences(str(start_time), str(end_time), date, players, courses, id_token)

if __name__ == "__main__":
    main()