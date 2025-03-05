import requests
import webbrowser

gray_color = "\033[90m"
reset_color = "\033[0m"

ascii_art = """
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⢠⣴⣶⣤⣶⣦⡀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣶⣿⣿⣯⣿⣿⣿⣿⣿⣿⠃
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠃⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣯⡭⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣼⣿⣿⣿⣿⣿⢿⣿⣿⣿⣿⣿⣿⣿⠇⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⣿⣿⣿⣿⢟⣵⣿⣿⣿⣿⣿⡿⠟⠁⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣰⣿⢿⣿⣿⠟⣡⣾⣿⣿⣿⣿⣿⠶⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣼⣿⣿⣿⡿⢫⣾⣿⣿⣿⣿⡿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⡀⣿⣿⣿⡟⣱⣿⣿⣿⣿⣯⠅⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⣸⣷⣿⣿⢏⣼⣿⣿⣿⣿⡿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⣾⣿⣿⣿⢃⣾⣿⣿⣿⡏⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⣿⣿⡿⢡⣿⣿⣿⡿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⢿⡿⢡⣿⡿⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⣸⠃⠈⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⢠⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⢀⡎⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⣸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⢀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
"""

gray_ascii = "\n".join(gray_color + line + reset_color for line in ascii_art.split("\n"))

print(gray_ascii)

urls_file = "urls.txt"

urls = []
try:
    with open(urls_file, 'r') as file:
        urls = [line.strip() for line in file.readlines() if line.strip()]
except FileNotFoundError:
    print(f"File {urls_file} not found. Please ensure the file exists.")
    exit()

def fetch_data_from_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch data from {url}. Status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return None

combined_downloads = []
for url in urls:
    data = fetch_data_from_url(url)
    if data:
        downloads = data.get("downloads", [])
        combined_downloads.extend(downloads)

def display_games(games_list):
    """Function to display games with their index and title."""
    for index, game in enumerate(games_list):
        title = game.get("title", "No Title")
        file_size = game.get("fileSize", "No Size")
        print(f"[{index + 1}] {title} | {file_size}")

def search_game(query):
    """Function to search games by a partial title."""
    query_lower = query.lower()
    filtered_games = [game for game in combined_downloads if query_lower in game.get("title", "").lower()]
    return filtered_games

print("Choose an option:")
print("1. Show all games")
print("2. Search for a game")

try:
    choice = int(input("\nEnter your choice (1 or 2): "))

    if choice == 1:
        print("\nShowing all games:")
        display_games(combined_downloads)
        games_list_to_select_from = combined_downloads
    elif choice == 2:
        query = input("\nEnter the game title: ").strip()
        search_results = search_game(query)

        if search_results:
            print("\nSearch results:")
            display_games(search_results)
            games_list_to_select_from = search_results
        else:
            print("\nNo games found with that search query.")
            games_list_to_select_from = []
    else:
        print("Invalid option.")
        games_list_to_select_from = []

    if games_list_to_select_from:
        try:
            selection = int(input("\nEnter the game number: "))
            if 1 <= selection <= len(games_list_to_select_from):

                selected_game = games_list_to_select_from[selection - 1]
                magnet_link = selected_game.get("uris", [None])[0]

                if magnet_link:
                    print(f"Opening magnet link for: {selected_game['title']}")
                    webbrowser.open(magnet_link)
                else:
                    print("No magnet link found for the selected game.")
            else:
                print("Invalid selection.")
        except ValueError:
            print("Please enter a valid number.")
    else:
        print("No games to select from.")

except ValueError:
    print("Please enter a valid number.")
