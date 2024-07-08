import sqlite3
import time
import hashlib
from datetime import date
import getpass
from operator import itemgetter
import sys

connection = None
cursor = None

def connect(path):
    global connection, cursor

    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute(' PRAGMA forteign_keys=ON; ')
    connection.commit()
    return

'''
sub-function: check_if_user
Arguments: entered_id
Returns: True if entered id is a user and False if entered id is not a user
Functionality: checks if the id that the user entered is a user or not
'''
def check_if_user(entered_id): 
    global connection, cursor
    # check if is a user: 
    cursor.execute('''
                  SELECT u.uid 
                  FROM users u
                  WHERE u.uid LIKE :id
                  ''', {'id': entered_id})

    users = cursor.fetchall()
    user_list = []

    for user in users:
        user_list.append(user)  

    is_user = False

    # is a user
    if (len(user_list) == 1):
        is_user = True
        return True
    else:
        return False

'''
sub-function: check_if_valid_user
Arguments: entered_id, password
Returns: True if entered id is a valid user and False if entered id is not a valid user
Functionality: checks if the id that the user entered and the password match any registered users
'''
def check_if_valid_user(entered_id, password): 
    global connection, cursor
    # first case check if a valid user
    cursor.execute('''
                  SELECT u.uid 
                  FROM users u
                  WHERE u.uid LIKE :id
                  AND u.pwd = :password
                  ''', {'id': entered_id, 'password': password})

    users = cursor.fetchall()
    user_list = []

    for user in users:
        user_list.append(user)  

    is_user = False

    # is a valid user
    if (len(user_list) == 1):
        is_user = True
        return True
    else:
        return False

'''
sub-function: check_if_artist
Arguments: entered_id
Returns: True if entered id is an artist and False if entered id is not an artist
Functionality: checks if the id that the artist entered is an artist or not
'''
def check_if_artist(entered_id): 
    global connection, cursor
    # check if is an artist: 
    cursor.execute('''
                  SELECT a.aid 
                  FROM artists a
                  WHERE a.aid = :id
                  ''', {'id': entered_id})

    artists = cursor.fetchall()
    artist_list = []

    for artist in artists:
        artist_list.append(artist)  

    is_artist = False

    # is an artist
    if (len(artist_list) == 1):
        is_artist = True  
        return True
    else:
        return False

'''
sub-function: check_if_valid_artist
Arguments: entered_id, password
Returns: True if entered id is a valid artist and False if entered id is not a valid artist
Functionality: checks if the id that the artist entered and the password match any registered artist
'''    
def check_if_valid_artist(entered_id, password):  
    global connection, cursor
    # check if valid artist
    cursor.execute('''
                  SELECT a.aid 
                  FROM artists a
                  WHERE a.aid LIKE :id
                  AND a.pwd = :password
                  ''', {'id': entered_id, 'password': password})

    artists = cursor.fetchall()
    artist_list = []

    for artist in artists:
        artist_list.append(artist)  

    is_artist = False

    #is a valid artist
    if (len(artist_list) == 1):
        is_artist = True  
        return True
    else:
        return False

'''
main-function: login_page
Arguments: None
Returns: None
Functionality: logs in a user or an artist by asking for an id and a password. It will register users who are not already registered
''' 
def login_page(): 
    global connection, cursor

    choice_not_made = True

    while(choice_not_made):
        choice = input("Do you want to register or login? Type 'r' if you want to register and 'l' to login: ")

        if (choice == 'r'):
            # will register the user
            choice_not_made = False

            user_name = register_user()

            #enter a name and a password
            new_name = input('Enter your name: ')
            new_password = input('Enter a password: ')

            cursor.execute('''
            INSERT INTO users (uid, name, pwd) VALUES
            (:uid, :uname, :upass);''', {'uid': user_name,'uname': new_name,'upass': new_password})

            print('Success! You have been registered!')

            connection.commit()  

            # logs in the user
            login_user(user_name)


        elif(choice == 'l'):
            choice_not_made = False
            # try to login the user
            try_login()

    return

'''
main-function: try_login
Arguments: None
Returns: None
Functionality: tries to log in a user or an artist, if it fails, it will register a user
''' 
def try_login():  
    decision_not_valid = True
    while(decision_not_valid):
        print("Enter an id and a password: ")

        entered_id = input("id: ").lower()

        # hides password
        password = getpass.getpass() # will be hidden when using the terminal    

        is_user = check_if_user(entered_id)
        is_valid_user = check_if_valid_user(entered_id, password)

        is_artist = check_if_artist(entered_id)
        is_valid_artist = check_if_valid_artist(entered_id, password)

        # if both user and artist ask which they want to login as
        if ((is_user and is_valid_artist) or (is_valid_user and is_artist) or (is_valid_user and is_valid_artist)):
            decision_not_valid = False
            print('We can see you are a user and an artist. What do you want to sign in as? ')
            decision_not_made = True
            while(decision_not_made):
                choice = input("Type 'user' if you want to sign in as a user and 'artist' if you want to sign in as an artist: ")
                if (choice == 'user'):
                    #logs in as a user
                    login_user(entered_id)
                    return
                elif (choice == 'artist'):
                    # logs in as an artist
                    login_artist(entered_id)
                    return
                else:
                    print('That was invalid, please try again.')


        # if neither, register them
        if (((not is_artist) and (not is_user))):
            decision_not_valid = False
            print('It looks like you are not a user or an artist. We are going to register you: ')
            #registers the user

            user_name = register_user()

            new_name = input('Enter your name: ')
            new_password = input('Enter a password: ')

            # inserts the new user into users table
            cursor.execute('''
            INSERT INTO users (uid, name, pwd) VALUES
            (:uid, :uname, :upass);''', {'uid': user_name,'uname': new_name,'upass': new_password})

            print('Success! You have been registered!')

            # logs in the user
            login_user(user_name)

            connection.commit()

            return


        # if one or the other, log in the user or the artist:
        elif (is_valid_user):
            decision_not_valid = False
            login_user(entered_id)
            return

        elif(is_valid_artist):
            decision_not_valid = False
            login_artist(entered_id)
            return

        else:
            print('Your password is incorrect, please try again.')

    return

