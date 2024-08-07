from pypresence import Presence
import glob, urllib, requests, json, os, time, win32gui, random

# Set this to your own client id from Discord developer portal
clientId = "1155101158780702830"

# Dont touch something below here unless you tryna do something or modify

updatable = True
redo = False

def consoleLog(out):
    print("[Console] :: {}".format(out))

def find_between(s, first, last):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""
    
def getUser():
    return os.environ['USERPROFILE'].replace("C:\\Users\\", "")
    
def getCacheLog():
    list_of_files = glob.glob("C:\\Users\\" + getUser() + "\\AppData\\Local\\Roblox\\logs" + "\*.log")
    latest_file = max(list_of_files, key=os.path.getctime)
    fin = open(latest_file, "r", encoding = "ISO-8859-1")
    return fin

consoleLog("Starting Client")
consoleLog("Waiting for Discord network...")

RPC = Presence(clientId)
RPC.connect()
connected = True

consoleLog("Connected to Discord network!")

lastLogFile = None
lastJobid = 0

while True:
    if win32gui.FindWindow(None, "Roblox"):
        updatable = True

        logFile = getCacheLog()

        if lastLogFile != logFile:
            lastLogFile = logFile

            placeId = 0
            jobId = 0
            serverIp = 0
            usrId = 1
            isPrivate = False
            
            for line in logFile:
                if line.find("place") > 0:
                    toReplace = find_between(line, 'place ', " at")
                    if toReplace != "":
                        placeId = toReplace

                if line.find("Joining game") > 0:
                    toReplace = find_between(line, "Joining game '", "'")
                    if toReplace != "":
                        jobId = toReplace
            
                if line.find("UDMUX") > 0:
                    toReplace = find_between(line, "UDMUX server ", ",")
                    if toReplace != "":
                        serverIp = toReplace.split(":")
            
                if line.find("userid") > 0:
                    toReplace = find_between(line, "userid:", ",")
                    if toReplace != "":
                        usrId = toReplace

                if line.find("joinGamePostPrivateServer") > 0:
                    isPrivate = True

            if placeId and jobId:
                if redo or lastJobid != jobId:
                    universalId = urllib.request.urlopen("https://apis.roblox.com/universes/v1/places/" + placeId + "/universe")
                    universalData = json.loads(universalId.read())
                    theId = universalData["universeId"]

                    lastJobid = jobId
                    redo = False

                    if theId:
                        print(universalData, jobId)
                        
                        response = urllib.request.urlopen("https://games.roblox.com/v1/games?universeIds=" + str(theId))
                        data = json.loads(response.read())

                        responsePlayer = urllib.request.urlopen("https://users.roblox.com/v1/users/" + str(usrId))
                        dataPlayer = json.loads(responsePlayer.read())

                        responeIcon = urllib.request.urlopen("https://thumbnails.roblox.com/v1/games/icons?universeIds=" + str(theId) + "&size=512x512&format=Png&isCircular=false")
                        dataIcon = json.loads(responeIcon.read())

                        responePfp = urllib.request.urlopen("https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds=" + str(usrId) + "&size=48x48&format=Png&isCircular=false")
                        dataPfp = json.loads(responePfp.read())

                        gameIcon = dataIcon["data"][0]["imageUrl"]
                        pfpIcon = dataPfp["data"][0]["imageUrl"]

                        if isPrivate:
                            RPC.update(
                                large_image= gameIcon,
                                small_image= "https://blog.roblox.com/wp-content/uploads/2022/08/RBLX_Logo_Launch_Wordmark.png",
                                small_text= "Protected",
                                large_text= data["data"][0]["name"],
                                details= data["data"][0]["name"],
                                state= "Reversed server",
                                start= int(time.time()),
                                buttons= [{"label": "View on website" ,"url": "https://www.roblox.com/games/" + placeId + "/"}]
                            )
                        else:
                            RPC.update(
                                large_image= gameIcon,
                                small_image= pfpIcon,
                                small_text= dataPlayer["name"],
                                large_text= data["data"][0]["name"],
                                details= data["data"][0]["name"],
                                state= "By " + data["data"][0]["creator"]["name"],
                                start= int(time.time()),
                                buttons= [{"label": "View on website" ,"url": "https://www.roblox.com/games/" + placeId + "/"}]
                            )
                            # if you want to show a Join Server button use this
                            
                            '''
                            RPC.update(
                                large_image= gameIcon,
                                small_image= pfpIcon,
                                small_text= dataPlayer["name"],
                                large_text= data["data"][0]["name"],
                                details= data["data"][0]["name"],
                                state= "By " + data["data"][0]["creator"]["name"],
                                start= int(time.time()),
                                buttons= [{"label": "Join server" ,"url": "roblox://experiences/start?placeId=" + placeId + "&gameInstanceId=" + jobId}, {"label": "View on website" ,"url": "https://www.roblox.com/games/" + placeId + "/"}]
                            )
                            '''
    else:
        redo = True

        if updatable:
            RPC.update(
                large_image= "https://blog.roblox.com/wp-content/uploads/2022/08/RBLX_Logo_Launch_Wordmark.png",
                details= "Idle in Client",
                start= int(time.time()),
            )

            updatable = False
            
    time.sleep(5)
