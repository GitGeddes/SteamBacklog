# SteamBacklog

Using the Steam Web API and HowLongToBeat.com, pick a random game to finish and a random game to begin.

#### You need to modify settings.json and add your own Steam API key, your Steam Community ID number, and your Steam Username
Your Steam username can be anything that works with the HowLongToBeat link below.
*Also, your games library needs to be public on Steam for this script to work.*

**[Go to this link to get your Steam API Key.](https://steamcommunity.com/dev/apikey)**
If you don't have a domain, use "_172.0.0.1_" and run this script on your local machine.

[Where I'm querying the Steam Web API](http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=XXXXX&steamid=XXXXX&include_appinfo=1&format=json) (Must modify link with your credentials)

[Where I'm getting HowLongToBeat's data](https://howlongtobeat.com/steam.php)

If you have played a game for a longer amount of time than HowLongToBeat thinks it takes to beat, then this script will not suggest that game. If you've played it that long, you've probably beaten that game. This isn't always right, so keep that in mind.

If you have beaten a game on Steam but you have beaten it in a shorter amount of time than on HowLongToBeat, then this script will think you haven't beaten the game. So if you are suggested a game you've already beaten, just run it again. For example, I have 100% FEZ but it still gets suggested to finish.

HowLongToBeat is not completely accurate. For example, it thinks that PlayerUnknown's BattleGrounds can be beaten, when it's a completely multiplayer game with no story. So games that can't be "beaten" in the traditional sense might be suggested by this script. This is HowLongToBeat's fault, not the script.