'''
main-function: register_user
Arguments: None
Returns: None
Functionality: It will register users who are not already registered
'''         
def register_user():  
    user_name = input('Enter a username: ').lower()

    cursor.execute('''
                  SELECT u.uid 
                  FROM users u
                  WHERE u.uid LIKE :user_id
                  ''', {'user_id': user_name})

    users = cursor.fetchall()
    user_list = []

    for user in users:
        user_list.append(user)

    if ((len(user_list) != 1) and (len(user_name) >= 1) and (len(user_name) <= 4)):
        #valid uid has been chosen
        print('valid uid')
        return user_name
    else:
        # else it will loop again
        print('please try again')
        register_user()
        return

'''
main-function: login_user
Arguments: userId
Returns: None
Functionality: It give the user 4 options of activivities to perform
'''   
def login_user(userId): 
    global connection, cursor

    choice = 'temp'

    while((choice != '0') or (choice != 'exit')):
        print('What would you like to do? Please type the respective number corresponding to the action you want to perform: ')
        print('Options: \n(1) Start a Session \n(2) Search for Songs and Playlists \n(3) Search for Artists \n(4) End the Session\n(0) Return to Login Screen\n(exit) Exit the Application')
        choice = input('Your decision: ')   

        if(choice in ('0', 'exit')):
            break

        #Start a session
        if (choice == '1'):
            print('Starting a session')
            start_a_session(userId)


        #Search for songs and playlists
        elif (choice == '2'):
            print('searching for songs and playlists')
            search_song_and_playlist(userId)


        #Search for artists    
        elif (choice == '3'):
            print('searching for artists')
            search_artist(userId)

        elif (choice == '4'):
            print('ending user session')
            end_the_session(userId)


        elif(choice not in ('1', '2', '3', '4', '0', 'exit')):
            print('Invalid decision, please try again.')

    #End the session for all users
    if(choice == '0'):
        end_the_session(userId)
        login_page()

    elif(choice == 'exit'):
        end_the_session_for_all_users()
        return
    return

'''
main-function: search_song_and_playlist
Arguments: user_name
Returns: None
Functionality: It allows the user to search for songs or playlists and will print matching songs and/or playlists, then the user can select a song or a playlist
and perform song actions with the song or the songs in the playlist
'''   
def search_song_and_playlist(user_name):  
    search = input('Please enter what you want to search for: ')

    # gets a list of keywords
    split_search = search.split()

    song_string = "select 'song', sid, count(a.keyword) FROM"

    playlist_string = "select 'playlist', pid, count(a.keyword) FROM"

    string = ' (SELECT '    

    p = 0

    # case where user enters nothing
    if (split_search == []):
        split_search = ['']    

    length = len(split_search) - 1

    for i in split_search:
        # build string for query to search for songs and playlist titles that match the keywords
        if p == 0:
            string = string + "'" + i + "'" + " keyword UNION "

        else:
            string = string + "SELECT '" + i + "'" + " keyword UNION "        

        string = string + "SELECT '% " + i + " %'" + " UNION "

        string = string + "SELECT '" + i + " %'" + " UNION "

        if (p != length):
            string = string + "SELECT '% " + i + "' UNION "

        elif (p == length):
            string = string + "SELECT '% " + i + "' ) a "
        p += 1

    song_string = song_string + string

    # query to get song titles that match with keywords
    song_string = song_string + 'JOIN songs s ON s.title LIKE a.keyword GROUP BY s.title ORDER BY count(a.keyword) DESC'

    playlist_string = playlist_string + string

    # query to get playlist titles that match with keywords
    playlist_string = playlist_string + 'JOIN playlists p ON p.title LIKE a.keyword GROUP BY p.title ORDER BY count(a.keyword) DESC'

    songs_list = search_for_keyword(song_string)

    playlists_list = search_for_keyword(playlist_string)

    items = playlists_list + songs_list

    # sorts the counts of playlists and song id's in order based on keyword matches
    sorted_items = sorted(items, key=itemgetter(2), reverse=True)

    compile_results(user_name, sorted_items)

    return

'''
main-function: search_artist
Arguments: user_name
Returns: None
Functionality: It allows the user to search for artists and will print any songs with matching titles or artists and allows the user to pick an artist and view their songs
'''   
def search_artist(user_name):  
    search = input('Please enter what you want to search for: ')

    # gets a list of keywords
    split_search = search.split()

    artist_string = "SELECT aid, count(a.keyword) count FROM"

    song_string = "SELECT p.aid aid, count(a.keyword) count FROM"

    string = ' (SELECT '    

    p = 0

    if (split_search == []):
        split_search = ['']        

    length = len(split_search) - 1

    for i in split_search:
        # build string for query to get matching artist names and song titles
        if p == 0:
            string = string + "'" + i + "'" + " keyword UNION "
        else:
            string = string + "SELECT '" + i + "'" + " keyword UNION "

        string = string + "SELECT '% " + i + " %'" + " UNION "

        string = string + "SELECT '" + i + " %'" + " UNION "

        if (p != length):
            string = string + "SELECT '% " + i + "' UNION "

        elif (p == length):
            string = string + "SELECT '% " + i + "' ) a "
        p += 1

    artist_string = artist_string + string

    # query to get artist names that match with keywords
    artist_string = artist_string + 'JOIN artists art ON art.name LIKE a.keyword GROUP BY art.name ORDER BY count(a.keyword) DESC'

    song_string = song_string + string

    # query to get song titles that match with keywords
    song_string = song_string + 'JOIN songs s ON s.title LIKE a.keyword, perform p WHERE p.sid = s.sid GROUP BY p.aid ORDER BY count(a.keyword) DESC'

    artist_list_1 = search_for_keyword(artist_string)

    artist_list_2 = search_for_keyword(song_string)

    items = artist_list_1 + artist_list_2

    temp = {}

    for i, j in items:
        state = is_key_in_dict(i, temp)
        if (state):
            temp[i] += j
        else:
            temp[i] = j


    merged_items = []

    for i in temp.items():
        merged_items.append(i)

    # sorts the counts of songs and artists id's in order based on keyword matches
    sorted_items = sorted(merged_items, key=itemgetter(1), reverse=True)

    compile_results_artist(user_name, sorted_items)

    return

