import requests
import base64
from datetime import datetime
import json
import yaml
from PIL import Image
import tkinter
import tkinter.font as font
import tkinter
import time
from datetime import datetime
from tkinter import filedialog


FMT = "%Y-%m-%d %H:%M:%S"

class Requester:

    def __init__(self, lol_location):

        self.location = lol_location

        self.port = None
        self.password = None
        self.process_id = None

        self.root_url = None
        self.host = None
        self.encoded_auth = None
        self.auth = None
        self.accept = "application/json"
        self.content_type = "application/json"

    def GetLockFileData(self):

        file = open(self.location + "\\lockfile", "r")
        fileData = file.read()
        file.close()
        fileData = fileData.split(":")
        self.RedefineAttributs(fileData)

    def GetInstantTime(self):

        now = datetime.now()
        return(now)

    def RedefineAttributs(self, dataList):

        self.port = dataList[2]
        self.password = dataList[3]
        self.process_id = dataList[1]

        self.root_url = "https://127.0.0.1:" + self.port
        self.host = "127.0.0.1:" + self.port

        combination = "riot:" + self.password
        bytes_enc = combination.encode("ascii")
        b64byte = base64.b64encode(bytes_enc)
        self.encoded_auth = b64byte.decode("ascii")
        self.auth = "Basic " + self.encoded_auth


    def MakeGetRequest(self, url):

        if self.root_url != None :
            
            headers = {
                "Host": self.host,
                "Authorization": self.auth,
                "Accept": self.accept,
            }

            prepared_url = self.root_url + url


            try:
                requests.packages.urllib3.disable_warnings()

            except Exception as e:
                responseString+=str(e)

            resp = requests.get(prepared_url, headers=headers, verify=False)

            return(resp.json())

        
    def MakePostRequest(self, url, data):

            if self.root_url != None :

                
                headers = {
                    "Host": self.host,
                    "Authorization": self.auth,
                    "Accept": self.accept,
                }

                prepared_url = self.root_url + url

                try:
                    requests.packages.urllib3.disable_warnings()
                    resp = requests.post(prepared_url, headers=headers, data=data, verify=False)

                    return(resp.json())

                except Exception as e:

                    return(str(e))

def reportSumm():

    global summEntry

    summName = summEntry.get()

    with open("config/conf.yaml", "r") as conf:
        confData = yaml.safe_load(conf)
        leaguePath = confData["leaguePath"]

    try:

        Request3r = Requester(leaguePath)
        Request3r.GetLockFileData()
    except:
        errorLabel.configure(text="[Error] League may be not started or wrong path.")
        return()

    summData = Request3r.MakeGetRequest("/lol-summoner/v1/summoners?name=" + summName)

    summId = summData["accountId"]
    summPuuid = summData["puuid"]


    matchHistory = Request3r.MakeGetRequest("/lol-match-history/v1/products/lol/" + summPuuid + "/matches")
    maxDeath = 0
    gameId = None

    for d in matchHistory["games"]["games"]:
        for i in d["participants"]:
            if i["stats"]["deaths"] > maxDeath:
                maxDeath = i["stats"]["deaths"]
                gameId = d["gameId"]


    reportObject = {
        "comment": """Full inter, full hater. He said that I was a "fucking monkey" and just spam ping. More than that, he's a HUGE inter. How can he still play League ?!""",
        "gameId": gameId,
        "offense": "Negative Attitude, Verbal Abuse, Intentional Feeding",
        "reportedSummonerId": summId
    }

    report = Request3r.MakePostRequest("/lol-end-of-game/v2/player-complaints", data=json.dumps(reportObject))
    if report["httpStatus"] == 403:
        if report["message"] == "Account was already reported.":
            errorLabel.configure(text=report["message"] + " Please wait one hour.")
        else:
            errorLabel.configure(text=report["message"])

    elif report["httpStatus"] == 200:

        errorLabel.configure(text="Account reported.")

        with open("config/conf.yaml", "r") as conf:
            confData = yaml.safe_load(conf)

            now = datetime.now()
            confData["lastReport"] = datetime.strftime(now, FMT)

        with open("config/conf.yaml", "w") as conf:
            yaml.dump(confData, conf)


def configPath():

    folder_selected = filedialog.askdirectory()
    with open("config/conf.yaml", "r") as conf:
        confData = yaml.safe_load(conf)

        confData["leaguePath"] = folder_selected

    with open("config/conf.yaml", "w") as conf:
        yaml.dump(confData, conf)

    errorLabel.configure(text="League Path modified.")
    


app = tkinter.Tk()
app.geometry("400x300")
app.title("leagueReap3r")
app.maxsize(400, 300)
app.minsize(400, 300)
app.iconbitmap("src/img/reaperICO.ico")
police = font.Font(family='Courier', size=10)

img = tkinter.PhotoImage(file="src/img/background.png")
bg = tkinter.Label(app,image=img)
bg.place(x=-2, y=-1)


with open("config/conf.yaml", "r") as conf:
    confData = yaml.safe_load(conf)

    lastReport = confData["lastReport"]

tdelta = datetime.now() - datetime.strptime(lastReport, FMT)
lastReportLabel = tkinter.Label(app, text="Time since last report : " + str(tdelta), background="black", fg="white")
lastReportLabel.place(x=10, y=100)
lastReportLabel['font'] = font.Font(family='Courier', size=9)

summLabel = tkinter.Label(app, text="Summoner name:", background="black", fg="white")
summLabel.place(x=17, y=155)
summLabel['font'] = font.Font(family='Courier', size=11)

summEntry = tkinter.Entry(app)
summEntry.place(x=20, y=180)

reportButton = tkinter.Button(app, text="rep0rt", command=reportSumm)
reportButton.place(x=155, y=175)
reportButton['font'] = police

errorLabel = tkinter.Label(app, text="", background="black", fg="white")
errorLabel.place(x=10, y=220)
errorLabel['font'] = font.Font(family='Courier', size=9)

configLeaguePath = tkinter.Button(app, text="config League path", command=configPath)
configLeaguePath.place(x=254, y=270)
configLeaguePath['font'] = font.Font(family='Courier', size=8)

author = tkinter.Label(app, text="by akira :)", background="black", fg="white")
author.place(x=10, y=280)
author['font'] = font.Font(family='Courier', size=8)



app.mainloop()
