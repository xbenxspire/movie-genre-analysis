# Movie Genre Analysis Microservice

A Flask-based microservice that categorizes movies and identifies genre patterns.

## Overview

This microservice is part of the Movie Recommendation System and provides genre analysis functionality. It analyzes movie genres, identifies trends, and provides personalized genre insights based on user watch history.

## API Endpoints

### GET /
- **Description**: Home route with API information
- **Response**: JSON object with available endpoints

### GET /health
- **Description**: Health check endpoint
- **Response**: Status and timestamp

### GET /genres
- **Description**: List all genres with movie counts
- **Response**: JSON object with genre statistics:
  ```json
  {
    "genres": [
      {"name": "Action", "count": 25},
      {"name": "Comedy", "count": 18},
      ...
    ],
    "total_movies": 120,
    "timestamp": "2025-02-25T21:45:30.123456"
  }
  ```

### GET /genres/popular
- **Description**: Get most popular genres based on movie count
- **Response**: JSON object with top 5 genres:
  ```json
  {
    "popular_genres": [
      {"name": "Action", "count": 25, "percentage": 20.8},
      {"name": "Comedy", "count": 18, "percentage": 15.0},
      ...
    ],
    "total_movies": 120,
    "timestamp": "2025-02-25T21:45:30.123456"
  }
  ```

### GET /genres/analysis
- **Description**: Get detailed genre analysis including trends by decade
- **Response**: JSON object with comprehensive genre analysis

### GET /genres/user/<user_id>
- **Description**: Get genre analysis for a specific user based on watch history
- **Response**: JSON object with user-specific genre analysis:
  ```json
  {
    "user_id": 1,
    "watched_movies": 15,
    "genre_breakdown": [
      {"name": "Action", "count": 8, "percentage": 53.3},
      {"name": "Comedy", "count": 4, "percentage": 26.7},
      ...
    ],
    "top_genres": ["Action", "Comedy", "Sci-Fi"],
    "suggested_new_genres": ["Horror", "Documentary", "Animation"],
    "timestamp": "2025-02-25T21:45:30.123456"
  }
  ```

## How to Call from Main Program

### Using Python Requests

```python
import requests

def get_genre_analysis(user_id=None):
    """Get genre analysis from Microservice C"""
    try:
        # For general genre analysis
        if user_id is None:
            response = requests.get("http://127.0.0.1:8002/genres/analysis")
        # For user-specific genre analysis
        else:
            response = requests.get(f"http://127.0.0.1:8002/genres/user/{user_id}")
        
        # Check for successful response
        response.raise_for_status()
        
        # Parse and return analysis
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to genre analysis service: {str(e)}")
        return None
```

### Example Usage

```python
# Get general genre analysis
genre_analysis = get_genre_analysis()

# Display popular genres
if genre_analysis and "genres" in genre_analysis:
    print("Movie Genres:")
    for genre in genre_analysis["genres"]:
        print(f"- {genre['name']}: {genre['count']} movies")
    
    print("\nGenre Trends by Decade:")
    for decade in genre_analysis["decades"]:
        print(f"\n{decade['decade']}:")
        for genre in decade['top_genres']:
            print(f"- {genre['name']}: {genre['count']} movies")
else:
    print("Genre analysis not available at this time.")

# Get user-specific genre analysis
user_id = 1
user_analysis = get_genre_analysis(user_id)

if user_analysis and "genre_breakdown" in user_analysis:
    print(f"\nUser {user_id} Genre Preferences:")
    for genre in user_analysis["genre_breakdown"]:
        print(f"- {genre['name']}: {genre['count']} movies ({genre['percentage']}%)")
    
    print("\nSuggested New Genres to Explore:")
    for genre in user_analysis["suggested_new_genres"]:
        print(f"- {genre}")
else:
    print(f"No genre analysis available for user {user_id}.")
```

## Setup and Running

1. Ensure Flask and required dependencies are installed:
   ```
   pip install flask
   ```

2. Run the service:
   ```
   python service_c.py
   ```

3. The service will start on port 8002 (http://127.0.0.1:8002)

## Data Requirements

The service expects the following data files in the `../data` directory:
- `movies.json` - Movie database
- `history.json` - Watch history

## Error Handling

The service includes comprehensive error handling and logging. Errors are returned as JSON responses with appropriate HTTP status codes.