'''
sub-function: compile_results_artist
Arguments: user_name, items
Returns: None
Functionality: it will format the artists provided into the correct string format
'''  
def compile_results_artist(user_name, items): 
    print('These are the results:')
    list_length = len(items)

    current_start = 0
    current_end = 5

    not_done = True

    results = []
    result_list = []

    result_number = 1

    for i in items:
        cursor.execute('''
        SELECT a.aid, a.name, a.nationality, COUNT(p.sid)
        FROM artists a, perform p
        WHERE a.aid = :aid
        AND a.aid = p.aid;
        ''', {'aid': i[0]})
        details = cursor.fetchall()

        aid = details[0][0]
        name = details[0][1]
        nationality = details[0][2]
        song_count  = details[0][3]

        # all artist details
        results.append('(' + str(result_number) + ') Artist: ' + ' aid: ' + str(aid) + ' Name: ' + name + ' Nationality: ' + str(nationality) + ' Number of Songs Performed: ' + str(song_count))      

        result_list.append(aid)

        result_number += 1

    # will print all artist details
    show_results_artists(user_name, results, result_list)

    return


'''
sub-function: show_results_artists
Arguments: user_name, results, result_list
Returns: None
Functionality: it will print the results previously compiled and allow the user to select a song or a playlist
'''  
def show_results_artists(user_name, results, result_list): 

    length = len(results)

    total_pages = 1

    page_num_not_found = True

    range_of_options = range(0, length + 1)

    valid_options = []

    # gets all valid options to select artists
    for i in range_of_options:
        valid_options.append(str(i))    

    # get number of pages
    while(page_num_not_found):

        if(length > total_pages * 5):
            total_pages += 1
        else:
            page_num_not_found = False

    not_done = True

    current_start = 0
    current_end = 5

    if(length == 0):
        print('No results were found.')
        return

    current_page = 1

    while(not_done):
        while((current_start < current_end) and (current_start < length)):
            # prints artists in correct order
            print(results[current_start])
            current_start += 1

        if (current_end < length):
            print('(more) See more options\n(exit) Return to main menu')
            print('Page: ' + str(current_page) + '/' + str(total_pages))
            current_page += 1

        elif(current_start == length):
            print('(exit) Return to main menu\nPlease select one of the options from above')
            print('Page: ' + str(current_page) + '/' + str(total_pages))
            current_start += 1

        elif ((current_end >= length) and (length != 0)):
            print('(exit) Return to main menu\nNo more options, please select one of the options from above')

        decision = input('Your decision: ').lower()

        if(decision == 'more'):
            current_end += 5

        elif(decision == 'exit'):
            not_done = False        


        elif(decision in valid_options):
            # get artist id

            position = (int(decision) - 1)

            aid = result_list[position]

            show_artist_songs(aid, user_name)

            return

        elif(decision not in valid_options):
            print('Invalid decision, please try again.')

    return

'''
main-function: get_info_about_song
Arguments: sid
Returns: None
Functionality: Given the sid of a song by the user, it retrieves the names of artists, id, title and duration of the song as well as the names of playlists the song is in (if any). 
'''      
def get_info_about_song(sid): 
    cursor.execute ('''
                    SELECT a.name, s.sid, s.title, s.duration
                    FROM artists a, songs s, perform p
                    WHERE s.sid = :sid
                    AND p.sid = s.sid
                    AND p.aid = a.aid
                    ''', {'sid': sid}) 

    more_info = cursor.fetchall()[0]

    print('Artist Name: ' + more_info[0] + ' sid: ' + str(more_info[1]) + ' Song Title: ' + more_info[2] + ' Song Duration: ' + str(more_info[3]))

    cursor.execute ('''
                    SELECT p.title
                    FROM playlists p, plinclude pl
                    WHERE pl.pid = p.pid
                    AND pl.sid = :sid
                    ''', {'sid': sid}) 
    playlists_names = cursor.fetchall()

    print('Playlists that ' + more_info[2] + ' is in: ')
    for playlist in playlists_names:
        print('- ' + playlist[0])

    return


'''
main-function: add_songs_playlist
Arguments: song ID, user ID
Returns: None
Functionality:
	song from arguments can be added to an existing playlist owned by the user (if any) or to a new playlist. 
	get choice from user to add to existing or create new playlist
	When it is added to a new playlist, a new playlist should be created with a unique id (created by your system) 
	and the uid set to the id of the user and a title should be obtained from input. 
''' 
def add_song_playlist(songID, userID):
    # MAIN add_a_song_playlist

    # prompt for input until user decides (1): add song to existing playlist or (2) create new playlist
    valid = False
    print("Would you like to:\n(1) Add song to one of your existing playlists\n(2) Add song to a new playlist\n(0) Home page")
    choice = input("Your decision: ")
    while not valid:
        if choice == '1':
            valid = True
            add_to_playlist(userID, songID)
        elif choice == '2':
            valid = True
            create_new_playlist(userID, songID)
        elif choice != '0':
            choice = input("Please enter a valid option number: ")
        else:
            valid = True    # will exit add song to playlist and take you back to home page 


    return

