import os 
import shutil as su
import requests
import pyttsx3
import base64
import os
import lyricsgenius
import json

with open('data.json', 'r') as f: 
    keys = json.load(f) # Load the file data.json

def get_artist(artist_id, save_images=False):
    endpoint = 'https://api.spotify.com/v1/' 
    method = f'artists/{artist_id}'
    client_id = f'{keys["spotify"]["client_id"]}'
    client_secret = f'{keys["spotify"]["client_secret"]}'

    # Use client ID and client secret to obtain an access token
    token_url = 'https://accounts.spotify.com/api/token'
    encoded_client_credentials = base64.b64encode(
        f"{client_id}:{client_secret}".encode('ascii')).decode('ascii')
    headers = {
        'Authorization': f'Basic {encoded_client_credentials}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {'grant_type': 'client_credentials'}
    response = requests.post(token_url, headers=headers, data=data)
    if response.status_code == 200: 
        access_token = response.json()['access_token']
    else:
        return f"Error: {response.status_code} - {response.reason}"

    # Make the request to the API using the access token
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        'market': 'US'
    }

    response = requests.get(endpoint + method, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        if save_images == True or save_images == None: # Save image locally
            folder_path = os.path.abspath(f'artist_icons/{data["name"]}')
            if not os.path.exists(folder_path): # Create path if not pre-made
                os.makedirs(folder_path)
            file_path = f"{folder_path}/{data['images'][0]['url'].split('/')[-1]}.png"
            image_response = requests.get(data["images"][0]["url"])
            with open(file_path, 'wb') as f: 
                f.write(image_response.content) # Upload the image

        return f'Stats of {data["name"]}:\nFollowers - {data["followers"]["total"]}\nType - {data["type"]}\nGenres - {"".join(data["genres"])}\nAvatar - {data["images"][0]["url"]}'
    else:
        return 'Error, status code returned as ' + str(response.status_code)


        
        

def get_lyrics(track_name, artist_name, engine='genius', return_json=False):
    if engine == 'musix':
        endpoint = 'http://api.musixmatch.com/ws/1.1/'
        # Define the endpoint for the API method
        method = 'matcher.lyrics.get'
        api_key = f'{keys["musixmatch"]["api_key"]}'
        # Define the query parameters
        params = {
            'apikey': api_key,
            'q_track': track_name,
            'q_artist': artist_name,
            'format': 'json',
            'f_has_lyrics': 1,
            'page_size': 1
        }

        # Make the request to the API
        response = requests.get(endpoint + method, params=params)
        if response.status_code == 200:
            data = response.json()
            if data['message']['header']['status_code'] == 200:
                if return_json == False:
                    return data['message']['body']['lyrics']['lyrics_body'] 
                else:
                    return json.dumps({'lyrics': data['message']['body']['lyrics']['lyrics_body']}, indent=4) # If return_json is set to True, create a JSON file with the data in it
            else:
                return 'Error, status code returned as' + data['message']['header']['status_code']
    elif engine == 'genius':
        genius = lyricsgenius.Genius(f'{keys["genius"]["token"]}') 

        song = genius.search_song(track_name, artist_name)

        lyrics = song.lyrics
        if return_json == False:
            return lyrics
        else:
            return json.dumps({'lyrics': lyrics}, indent=4) # If return_json is set to True, create a JSON file with the data in it
    else:
        return 'Invalid engine specified' 


    
def get_cover(track_id):
    endpoint = 'https://api.spotify.com/v1/'
    method = f'tracks/{track_id}'
    client_id = f'{keys["spotify"]["client_id"]}'
    client_secret = f'{keys["spotify"]["client_secret"]}'

    # Use client ID and client secret to obtain an access token
    token_url = 'https://accounts.spotify.com/api/token'
    encoded_client_credentials = base64.b64encode(
        f"{client_id}:{client_secret}".encode('ascii')).decode('ascii')
    headers = {
        'Authorization': f'Basic {encoded_client_credentials}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {'grant_type': 'client_credentials'}
    response = requests.post(token_url, headers=headers, data=data)
    if response.status_code == 200:
        access_token = response.json()['access_token']
    else:
        return f"Error: {response.status_code} - {response.reason}"

    # Make the request to the API using the access token
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        'market': 'US'
    }
    response = requests.get(endpoint + method, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        cover_url = data['album']['images'][0]['url']
        
        folder_path = os.path.abspath('images')

        
        requests.get(cover_url)
        
        if os.path.exists(folder_path) == False: # Create folder if not pre-made
            os.mkdir('images')
        file_path = f"{folder_path}/{cover_url.split('/')[-1]}.png"
        response = requests.get(cover_url)
        with open(file_path, 'wb') as f:
            f.write(response.content) # Download the image locally
        
        return cover_url
    else:
        return f"Error: {response.status_code} - {response.reason}"


# code to delete X files and folders with the word " Y " in it
def delete_file_with_name(folder_directory=None, keyword='', amount=1):
    
    if not folder_directory: # if folder param is empty, use home ( i think haha )
        folder_path = os.getcwd()
    else:
        folder_path = os.path.abspath(folder_directory) # Folder path specified
        
        if amount >= len(os.listdir(folder_path)): # if specified amount is bigger than the found items ( you can remove this statement and code will run fine, it's here more for the logic
            print(f'There were only {len(os.listdir(folder_path))} items found, you can\'t delete {amount} items.')
            return

    i = 1
    files_deleted = 0
    while i <= amount and files_deleted < amount: # As long as the amount is bigger than variable i and the deleted files is lesser than the specified amount ( i should brush up on operators )
        for filename in os.listdir(folder_path):
            if str(keyword) in filename:
                filepath = os.path.join(folder_path, filename)
                if os.path.isfile(filepath):
                    os.remove(filepath)
                    files_deleted += 1
                else:
                    su.rmtree(filepath)
                    files_deleted += 1
            if files_deleted >= amount:
                break
        i += 1



# code to create X folders with the name Y and a file in it with the text " Z " in it
def create_folder(folder_directory=None, amount=1, name='New Folder', content="Empty"):
    if not folder_directory:
        folder_path = os.getcwd()
    else:
        folder_path = os.path.abspath(folder_directory)
        
    os.makedirs(folder_path, exist_ok=True)
    
    i = 1 
    while i <= amount:
        dirname = f"{name} {i}"
        os.mkdir(os.path.join(folder_path, dirname))
        path_join = os.path.join(folder_path, dirname, f'{name}.txt')
        file = open(path_join, 'w')
        file.write(content)
        file.close()
        i += 1 
