"""
Microservice C: Genre Analysis Service
-------------------------------------
Categorizes movies and identifies genre patterns.
"""

from flask import Flask, request, jsonify
import json
import os
import logging
from datetime import datetime
from collections import Counter

# Configure logging
logging.basicConfig(
    filename='genre_analysis_service.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

app = Flask(__name__)

# Disable Flask's default output
import sys
cli = sys.modules['flask.cli']
cli.show_server_banner = lambda *x: None

# Path to data files
DATA_DIR = '../data'
MOVIES_FILE = os.path.join(DATA_DIR, 'movies.json')
HISTORY_FILE = os.path.join(DATA_DIR, 'history.json')

def read_json_file(filename):
    """Read and parse a JSON file"""
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
            logging.info(f"Read data from {filename}.")
            return data
    except FileNotFoundError:
        logging.error(f"File not found: {filename}")
        return {}
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error in {filename}: {str(e)}")
        return {}

@app.route('/')
def home():
    """Home route with API info"""
    logging.info(f"Received {request.method} request on {request.path}")
    return jsonify({
        "message": "Genre Analysis Service API",
        "endpoints": [
            "/genres - List all genres with movie counts",
            "/genres/popular - Get most popular genres",
            "/genres/analysis - Get detailed genre analysis",
            "/genres/user/<user_id> - Get genre analysis for specific user",
            "/health - Check service health"
        ]
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/genres', methods=['GET'])
def list_genres():
    """List all genres with movie counts"""
    logging.info(f"Received request to list genres")
    
    try:
        # Get all movies
        movies = read_json_file(MOVIES_FILE)
        if not movies:
            return jsonify({"error": "Could not read movies data"}), 500
        
        # Count movies by genre
        genre_counts = Counter([movie['genre'] for movie in movies])
        
        # Format response
        genres = [
            {"name": genre, "count": count}
            for genre, count in sorted(genre_counts.items())
        ]
        
        logging.info(f"Found {len(genres)} genres")
        return jsonify({
            "genres": genres,
            "total_movies": len(movies),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logging.error(f"Error listing genres: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/genres/popular', methods=['GET'])
def popular_genres():
    """Get most popular genres based on movie count"""
    logging.info(f"Received request for popular genres")
    
    try:
        # Get all movies
        movies = read_json_file(MOVIES_FILE)
        if not movies:
            return jsonify({"error": "Could not read movies data"}), 500
        
        # Count movies by genre
        genre_counts = Counter([movie['genre'] for movie in movies])
        
        # Get top genres (limit to top 5)
        top_genres = genre_counts.most_common(5)
        
        # Format response
        popular = [
            {"name": genre, "count": count, "percentage": round((count / len(movies)) * 100, 1)}
            for genre, count in top_genres
        ]
        
        logging.info(f"Found {len(popular)} popular genres")
        return jsonify({
            "popular_genres": popular,
            "total_movies": len(movies),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logging.error(f"Error getting popular genres: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/genres/analysis', methods=['GET'])
def genre_analysis():
    """Get detailed genre analysis including trends by decade"""
    logging.info(f"Received request for genre analysis")
    
    try:
        # Get all movies
        movies = read_json_file(MOVIES_FILE)
        if not movies:
            return jsonify({"error": "Could not read movies data"}), 500
        
        # Count movies by genre
        genre_counts = Counter([movie['genre'] for movie in movies])
        
        # Analyze genres by decade
        decades = {}
        for movie in movies:
            try:
                year = int(movie['release_date'].split('-')[0])
                decade = (year // 10) * 10  # e.g., 1990, 2000, 2010
                
                if decade not in decades:
                    decades[decade] = Counter()
                
                decades[decade][movie['genre']] += 1
            except (ValueError, IndexError):
                # Skip movies with invalid release dates
                continue
        
        # Format decade data
        decade_analysis = []
        for decade, counts in sorted(decades.items()):
            top_genres = counts.most_common(3)
            decade_analysis.append({
                "decade": f"{decade}s",
                "top_genres": [
                    {"name": genre, "count": count}
                    for genre, count in top_genres
                ],
                "total_movies": sum(counts.values())
            })
        
        # Format response
        analysis = {
            "genres": [
                {"name": genre, "count": count}
                for genre, count in sorted(genre_counts.items())
            ],
            "decades": decade_analysis,
            "total_movies": len(movies),
            "timestamp": datetime.now().isoformat()
        }
        
        logging.info(f"Completed genre analysis")
        return jsonify(analysis)
        
    except Exception as e:
        logging.error(f"Error performing genre analysis: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/genres/user/<int:user_id>', methods=['GET'])
def user_genre_analysis(user_id):
    """Get genre analysis for a specific user based on watch history"""
    logging.info(f"Received request for user {user_id} genre analysis")
    
    try:
        # Get all movies
        movies = read_json_file(MOVIES_FILE)
        if not movies:
            return jsonify({"error": "Could not read movies data"}), 500
        
        # Get user history
        history = read_json_file(HISTORY_FILE)
        user_history = history.get(str(user_id), [])
        
        if not user_history:
            return jsonify({
                "user_id": user_id,
                "message": "No watch history found for this user",
                "genres": [],
                "recommendations": []
            })
        
        # Count genres in user history
        genre_counts = Counter([movie['genre'] for movie in user_history if 'genre' in movie])
        
        # Get user's top genres
        top_genres = [genre for genre, _ in genre_counts.most_common()]
        
        # Find underrepresented genres (genres with movies but user hasn't watched)
        all_genres = set(movie['genre'] for movie in movies)
        unwatched_genres = all_genres - set(genre_counts.keys())
        
        # Format response
        analysis = {
            "user_id": user_id,
            "watched_movies": len(user_history),
            "genre_breakdown": [
                {"name": genre, "count": count, "percentage": round((count / len(user_history)) * 100, 1)}
                for genre, count in genre_counts.most_common()
            ],
            "top_genres": top_genres[:3],
            "suggested_new_genres": list(unwatched_genres)[:3],
            "timestamp": datetime.now().isoformat()
        }
        
        logging.info(f"Completed genre analysis for user {user_id}")
        return jsonify(analysis)
        
    except Exception as e:
        logging.error(f"Error performing user genre analysis: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print(f"Starting Genre Analysis Service on port 8002...")
    app.run(host='127.0.0.1', port=8002, debug=False)