'''
helper-function: create_new_playlist
to:	main-function: add_songs_playlist
Arguments: user ID, song ID
Returns: None
Functionality:
	Creates new playlist with a unique pID, with the title obtained from input
	and the uid set to the id of the user with title obtained from input.
	Adds song from arguments into new playlist
''' 
def create_new_playlist(userID, songID): 
    # HELPER function to MAIN add_songs_playlist

    # obtain title from input
    play_title = input("What would you like to name your new playlist? : ")

    # find unique pID: Assuming best algorithm, next available pID will be one plus the number of playlists
    # (meaning pids increase by 1 uniformly when a new one is added).
    # In worse scenario, pIDs are random, in this case I will chose the starting point to be one plus the number of playlists
    # and increment by 1 until we find a pID that is not in use

    # find number of playlists
    cursor.execute('''
        SELECT count(p.pid)
        FROM playlists p;
    ''')
    pid_count_temp = cursor.fetchall()
    pid_count = pid_count_temp[0][0]
    try_pid = pid_count + 1 # one plus number of playlsts. Will be new pID in best case

    # find and append all existing pids to list
    cursor.execute('''
        SELECT p.pid
        FROM playlists p;
    ''')
    pid_list_temp = cursor.fetchall()
    pid_list = []
    for _pid in pid_list_temp:
        pid_list.append(_pid[0])

    # increment test pid until it is unique 
    while try_pid in pid_list:
        try_pid = try_pid + 1
        print(try_pid)

    new_pid = int(try_pid)  # set new_pid to be unique pid we found

    # create new playlist
    cursor.execute('''
        INSERT into playlists (pid, title, uid)
        VALUES (:p_pid, :p_title, :u_uid); ''', {'p_pid': new_pid, 'p_title' : play_title, 'u_uid': userID})

    # insert song into playlist. Since its a new playlist we make sorder = 1
    cursor.execute('''
        INSERT into plinclude (pid, sid, sorder)
        VALUES (:p_pid, :newsid, 1);''', {'p_pid': new_pid, 'newsid': songID})

    # get song title for output message
    cursor.execute('''
        SELECT s.title
        FROM songs s
        WHERE s.sid = :s_sid;
        ''', {'s_sid': songID})
    s_title_temp = cursor.fetchall()
    song_title = s_title_temp[0][0]

    # output success message
    print("Successfully created new playlist \""+play_title+"\" (ID: "+str(new_pid)+")")
    print("\""+song_title.title()+"\" was successfully added to: "+ play_title)

    return


'''
helper-function: add_to_playlist
to:	main-function: add_songs_playlist
Arguments: user ID, song ID
Returns: None
Functionality:
	Add a song to an existing playlist, getting the pID or playlist title from input
	and checking it is a valid playlist that the user created
''' 
def add_to_playlist(userID, songID): 
    # HELPER function to MAIN add_songs_playlist

    # get song title for output message
    cursor.execute('''
        SELECT s.title
        FROM songs s
        WHERE s.sid = :songsid;
        ''',{'songsid': songID})
    song_title_temp = cursor.fetchall()
    song_title = song_title_temp[0][0]

    # get inout from user, either playlist ID or playlist Title
    playlist_info = input("Please enter the Playlist Title OR Playlist ID that you wish to add \""+ song_title.title() +"\" to: ").lower()

    found = False   # False while input is not checked to be a valid pID or pTitle

    # check 1: check if user entered playlist ID, get playlist id and title if yes
    cursor.execute('''
        SELECT p.pid, p.title 
        FROM playlists p
        WHERE p.uid = :p_uid;
        ''',{'p_uid' : userID})

    all_user_pids = cursor.fetchall()

    for _pids in all_user_pids:
        if playlist_info == str((_pids[0])):
            play_pid = playlist_info
            play_title = _pids[1]
            found = True

    # check 2: check if user entered playlist title, get playlist id and title if yes
    if not found:
        cursor.execute('''
            SELECT p.title
            FROM playlists p
            WHERE p.uid = :p_uid;
            ''', {'p_uid': userID})

        all_ptitle = cursor.fetchall()

        for _title in all_ptitle:
            if playlist_info.lower() == (_title[0]).lower():
                play_title = playlist_info
                cursor.execute('''
                    SELECT p.pid
                    FROM playlists p
                    WHERE p.title LIKE :ptitle
                    AND p.uid = :p_uid;
                    ''', {'ptitle': play_title, 'p_uid': userID})

                play_pid_temp = cursor.fetchall()
                play_pid = play_pid_temp[0][0]
                found = True

    # failed check 1 & 2: not a valid input. Restart user at add_song_playlist to allow exit or re-input of playlist choice
    if not found:
        print("Could not find playlist under your user ID. Song addition to playlist was unsuccessful, please try again. ")
        add_song_playlist(songID, userID)

    # passed check 1 or 2: use found pID to add song to playlist
    else:

        # find s order or new addition, will be one plus size of the playlist, meaning we append the song to the back of the playlist
        cursor.execute('''
            SELECT pl.pid, pl.title, count(pli.sid)
            FROM playlists pl, plinclude pli
			WHERE pl.pid = :p_pid
            AND pl.pid = pli.pid
			GROUP BY pl.pid;
        ''',{'p_pid' : int(play_pid)})
        num_songs= cursor.fetchall()
        play_order = int(num_songs[0][2]) + 1

        # inset values into playlist
        cursor.execute('''
            INSERT into plinclude (pid, sid, sorder)
            VALUES (:newpid, :newsid, :newsorder);''', {'newpid': play_pid, 'newsid': songID, 'newsorder' : play_order})

        # print success message
        print("\""+song_title.title()+"\" was successfully added to: "+ play_title.title())


        # prompt user to ask if they would like to add another song -> return to song?playlist search page
        # if no, will return to home screen
        restart = input("Would you like to add another song to a playlist? (Y/N): ").lower()
        if restart == 'y' or restart == 'yes':
            print("Taking you back to Song and Playlist search page...")
            search_song_and_playlist(userID)
        else:
            pass
    return


'''
main-function: end_the_session
Arguments: user_name
Returns: None
Functionality: it will end the session for the user provided
'''   
def end_the_session(user_name): 
    # get the date at the end of the session
    end = time.strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute('''
                    UPDATE sessions 
                    SET end = :end
                    WHERE uid = :uid
                    AND end IS NULL;
                    ''', {'end': end, 'uid': user_name})

    connection.commit()

    return 

'''
main-function: end_the_session
Arguments: user_name
Returns: None
Functionality: it will end the session for all users with active sessions
'''  
def end_the_session_for_all_users(): 
    # end session for all users
    end = time.strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute('''
                    UPDATE sessions 
                    SET end = :end
                    WHERE end IS NULL;
                    ''', {'end': end})

    connection.commit()

    return 

