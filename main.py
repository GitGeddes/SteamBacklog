from bs4 import BeautifulSoup as bs
import json
import mechanize
import random
import requests

PRETTY_PRINT = False
REQUEST_HLTB = False
with open('settings.json') as f:
    data = json.load(f)
    API_KEY = data['API_KEY']
    STEAM_ID = data['STEAM_ID']
    USERNAME = data['USERNAME']

# Query the Steam Web API for the list of owned games given an API key and a Steam ID
def getOwnedGames(apiKey, steamID):
    response = requests.get('http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key='+apiKey+'&steamid='+steamID+'&include_appinfo=1&format=json')
    response = response.json()['response']

    # Sort games list by appid
    response['games'] = sorted(response['games'], key=lambda k: k['appid'])

    gameNames = []
    for game in response['games']:
        # Convert from unicode strings to regular strings
        gameNames.append(game['name'].encode('utf-8'))

    # Pretty print
    if PRETTY_PRINT:
        print(json.dumps(response['games'], indent=2, sort_keys=True))
    return response, gameNames


# Fill out the php form on HowLongToBeat given a Steam username and return the html response
def getHowLongToBeatHTML(username):
    # Fake browser
    br = mechanize.Browser()

    # Make website think I'm not a bot
    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

    # Browser variables
    br.set_handle_equiv(True)
    br.set_handle_gzip(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(True)

    # Open URL
    # BROKEN
    br.open('https://howlongtobeat.com/steam.php')

    # Select the username field (index 0 is the search bar)
    br.select_form(nr=1)

    # Set the username
    br.form.controls[0]._value = username

    # Submit the form and get the response
    response = br.submit()

    # Pretty print (breaks parseTable, but it looks nice)
    # print bs(response.read(), 'html.parser').prettify()
    return response.read()


# Parse the html from HowLongToBeat and extract the table of games and times to beat them
def parseTable(html):
    soup = bs(html, 'html5lib')

    table = soup.findAll('table')[0]  # Get the first table on the page

    parsedTable = {}
    # Parse through rows excluding header and footer
    for row in table.findAll('tr')[1:-2]:
        # Get all table values
        parsedRow = [td.get_text().encode('utf-8') for td in row.findAll('td')]
        # Remove space from end of time field
        parsedRow[1] = parsedRow[1][:-1]
        parsedTable[parsedRow[0]] = parsedRow[1]

    # Pretty print
    if PRETTY_PRINT:
        for key in parsedTable.keys():
            print("{0:<70} {1}".format(key, parsedTable[key]))

    return parsedTable


# Convert games list from SteamAPI response to just game names and total playtime
def gamesToPlaytime(data):
    started, unstarted = {}, {}
    sum = 0

    for game in data['games']:
        if game['playtime_forever'] > 0:
            # I have at least 1 minute tracked on Steam
            started[game['name'].encode('utf-8')] = game['playtime_forever']
            sum += game['playtime_forever']
        else:
            # I have never launched this game
            unstarted[game['name'].encode('utf-8')] = game['playtime_forever']

    return started, unstarted, sum


# Convert "##h ##m" to minutes
def hltbTimeToMinutes(table):
    for key in table.keys():
        if table[key] == '--':
            # HowLongToBeat either considers this game unbeatable or doesn't have data
            table[key] = -1
        else:
            minutes = 0
            firstNum = 0
            secondNum = 0
            for char in table[key]:
                if char == ' ' or char == '-' or (char.isdigit() and int(char) == 0):
                    continue  # Ignore spaces, hyphens, and zeros
                elif minutes == 0:
                    if char == 'h':
                        minutes += 60 * firstNum
                    elif char == 'm':
                        minutes += firstNum
                    elif firstNum > 0:
                        firstNum *= 10
                        firstNum += int(char)
                    else:
                        firstNum += int(char)
                else:
                    if char == 'm':
                        minutes += secondNum
                    elif secondNum > 0:
                        secondNum *= 10
                        secondNum += int(char)
                    else:
                        secondNum += int(char)
            # End for
            table[key] = minutes
        # End else

    return table


# Select a random game that I've already started and haven't beaten
def selectRandomStartedGame(playTime, hoursLeft):
    # Remove games from list based on HowLongToBeat data
    for gameName in hoursLeft.keys():
        # HLTB deems this game unbeatable (multi-player, infinite runner, etc.)
        if hoursLeft[gameName] == -1:
            playTime.pop(gameName, None)

        # I've played this game longer than HLTB says it takes to beat, so presumably I've beaten it
        if gameName in playTime and playTime[gameName] > hoursLeft[gameName]:
            playTime.pop(gameName)

    print("Finish a game!\t\t", random.choice(list(playTime)))
    return


# Select a random game that I haven't started before
def selectRandomUnstartedGame(playTime, hoursLeft):
    # Remove games that HowLongToBeat deems unbeatable or doesn't have data
    for gameName in hoursLeft.keys():
        if hoursLeft[gameName] == -1:
            playTime.pop(gameName, None)

    print("Play a new game!\t", random.choice(list(playTime)))
    return


def printPlaytime(time: int):
    minutes = time % 60
    hours = round(time / 60) % 24
    days = round(time / 60 / 24)

    print("All playtime:", days, "days", hours, "hours", minutes, "minutes")


def main():
    steamGames, gameNames = getOwnedGames(API_KEY, STEAM_ID)

    started, unstarted, sum = gamesToPlaytime(steamGames)
    printPlaytime(sum)

    if REQUEST_HLTB:
        hoursLeft = hltbTimeToMinutes(parseTable(getHowLongToBeatHTML(USERNAME)))

        selectRandomStartedGame(started, hoursLeft)
        print  # Add an extra line
        selectRandomUnstartedGame(unstarted, hoursLeft)


main()
