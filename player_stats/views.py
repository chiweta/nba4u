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

            # Render player info and stats to the template
            return render(request, 'player_stats.html', {
                'player': exact_player,
                'stats': stats
            })

        except RequestException as e:
            error_message = f"An error occurred while fetching the data: {str(e)}"
            return render(request, 'player_stats.html', {'error': error_message})

    return render(request, 'search.html')