'''
main-function: show_artist_songs
Arguments: aid, user_name
Returns: None
Functionality: it will allow the user to view the songs from an artist and select a song to perform 'song actions' with it
'''        
def show_artist_songs(aid, user_name):  
    # get all the songs from the artist and give the user the option to pick a song to listen to
    song_details_list = get_artist_songs(aid)

    results = song_details_list[0]

    song_names = song_details_list[1]

    length = len(results)

    range_of_options = range(0, length + 1)

    valid_options = []

    for i in range_of_options:
        valid_options.append(str(i))        

    decision_not_made = True

    while(decision_not_made):
        for i in results:
            print(i)

        print('(exit) Return to main menu')        
        decision = input("Which song would you like to select? Please input the respective number or 'exit' to return to the main menu: ").lower()

        if(decision in valid_options):
            choice_not_made = False
            play_song(song_names[int(decision) - 1], user_name)

        elif(decision == 'exit'):
            decision_not_made = False

        else:
            print('That was an invalid entry, please try again.')

    return

'''
sub-function: get_artist_songs
Arguments: sid, user_name
Returns: None
Functionality: it will get all the songs from an artist
'''   
def get_artist_songs(aid): 
    # query to get all artist songs:
    cursor.execute('''
    SELECT p.sid, s.title, s.duration
    FROM artists a, perform p, songs s
    WHERE p.aid = :aid
    AND p.sid = s.sid    
    AND a.aid = p.aid
    ORDER BY s.title ASC
    ''', {'aid': aid})
    details = cursor.fetchall()

    results = []

    song_sids = []

    i = 0

    for song in details:

        sid = details[i][0]
        title = details[i][1]
        duration = details[i][2]

        # creates format for each song in the playlist in a string
        results.append('(' + str(i + 1) + ') Song: ' + ' sid: ' + str(sid) + ' Title: ' + title + ' Duration: ' + str(duration))  

        song_sids.append(sid)

        i += 1

    return [results, song_sids]

'''
sub-function: compile_results
Arguments: user_name, items
Returns: None
Functionality: it will format the songs and playlists provided into the correct string format
'''  
def compile_results(user_name, items): 
    print('These are the results:')
    list_length = len(items)

    current_start = 0
    current_end = 5

    not_done = True

    results = []
    result_list = []

    result_number = 1

    for i in items:

        # if it's a song, get the sid, the title and the duration
        if (i[0] == 'song'):
            cursor.execute('''
            SELECT sid, title, duration
            FROM songs
            WHERE sid = :sid;
            ''', {'sid': i[1]})
            details = cursor.fetchall()

            sid = details[0][0]
            title = details[0][1]
            duration = details[0][2]

            result_list.append(['song', sid])

            results.append('(' + str(result_number) + ') Song: ' + ' sid: ' + str(sid) + ' Title: ' + title + ' Duration: ' + str(duration))

        # if it's a playlist, get the pid, the title and the total duration of all songs duration
        elif(i[0] == 'playlist'):
            cursor.execute('''
            SELECT p.pid, p.title, SUM(s.duration)
            FROM playlists p, songs s, plinclude pl
            WHERE p.pid = :pid
            AND pl.pid = p.pid
            AND pl.sid = s.sid
            GROUP BY p.pid;
            ''', {'pid': i[1]})
            details = cursor.fetchall()

            pid = details[0][0]
            title = details[0][1]
            duration = details[0][2]

            result_list.append(['playlist', pid])

            results.append('(' + str(result_number) + ') Playlist: ' + ' pid: ' + str(pid) + ' Title: ' + title + ' Total Duration of all Songs: ' + str(duration))           

        result_number += 1

    show_results(user_name, results, result_list)

    return

'''
sub-function: show_results
Arguments: user_name, results, result_list
Returns: None
Functionality: it will print the results previously compiled and allow the user to select a song or a playlist
'''  
def show_results(user_name, results, result_list): 

    length = len(results)

    total_pages = 1

    page_num_not_found = True

    range_of_options = range(0, length + 1)

    valid_options = []

    # gets all the valid options that we can select the song or playlist to be
    for i in range_of_options:
        valid_options.append(str(i))    

    # gets the number of page results
    while(page_num_not_found):

        if(length > total_pages * 5):
            total_pages += 1
        else:
            page_num_not_found = False

    not_done = True

    current_start = 0
    current_end = 5

    if(length == 0):
        print('No results were found.')
        return

    current_page = 1

    while(not_done):
        while((current_start < current_end) and (current_start < length)):
            print(results[current_start])
            current_start += 1

        if (current_end < length):
            print('(more) See more options\n(exit) Return to main menu')
            print('Page: ' + str(current_page) + '/' + str(total_pages))
            current_page += 1

        elif(current_start == length):
            print('(exit) Return to main menu\nPlease select one of the options from above')
            print('Page: ' + str(current_page) + '/' + str(total_pages))
            current_start += 1

        elif ((current_end >= length) and (length != 0)):
            print('(exit) Return to main menu\nNo more options, please select one of the options from above')

        decision = input('Your decision: ').lower()

        # see more results
        if(decision == 'more'):
            current_end += 5
        #exit
        elif(decision == 'exit'):
            not_done = False        


        elif(decision in valid_options):
            # get song/playlist title

            position = (int(decision) - 1)

            chosen = result_list[position]

            song_or_playlist_id = chosen[1]

            if(chosen[0] == 'song'):
                # chose to see more song details for that song
                not_done = False
                play_song(song_or_playlist_id, user_name)
                return
            if(chosen[0] == 'playlist'):
                # chose to see the songs in the chosen playlist
                not_done = False
                play_playlist(song_or_playlist_id, user_name)
                return

        elif(decision not in valid_options):
            print('Invalid decision, please try again.')

    return


'''
main-function: play_song
Arguments: sid, user_name
Returns: None
Functionality: it will allow the user to perform various activities related to a song
'''          
def play_song(sid, user_name):  

    choice = 0

    choice_not_made = True

    # gets the song title
    cursor.execute('''
    SELECT title
    FROM songs
    WHERE sid = :sid
    ''', {'sid': sid})  

    title = cursor.fetchone()[0]

    while(choice_not_made):
        print('What would you like to do?\nOptions:\n(1) Listen to ' + title + '\n(2) See more information about ' + title + '\n(3) Add ' + title + ' to a playlist\n(exit) Return to main menu')
        choice = input('Your decision: ').lower()        
        #Listen to the song
        if (choice == '1'):
            print('Listen to: ' + title)
            choice_not_made = False
            listen_to_song(sid, user_name)


        #See more information about the song, then ask if you want to listen to it
        elif (choice == '2'):
            print('See more information about ' + title)
            choice_not_made = False
            get_info_about_song(sid)


        #Add song to playlist
        elif (choice == '3'):
            print('Adding ' + title + ' to playlist')
            choice_not_made = False
            add_song_playlist(sid, user_name)


        #Return to main menu
        elif (choice == 'exit'):
            choice_not_made = False        


        elif(choice not in ('1', '2', '3', 'exit')):
            print('Invalid decision, please try again.')

    return

