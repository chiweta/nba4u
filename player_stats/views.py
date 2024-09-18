from django.shortcuts import render
import requests
from requests.exceptions import RequestException

API_KEY = 'b902502d-d944-434e-89c3-951cbb462fe9'

# Home view to display the main page (search form)
def home(request):
    return render(request, 'home.html')

# Search Player view to display the search form
def search_player(request):
    return render(request, 'search.html')

def calculate_score_and_grade(stats):
    # Basic scoring logic: Higher points, rebounds, assists, etc., increase the score.
    score = 0
    score += stats.get('pts', 0) * 2       # Points are weighted heavily
    score += stats.get('reb', 0) * 1.5     # Rebounds are also important
    score += stats.get('ast', 0) * 1.5     # Assists are important
    score += stats.get('stl', 0) * 2       # Steals and blocks are defensive stats
    score += stats.get('blk', 0) * 2
    score += stats.get('fg_pct', 0) * 50   # Field Goal percentage is given weight
    score += stats.get('ft_pct', 0) * 30   # Free throw percentage
    score += stats.get('fg3_pct', 0) * 40  # 3-point percentage

    # Ensure the score is out of 100
    max_score = 100
    score = min(score, max_score)

    # Define the grade based on the score
    if score >= 90:
        grade = 'A+'
    elif score >= 80:
        grade = 'A'
    elif score >= 70:
        grade = 'B'
    elif score >= 60:
        grade = 'C'
    elif score >= 50:
        grade = 'D'
    else:
        grade = 'F'

    return score, grade

# Player Stats view to display the stats of the player based on input
def player_stats(request):
    if request.method == 'POST':
        player_name = request.POST.get('player_name').strip()
        name_parts = player_name.split()

        headers = {
            "Authorization": "b902502d-d944-434e-89c3-951cbb462fe9"  # Your API Key
        }

        try:
            # Search by last name
            player_url = f"https://api.balldontlie.io/v1/players?search={name_parts[-1]}"
            player_response = requests.get(player_url, headers=headers)

            if player_response.status_code != 200:
                error_message = f"Error fetching player data. Status code: {player_response.status_code}"
                return render(request, 'player_stats.html', {'error': error_message})

            player_data = player_response.json()

            if not player_data['data']:
                error_message = "Player not found. Please try again with a different name."
                return render(request, 'player_stats.html', {'error': error_message})

            # Find exact match by first and last name
            exact_player = None
            for player in player_data['data']:
                if len(name_parts) == 2 and player['first_name'].lower() == name_parts[0].lower() and player['last_name'].lower() == name_parts[1].lower():
                    exact_player = player
                    break

            if not exact_player:
                error_message = "Exact player not found. Please try again."
                return render(request, 'player_stats.html', {'error': error_message})

            # Fetch the player stats
            player_id = exact_player['id']
            stats_url = f"https://api.balldontlie.io/v1/season_averages?season=2023&player_ids[]={player_id}"
            stats_response = requests.get(stats_url, headers=headers)

            if stats_response.status_code != 200:
                error_message = f"Error fetching player stats. Status code: {stats_response.status_code}"
                return render(request, 'player_stats.html', {'error': error_message})

            stats_data = stats_response.json()

            if not stats_data['data']:
                error_message = "No stats available for this player."
                return render(request, 'player_stats.html', {'error': error_message})

            stats = stats_data['data'][0]  # Latest season stats

            # Calculate score and grade based on stats
            score, grade = calculate_score_and_grade(stats)

            # Render player info, stats, score, and grade to the template
            return render(request, 'player_stats.html', {
                'player': exact_player,
                'stats': stats,
                'score': score,
                'grade': grade
            })

        except RequestException as e:
            error_message = f"An error occurred while fetching the data: {str(e)}"
            return render(request, 'player_stats.html', {'error': error_message})

    return render(request, 'search.html')