'''
main-function: listen_to_song
Arguments: sid, user_name
Returns: None
Functionality: it will allow the user to listen to a song during a session
'''     
def listen_to_song(sid, user_name):  
    # check if session has been started (there is a null in the end column), if not, start one
    cursor.execute('''
    SELECT IFNULL(MAX(sno), 'does not have an open session')
    FROM sessions
    WHERE uid = :uid
    AND end IS NULL
    ''', {'uid': user_name})    

    session_number = cursor.fetchone()[0]

    # create a new session if needed
    if(session_number == 'does not have an open session'):
        print('Starting New Session')
        start_a_session(user_name)

        cursor.execute('''
        SELECT sno
        FROM sessions
        WHERE uid = :uid
        AND end IS NULL
        ORDER BY sno DESC
        ''', {'uid': user_name})    

        session_number = cursor.fetchone()[0]

    cursor.execute('''
    SELECT COUNT(l.cnt)
    FROM listen l, sessions s
    WHERE l.uid = :uid
    AND l.sno = s.sno
    AND l.uid = s.uid
    AND l.sno = :sno
    AND l.sid = :sid
    AND s.end IS NULL
    ORDER BY s.sno DESC
    ''', {'uid': user_name, 'sno': session_number, 'sid': sid})   

    count = cursor.fetchone()[0]

    if (int(count) == 0):
        # has not been listened to 
        # add it to listen
        cursor.execute('''
        INSERT INTO listen (uid, sno, sid, cnt) VALUES
        (:uid, :sno, :sid, :cnt);''', {'uid': user_name,'sno': session_number,'sid': sid, 'cnt': 1})

    else:
        #has been listened to
        #update listen += 1
        cursor.execute('''
        UPDATE listen 
        SET uid = :uid, sno = :sno, sid =  :sid, cnt = cnt + 1
        WHERE uid = :uid
        AND sno = :sno
        AND sid = :sid;''', {'uid': user_name,'sno': session_number,'sid': sid})        

    connection.commit()
    return

'''
main-function: play_playlist
Arguments: pid, user_name
Returns: None
Functionality: it will allow the user to view the songs in a playlist and select a song to perform 'song actions' with it
'''        
def play_playlist(pid, user_name):      
    # get all the songs from the playlist and give the user the option to pick a song to listen to
    song_details_list = get_playlist_songs(pid)

    results = song_details_list[0]

    # all song titles
    song_names = song_details_list[1]

    length = len(results)

    range_of_options = range(0, length + 1)

    valid_options = []

    # valid song options the user can choose from
    for i in range_of_options:
        valid_options.append(str(i))        

    decision_not_made = True

    while(decision_not_made):
        for i in results:
            print(i)

        print('(exit) Return to main menu')        
        decision = input("Which song would you like to select? Please input the respective number or 'exit' to return to the main menu: ").lower()

        if(decision in valid_options):
            choice_not_made = False
            play_song(song_names[int(decision) - 1], user_name)

        elif(decision == 'exit'):
            decision_not_made = False

        else:
            print('That was an invalid entry, please try again.')

    return

'''
sub-function: get_playlist_songs
Arguments: sid, user_name
Returns: None
Functionality: it will get all the songs in a playlist
'''   
def get_playlist_songs(pid):      
    # query to get all playlist songs
    cursor.execute('''
    SELECT pl.sid, s.title, s.duration
    FROM playlists p, plinclude pl, songs s
    WHERE p.pid = :pid
    AND p.pid = pl.pid
    AND pl.sid = s.sid    
    ORDER BY pl.sorder ASC
    ''', {'pid': pid})
    details = cursor.fetchall()

    results = []

    song_sids = []

    i = 0

    for song in details:

        sid = details[i][0]
        title = details[i][1]
        duration = details[i][2]

        # creates format for each song in the playlist in a string
        results.append('(' + str(i + 1) + ') Song: ' + ' sid: ' + str(sid) + ' Title: ' + title + ' Duration: ' + str(duration))  

        song_sids.append(sid)

        i += 1

    return [results, song_sids]


'''
sub-function: search_for_keyword
Arguments: string
Returns: a the results of the query
Functionality: executes a query and returns the results
'''  
def search_for_keyword(string):      

    # finding all items
    cursor.execute(string)

    results = cursor.fetchall()

    return results


'''
sub-function: is_key_in_dict
Arguments: keyword, dictionary
Returns: True if the key is in the dictionary and False if it is not in the dictionary
Functionality: Checks if a key is in a dictionary or not
'''  
def is_key_in_dict(key, dictionary):      
    if key in dictionary.keys():
        return True
    else:
        return False


'''
main-function: start_a_session
Arguments: user_name
Returns: None
Functionality: it will start a valid session for the user provided
'''   
def start_a_session(user_name):      
    # get today's date
    today = time.strftime("%Y-%m-%d %H:%M:%S")

    # get current largest value for session number
    cursor.execute('''SELECT IFNULL(MAX(sno), 0) FROM sessions WHERE uid LIKE :uid;''', {'uid': user_name})
    max_session_number = cursor.fetchone()[0]

    if (max_session_number >= 1):
        unique_session_num = max_session_number + 1
    else:
        unique_session_num = 1

    cursor.execute('''INSERT INTO sessions (uid, sno, start, end) VALUES (:uid, :sno, :start_date, NULL);''', {'uid': user_name,'sno': unique_session_num,'start_date': today})

    connection.commit()

    return 

'''
main-function: login_artist
Arguments: artistID
Returns: None
Functionality:
	Login page for artists. Prompts for 3 choices, add a song, find top 3 fans, or exit.
	Sends to appropriate functions
'''      
def login_artist(artistID):         
    global connection, cursor

    print("Welcome Artist")

    choice = 'temp'

    # Prompt artist for what action they would like to do
    while choice != '0':    # 0 = exit condition
        print('What would you like to do? Please type the respective number corresponding to the action you want to perform: ')
        print('Options: \n(1) Add a song \n(2) Find your top 3 fans \n(3) Find top 3 playlists \n(0) Exit')
        choice = input('Your decision: ') 

        # Invalid choice
        while choice not in ('1', '2', '3', '0'):
            print('Invalid decision, please try again.')
            choice = input('Your decision: ') 

        # Add a song
        if (choice == '1'):
            print('Add a song')
            add_a_song(artistID)

        # Find top fans
        elif (choice == '2'):
            print('Searching for top fans')
            find_top_fans(artistID)

        # Find top playlists
        elif (choice == '3'):
            print('Searching for top playlists')
            find_top_playlists(artistID)  

    #End the session 
    print('Exiting...\nGoodbye') 
    return

'''
main-function: add_a_song
Arguments: artist ID
Returns: None
Functionality:
	Artists can add a song by providing a title and a duration. The system checks if the artists already has a song with the same title and duration. 
	If not, the song is added with a unique id and along with any additional artist who may have performed the song with their ids obtained from input.
''' 
def add_a_song(artistID):         
    # MAIN add_a_song

    # get title (string)
    title = input("Enter the title: ").lower()
    # get duration (int = seconds)
    while True:
        try:
            duration = int(input("Enter the duration in seconds: "))
            break
        except ValueError:
            print('Please enter a number.')

    # check if artists already has the same song title and duration
    song_exists = check_song_exists(artistID, title, duration)

    if (song_exists == True): # do not allow addition of song with existing name and duration
        print("A song with the same title and duration already exists under your artist ID. Unable to add song")
    else:
        valid = False
        while not valid: # take input until valid one given
            extra = input("Do any other artists perform the song with you? Y/N ").lower()

            #  assess song with multiple artists
            if extra == 'y' or extra == 'yes': 
                valid = True
                add_song_mul_artists(artistID, title, duration)

            # if artistID is the only performer
            elif extra == 'n' or extra == 'no':
                valid = True

                # find unused sid to assign to song
                new_sid = find_unique_sid()

                # add song to database
                update_add_song(artistID, title, duration, new_sid)
                print("New song added successfully to your account.") 

            else:
                print("Please enter only Y or N")


    # ask user if they want to add another song
    repeat_func = input("Would you like to add another song? Y/N ").lower()
    if repeat_func == 'y':
        add_a_song(artistID)
    else:
        return

'''
helper-function: add_song_mul_artists
to: 	main-function: add_a_song
Arguments: artist ID, song title, song duration
Returns: None
Functionality:
	will assess the case where multiple artists perform the song to be added
	checks if ID's entered from input are valid, if the song already exists, and updates
	database respectively when all checks pass
'''    
def add_song_mul_artists(artistID, title, duration):         
    # HELPER function to MAIN add_a_song

    extra_artists = input("Please list their artists IDs (separating each ID with a space): ").split()
    song_exists = False
    check_artist = False

    # Check if valid artists entered
    for ex_aid in extra_artists:
        if ex_aid == artistID:
            print("Cannot input your own artist ID. Song addition was not successful, please try again.")
            break
        else:
            check_artist = check_if_artist(ex_aid) function to see if an artists exists given aid

            if check_artist == True: 
                pass
            else:
                print(ex_aid + " is not a valid ID. Song addition was not successful, please try again.")
                break

    if check_artist == True:
        for ex_aid in extra_artists:
            # Check if the extra artists already performs this song with the same title and duration
            artist_sings = check_song_exists(ex_aid, title, duration)

            # If the song exists and is performed by this artist, retrieve existing sid
            if (artist_sings == True):
                song_exists = True
                # get sid
                cursor.execute(''' 
                SELECT s.sid
                FROM songs s
                WHERE (s.title LIKE :stitle)
                AND (s.duration = :sduration);
                ''', {'stitle' : title, 'sduration' : duration})
                temp_sid = cursor.fetchall()
                new_sid = temp_sid[0][0]

            else:  
                # if the song exists but this artist does not perform it        
                if song_exists == True:    
                    # update database to add artists under a performer of this song  
                    update_add_perform(ex_aid, new_sid)
                # if the song does not exist
                else:
                    # find unused sid and create new song with given user
                    song_exists = True
                    new_sid = find_unique_sid()
                    update_add_song(ex_aid, title, duration, new_sid)

        update_add_perform(artistID, new_sid)
        print("New song added successfully to all artists.") 

    return

'''
helper-function: update_add_song
to: 	main-function: add_a_song
Arguments: artist ID, song title, song duration, new song ID
Returns: None
Functionality:
	updates songs and perform tables to add a new song given an artist id that performs it
''' 
def update_add_song(a_aid, title, duration, new_sid):         
    # HELPER function to MAIN add_a_song

    # add new song
    cursor.execute('''
        INSERT into songs (sid, title, duration)
        VALUES (:newsid, :newtitle, :newduration);''', {'newsid': new_sid, 'newtitle': title, 'newduration' : duration})

    # make artist perform this song
    cursor.execute('''
        INSERT into perform (aid, sid)
        VALUES (:a_aid, :newsid);''', {'a_aid': a_aid, 'newsid': new_sid})

    return


'''
helper-function: update_add_perform
to: 	main-function: add_a_song
Arguments: artist ID, song ID
Returns: None
Functionality:
	updates perform table to include given artist ID that performs it with an existing song 
''' 
def update_add_perform(a_aid, new_sid):         
    # HELPER function to MAIN add_a_song

    # make artist perform this song
    cursor.execute('''
        INSERT into perform (aid, sid)
        VALUES (:a_aid, :newsid);''', {'a_aid': a_aid, 'newsid': new_sid})
    return


'''
helper-function: check_song_exists
to: 	main-function: add_a_song
Arguments: artist ID, song title, song duration
Returns: True if song exists by artist, False otherwise
Functionality:
	checks if given artists performs a song with given title and duration
	returns true if yes, false otherwise
''' 
def check_song_exists(a_aid, title, duration):         
    # HELPER function to MAIN add_a_song

    cursor.execute('''
        SELECT s.title
        FROM songs s, perform p
        WHERE (p.aid = :artid)
        AND (p.sid = s.sid)
        AND (s.title LIKE :stitle)
        AND (s.duration = :sduration);
        ''', {'artid' : a_aid, 'stitle' : title, 'sduration' : duration})

    song_exist_list = cursor.fetchall()

    if len(song_exist_list)>0:
        song_exists = True
    else:
        song_exists = False

    return song_exists

'''
helper-function: find_unique_sid
to:	main-function: add_a_song
Arguments: None
Returns: a unique sid (int)
Functionality:
	Fins a unique, unused sID in the database and returns it
''' 
def find_unique_sid():          
    # HELPER function to MAIN add_a_song
    # find unique sID: Assuming best algorithm, next availble sID will be one plus the number of songs
    # (meaning sIDs increase by 1 uniformally when a new song is added).
    # In worse scenario, sIDs are random, in this case we chose the starting point to be one plus the number of songs
    # and increment by 1 until we find a sID that is not in use

    # find number of songs
    cursor.execute('''
        SELECT count(s.sid)
        FROM songs s;
    ''')
    sid_count_temp = cursor.fetchall()
    sid_count = sid_count_temp[0][0]
    try_sid = sid_count + 1 # one plus number of songs. Will be new sID in best case

    # find and append all existing sids to list
    cursor.execute('''
        SELECT s.sid
        FROM songs s;
    ''')
    sid_list_temp = cursor.fetchall()
    sid_list = []
    for _sid in sid_list_temp:
        sid_list.append(_sid[0])

    # increment test sid until it is unique 
    while try_sid in sid_list:
        try_sid = try_sid + 1

    new_sid = int(try_sid)  # set new_sid to be unqie sid we found

    return new_sid


'''
main-function: find_top_fans
Arguments: artist ID
Returns: None
Functionality:
	Find top fans. The artist is able to list top 3 users who listen to their songs the longest time 
	If there are less than 3 such users, fewer number of users will be printed. 
''' 
def find_top_fans(artistID):          
    # MAIN find_top_sings

    # find all users who listen to artist, order by time listened descending 
    cursor.execute('''
        SELECT u.uid, a.aid, sum(l.cnt) as time_listened
        FROM songs s, perform p, artists a, listen l, users u, sessions s
        WHERE a.aid = :a_aid
        AND a.aid = p.aid 
        AND p.sid = s.sid
        AND s.sid = l.sid 
        AND l.sno = s.sno 
        AND s.uid = u.uid
        GROUP BY u.uid, a.aid
        ORDER BY time_listened DESC; 
        ''', {'a_aid': artistID})

    # list of top fans in format (uid, artistID, time listened)
    top_fans = cursor.fetchall()

    # send info to helper function find_top_three() to find top 3 fans
    str1 = "You have no listeners. Get users to listen to your songs to see your top fans here."
    str2 = " fans and the amount of time they listened to you are: "
    _type = "user"
    find_top_three(top_fans, str1, str2, _type)

    return


'''
main-function: find_top_playlists
Arguments: artist ID
Returns: None
Functionality:
	Find top playlists. The artist is able to list top 3 playlists that include the largest number of their songs.
	If there are less than 3 such playlists, fewer number of playlists will be printed. 
''' 
def find_top_playlists(artistID):         
    # MAIN find_top_playlists

    # find all playlists that include artist, order by number of times their song is included in playlist descending
    cursor.execute('''    
        SELECT pl.title, a.aid, count(DISTINCT pli.sid) as times_included
        FROM artists a, songs s, perform p, playlists pl, plinclude pli
        WHERE a.aid = :a_aid
        AND a.aid = p.aid 
        AND p.sid = s.sid
        AND s.sid = pli.sid
        AND pli.pid = pl.pid
        GROUP BY pl.title, a.aid
        ORDER BY a.aid, times_included DESC;
        ''', {'a_aid': artistID})

    # list of all top playlists in format (pid, artistID, title)
    playlist_info = cursor.fetchall()

    # send info to helper function find_top_three() to find top 3 playlists
    str1 = "You are not included in any playlists. Become a user and make a playlist to change that!"
    str2 = " playlists titles and the number of times you are included in each is:"
    _type = 'playlist'

    find_top_three(playlist_info, str1, str2, _type)

    return



'''
helper-function: find_top_three
to:	main-function: find_top_playlists
and	main-function: find_top_fans
Arguments: list_info (list of information to print), str1, str2, _type
Returns: None
Functionality:
	Prints top 3 values, or less if three values does not exists, of given list with 
	information on either top playlist or users, which is it's identified in the _type parameter 
	Outputs top 3 with help of strings from input based on _type
''' 
def find_top_three(list_info, str1, str2, _type): #Vera
    # HELPER function to MAIN find_top_fans and MAIN find_top_playlists

    info_exists = True
    # if there is no information in the list, the artist does not have any users/playlist (dept on _type)
    if len(list_info) == 0:
        print(str1)
        info_exists = False
    # if three values do not exists, take maximum amount less than 3 to print
    elif len(list_info) < 3:
        top_amount = len(list_info)
    # if more than 3 values exist, we ill present the top 3
    else:
        top_amount = 3

    # if we found values of users/playlists
    if info_exists:
        i = 0
        top_three = [] 
        # append to list values of either:
        # (uid, time_listened) if _type = 'user'
        # (playlist_title, times_included) if _type = 'playlist'
        while i <= (top_amount-1):
            top_three.append(list_info[i][0])
            top_three.append(list_info[i][2])
            i = i+1

        # print top 3 (or less) results in appropriate format
        j=0
        place = 1
        top_limit = (i*2) - 1
        print("Your top " + str(top_amount) + str2)
        while j<=top_limit:
            print(str(place) +". ", end ='')
            if _type == "playlist":
                print("{:20s} {:.0f}".format(top_three[j], top_three[j+1]))
            elif _type == "user":
                print("{:10s} {:.2f}".format(top_three[j], top_three[j+1]))
            j = j+2
            place = place + 1

    return

def main():
    global connection, cursor

    database_name = str(sys.argv[1])

    path = './' + database_name

    connect(path)

    # login the user
    login_page()

    connection.commit()
    connection.close()
    return

if __name__ == "__main__":
    main()