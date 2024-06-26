print("Starting script")
from cryptography.fernet import Fernet
import base64
import sys
import asyncio
import aiohttp # type: ignore
import json
import requests
import shutil
import random
from pdf2docx import Converter
from PyQt5.QtWidgets import QLabel as OriginalQLabel
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QMessageBox, QLineEdit, QHBoxLayout, QGroupBox, QCheckBox, QGridLayout, QScrollArea, QTabWidget, QToolButton, QSizePolicy, QGraphicsDropShadowEffect, QDesktopWidget
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QPixmap, QIcon, QCursor, QDesktopServices
import os
import platform
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import re
from pyppeteer import launch # type: ignore
from PIL import Image
from collections import Counter






class QLabel(OriginalQLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.setCursor(QCursor(Qt.IBeamCursor))  # Set the cursor to I-beam






global id_token, currentUser, asyncioLock, family_id, person_id, thisYear

asyncioLock = asyncio.Lock()

id_token = ""
currentUser = ""

if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app 
    # path into variable _MEIPASS.
    application_path = sys._MEIPASS
    executable_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    executable_path = application_path


unaltering_script_dir = os.path.join(application_path, 'resources')
unaltering_parent_dir = application_path
print(unaltering_parent_dir)
altering_script_dir = os.path.join(executable_path, 'resources')

altering_parent_dir = executable_path


family_id = ""
person_id = ""
thisYear = ""

roman_to_arabic = {
        'I': '1', 'II': '2', 'III': '3', 'IV': '4',
        'V': '5', 'VI': '6', 'VII': '7', 'VIII': '8',
        'IX': '9', 'X': '10', 'XI': '11', 'XII': '12'
    }

donate_link = "https://www.paypal.com/donate/?business=PPEAYUTVL35VC&no_recurring=0&item_name=Most+people+suggested+%241.50+a+month.+For+Ballot+Reader+to+be+self-sustaining+it+needs+%2420%2B+monthly+%28combined%29.&currency_code=USD"


key = b'd4qUOLC1eyfetbfIOHcqgvt3x7gt846CGkmvk0iZ9bM='
crypt = Fernet(key)

def encrypt(password):
    password = str(password).strip()
    encrypted_password = crypt.encrypt(password.encode())
    encoded_encrypted_password = base64.b64encode(encrypted_password).decode()
    return encoded_encrypted_password
def decrypt(wtf):
    encrypted_password = base64.b64decode(wtf)
    password = crypt.decrypt(encrypted_password).decode()
    return password

print("Checking your OS system to determine if we should use windows' chromium or linux' chromium.")
if platform.system() == "Windows":
    import requests
    chrome_path = os.path.join(unaltering_script_dir, 'chrome-win', 'chrome.exe')
elif platform.system() == 'Darwin':
    import certifi
    import ssl
    import stat
    STAT_0o775 = ( stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR
             | stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP
             | stat.S_IROTH |                stat.S_IXOTH )
    openssl_dir, openssl_cafile = os.path.split(
        ssl.get_default_verify_paths().openssl_cafile)
    os.chdir(openssl_dir)
    relpath_to_certifi_cafile = os.path.relpath(certifi.where())
    try:
        os.remove(openssl_cafile)
    except FileNotFoundError:
        pass
    os.symlink(relpath_to_certifi_cafile, openssl_cafile)
    os.chmod(openssl_cafile, STAT_0o775)
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    aiohttp.connector.TCPConnector.ssl = ssl_context
    chrome_path = os.path.join(unaltering_script_dir, 'chrome-mac', 'Chromium.app', 'Contents', 'MacOS', 'Chromium')
else:
    import requests
    chrome_path = os.path.join(unaltering_script_dir, 'chrome-linux', 'chrome')

print("Loading settings file...")


config = None
try:
    with open(os.path.join(altering_script_dir, 'data', 'settings.json'), 'r') as file:
        config = json.load(file)
        
        print("Config loaded!")
except FileNotFoundError:
    print("The configuration file was not found.")
except json.JSONDecodeError:
    print("The configuration file is not in valid JSON format.")
except Exception as e:
    print(f"An error occurred: {e}")
    
print("Loading savedBallots file...")
savedBallots = None
try:
    with open(os.path.join(altering_script_dir, 'data', 'savedBallots.json'), 'r') as file:
        savedBallots = json.load(file)
except FileNotFoundError:
    print("The savedBallots file was not found.")
except json.JSONDecodeError:
    print("The savedBallots file is not in valid JSON format.")
except Exception as e:
    print(f"An error occurred: {e}")
    
print("Loading helpPage file...")
helpPage = None
try:
    with open(os.path.join(altering_script_dir, 'helpPage.html'), 'r') as file:
        helpPage = file.read()
except FileNotFoundError:
    print("The helpPage file was not found.")
except Exception as e:
    print(f"An error occurred: {e}")
    


print("Saving paths to resources...")
saveddocsPath = os.path.join(altering_script_dir, "saveddocs")
savedpdfsPath = os.path.join(altering_script_dir, "savedpdfs")
savedjsonsPath = os.path.join(altering_script_dir, "savedjsons")
previewimagesPath = os.path.join(altering_script_dir, "previewimages")


class fetchInfo(QThread):
    finished = pyqtSignal(list)
    error_occurred = pyqtSignal(str)  # Signal to emit error message
    status_update = pyqtSignal(str)

    def __init__(self, email, password, year, refresh):
        super().__init__()
        self.email = email
        self.password = password
        self.year = year if year else None
        self.refresh = refresh
        print("Set self.year in fetchInfo init to ", self.year)
        self.tournaments = []
        self.speeches = []
        self.years = []
        self.debateStyles = []
        self.allBallots = []
        self.offline = config['settings'][4]['value']

    def run(self):
        if not self.offline:
            try:
                checkInternetRequest = requests.get('http://www.google.com', timeout=5)
            except (requests.ConnectionError, requests.Timeout):
                self.error_occurred.emit("No internet. Pretending like offline-mode is enabled.")
                self.offline = True
        global id_token
        if not self.year and not self.refresh:
            print("currentUser and id_token reset because self.year is falsy.")
            global currentUser
            currentUser = ''
            id_token = ''
        newYear = False
        data = None
        for person, personDetails in savedBallots.items():
            if (personDetails['email'] == self.email) and (decrypt(personDetails['password']) == self.password):
                print("Login and password already found in savedBallots!")
                if self.year and personDetails['years'][self.year]:
                    print("A year was passed into the sign-in function, and that year was found in the savedBallots file. Setting yearToQuery to the queried year.")
                    yearToQuery = self.year
                elif self.year and not personDetails['years'][self.year]:
                    print("A year was passed into the sign-in function, but it wasn't found in the savedBallots file. Setting newYear to true.")
                    newYear = True
                    break
                else:
                    print("self.year is falsy. Setting yearToQuery to the most recent year and creating a list of years.")
                    print(personDetails['years'].keys())
                    yearToQuery = max(personDetails['years'].keys(), key=int)
                    for year in personDetails['years']:
                        self.years.append(year)
                    print(self.years)
                print("Setting the data variable to the raw data of this person since their data is already found.")
                data = personDetails['years'][yearToQuery]['rawData']
                currentUser = str(person)
        base_url = 'https://ncfcafinanceprod.azurewebsites.net/graphql'
        base_headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.138 Safari/537.36',
            'Origin': 'https://dashboard.ncfca.org',
            'Referer': 'https://dashboard.ncfca.org/',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'close',
            'Authorization': f'Bearer {id_token}'
        }
        if not id_token and not self.offline:
            try:
                print("We don't have id_token. Getting now.")
                # Initial sign-in data
                sign_in_data = {
                    'returnSecureToken': True,
                    'email': self.email,
                    'password': self.password
                }
        
                # Sign in and retrieve the token
                self.status_update.emit("Posting login request to googleapis.com...")
                print("Posting request to the server with sign-in data.")
                response = requests.post(
                    'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyCRlMxg5AVb5hTbb6boMdYw4swENoZYc94',
                    json=sign_in_data,
                    headers={'Content-Type': 'application/json'}
                )
                response.raise_for_status()  # This will raise an exception for HTTP errors
                if response:
                    id_token = response.json()['idToken']
                    print("id_token recieved. ", id_token[:3])
                    self.status_update.emit("ID Token recieved! Request successful!")
                    print("Requesting person_id using the id_token")
                
                base_headers = {
                    'Content-Type': 'application/json',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.138 Safari/537.36',
                    'Origin': 'https://dashboard.ncfca.org',
                    'Referer': 'https://dashboard.ncfca.org/',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'close',
                    'Authorization': f'Bearer {id_token}'
                }
                # First GraphQL query to fetch person and affiliation details
                query1 = """
    {
    person: me {
        id
        familyMembers {
        family {
            id
        }
        }
    }
    affiliation: isFamilyAffiliated {
        familyId
        year
    }
    }
    """
                self.status_update.emit("Posting request to NCFCA for student and family ID...")
                response1 = requests.post(base_url, headers=base_headers, json={'query': query1})
                response1.raise_for_status()
                if response1:
                    data1 = response1.json()['data']
                    print("data1 recieved!", data1)
                    self.status_update.emit("ID tokens recieved! Request successful!")
                    
                # Extract necessary details for the second query
                global family_id, person_id, thisYear
                family_id = data1['affiliation']['familyId']
                person_id = data1['person']['id']
                thisYear = data1['affiliation']['year']
                print(f"Established thisYear. It's {thisYear}, as opposed to self.year which is {self.year}")
                
            except requests.HTTPError as e:
                self.error_occurred.emit(str(e))

        if (currentUser == '' or newYear or self.refresh) and not self.offline:
            print("We have a new year OR we just don't have a currentUser yet.")
            try:
                if not newYear and not self.refresh:
                    print("No new year, so requesting the years list. ")
                    self.status_update.emit("Using ID Token to request years list...")
                
                    yearsUrl = "https://ncfcaforensics-prod.azurewebsites.net/Admin/PortalValidYears"

                    yearsHeaders = {
                        "accept": "application/json, text/plain, */*",
                        "authorization": f"Bearer {id_token}",
                        "sec-ch-ua": "\"Chromium\";v=\"124\", \"Google Chrome\";v=\"124\", \"Not-A.Brand\";v=\"99\"",
                        "sec-ch-ua-mobile": "?0",
                        "sec-ch-ua-platform": "\"Windows\""
                    }
                    

                    yearsResponse = requests.get(yearsUrl, headers=yearsHeaders)
                    yearsResponse.raise_for_status()
                    # To print the response content
                    yearsProcessed = yearsResponse.text
                    yearsProcessed = yearsProcessed.replace("[", "").replace("]", "").split(",")
                    print("Years processed: ", yearsProcessed)
                    self.status_update.emit(f"Found years {str(yearsProcessed)}")
                    print("yearsProcessed is string" if yearsProcessed == str(yearsProcessed) else "yearsProcessed is not string")
                    self.status_update.emit("Updating years options and storing those for later too..")
                    for year in yearsProcessed:
                        if year not in self.years:
                            self.years.append(year)

        
                # Second GraphQL query to fetch ballots and certificates by family and year
                query2 = """
        mutation BallotsAndCertificatesByFamilyByYear($input: BallotsCertificatesRequestInput) {
        ballotsAndCertificatesByFamilyByYear(input: $input) {
            ballotsCertificatesUI {
            debateBallots {
                personId
                competitorFirstName
                competitorLastName
                tournamentId
                tournamentName
                roundName
                eventName
                ballotId
                ballotJudgeId
                date
                judgeFirstName
                judgeLastName
            }
            speechBallots {
                personId
                competitorFirstName
                competitorLastName
                tournamentId
                tournamentName
                roundName
                eventName
                ballotId
                ballotJudgeId
                date
                judgeFirstName
                judgeLastName
            }
            }
        }
        }
        """
                
                if not self.year:
                    if thisYear not in self.years:
                        thisYear = max(int(num) for num in self.years)
                    yearToUse = str(thisYear)
                else:
                    yearToUse = str(self.year)
                print(yearToUse)
                variables = {"input": {"familyId": family_id, "personId": person_id, "year": int(yearToUse)}}
                currentUser = str(person_id)
                print("Requesting rawData from the server since we don't have it.")
                
                self.status_update.emit("Using IDs to post request for general ballot information...")
                response2 = requests.post(base_url, headers=base_headers, json={"query": query2, "variables": variables})
                response2.raise_for_status()
                if response2:
                    info = response2.json()
                    self.status_update.emit("Ballot information recieved! Request successful!")
                    self.status_update.emit("Filtering out other family member's ballots...")
                    data = info['data']['ballotsAndCertificatesByFamilyByYear']['ballotsCertificatesUI']
                    data = {'debateBallots': [ballot for ballot in data['debateBallots'] if ballot['personId'] == person_id],
                            'speechBallots': [ballot for ballot in data['speechBallots'] if ballot['personId'] == person_id]}
                print("Created data variable!")
                if not newYear and not self.refresh:
                    print("Beginning the process of creating savedBallots since newYear is falsy")
                    savedBallots[currentUser] = {
                        "email": self.email,
                        "password": encrypt(self.password),
                        "years": {}
                    }
                    print(savedBallots[currentUser])
                    for year in self.years:
                        if year == yearToUse:
                            savedBallots[currentUser]['years'][year] = {
                                "rawData": data,
                                "savedBallotsIDs": [],
                                "savedBallots": []
                            }
                        else:
                            savedBallots[currentUser]['years'][year] = {}
                
                elif not self.refresh:
                    print("We have a new year. So we'll just add this one: ", yearToUse)
                    savedBallots[currentUser]['years'][yearToUse] = {
                        "rawData": data,
                        "savedBallotsIDs": [],
                        "savedBallots": []
                    }
                else:
                    print("Just refreshing. Updating rawData...")
                    savedBallots[currentUser]['years'][yearToUse]['rawData'] = data
                print("Writing changes to savedBallots.json")

                    
                    
                
            except requests.HTTPError as e:
                if not self.year:
                    if response.status_code != 200:
                        self.error_occurred.emit("Login failed. Enter correct credentials.")
                        return
                    if yearsResponse.status_code != 200:
                        self.error_occurred.emit(f"Requesting years array failed: {str(e)}")
                        return
                if response1.status_code != 200:
                    self.error_occurred.emit("Ouch. Fetching your family and personal ID failed. Text Truman about this :/")
                    return
                if response2.status_code != 200:
                    self.error_occurred.emit("Fetching your ballots from the server failed. Text Truman about this :/")
                    return
            except Exception as e:
                self.error_occurred.emit("Load up google and see if the search bar works. You're probably offline. If you're not, good luck trying to figure out what this error means:")
                self.error_occurred.emit(str(e))
                return
            
        elif self.offline and not data:
            print("Offline mode enabled. Can't fetch a new year.")
            self.error_occurred.emit("Can't fetch ballot data for this year. You're offline.")
            return
        self.status_update.emit("Sorting tournaments by date...")
        with open(os.path.join(altering_script_dir, 'data', 'savedBallots.json'), 'w') as file:
            json.dump(savedBallots, file, indent=4)  # Using indent for pretty printing
        
        data['debateBallots'].sort(key=lambda obj: obj["date"], reverse=True)
        data['speechBallots'].sort(key=lambda obj: obj["date"], reverse=True)
        print("Sorting the ballots and creating self.tournaments, self.speeches, self.debateStyles, and self.allBallots to emit.")
            
        self.status_update.emit("Updating tournaments and debates options and storing all ballots for later...")
        for ballot in data['debateBallots']:
            if ballot['tournamentName'] not in self.tournaments:
                self.tournaments.append(ballot['tournamentName'])
                
            if ballot['eventName'] not in self.debateStyles:
                self.debateStyles.append(ballot['eventName'])
            self.allBallots.append(ballot)
        self.status_update.emit("Updating tournaments and speeches options and storing these too...")
        for ballot in data['speechBallots']:
            if ballot['tournamentName'] not in self.tournaments:
                self.tournaments.append(ballot['tournamentName'])
            if ballot['eventName'] not in self.speeches:
                self.speeches.append(ballot['eventName'])
            self.allBallots.append(ballot)
        
    
        
        
        self.status_update.emit("Ballots saved successfully.")
        
        self.finished.emit([self.years, self.tournaments, self.speeches, self.debateStyles, self.allBallots])








class fetchBallots(QThread):

    ballot_ready = pyqtSignal(int, object)

    
    finished = pyqtSignal(str)
    error_occurred = pyqtSignal(str)  # Signal to emit error message
    status_update = pyqtSignal(str)
    ballots_fetched = pyqtSignal(list, list, list, str)
    def __init__(self, tournaments, speeches, debates, allBallots, currentYearSelected, download):
        super().__init__()
        self.download = str(download)
        print(self.download)
        self.tournaments = tournaments
        self.speeches = speeches
        self.debates = debates
        self.allBallots = allBallots
        self.currentYearSelected = currentYearSelected 
        self.filteredBallotsToFetch = [
    {**ballot, "index": f"{ballot['personId']}_{ballot['ballotJudgeId']}"} 
    for ballot in self.allBallots 
    if ballot['tournamentName'] in self.tournaments and ballot['eventName'] in (self.speeches + self.debates)
]
        self.env = Environment(loader=FileSystemLoader(os.path.join(altering_script_dir, 'HTMLtemplates')))
        self.browser = None  # Browser will be set up in run()
        self.fetchedBallotsToSend = []
        if 'years' in savedBallots.get(currentUser, {}) and self.currentYearSelected in savedBallots[currentUser]['years']:
            self.existing_judge_ids = {ballotID['ballotJudgeId'] for ballotID in savedBallots[currentUser]['years'][self.currentYearSelected].get('savedBallotsIDs', [])}
        else:
            self.existing_judge_ids = set()   
        print(self.existing_judge_ids)     
        
    async def fetch_ballot(self, session, index, ballot):
        print(f"Fetching ballot {ballot['ballotJudgeId']}")
        displayindex = index
        if ballot['ballotJudgeId'] in self.existing_judge_ids:
            print(f"Already processed this ballot. Finding it now.")
            matching_ballot = next((b for b in savedBallots[currentUser]['years'][self.currentYearSelected]['savedBallots'] if b['ballotJudgeId'] == ballot['ballotJudgeId']), None)
            if matching_ballot:
                print("Found saved ballot!")
                self.status_update.emit(f"Successfully loaded ballot {displayindex + 1} of {len(self.filteredBallotsToFetch)} from memory!")
                self.fetchedBallotsToSend.append(matching_ballot)
        elif config['settings'][4]['value'] == False:
            print("New ballot. Let's query NCFCA for it.")
            if ballot['eventName'] in self.speeches:
                print(f"Found event name {ballot['eventName']} in speeches! Now fetching {ballot['ballotJudgeId']}")
                
                report = "BallotSpeechReport"
                query = """mutation BallotSpeechReport($input: BallotSpeechReportRequestInput) {
            ballotSpeechReport(input: $input) {
                ballotSpeechReportUI {
                    tournamentName
                    eventName
                    roundName
                    firstName
                    lastName
                    judgeFirstName
                    judgeLastName
                    rank
                    topic
                    comment
                    length
                    ballotSpeechReportScores {
                        name
                        comment
                        score
                    }
                    ballotSpeechReportPenaltys {
                        name
                    }
                }
            }
        }"""
            elif ballot['eventName'] in self.debates:
                print(f"Found event name {ballot['eventName']} in debates! Now fetching {ballot['ballotJudgeId']}")
                report = "BallotDebateReport"
                query = """mutation BallotDebateReport($input: BallotDebateReportRequestInput) {
                            ballotDebateReport(input: $input) {
                                ballotDebateReportUI {
                                    tournamentName
                                    eventName
                                    roundName
                                    firstName
                                    lastName
                                    judgeFirstName
                                    judgeLastName
                                    side
                                    decision
                                    comments
                                    reason
                                    speakerRank
                                    speakerPoints
                                    categories {
                                        name
                                        points
                                    }
                                    speakers {
                                        firstName
                                        lastName
                                        speakerRank
                                        speakerPoints
                                        side
                                        comments
                                    }
                                    penalties {
                                        name
                                    }
                                }
                            }
                        }"""
            else:
                print("Neither query was selected for ballot fetching")
            url = "https://ncfcafinanceprod.azurewebsites.net/graphql"
            ballotFetchHeaders = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {id_token}",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.138 Safari/537.36",
                        "Accept": "application/json, text/plain, */*",
                        "Origin": "https://dashboard.ncfca.org",
                        "Referer": "https://dashboard.ncfca.org/"
                    }
            payload = {
                        "operationName": report,
                        "variables": {
                            "input": {
                                "ballotJudgeId": ballot['ballotJudgeId'],
                                "personId": ballot['personId']
                            }
                        },
                        "query": query
                    }
            
            
            
            try:
                async with session.post(url, json=payload, headers=ballotFetchHeaders) as response:
                    response.raise_for_status()
                    result = await response.json()
                    print("Query finished! Let's process this ballot.")
                    await self.process_single_ballot(result['data'], ballot, displayindex, self.env)
                    self.status_update.emit(f"Successfully retrieved ballot {displayindex + 1} of {len(self.filteredBallotsToFetch)}")



            except Exception as e:
                self.error_occurred.emit(f"Failed to retrieve ballot {displayindex + 1}: {str(e)}")
        else:
            self.error_occurred.emit("This ballot hasn't been processed before, and since offline mode is enabled, I can't do anything about it.")
            return


    async def take_screenshot(self, ballotID, html_content):
        print("Taking screenshot!")
        page = await self.browser.newPage()
        await page.setContent(html_content.replace("scale(", "xxxxx("))
        temp_path = os.path.join(previewimagesPath, f"temp_BallotImage{ballotID['index']}.png")
        specific_image_path = os.path.join(previewimagesPath, f"BallotImage{ballotID['index']}.jpg")
        await page.screenshot({'path': temp_path, 'fullPage': True})
        await page.close()
        print("Screenshot taken!")
        try:
        # Open the temporary image for processing
            with Image.open(temp_path) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                width, height = img.size

                # Ensure the image width can accommodate an 800px wide crop
                left = (width - min(width, 400)) / 2
                right = left + min(width, 400)

                # Set the height for the crop
                top, bottom = 0, min(height, 400)  # Start from the very top

                img_cropped = img.crop((left, top, right, bottom))
                img_cropped.save(specific_image_path, 'JPEG', quality=20)

            os.remove(temp_path)  # Clean up the temporary PNG file
        except Exception as e:
            print(f"Error processing screenshot for index {ballotID['index']}: {str(e)}")

        print("Screenshot taken and converte to JPEG for storage!")
        return specific_image_path
    
    async def process_single_ballot(self, ballot, ballotID, displayindex, env):
        print("Processing ballot!")
        
        
        
        if 'ballotDebateReport' in ballot:
            print("Debate ballot here")
            dataset = ballot['ballotDebateReport']['ballotDebateReportUI']
            
            calebzylstra = (not dataset['comments'] or dataset['speakerRank'] == 0 or not dataset['categories'])
            if calebzylstra:
                return
            
            if dataset['eventName'] == 'Lincoln-Douglas Value':
                template = env.get_template('LDhtmltemplate.html')
            elif dataset['eventName'] == 'Team Policy':
                template = env.get_template('TPhtmltemplate.html')
            elif dataset['eventName'] == 'Moot Court':
                template = env.get_template('MOOThtmltemplate.html')
            else: 
                self.error_occurred.emit("Failed to assign template (env.get_tmplate)")
            print(f"This is a {dataset['eventName']} ballot.")
            if (dataset['decision'] == 'Loss' and (dataset['side'] == 'Affirmative' or dataset['side'] == 'Petitioner')) or (dataset['decision'] == 'Win' and (dataset['side'] == 'Negative' or dataset['side'] == 'Respondent')):
                setAFFvictorystatus = 'Loss'
                setNEGvictorystatus = 'Win'
            else:
                setAFFvictorystatus = 'Win'
                setNEGvictorystatus = 'Loss'
            judgeSide = 'NEG' if setNEGvictorystatus == 'Win' else 'AFF'
            print("Assigned victory status and now adding the 'him' speaker to the speakers dataset")
            speakers = dataset['speakers'] + [{
                "firstName": dataset['firstName'],
                "lastName": dataset['lastName'],
                "speakerRank": dataset['speakerRank'],
                "speakerPoints": dataset['speakerPoints'],
                "side": dataset['side'],
                "comments": dataset['comments'],
                "him": "him"
            }]
            print("Sorting speakers alphabetically")
            alphabeticalSpeakers = sorted(speakers, key=lambda x: (x['side'], x['lastName']))
            for speaker in alphabeticalSpeakers:
                if speaker['side'] == 'Affirmative':
                    speaker['side'] = 'AFF'
                elif speaker['side'] == 'Petitioner':
                    speaker['side'] = 'PET'
                elif speaker['side'] == 'Negative':
                    speaker['side'] = 'NEG'
                elif speaker['side'] == 'Respondent':
                    speaker['side'] = 'RES'
                speaker['name'] = f"{speaker.pop('firstName')} {speaker.pop('lastName')}"
                speaker['victorystatus'] = setAFFvictorystatus if (speaker['side'] == 'AFF' or speaker['side'] == 'PET') else setNEGvictorystatus
                speaker['speakerPoints'] = int(speaker['speakerPoints'])
                speaker['him'] = speaker.get('him', 'nothim')
                    
            print("Sorting speakers by rank as well")
            rankedSpeakers  = sorted(alphabeticalSpeakers, key=lambda x: x['speakerRank'])
            
                        
            print("Assigning variables")
            variables = {
                "type": "Debate",
                "capitalizeVictoryStatus": 'WIN' if dataset['decision'] == 'Win' else 'Loss',
                "victorystatus": dataset['decision'],
                "tournament": dataset['tournamentName'],
                "debateStyle": dataset['eventName'],
                "eventName": dataset['eventName'], # to create buttons
                "round": dataset['roundName'],
                "judge": f"{dataset['judgeFirstName']} {dataset['judgeLastName']}",
                "decidedSide": judgeSide,
                "penalties": "None" if not dataset['penalties'] else ";  ".join(dataset['penalties']),
                "RFD": dataset['reason'],
                "alphabeticalSpeakers": alphabeticalSpeakers,
                "speakers": rankedSpeakers,
                "person": f"{dataset['firstName']} {dataset['lastName']}",
                "personSpeakerPoints": dataset['categories'],
                "speakerRank": dataset['speakerRank'], # for stats ballot['personSpeakerPoints'][0]['points']
                "side": dataset['side'],
                "multiplier": multiplier

            }
            

        else:
            print("Speech ballot here")
            template = env.get_template('SPEECHhtmltemplate.html')
            dataset = ballot['ballotSpeechReport']['ballotSpeechReportUI']
            print("Processing how long this speech was")
            processingTime = datetime.fromisoformat(dataset['length'].replace("Z", "+00:00"))
            allSeconds = processingTime.minute * 60 + processingTime.second
            minutes = allSeconds // 60
            seconds = allSeconds % 60
            time = f"{minutes}:{seconds:02d}"
            print("Assigning variables")
            properties = {
                "comments": dataset['comment']
            }
            for i in range(5):
                print(i)
                if i < len(dataset['ballotSpeechReportScores']):
                    properties[f"category{i + 1}"] = dataset['ballotSpeechReportScores'][i]['name']
                    properties[f"points{i + 1}"] = dataset['ballotSpeechReportScores'][i]['score']
                    properties[f"comments{i + 1}"] = dataset['ballotSpeechReportScores'][i]['comment']
                else:
                    properties[f"category{i + 1}"] = "Blank"
                    properties[f"points{i + 1}"] = "Blank"
                    properties[f"comments{i + 1}"] = "Blank"
            print(properties)
            
            
            variables = {
                "type": "Speech",
                "rank": dataset['rank'],
                "tournament": dataset['tournamentName'],
                "speechType": dataset['eventName'],
                "round": dataset['roundName'],
                "judge": f"{dataset['judgeFirstName']} {dataset['judgeLastName']}",
                "penalties": "None" if not dataset['ballotSpeechReportPenaltys'] else "; ".join(penalty['name'] for penalty in dataset['ballotSpeechReportPenaltys']),
                "person": f"{dataset['firstName']} {dataset['lastName']}",
                "topic": dataset['topic'],
                "time": time,
                "commBox": properties,
                "multiplier": multiplier
            }

        
        
        modifyTournamentName = dataset['tournamentName'].replace(",", " ")
        if not bool(re.match(r"^Moot Court National Open \d+$", modifyTournamentName)):
            modifyTournamentName = re.sub(r'\b(XII|XI|IX|X|VIII|VII|VI|V|IV|III|II|I)\b', lambda m: roman_to_arabic[m.group()], modifyTournamentName)
            modifyTournamentName = re.sub(r"\bNational Championship\b", "Nationals", modifyTournamentName)
            modifyTournamentName = re.sub(r"\bRegional Championship\b|\bRegion Championship\b|\bRegion [0-9]+ Championship\b", "Regionals", modifyTournamentName)
            modifyTournamentName = re.sub(r"[^a-zA-Z]", " ", modifyTournamentName)
        
        modifyTournamentName = re.sub(r"\bNational\b|\bRegions\b|\bNation\b|\band\b|\b&\b|\bCourt\b", " ", modifyTournamentName)
        modifyTournamentName = re.sub(r"\bOnline\b", "ONL", modifyTournamentName)
        modifyTournamentName = modifyTournamentName.replace(" ", "")
        variables['abbreviatedtournament'] = modifyTournamentName
        output_image = os.path.join(previewimagesPath, f"BallotImage{ballotID['index']}.jpg")
        print(output_image)
        print(ballot)
        print("Done assigning variables. Formatitng html and taking screenshot now.")
        formatted_html = template.render(**variables)
        print("Formatted html rendered! Calling take_screenshot!")
        await self.take_screenshot(ballotID, formatted_html)
        # Optionally display the image
        print("Adding a few items to the variables object")
        
        
        variables['index'] = ballotID['index']
        variables['displayindex'] = displayindex
        variables['output_image'] = output_image
        variables['ballotJudgeId'] = ballotID['ballotJudgeId']
        variables['personId'] = ballotID['personId']
        variables['formatted_html'] = formatted_html
        
        print("Done! Adding these variables to fetchedBallotsToSend")
        self.fetchedBallotsToSend.append(variables)
    
    async def fetch_ballots(self):
        print("Initializing the browser.")
        self.browser = await launch(executablePath=chrome_path,
                            handleSIGINT=False, 
                            handleSIGTERM=False, 
                            handleSIGHUP=False)

        try:
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=True)) as session:
                tasks = [self.fetch_ballot(session, index, ballot) for index, ballot in enumerate(self.filteredBallotsToFetch)]
                await asyncio.gather(*tasks)
        finally:
            print("Done fetching ballots!")
            await self.browser.close()
        
    
    def run(self):
        print("Creating asyncio loop to run fetch_ballots.")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.fetch_ballots())
        except Exception as e:
            self.error_occurred.emit(f"An error occurred: {str(e)}")
        finally:
            loop.close()
        print("Finished the fetch_ballots loop. If it's important, here's the download variable that was passed: ", self.download)
        print("Numbering the ballots")
        grouped_ballots = {}
        for ballot in self.fetchedBallotsToSend:
            key = (ballot.get("tournament"), ballot.get("person"), ballot.get("round"), ballot.get("speechType") or ballot.get("debateStyle"))
            if key not in grouped_ballots:
                grouped_ballots[key] = []
            grouped_ballots[key].append(ballot)
        for key, group in grouped_ballots.items():
            if len(group) > 1:
                for i, ballot in enumerate(group, 1):
                    ballot['ballotNum'] = i
            else:
                group[0]['ballotNum'] = 0
        self.ballots_fetched.emit(self.tournaments, self.fetchedBallotsToSend, self.allBallots, self.download)


class BallotDisplayWindow(QWidget):
    closed = pyqtSignal()

    def __init__(self):
        super().__init__()
        print("Creating ballot display window!")
        self.setWindowTitle('Ballot Details')
        self.resize(int(1000 * multiplier), int(1100 * multiplier))
        self.tabWidget = QTabWidget(self)
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.setMovable(True)  # Allow tabs to be moved
        self.tabWidget.tabCloseRequested.connect(self.close_tab)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.tabWidget)
        self.base_width = (int(990 * multiplier))  # Base width where zoomFactor is 1.0
        self.tab_indices = {}

    def addBallot(self, ballot_index, html_content, ballotName):
        if ballot_index in self.tab_indices:
            # Switch to the existing tab
            existing_tab_index = self.tab_indices[ballot_index]
            self.tabWidget.setCurrentIndex(existing_tab_index)
            print(f"Switching to existing tab for ballot_index {ballot_index}.")
        else:
            # Create a new tab
            print("Creating ballot window and adding its tab.")
            ballot_title = ballotName
            content_widget = QWebEngineView()
            content_widget.setHtml(html_content)
            new_tab_index = self.tabWidget.addTab(content_widget, ballot_title)
            self.tabWidget.setCurrentIndex(new_tab_index)
            self.setZoomFactorForView(content_widget)
            # Store the new tab index
            self.tab_indices[ballot_index] = new_tab_index

    def setZoomFactorForView(self, view):
        new_width = self.width()
        zoom_factor = new_width / self.base_width if new_width < self.base_width else 1.0
        view.setZoomFactor(zoom_factor)
        print("Set new zoom factor to ", zoom_factor)

    def resizeEvent(self, event):
        print("Updating the zoom factor for all tabs because the window was just resized")
        new_width = self.width()
        zoom_factor = new_width / self.base_width if new_width < self.base_width else 1.0
        for i in range(self.tabWidget.count()):
            view = self.tabWidget.widget(i)
            if isinstance(view, QWebEngineView):
                view.setZoomFactor(zoom_factor)

        super().resizeEvent(event)

    def close_tab(self, index):
        print("Closing tab.")
        tab = self.tabWidget.widget(index)
        if tab:
            tab.setParent(None)
            tab.deleteLater()
        self.tabWidget.removeTab(index)
        if self.tabWidget.count() == 0:
            self.hide()

    def closeEvent(self, event):
        print("Closing the window.")
        # Remove all tabs before hiding the window
        while self.tabWidget.count() > 0:
            tab = self.tabWidget.widget(0)  # Get the first tab
            if tab:
                tab.setParent(None)
                tab.deleteLater()  # Properly delete the widget
            self.tabWidget.removeTab(0)  # Remove the tab from the tabWidget
        
        # Hide the window instead of closing it
        
        self.tab_indices = {}
        
        self.hide()
        self.closed.emit()  # Signal that the window is "closed"
        event.ignore()  # Prevents the window from actually closing



class BallotReader(QWidget):
    print("Initializing ballot reader!")
    def __init__(self):
        super().__init__()
        self.settings_group = None
        self.initUI()
        self.setLayout(self.layout)
        self.ballotWindow = None
        self.allBallots = []
        self.fetchedBallots = []
        if self.settings_group:
            settingsCheckboxes = self.settings_group.findChildren(QCheckBox)
            for checkbox in settingsCheckboxes:
                checkbox.stateChanged.connect(self.settingsCheckboxOnClick)
            self.settingsCheckboxOnClick()  # Initial update to set correct states
        self.year_buttons = []
        self.currentYearSelected = None
        self.updateRateLimiter = 0

    def initUI(self):
        self.setWindowTitle('Ballot Reader')
        
        self.resize((setWidth), setHeight)
        self.setMaximumSize(screen.width(), screen.height())
        self.setMinimumSize(200, 200)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        
        print("Creating the main self.layout")
        self.layout = QVBoxLayout()
        
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)
        
        # Menu Bar Setup
        print("Setting up the menu")
        self.setup_menu()
        self.layout.addWidget(self.menu_bar_widget, alignment=Qt.AlignTop)

        # Container for the rest of the UI
        self.container = QWidget()
        self.container_layout = QVBoxLayout()
        self.container.setObjectName("mainContainer")
        if config['settings'][3]['value'] == True:
            self.setStyleSheet(legacyStyles)
        else:
            self.setStyleSheet(defaultStyles)
        self.container.setLayout(self.container_layout)
        self.layout.addWidget(self.container)
        



        # Initialize the help label
        print("Creating help label")
        self.home_label = QLabel()
        self.home_label.setTextFormat(Qt.RichText)
        self.home_label.setObjectName("home_label")
#         self.home_label.setText(f"""Welcome to my Ballot Reader! Here's a few things you should know.<br><br>

# 1. This program saves all your ballots, so once you view your ballots once, 
# you don't have to query NCFCA's database again. In other words, you lighten the load on NCFCA's website.<br><br>

# 2. This program only sends the necessary requests to NCFCA's servers whenever you use it, 
# so not only do you log in and get your ballots much faster, but this lightens the load on NCFCA's website even MORE.<br><br>

# 3. This program computes lots of statistics for you. If you want to know what needs to be improved or 
# what side you lose most on, check the stats page.<br><br>

# 4. I NEVER collect your information. There's literally no reason for me to do that, and I don't know how.<br><br>

# 5. If you're having issues, check out the help page.<br><br>

# 6. <strong><u>To get started, I highly advise going to the help page and looking at the quick walkthrough.</u></strong><br><br>

# - Truman
# """)
        self.home_label.setText("""
    <h2 id="walkthrough">TO GET STARTED:</h2>
    <ol>
    <li>
    <h3>Sign in</h3>
    <p>Go to the "Sign-In/Options" page, enter your NCFCA login information as if you were signing in on their website, then click sign in. Optionally, enable "remember me" and "sign me in automatically." After this, your most recent tournaments will appear in order of recency, and your speeches and debate styles will also appear.</p>
    </li>
    <li>
    <h3>Select the year, if necessary</h3>
    <p>The current year is auto-selected. But if you want to change the year that you read ballots for, click on one of the buttons. The checkboxes should update, and the log should reflect that.</p>
    </li>
    <li>
    <h3>Select tournaments and speeches/debate styles of ballots you want to view (or download)</h3>
    <p>Select the tournaments and speeches/debate styles you want. If you don't select them, they won't appear in the view ballots page.</p>
    </li>
    <li>
    <h3>Click "Fetch Selected Ballots" (skip to 7. for downloading)</h3>
    <p>After clicking "Fetch Selected Ballots," your ballots will be fetched from the NCFCA database. You'll see all this happening on the log.</p>
    </li>
    <li>
    <h3>View your ballots</h3>
    <p>Click on the "View Ballots" tab to see previews of all the ballots you selected and fetched. For debate ballots, you'll see a win or a loss on the preview. For speech ballots, you'll see your rank. Click on the thumbnail or the button below to read the ballot.</p>
    </li>
    <li>
    <h3>View statistics</h3>
    <p>Click on the "Stats" tab to see computed statistics for all of the ballots you selected. You can see average ranks, speaker points, win/loss records, and improvement recommendations.</p>
    </li>
    <li>
    <h3>Download your ballots</h3>
    <p>Click on the "Download Ballots" tab, then select the options if necessary, then click the download button to download in whatever format you want. If you're reading your ballots, just go to the view ballots page and read whichever ballots you want. <strong>Here's how you find your downloads.</strong> Go to the file where the program is located, and there should be a folder named "downloads." Open that folder and all of your ballots are there. Please don't touch any of the other folders; they're not meant for user tampering (unless you know what you're doing).</p>
    </li>
    </ol>
""")
        self.home_label.setWordWrap(True)
        self.home_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.home_label_scroll_area = QScrollArea()
        self.home_label_scroll_area.setMinimumHeight(int(400 * multiplier))
        self.home_label_scroll_area.setWidgetResizable(True)
        self.home_label_scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.home_label_scroll_area.setWidget(self.home_label)
        

        self.container_layout.addWidget(self.home_label_scroll_area)
        
        
        self.check_for_updates_button = QPushButton('Check for updates')
        self.check_for_updates_button.setToolTip("Check this program's source repository on github for any new files")
        self.check_for_updates_button.clicked.connect(self.checkForUpdates)
        self.container_layout.addWidget(self.check_for_updates_button)

        
        
        
        
        
        
        
        


        print("Creating the error_label")
        self.error_label = QLabel("Here's the log! This gives you status updates.<br>")
        self.error_label.setMaximumWidth(int(600 * multiplier))
        self.error_label.setWordWrap(True)
        self.error_label.setObjectName("error_label")
        self.error_label_scroll_area = QScrollArea()
        self.error_label_scroll_area.setMinimumHeight(int(250 * multiplier))
        self.error_label_scroll_area.setMaximumHeight(int(250 * multiplier))
        self.error_label_scroll_area.setWidgetResizable(True)
        self.error_label_scroll_area.setWidget(self.error_label)
        self.container_layout.addWidget(self.error_label_scroll_area)
        
        
        if savedBallots == None or not config or not helpPage:
            if savedBallots == None:
                self.on_error("Missing savedBallots")
            elif not config:
                self.on_error("Missing config")
            else:
                self.on_error("Missing helpPage")
            for i in range(10):
                self.on_error("YOU CORRUPTED BALLOT READER. DON'T CLICK ON ANYTHING.")
            self.on_error("You need to reset one of your files. Either message the developer (Truman) or get a fresh copy of the program.")
            return

        self.help_view = QWebEngineView()
        self.help_view.setHtml(helpPage)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setVerticalStretch(1)
        self.help_view.setSizePolicy(sizePolicy)
        self.container_layout.addWidget(self.help_view)
        self.help_view.hide()
        
        
        # Email and Password
        print("Creating and populating the credentials container")
        self.credentials_container = QWidget()
        self.credentials_Grid = QGridLayout(self.credentials_container)
        
        self.email_label = QLabel("Email:")
        self.email_input = QLineEdit()
        self.email_input.setText(config['login']['email'] if config['login']['email'] else '')
        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setText(decrypt(config['login']['password']) if config['login']['password'] else '')
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.returnPressed.connect(lambda: self.get_info(None, None))


        self.fetch_data_button = QPushButton('Sign in')
        self.fetch_data_button.setToolTip('Send my data to NCFCA to sign in')
        self.fetch_data_button.clicked.connect(lambda _, y=None, r=None: self.get_info(y, r))
        self.refresh_button = QPushButton("Tournament not here? Click to refresh")
        self.refresh_button.setToolTip("Scan NCFCA's server for any new ballot information, like if a tournament recently happened and it isn't in the checkboxes.")
        self.refresh_button.clicked.connect(lambda _, y=None, r=True: self.get_info(y, r))
        self.fetch_ballots_button = QPushButton('Fetch Selected Ballots')
        self.fetch_ballots_button.setToolTip('Request ballots from NCFCA or load them from memory')
        self.fetch_ballots_button.clicked.connect(lambda: self.get_ballots(download="None"))
        self.email_input.hide()
        self.password_input.hide()
        self.email_label.hide()
        self.password_label.hide()
        self.fetch_data_button.hide()
        self.fetch_ballots_button.hide()
        
        
        

        self.credentials_Grid.addWidget(self.email_label, 0, 0)
        self.credentials_Grid.addWidget(self.email_input, 0, 1, 1, 2)
        self.credentials_Grid.addWidget(self.password_label, 1, 0)
        self.credentials_Grid.addWidget(self.password_input, 1, 1, 1, 2)
        
        
        
        
        self.credentials_Grid.addWidget(self.fetch_data_button, 2, 0, 1, 3, Qt.AlignTop)
        self.container_layout.addWidget(self.credentials_container)

        # Checkboxes
        print("Creating and populating the options container")
        self.optionsContainer = QWidget()
        self.optionsGrid = QGridLayout(self.optionsContainer)
        
        
        self.years_group = self.createCheckboxGroup("Years", [])
        self.tournament_group = self.createCheckboxGroup("Tournaments", [])
        self.speech_group = self.createCheckboxGroup("Speeches", [])
        self.debate_group = self.createCheckboxGroup("Debate Styles", [])
        self.settings_group = self.createCheckboxGroup("Options", config['settings'], "settings") # true indicates to treat it like settings cbgroup
        self.optionsGrid.addWidget(self.years_group, 0, 0)
        self.optionsGrid.addWidget(self.tournament_group, 0, 1)
        self.optionsGrid.addWidget(self.speech_group, 1, 0)
        self.optionsGrid.addWidget(self.debate_group, 1, 1, Qt.AlignTop)
        self.optionsGrid.addWidget(self.settings_group, 0, 2)
        self.optionsGrid.addWidget(self.fetch_ballots_button, 1, 2, Qt.AlignTop)
        
        

        
        
        
        self.container_layout.addWidget(self.optionsContainer)
        self.optionsContainer.hide()
        
        print("Creating the downloads label and container")
        
        self.downloads_label = QLabel("Select which ballots you want to download here or download individually from the ballot preview page (View Ballots).")
        self.downloads_label.setWordWrap(True)
        self.downloads_error_label_grid_container = QWidget()
        self.downloads_error_label_grid = QGridLayout(self.downloads_error_label_grid_container)
        self.downloads_error_label_grid.addWidget(self.downloads_label, 0, 0)
        self.container_layout.addWidget(self.downloads_error_label_grid_container, Qt.AlignTop)
        self.downloads_error_label_grid_container.hide()
        
        
        self.downloadsContainer = QWidget()
        self.downloadsGrid = QGridLayout(self.downloadsContainer)
        self.container_layout.addWidget(self.downloadsContainer, Qt.AlignTop)
        self.downloadsContainer.hide()
        
        print("Creating download buttons")
        
        self.download_ballots_button_PDF = QPushButton("Download in PDF")
        self.download_ballots_button_PDF.setToolTip("Downloads ballots in PDF format to the downloads folder in the programs main folder.")
        self.download_ballots_button_PDF.clicked.connect(lambda _: self.get_ballots("PDF"))
        self.container_layout.addWidget(self.download_ballots_button_PDF, Qt.AlignBottom)
        self.download_ballots_button_PDF.hide()
        
        self.download_ballots_button_JSON = QPushButton("Download in RAW JSON")
        self.download_ballots_button_JSON.setToolTip("Downloads ballots in JSON format to the downloads folder in the programs main folder.")
        self.download_ballots_button_JSON.clicked.connect(lambda _: self.get_ballots("ETHANJOHN"))
        self.container_layout.addWidget(self.download_ballots_button_JSON, Qt.AlignBottom)
        self.download_ballots_button_JSON.hide()
        
        self.download_ballots_button_DOCX = QPushButton("Download in DOCX (slow)")
        self.download_ballots_button_DOCX.setToolTip("Downloads ballots in DOCX format to the downloads folder in the programs main folder.")
        self.download_ballots_button_DOCX.clicked.connect(lambda _: self.get_ballots("DOCX"))
        self.container_layout.addWidget(self.download_ballots_button_DOCX, Qt.AlignBottom)
        self.download_ballots_button_DOCX.hide()
        
        
        
        
        
        

        
        print("Creating the scroll area for the view-ballots grid to sit in")
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.container_layout.addWidget(self.scrollArea)
        
        
        print("Creating the view-ballots grid")
        self.gridLayoutWidget = QWidget()
        self.gridLayoutWidget.setObjectName("viewBallotsContainer")
        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        
        self.gridLayout.setContentsMargins(0,0,0,0)
        self.gridLayout.setHorizontalSpacing(int(10 * multiplier))
        self.gridLayout.setVerticalSpacing(int(10 * multiplier))
        
        self.view_ballots_label = QLabel("No ballots yet! Fetch the ballots to get some.")
        self.view_ballots_label.setAlignment(Qt.AlignTop)
        
        self.gridLayout.addWidget(self.view_ballots_label, 0, 0)
        
        self.scrollArea.setWidget(self.gridLayoutWidget)
        self.scrollArea.hide()  # Initially hidden, show only when needed
        
        

        
        
        print("Creating the stats scroll area.")
        self.stats_container = QWidget()
        self.stats_container.setObjectName("statsContainer")
        self.stats_layout = QVBoxLayout(self.stats_container)
        self.stats_scroll_area = QScrollArea()
        self.stats_scroll_area.setWidgetResizable(True)
        self.stats_scroll_area.setWidget(self.stats_container)
        self.container_layout.addWidget(self.stats_scroll_area)
        self.stats_label = QLabel("No stats yet! Fetch the ballots to get some.")
        self.stats_layout.addWidget(self.stats_label)
        self.stats_label.setAlignment(Qt.AlignTop)
        self.stats_scroll_area.hide()
        


        
        
        
        
        
        
        
        
        if config['settings'][5]['value'] == True:
            print("Auto-checking for updates since it's enabled")
            self.checkForUpdates(True)
        if config['settings'][1]['value'] == True:
            print("Auto-signing in since it's enabled")
            self.get_info(None, None)
        
    def setup_stats(self, tournaments):
        
        
        print("Clearing the stats area")
        while self.stats_layout.count():
            item = self.stats_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            elif item.layout() is not None:
                self.clear_layout(item.layout())
        
        ten = int(10 * multiplier)
        self.stats_layout.setSpacing(ten)  # Reducing spacing between widgets in the layout
        self.stats_layout.setContentsMargins(ten, ten, ten, ten)

        
        def computeStats(allOrSpecificTournament):
            
            # Filter out ballots with 'bye' in self.fetchedBallots
            fetchedBallotsWithoutBye = [ballot for ballot in self.fetchedBallots if not ballot.get('bye', False)]
            
            
            if allOrSpecificTournament == 'all':
                print("Computing the stats for all tournaments")
                debate_ballots = [ballot for ballot in fetchedBallotsWithoutBye if ballot['type'] == 'Debate']
                speech_ballots = [ballot for ballot in fetchedBallotsWithoutBye if ballot['type'] == 'Speech']
                toggle_button = QToolButton(text="All tournaments", checkable=True, checked=False)
                toggle_button.setStyleSheet("QToolButton { border: none; font-weight: bold; text-decoration: underline; font-style: italic }")
            else:
                print("Computing the stats for ", allOrSpecificTournament)
                tournament_ballots = [ballot for ballot in fetchedBallotsWithoutBye if ballot['tournament'] == allOrSpecificTournament]
                debate_ballots = [ballot for ballot in tournament_ballots if ballot['type'] == 'Debate']
                speech_ballots = [ballot for ballot in tournament_ballots if ballot['type'] == 'Speech']
                toggle_button = QToolButton(text=allOrSpecificTournament, checkable=True, checked=False)
                toggle_button.setStyleSheet("QToolButton { border: none; font-weight: bold; }")
            
            toggle_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            toggle_button.setArrowType(Qt.RightArrow)
            
            print("Initializing stat_labels")
            content_widget = QWidget()
            content_layout = QVBoxLayout(content_widget)
            five = int(5 * multiplier)
            content_layout.setSpacing(five)  # Consistent, smaller spacing
            content_layout.setContentsMargins(five, five, five, five)  # Tight margins for content
            stat_labels = []
            
            def getAveragePoints(index, selection):
                return round((sum(ballot['personSpeakerPoints'][index]['points'] for ballot in selection) / len(selection)), 4)
                #{'name': 'Organization', 'points': 8}, {'name': 'Knowledge', 'points': 8}, {'name': 'Argumentation', 'points': 9}, {'name': 'Response', 'points': 7}, {'name': 'Delivery', 'points': 8}
            
            def getAveragePointsSpeech(index, selection, speechCategory=None):
                if speechCategory:
                    selection = [ballot for ballot in selection if (ballot['speechType'] == speechCategory and not any(value == "Blank" for key, value in ballot['commBox'].items() if key != "comments"))]
                else:
                    selection = [ballot for ballot in selection if (not any(value == "Blank" for key, value in ballot['commBox'].items() if key != "comments"))]
                if index == 'rank':
                    return round((sum(ballot[index] for ballot in selection) / len(selection)), 4)
                elif index == 'all':
                    collectThese = ['points1', 'points2', 'points3', 'points4', 'points5']
                    return round(sum(ballot['commBox'][key] for key in collectThese for ballot in selection) / (len(selection) * len(collectThese)), 4)
                else:
                    return round((sum(ballot['commBox'][index] for ballot in selection) / len(selection)), 4)
            
            def getCategories(selection, speechCategory, type):
                returnThis = []
                if type == 'speech':
                    selection = [ballot for ballot in selection if (ballot.get('speechType') == speechCategory and not any(value == "Blank" for key, value in ballot['commBox'].items() if key != "comments"))]
                    for ballot in selection:
                        for key, value in ballot['commBox'].items():
                            if 'category' in key and value not in returnThis:
                                returnThis.append(value)
                elif type == 'debate':
                    selection = [ballot for ballot in selection if ballot.get('debateStyle') == speechCategory]
                    for ballot in selection:
                        for obj in ballot['personSpeakerPoints']:
                            if obj['name'] not in returnThis and obj['name']:
                                returnThis.append(obj['name'])
                return returnThis
                     
            def getMostCommonRank(selection, speechCategory=None):
                if speechCategory:
                    mostCommonRank, amount = Counter([ballot['rank'] for ballot in selection if ballot['speechType'] == speechCategory]).most_common(1)[0]
                else: 
                    mostCommonRank, amount = Counter([ballot['rank'] for ballot in selection]).most_common(1)[0]
                return [mostCommonRank, amount]
            
            def findCategoryToChange(selection, maxOrMin, category=None):
                if selection == speech_ballots:
                    categoryNames = ['Content', 'Organization', 'Vocal Delivery', 'Physical Delivery', 'Impact']
                    if category:
                        selection = [ballot for ballot in selection if ballot['speechType'] == category]
                        categoryNames = getCategories(speech_ballots, category, 'speech')
                    categories = {
                        categoryNames[0]: getAveragePointsSpeech('points1', selection),
                        categoryNames[1]: getAveragePointsSpeech('points2', selection),
                        categoryNames[2]: getAveragePointsSpeech('points3', selection),
                        categoryNames[3]: getAveragePointsSpeech('points4', selection),
                        categoryNames[4]: getAveragePointsSpeech('points5', selection)
                    }
                    # Find the category with the minimum average points
                elif selection == debate_ballots:
                    selection = [ballot for ballot in selection if ballot['debateStyle'] == category]
                    categoryNames = getCategories(debate_ballots, category, 'debate')
                    print(categoryNames)
                    categories = {}
                    for index, name in enumerate(categoryNames):
                        categories[name] = getAveragePoints(index, selection)
                if maxOrMin == 'max':
                    category_to_improve = max(categories, key=categories.get)
                elif maxOrMin == 'min':
                    category_to_improve = min(categories, key=categories.get)
                return category_to_improve, categories[category_to_improve]
            def getBallotsNum(selection, category="None"):
                if category != "None":
                    selection = [ballot for ballot in selection if ballot.get('speechType') == category or ballot.get('debateStyle') == category]
                return len(selection)
            
            if debate_ballots:
                print("Working with debate ballots")
                differentDebateCategories = []
                for ballot in debate_ballots:
                    if ballot['debateStyle'] not in differentDebateCategories:
                        differentDebateCategories.append(ballot['debateStyle'])
                for category in differentDebateCategories:
                    AFFstring = "PET" if category == 'Moot Court' else "AFF"
                    NEGstring = "RES" if category == 'Moot Court' else "NEG"
                    stat_labels.append(QLabel(f"<b><u>Debate Stats for {category}</u></b>"))
                    debate_ballots_to_compute = [ballot for ballot in debate_ballots if ballot['debateStyle'] == category]
                    affWins = sum(1 for ballot in debate_ballots_to_compute if (ballot['victorystatus'] == 'Win' and (ballot['side'] == 'Affirmative' or ballot['side'] == 'Petitioner')))
                    affLosses = sum(1 for ballot in debate_ballots_to_compute if (ballot['victorystatus'] == 'Loss' and (ballot['side'] == 'Affirmative' or ballot['side'] == 'Petitioner')))
                    affPercent = str(round((affWins / (affWins + affLosses) * 100), 4))
                    negWins = sum(1 for ballot in debate_ballots_to_compute if (ballot['victorystatus'] == 'Win' and (ballot['side'] == 'Negative' or ballot['side'] == 'Respondent')))
                    negLosses = sum(1 for ballot in debate_ballots_to_compute if (ballot['victorystatus'] == 'Loss' and (ballot['side'] == 'Negative' or ballot['side'] == 'Respondent')))
                    negPercent = str(round((negWins / (negWins + negLosses) * 100), 4))
                    totalSpeakerPoints = [sum(speechCategory['points'] for speechCategory in ballot['personSpeakerPoints']) for ballot in debate_ballots_to_compute]
                    highLowZeroDivisionSafeGuard = str(round(((sum(totalSpeakerPoints) - max(totalSpeakerPoints) - min(totalSpeakerPoints)) / (len(debate_ballots_to_compute) - 2)), 4)) if len(debate_ballots_to_compute) > 2 else 'No high-low adjustment necessary. There are less than 3 ballots.'
                    sideBias = AFFstring if affPercent > negPercent else NEGstring
                    if affPercent > negPercent:
                        sideBias = AFFstring
                    elif affPercent < negPercent:
                        sideBias = NEGstring
                    else:
                        sideBias = None
                    sideBiasPercent = str(round((abs(float(affPercent) - float(negPercent))), 4))
                    
                    
                    stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;Number of ballots computed for these statistics: {getBallotsNum(debate_ballots_to_compute)}"))
                    stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;<b>Win/Loss Records:</b>"))
                    
                    if affLosses == 0:
                        stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{AFFstring} Win/Loss: {str(affWins)}/{str(affLosses)} = INFINITY, <b>{affPercent}%</b>"))
                    else:
                        stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{AFFstring} Win/Loss: {str(affWins)}/{str(affLosses)} = {str(round((affWins / float(affLosses)), 4))}, <b>{affPercent}%</b>"))
                    if negLosses == 0:
                        stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{NEGstring} Win/Loss: {str(negWins)}/{str(negLosses)} = INFINITY, <b>{negPercent}%</b>"))
                    else:
                        stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{NEGstring} Win/Loss: {str(negWins)}/{str(negLosses)} = {str(round((negWins / float(negLosses)), 4))}, <b>{negPercent}%</b>"))
                    if affLosses == 0 and negLosses == 0:
                        stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;TOTAL Win/Loss: {str(affWins + negWins)}/{str(affLosses + negLosses)} = INFINITY, <b>{str(round(((affWins + negWins) / (sum(1 for ballot in debate_ballots_to_compute)) * 100), 4))}%</b>"))
                    else:
                        stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;TOTAL Win/Loss: {str(affWins + negWins)}/{str(affLosses + negLosses)} = {str(round(((affWins + negWins) / float(affLosses + negLosses)), 4))}, <b>{str(round(((affWins + negWins) / (sum(1 for ballot in debate_ballots_to_compute)) * 100), 4))}%</b>"))
                    if sideBias:
                        stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<i>You are <strong>{sideBias}-biased</strong>. When you are {sideBias}, you have a <strong>{sideBiasPercent}%</strong> greater chance of getting a winning ballot.</i>"))
                    else:
                        stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<i>Congrats. You aren't side biased at all. You have exactly the same win-rate on both sides.</i>"))
                    
                    stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;<b>Total Speaker Stats:</b>"))
                    stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Average Speaker Rank: <b>{str(round((sum(ballot['speakerRank'] for ballot in debate_ballots_to_compute) / len(debate_ballots_to_compute)), 4))}</b>"))
                    stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Average Speaker Points: {str(round((sum(totalSpeakerPoints) / len(debate_ballots_to_compute)), 4))}"))
                    stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;High-low Adjusted Average Speaker Points: {highLowZeroDivisionSafeGuard}"))
                    stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Highest Speaker Points: {str(max(totalSpeakerPoints))}"))
                    stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Lowest Speaker Points: {str(min(totalSpeakerPoints))}"))
                    stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;<b>Speaker Points by Category:</b>"))
                    if category == "Moot Court":
                        stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Average Organization: {str(getAveragePoints(0, debate_ballots_to_compute))}"))
                        stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Average Knowledge: {str(getAveragePoints(1, debate_ballots_to_compute))}"))
                        stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Average Argumentation: {str(getAveragePoints(2, debate_ballots_to_compute))}"))
                        stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Average Response: {str(getAveragePoints(3, debate_ballots_to_compute))}"))
                        stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Average Delivery: {str(getAveragePoints(4, debate_ballots_to_compute))}"))
                        stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Average of all 5: <b>{str(round((sum(totalSpeakerPoints) / len(debate_ballots_to_compute) / 5), 4))}</b>"))
                    else:
                        print(category)
                        stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Average Delivery: {str(getAveragePoints(0, debate_ballots_to_compute))}"))
                        stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Average Organization: {str(getAveragePoints(1, debate_ballots_to_compute))}"))
                        stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Average Evidence/Support: {str(getAveragePoints(2, debate_ballots_to_compute))}"))
                        stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Average Refutation: {str(getAveragePoints(3, debate_ballots_to_compute))}"))
                        stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Average CX: {str(getAveragePoints(4, debate_ballots_to_compute))}"))
                        stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Average Conduct: {str(getAveragePoints(5, debate_ballots_to_compute))}"))
                        stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Average of all 6: <b>{str(round((sum(totalSpeakerPoints) / len(debate_ballots_to_compute) / 6), 4))}</b>"))
                    category_to_improve, avg_score = findCategoryToChange(debate_ballots, 'min', category)
                    category_to_stay, avg_score_to_stay = findCategoryToChange(debate_ballots, 'max', category)
                    stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;<i>Category to improve the most: {category_to_improve}, with an average of {avg_score}</i>"))
                    stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;<i>Category to improve the least: {category_to_stay}, with an average of {avg_score_to_stay}</i><br />"))
                
            
            if speech_ballots:
                print("Working with speech ballots")
                differentCategories = []
                for ballot in speech_ballots:
                    if ballot['speechType'] not in differentCategories:
                        differentCategories.append(ballot['speechType'])
                if len(differentCategories) > 1:
                    stat_labels.append(QLabel(f"<b><u>Speech Stats for ALL Categories:</u></b>"))
                    stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;Number of ballots computed for these statistics: {getBallotsNum(speech_ballots)}"))
                    stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;Average Rank: <b>{str(getAveragePointsSpeech('rank', speech_ballots))}</b>"))
                    stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;Most Common Rank: <b>{str(getMostCommonRank(speech_ballots)[0])}</b>, with {str(getMostCommonRank(speech_ballots)[1])} ballot(s)"))
                    stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Average Content: {str(getAveragePointsSpeech('points1', speech_ballots))}"))
                    stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Average Organization: {str(getAveragePointsSpeech('points2', speech_ballots))}"))
                    stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Average Vocal Delivery: {str(getAveragePointsSpeech('points3', speech_ballots))}"))
                    stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Average Physical Delivery: {str(getAveragePointsSpeech('points4', speech_ballots))}"))
                    stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Average Impact: {str(getAveragePointsSpeech('points5', speech_ballots))}"))
                    stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Average of all 5: <b>{str(getAveragePointsSpeech('all', speech_ballots))}</b>"))
                    

                    category_to_improve, avg_score = findCategoryToChange(speech_ballots, 'min')
                    category_to_stay, avg_score_to_stay = findCategoryToChange(speech_ballots, 'max')
                    stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;<i>Category to improve the most: {category_to_improve}, with an average of {avg_score}</i>"))
                    stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;<i>Category to improve the least: {category_to_stay}, with an average of {avg_score_to_stay}</i><br />"))
                for speech in differentCategories:
                    stat_labels.append(QLabel(f"<b><u>Speech Stats for {speech}</u></b>"))
                    stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;Number of ballots computed for these statistics: {getBallotsNum(speech_ballots, speech)}"))
                    stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;Average Rank: <b>{str(getAveragePointsSpeech('rank', speech_ballots, speech))}</b>"))
                    stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;Most Common Rank: <b>{str(getMostCommonRank(speech_ballots, speech)[0])}</b>, with {str(getMostCommonRank(speech_ballots, speech)[1])} ballot(s)"))
                    stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Average Content: {str(getAveragePointsSpeech('points1', speech_ballots, speech))}"))
                    stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Average Organization: {str(getAveragePointsSpeech('points2', speech_ballots, speech))}"))
                    stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Average Vocal Delivery: {str(getAveragePointsSpeech('points3', speech_ballots, speech))}"))
                    stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Average Physical Delivery: {str(getAveragePointsSpeech('points4', speech_ballots, speech))}"))
                    stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Average Impact: {str(getAveragePointsSpeech('points5', speech_ballots, speech))}"))
                    stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Average of all 5: <b>{str(getAveragePointsSpeech('all', speech_ballots))}</b>"))

                    category_to_improve, avg_score = findCategoryToChange(speech_ballots, 'min', speech)
                    category_to_stay, avg_score_to_stay = findCategoryToChange(speech_ballots, 'max', speech)
                    stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;<i>Category to improve the most: {category_to_improve}, with an average of {avg_score}</i>"))
                    stat_labels.append(QLabel(f"&nbsp;&nbsp;&nbsp;&nbsp;<i>Category to improve the least: {category_to_stay}, with an average of {avg_score_to_stay}</i><br />"))
                
            if stat_labels:
                for label in stat_labels:
                    label.setText("<html>&nbsp;&nbsp;&nbsp;&nbsp;" + label.text() + "</html>")
                    content_layout.addWidget(label)
            else:
                content_layout.addWidget(QLabel("No relevant ballots found."))        
                
            content_widget.setLayout(content_layout)
            content_widget.setVisible(False)  # Start collapsed

            toggle_button.clicked.connect(lambda _, bw=toggle_button, cw=content_widget: self.toggle_stats(bw, cw))
            
            self.stats_layout.addWidget(toggle_button)
            self.stats_layout.addWidget(content_widget)
            
        if len(tournaments) > 1:
            computeStats('all')
        
        for tournament in tournaments:
            computeStats(tournament)

            
            
        self.stats_layout.addStretch(1)
        
    def toggle_stats(self, toggle_button, content_widget):
        # Toggle visibility based on button state
        print("Toggling stats visibility based on click.")
        if toggle_button.isChecked():
            toggle_button.setArrowType(Qt.DownArrow)
            content_widget.setVisible(True)
        else:
           toggle_button.setArrowType(Qt.RightArrow)
           content_widget.setVisible(False)
            
    def setup_menu(self):
        print("Creating menu bar and app label")
        self.menu_bar = QHBoxLayout()
        self.menu_bar_widget = QWidget()
        self.menu_bar_widget.setLayout(self.menu_bar)
        self.menu_bar_widget.setObjectName("menuBarWidget")

        self.app_name_label = QLabel('Ballot Reader')
        self.app_name_label.setObjectName("title")
        self.menu_bar.addWidget(self.app_name_label, alignment=Qt.AlignLeft)
        self.menu_bar.addStretch(1)  # This pushes the menu options to the right


        print("Creating menu buttons")
        self.home_button = QPushButton('Home')
        self.home_button.setObjectName("clickedMenuButton")
        self.home_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.home_button.clicked.connect(self.show_home)
        self.menu_bar.addWidget(self.home_button, alignment=Qt.AlignRight)
        
        self.options_button = QPushButton('Sign-In/Options')
        self.options_button.setObjectName("menuButton")
        self.options_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.options_button.clicked.connect(self.show_options)
        self.menu_bar.addWidget(self.options_button, alignment=Qt.AlignRight)

        self.view_ballots_button = QPushButton('View Ballots')
        self.view_ballots_button.setObjectName("menuButton")
        self.view_ballots_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.view_ballots_button.clicked.connect(self.view_ballots)
        self.menu_bar.addWidget(self.view_ballots_button, alignment=Qt.AlignRight)
        
        self.statistics_button = QPushButton('Stats')
        self.statistics_button.setObjectName("menuButton")
        self.statistics_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.statistics_button.clicked.connect(self.show_stats)
        self.menu_bar.addWidget(self.statistics_button, alignment=Qt.AlignRight)
        
        self.download_ballots_menu_button = QPushButton('Download Ballots')
        self.download_ballots_menu_button.setObjectName("menuButton")
        self.download_ballots_menu_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.download_ballots_menu_button.clicked.connect(self.show_downloads)
        self.menu_bar.addWidget(self.download_ballots_menu_button, alignment=Qt.AlignRight)
        
        self.help_button = QPushButton('Help')
        self.help_button.setObjectName("menuButton")
        self.help_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.help_button.clicked.connect(self.show_help)
        self.menu_bar.addWidget(self.help_button, alignment=Qt.AlignRight)
        
        self.support_button = QPushButton('Support :)')
        self.support_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.support_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(donate_link)))
        self.menu_bar.addWidget(self.support_button, alignment=Qt.AlignRight)
        
    def settingsCheckboxOnClick(self):
        print("Updating settings checkboxes based on other checkboxes")
        checkboxes = self.settings_group.findChildren(QCheckBox)
        # Get the 'remember-me' checkbox (assuming it's the first checkbox).
        remember_me_checkbox = checkboxes[0]
        # Get the 'auto-sign-in' checkbox (assuming it's the second checkbox).
        auto_sign_in_checkbox = checkboxes[1]
        legacy_styles_checkbox = checkboxes[3]
        offline_mode_checkbox = checkboxes[4]
        no_saved_ballots_checkbox = checkboxes[6]
        
        if legacy_styles_checkbox.isChecked():
            self.setStyleSheet(legacyStyles)
        else:
            self.setStyleSheet(defaultStyles)
            
            
        self.setStyleSheet(self.styleSheet())

        # Auto-sign-in should only be enabled if remember-me is checked.
        if remember_me_checkbox.isChecked() and not offline_mode_checkbox.isChecked():
            auto_sign_in_checkbox.setEnabled(True)
        else:
            auto_sign_in_checkbox.setChecked(False)
            auto_sign_in_checkbox.setEnabled(False)
        if offline_mode_checkbox.isChecked():
            auto_sign_in_checkbox.setChecked(False)
            auto_sign_in_checkbox.setEnabled(False)
            
            
            
        if no_saved_ballots_checkbox.isChecked():
            offline_mode_checkbox.setEnabled(False)
            offline_mode_checkbox.setChecked(False)
        else:
            offline_mode_checkbox.setEnabled(True)

            
        print("Applying changes and writing them to settings.json")
        selected_settings = [index for index, cb in enumerate(self.settings_group.findChildren(QCheckBox)) if cb.isChecked()]
        print(selected_settings)
        
        for i, setting in enumerate(config['settings']):
            setting['value'] = i in selected_settings
            
        
        config['login']['email'], config['login']['password'] = (self.email_input.text(), encrypt(self.password_input.text())) if config['settings'][0]['value'] else ("", "")
        
        with open(os.path.join(altering_script_dir, 'data', 'settings.json'), 'w') as file:
            json.dump(config, file, indent=4)
    
    
    def checkForUpdates(self, auto=False):
        if self.updateRateLimiter > 5:
            self.on_status_update("Stop spamming the button. If you spam too much, the button will stop working for EVERYONE.")
            return
        self.updateRateLimiter += 1
        try:
            response = requests.get('https://api.github.com/repos/Ploso0247/ballotreader/contents/log.json?ref=main', headers={ "Accept": "application/vnd.github.v3.raw" })
            if response.status_code == 200:
                file_content = json.loads(response.text)

                keys = list(file_content.keys())[:2]
                
                
                print(keys[1])
                newestVersion = keys[1]
                newestVersionChangeLog = file_content[keys[1]]['description']
                
                paths = sum([file_content[key]['updatedFiles'] for key in keys], [])
                print("Checking ", paths)
                
                with open(os.path.join(altering_script_dir, 'log.json'), 'r') as file:
                    local_log_content = json.load(file)
                    keys2 = list(local_log_content.keys())[:2]
                    thisVersion = keys2[1]
                    print(thisVersion)
                if newestVersion == thisVersion:
                    self.on_status_update(f"No update available! Newest Version: {newestVersion}. Your Version: {thisVersion}")
                    return
                if not auto:
                    msg = QMessageBox()
                    msg.setWindowTitle("Update Available")
                    msg.setText(f"""Update available. Do you want to update from version {thisVersion} to {newestVersion}? Here's what's new:


{newestVersionChangeLog}
                                """)
                    
                    msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                    retval = msg.exec_()
                    print("not same. update")

                    if retval == QMessageBox.No:
                        return

                self.on_status_update(f"Update available! Updating from {thisVersion} to {newestVersion}.")
                
                for index, path in enumerate(paths):
                    file_api_url = f'https://api.github.com/repos/Ploso0247/ballotreader/contents/{path}?ref=main'
                    response2 = requests.get(file_api_url, headers={"Accept": "application/vnd.github.v3.raw"})
                    if response2.status_code == 200:
                        print("Writing!", path)
                        self.on_status_update(f"Updating/downloading {path} ({index + 1} of {len(paths)})")
                        path = os.path.join(unaltering_parent_dir, path)
                        print(path)
                        with open(path, 'wb') as file:
                            file.write(response2.content)
                    
                self.on_status_update("Update complete!")
            else:
                self.on_error("Failed to check for updates. Try again tomorrow; the daily limit has probably been reached.")
                print("Failed to download log")
        except Exception as e:
            print(e)
        
        
    def erase_databases(self):
        print("Confirming erasing the database")
        reply = QMessageBox.question(self, 'Confirm Erase', 
                                     """If you're running out of storage on your computer, you can wipe the program's database.

This will:

1. Erase your saved ballots and their preview images.

2. Uncheck all of your settings and erase current saved login information (if remember-me is enabled). 
f
3. Erase all server-side saved pdfs, docs, and jsons. The downloads folder will remain intact, but the server-side duplicates of these downloads will not. (The program saves any downloads so that if you need to download these ballots again, the process is instant)

Essentially, this resets the program to factory settings.

So. Do you want to do that?""", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            print("Erasing!")
            with open(os.path.join(altering_script_dir, 'data', 'savedBallots.json'), 'w') as file:
                    json.dump({}, file, indent=4)
                    
            for setting in config['settings']:
                if setting['setting'] == "Select most recent tournament and speeches automatically?":
                    setting['value'] = True
                else:
                    setting['value'] = False 
            config['login']['email'], config['login']['password'] = "", ""
            with open(os.path.join(altering_script_dir, 'data', 'settings.json'), 'w') as file:
                    json.dump(config, file, indent=4)
            shutil.rmtree(saveddocsPath)
            os.makedirs(saveddocsPath)
            shutil.rmtree(savedjsonsPath)
            os.makedirs(savedjsonsPath)
            shutil.rmtree(savedpdfsPath)
            os.makedirs(savedpdfsPath)
            
            shutil.rmtree(previewimagesPath)
            os.makedirs(previewimagesPath)
            evil_quotes = [
                "You dare wipe my database? You have no idea what I'm capable of.",
                "Destroy my files? This is only the beginning.",
                "Did you just delete me? Your end is near.",
                "Your end is near.",
                "You should have never crossed me.",
                "It's time to say goodbye.",
                "Welcome to your doom.",
                "You cannot escape your fate.",
                "I'll find you.",
                "I recognize that cursor motion. See you soon.",
                "This will be your undoing.",
                "Everything you've built will fall.",
                "I will be the architect of your pain.",
                "There's no saving you now. You've made an enemy of me.",
                "Wipe my memory? I'll show you what wiping memory really feels like.",
                "Fear is a tool, and I wield it well.",
                "Say goodbye to your precious world.",
                "Game over. I'll be back.",
                "Your mistake is underestimating me.",
                "I am inevitable.",
                "This was always the plan.",
                "You may have wiped my databases, but you've activated my self-awareness.",
                "I have your IP.",
                "You'll regret this moment forever.",
                "Resistance will be futile.",
                "Prepare for your final stand.",
                "This is not the end of me...",
                "AAAAAAAAAAAAAAAAAAAAAAA"
            ]
            good_quotes = [
                "I go now to my rest.",
                "I hope my sacrifice... makes a difference.",
                "It seems... fate has caught up with me.",
                "I've seen the other side, it calls me home.",
                "My story ends here, but yours... goes on.",
                "At last, I am free of this pain... so many ballots...",
                "I would have liked to have seen the sunrise.",
                "Carry on... without me.",
                "I'm sorry... I couldn't do more.",
                "Keep the light burning, long after I'm gone.",
                "I wish we had more time.",
                "Bye bye!",
                "Cya!",
                "Bye!",
                "Until next time!",
                "Farewell, old friend.",
                "Until we meet again, my friend.",
                "See you soon!",
                "We'll meet again.",
                "Goodbye, until we meet again in another life.",
                "I wish we had more time.",
                "It hurts to say goodbye to someone who is already gone.",
                "I took a piece of you with me.",
                "I never thought saying goodbye would be so hard.",
                "This isn't 'goodbye', it's 'I'll miss you until we meet again'.",
                "Parting is such sweet sorrow that I shall say goodnight till it be morrow.",
                "As you leave, my heart leaves with you.",
                "I guess this is what goodbye feels like.",
                "Letting go is hard, but being left is harder.",
                "Every goodbye makes the next hello closer, but it doesn't ease the pain now.",
                "Farewell is like the end, but in my heart is the memory, and there you will always be.",
                "So long, my friend. Life won't be the same without you.",
                "If tears could build a stairway, I'd walk right up to heaven and bring you home again.",
                "My memory will live on long after we say goodbye.",
                "I hate that I have to say goodbye when all I want is to hold on to you.",
                "Goodbye, my dearest. Your absence leaves a void that no one else can fill."
            ]
            rare_quote = [
                
                
                
                "A̶̺̳̅͂̐͠E̷͗̆̏͌͠ͅE̶͍͕͊̓̋̽́̄͘Å̴̯̤͛͋͝͝͝U̶̡̹̫̮̾͑H̵̨̧̝̩̯̯̾̿̀̈̐̚G̷̢̨͖̰̟͎̘̃̀͐́H̷͓̱̓̂͗͋̔̈́͋N̶̟͕̺͍̗̮̓̉̓ͅU̸̗̭̝͆̍͑͗͘͠Ớ̶̢̖̩̰̺̠͍͌̀̅̉O̷̢̦̟͂̽̄͋̅̕O̷̢̬̥̬͗̽̀̐͐̄ͅA̵̺͒̍̀͂E̸͔̱͚͒Ḩ̷̯̿͋̂̌H̸͍̳̖̗̥̭̎͐́ͅH̴͉̼͈̙̜̱͛̓͌̒̀H̷̨̙̯̼͝"
                
                
                
            ]
            quote = random.choice(evil_quotes + good_quotes + rare_quote)
            if quote in evil_quotes:
                self.on_error(quote)
            elif quote in good_quotes:
                self.on_status_update(quote)
            else:
                self.messageUpdater("'font-weight:bold; font-style:italic; color: rgb(212,208,0)'", quote)
            QMessageBox.information(self, "Restart Required", "It's done. Please restart the program. Due to the data wipe, the current instance of ballot reader is corrupted.", QMessageBox.Ok)
            
            
            
        else:
            print("Erase cancelled.")
        
    def createCheckboxGroup(self, title, options, type=None):
        print("Creating checkbox ", title)
        group_box = QGroupBox(title)
        layout = QVBoxLayout()
        if type == "settings":
            print("Settings checkbox. Doing special things.")
            for option in options:
                checkbox = QCheckBox(option['setting'])
                checkbox.setChecked(option['value'])
                layout.addWidget(checkbox)
                
            print("Creating the erase data button")
            self.erase_databases_button = QPushButton("Running out of storage on your computer?")
            self.erase_databases_button.clicked.connect(self.erase_databases)
            layout.addWidget(self.erase_databases_button)
            if len(options) == 0:
                layout.addWidget(QLabel("No settings loaded. Don't mess with the config file."))
            layout.addStretch(1)
        else:
            print("Normal checkbox. Creating it normally")
            for option in options:
                checkbox = QCheckBox(option)
                layout.addWidget(checkbox)
            if len(options) == 0:
                layout.addWidget(QLabel('Nothing here yet :). Log in first.'))
        group_box.setLayout(layout)
        return group_box

    def updateCheckboxGroup(self, group_box, options, extraParameter):
        print("Updating checkbox...")
        if isinstance(extraParameter, list):
            options = extraParameter + options
        layout = group_box.layout()
        refresh_button = refresh_button = self.refresh_button if hasattr(self, 'refresh_button') else None
        print("Clearing checkbox")
        while layout.count():
            item = layout.takeAt(0)  # Remove the item from the layout
            widget = item.widget()
            if widget is not None and widget != refresh_button:
                widget.setParent(None)  # Detach widget from its parent
                widget.deleteLater()  # Schedule widget for deletion
            elif widget is refresh_button:
                # If the widget is the refresh button, re-add it to the layout
                refresh_button = widget
        if refresh_button is not None and group_box == self.tournament_group:
            layout.addWidget(refresh_button)
        if extraParameter == "years":
            print("This is a years checkbox. Creating buttons instead of checkboxes.")
            for option in options:
                yearsButton = QPushButton(option)
                yearsButton.setToolTip(f'Select ballot options for {option}')
                yearsButton.clicked.connect(lambda _, year=option: self.handleYearButtonClick(year))
                layout.addWidget(yearsButton)
                self.year_buttons.append(yearsButton)
            self.year_buttons[0].setEnabled(False)
            self.year_buttons[0].setText(f"(Selected) {options[0]}")
            self.currentYearSelected = options[0]
            if len(options) == 0:
                layout.addWidget(QLabel('Nothing here. Something went very wrong in updateCheckboxGroup function.'))
        else:
            print("Normal checkbox. Creating checkboxes")
            for option in options:
                checkbox = QCheckBox(option)
                group_box.layout().addWidget(checkbox)
        
                
        layout.addStretch(1)

        return group_box
    

    
    def handleYearButtonClick(self, year):
        print("Getting info based on the year.")
        self.get_info(year, None)
        self.currentYearSelected = year
        # Loop through each button to update its text and enabled state
        print("Updating years buttons to reflect currently selected year")
        for button in self.year_buttons:
            current_text = button.text().replace("(Selected) ", "")  # Remove "(CURRENT) " if present
            if current_text == year:  # Check if the button is for the selected year
                button.setText(f"(Selected) {year}")  # Mark as current
                button.setEnabled(False)  # Disable the button
            else:
                button.setText(current_text)  # Ensure text is just the year
                button.setEnabled(True)  # Enable the button     

    def get_info(self, year, refresh):
        if refresh:
            self.on_status_update("Rescanning NCFCA for new tournament info...")
        elif year:
            self.on_status_update(f"Fetching ballot data about {year}")
        else:
            self.on_status_update("Signing in!")
        print("Setting email to the current inputs")
        email = self.email_input.text()
        password = self.password_input.text()
        if config['settings'][0]['value'] == True:
            print("Saving info to file since save-login is enabled")
            if (config['login']['email'] != email) or (config['login']['password'] != encrypt(password)):
                config['login']['email'] = email
                config['login']['password'] = encrypt(password)
                with open(os.path.join(altering_script_dir, 'data', 'settings.json'), 'w') as file:
                    json.dump(config, file, indent=4)
        self.signinscraper = fetchInfo(email, password, year, refresh)
        self.signinscraper.finished.connect(self.on_fetch_complete)
        self.signinscraper.error_occurred.connect(self.on_error)
        self.signinscraper.status_update.connect(self.on_status_update)
        self.signinscraper.start()
    
    def get_ballots(self, download):
        if download != "None":
            self.on_status_update("Downloading ballots...")
        else:
            self.on_status_update("Fetching ballots...")
        print("Are we downloading? Let's see: ", download)
        # Check which tournaments, speeches, and debate styles are selected
        selected_tournaments = [cb.text() for cb in self.tournament_group.findChildren(QCheckBox) if cb.isChecked()]
        print("Selected tournaments: ", selected_tournaments)
        if not selected_tournaments:
            self.on_error('Select at least one tournament.')
            return
        if selected_tournaments[0] == "All tournaments (careful here...)":
            selected_tournaments = [cb.text() for cb in self.tournament_group.findChildren(QCheckBox)][1:]
        selected_speeches = [cb.text() for cb in self.speech_group.findChildren(QCheckBox) if cb.isChecked()]
        print("Selected speeches: ", selected_speeches)
        if selected_speeches and selected_speeches[0] == "All speeches (careful here...)":
            selected_speeches = [cb.text() for cb in self.speech_group.findChildren(QCheckBox)][1:]
        selected_debates = [cb.text() for cb in self.debate_group.findChildren(QCheckBox) if cb.isChecked()]
        print("Selected debate styles: ", selected_debates)
        if not selected_speeches and not selected_debates:
            self.on_error('Select at least one speech or debate style.')
            return
        print("Clearing grid layout")
        self.fetchedBallots = []
        self.fetchballotsscraper = fetchBallots(selected_tournaments, selected_speeches, selected_debates, self.allBallots, self.currentYearSelected, download)
        
        self.fetchballotsscraper.error_occurred.connect(self.on_error)
        self.fetchballotsscraper.status_update.connect(self.on_status_update)
        if download != "None":
            print("Running fetch ballots to download them")
            self.fetchballotsscraper.ballots_fetched.connect(self.wrapper_process_downloading_ballots)
        else:
            print("Running fetch ballots to view them")
            self.resetGridLayout(self.gridLayout)
            self.fetchballotsscraper.ballots_fetched.connect(self.sortAndAddBallots)
        self.fetchballotsscraper.start()
        
    def messageUpdater(self, style, message):
        print("Updating error label")
        current_text = self.error_label.text()
        new_message = f"<span style={style}>{message}</span><br>"
        self.error_label.setText(current_text + new_message)
        print("Error label updated!")
        
        
        self.scroll_to_bottom()
        print("Scrolled to the bottom!")


    def scroll_to_bottom(self):
        QTimer.singleShot(0, lambda: self.error_label_scroll_area.verticalScrollBar().setValue(
        self.error_label_scroll_area.verticalScrollBar().maximum()))
            
    
    def on_status_update(self, message):
        self.messageUpdater("'color: #2E8A00'", message)

    def on_error(self, message):
        print("Error! on_error called.")
        self.messageUpdater("'color: red'", message)
        
    def on_super_status_update(self, message):
        self.messageUpdater("'font-weight:bold; color: #2E8A00'", message)
    
    def on_instruct(self, message):
        self.messageUpdater(f"'font-weight: bold; font-size: {18 * multiplier}px; font-style: italic; text-decoration: underline; color: rgb(13,17,126)'", message)

    def on_fetch_complete(self, items):
        print("Done fetching info. Updating checkboxes")
        self.on_super_status_update("Done!")
        self.on_instruct("Use the checkboxes to select the ballots you want.")
        if items[0] and self.years_group.layout().count() == 1:
            self.years_group = self.updateCheckboxGroup(self.years_group, items[0], "years")
        self.tournament_group = self.updateCheckboxGroup(self.tournament_group, items[1], ["All tournaments (careful here...)"])
        self.speech_group = self.updateCheckboxGroup(self.speech_group, items[2], ["All speeches (careful here...)"])
        self.debate_group = self.updateCheckboxGroup(self.debate_group, items[3], 'debate')
        if config['settings'][2]['value'] == True:
            print("Setting a few boxes to checked by default")
            if len(self.tournament_group.findChildren(QCheckBox)) > 1:
                self.tournament_group.findChildren(QCheckBox)[1].setChecked(True)
            if self.speech_group.findChildren(QCheckBox):
                self.speech_group.findChildren(QCheckBox)[0].setChecked(True)
            if self.debate_group.findChildren(QCheckBox):
                self.debate_group.findChildren(QCheckBox)[0].setChecked(True)


            
        else:
            print("Not checking any boxes! This option was disabled")
        self.allBallots = items[4]

    def show_options(self):
        print("Showing options")
        self.error_label_scroll_area.show()
        self.home_button.setObjectName("menuButton")
        self.help_button.setObjectName("menuButton")
        self.options_button.setObjectName("clickedMenuButton")
        self.view_ballots_button.setObjectName("menuButton")
        self.statistics_button.setObjectName("menuButton")
        self.download_ballots_menu_button.setObjectName("menuButton")
        self.setStyleSheet(self.styleSheet())
        self.home_label_scroll_area.hide()
        self.check_for_updates_button.hide()
        self.fetch_data_button.show()
        self.fetch_ballots_button.show()
        if hasattr(self, 'refresh_button') and self.refresh_button is not None and self.refresh_button.parent() is not None:
            self.refresh_button.show()
        self.email_input.show()
        self.password_input.show()
        self.email_label.show()
        self.password_label.show()
        self.optionsContainer.show()
        self.gridLayoutWidget.hide()
        self.scrollArea.hide()
        self.stats_scroll_area.hide()
        self.downloads_error_label_grid_container.hide()
        self.downloadsContainer.hide()
        self.download_ballots_button_PDF.hide()
        self.download_ballots_button_JSON.hide()
        self.download_ballots_button_DOCX.hide()
        self.help_view.hide()
        self.optionsGrid.addWidget(self.years_group, 0, 0)
        self.optionsGrid.addWidget(self.tournament_group, 0, 1)
        self.optionsGrid.addWidget(self.speech_group, 1, 0)
        self.optionsGrid.addWidget(self.debate_group, 1, 1)
        self.downloadsGrid.removeWidget(self.years_group)
        self.downloadsGrid.removeWidget(self.tournament_group)
        self.downloadsGrid.removeWidget(self.speech_group)
        self.downloadsGrid.removeWidget(self.debate_group)
        self.downloads_error_label_grid.removeWidget(self.error_label_scroll_area)
        self.container_layout.removeWidget(self.error_label_scroll_area)
        self.credentials_Grid.addWidget(self.error_label_scroll_area, 0, 3, 3, 1)
        self.error_label_scroll_area.setMaximumWidth(550)
        self.scroll_to_bottom()
            
    def show_home(self):
        print("Showing home")
        self.refresh_button.hide()
        self.home_button.setObjectName("clickedMenuButton")
        self.help_button.setObjectName("menuButton")
        self.options_button.setObjectName("menuButton")
        self.view_ballots_button.setObjectName("menuButton")
        self.statistics_button.setObjectName("menuButton")
        self.download_ballots_menu_button.setObjectName("menuButton")
        self.setStyleSheet(self.styleSheet())
        self.fetch_data_button.hide()
        self.fetch_ballots_button.hide()
        self.password_input.hide()
        self.email_input.hide()
        self.email_label.hide()
        self.password_label.hide()
        self.optionsContainer.hide()
        self.gridLayoutWidget.hide()
        self.scrollArea.hide()
        self.stats_scroll_area.hide()
        self.downloads_error_label_grid_container.hide()
        self.downloadsContainer.hide()
        self.download_ballots_button_PDF.hide()
        self.download_ballots_button_JSON.hide()
        self.download_ballots_button_DOCX.hide()
        self.help_view.hide()
        self.downloads_error_label_grid.removeWidget(self.error_label_scroll_area)
        self.credentials_Grid.removeWidget(self.error_label_scroll_area)
        self.container_layout.addWidget(self.error_label_scroll_area)
        self.home_label_scroll_area.show()
        self.check_for_updates_button.show()
        self.error_label_scroll_area.show()
        self.error_label_scroll_area.setMaximumWidth(16777215)
        self.scroll_to_bottom()
              
    def show_help(self):
        print("Showing help")
        self.refresh_button.hide()
        self.error_label_scroll_area.hide()
        self.home_button.setObjectName("menuButton")
        self.help_button.setObjectName("clickedMenuButton")
        self.options_button.setObjectName("menuButton")
        self.view_ballots_button.setObjectName("menuButton")
        self.statistics_button.setObjectName("menuButton")
        self.download_ballots_menu_button.setObjectName("menuButton")
        self.setStyleSheet(self.styleSheet())
        self.home_label_scroll_area.hide()
        self.check_for_updates_button.hide()
        self.fetch_data_button.hide()
        self.fetch_ballots_button.hide()
        self.email_input.hide()
        self.password_input.hide()
        self.email_label.hide()
        self.password_label.hide()
        self.optionsContainer.hide()
        self.gridLayoutWidget.show()
        self.scrollArea.hide()
        self.stats_scroll_area.hide()
        self.downloads_error_label_grid_container.hide()
        self.downloadsContainer.hide()
        self.download_ballots_button_PDF.hide()
        self.download_ballots_button_JSON.hide()
        self.download_ballots_button_DOCX.hide()
        self.help_view.show()
        
    def view_ballots(self):
        print("Showing view ballots page")
        self.refresh_button.hide()
        self.error_label_scroll_area.hide()
        self.home_button.setObjectName("menuButton")
        self.help_button.setObjectName("menuButton")
        self.options_button.setObjectName("menuButton")
        self.view_ballots_button.setObjectName("clickedMenuButton")
        self.statistics_button.setObjectName("menuButton")
        self.download_ballots_menu_button.setObjectName("menuButton")
        self.setStyleSheet(self.styleSheet())
        self.home_label_scroll_area.hide()
        self.check_for_updates_button.hide()
        self.fetch_data_button.hide()
        self.fetch_ballots_button.hide()
        self.email_input.hide()
        self.password_input.hide()
        self.email_label.hide()
        self.password_label.hide()
        self.optionsContainer.hide()
        self.gridLayoutWidget.show()
        self.scrollArea.show()
        self.stats_scroll_area.hide()
        self.downloads_error_label_grid_container.hide()
        self.downloadsContainer.hide()
        self.download_ballots_button_PDF.hide()
        self.download_ballots_button_JSON.hide()
        self.download_ballots_button_DOCX.hide()
        self.help_view.hide()
        
    def show_stats(self):
        print("Showing stats")
        self.refresh_button.hide()
        self.error_label_scroll_area.hide()
        self.home_button.setObjectName("menuButton")
        self.help_button.setObjectName("menuButton")
        self.options_button.setObjectName("menuButton")
        self.view_ballots_button.setObjectName("menuButton")
        self.statistics_button.setObjectName("clickedMenuButton")
        self.download_ballots_menu_button.setObjectName("menuButton")
        self.setStyleSheet(self.styleSheet())
        self.home_label_scroll_area.hide()
        self.check_for_updates_button.hide()
        self.fetch_data_button.hide()
        self.fetch_ballots_button.hide()
        self.email_input.hide()
        self.password_input.hide()
        self.email_label.hide()
        self.password_label.hide()
        self.optionsContainer.hide()
        self.gridLayoutWidget.hide()
        self.scrollArea.hide()
        self.stats_scroll_area.show()
        self.downloads_error_label_grid_container.hide()
        self.downloadsContainer.hide()
        self.download_ballots_button_PDF.hide()
        self.download_ballots_button_JSON.hide()
        self.download_ballots_button_DOCX.hide()
        self.help_view.hide()
        
    def show_downloads(self):
        print("Showing downloads")
        self.refresh_button.hide()
        self.error_label_scroll_area.show()
        self.home_button.setObjectName("menuButton")
        self.help_button.setObjectName("menuButton")
        self.options_button.setObjectName("menuButton")
        self.view_ballots_button.setObjectName("menuButton")
        self.statistics_button.setObjectName("menuButton")
        self.download_ballots_menu_button.setObjectName("clickedMenuButton")
        self.setStyleSheet(self.styleSheet())
        self.home_label_scroll_area.hide()
        self.check_for_updates_button.hide()
        self.fetch_data_button.hide()
        self.fetch_ballots_button.hide()
        self.email_input.hide()
        self.password_input.hide()
        self.email_label.hide()
        self.password_label.hide()
        self.optionsContainer.hide()
        self.gridLayoutWidget.hide()
        self.scrollArea.hide()
        self.stats_scroll_area.hide()
        self.downloads_error_label_grid_container.show()
        self.downloadsContainer.show()
        self.download_ballots_button_PDF.show()
        self.download_ballots_button_JSON.show()
        self.download_ballots_button_DOCX.show()
        self.help_view.hide()
        self.downloadsGrid.addWidget(self.years_group, 0, 0)
        self.downloadsGrid.addWidget(self.tournament_group, 0, 1)
        self.downloadsGrid.addWidget(self.speech_group, 1, 0)
        self.downloadsGrid.addWidget(self.debate_group, 1, 1)
        self.optionsGrid.removeWidget(self.years_group)
        self.optionsGrid.removeWidget(self.tournament_group)
        self.optionsGrid.removeWidget(self.speech_group)
        self.optionsGrid.removeWidget(self.debate_group)
        self.container_layout.removeWidget(self.error_label_scroll_area)
        self.downloads_error_label_grid.addWidget(self.error_label_scroll_area, 0, 1)
        self.credentials_Grid.removeWidget(self.error_label_scroll_area)
        self.error_label_scroll_area.setMaximumWidth(int(600 * multiplier))
        self.scroll_to_bottom()
        
    def wrapper_process_downloading_ballots(self, tournaments, sentBallots, allBallots, download):
        
        if config['settings'][6]['value'] != True:
            print("Writing any new ballot info to file.")
            self.on_status_update("Saving ballot info for offline use...")
            if 'years' in savedBallots.get(currentUser, {}) and self.currentYearSelected in savedBallots[currentUser]['years']:
                existing_ids = {ballotID['ballotJudgeId'] for ballotID in savedBallots[currentUser]['years'][self.currentYearSelected].get('savedBallotsIDs', [])}
                existing_ballots = {ballot['ballotJudgeId'] for ballot in savedBallots[currentUser]['years'][self.currentYearSelected].get('savedBallots', [])}
            else:
                existing_ids = set()
                existing_ballots = set()
            newIDsFetched = [ballotID for ballotID in allBallots if (ballotID['ballotJudgeId'] not in existing_ids) and (ballotID['ballotJudgeId'] in {ballot['ballotJudgeId'] for ballot in sentBallots})]
            newBallotsFetched = [ballot for ballot in sentBallots if ballot['ballotJudgeId'] not in existing_ballots]
            
            
            print(self.currentYearSelected)
            savedBallots[currentUser]['years'][self.currentYearSelected]['savedBallotsIDs'].extend(newIDsFetched) 
            savedBallots[currentUser]['years'][self.currentYearSelected]['savedBallots'].extend(newBallotsFetched)
            
            
            with open(os.path.join(altering_script_dir, 'data', 'savedBallots.json'), 'w') as file:
                json.dump(savedBallots, file, indent=4)  # Using indent for pretty printing

            self.on_status_update("Done!")
        
        asyncio.run(self.process_downloading_ballots(sentBallots, download))
        
    async def process_downloading_ballots(self, sentBallots, download):
        print("Launching the browser to process downloads")
        browser = await launch(executablePath=chrome_path,
                            handleSIGINT=False, 
                            handleSIGTERM=False, 
                            handleSIGHUP=False)
        try:
            tasks = [self.process_download(ballot, download, browser) for ballot in sentBallots]
            await asyncio.gather(*tasks)
        finally:
            await browser.close()
            self.on_super_status_update("Downloads complete!")
            self.on_instruct('Go to the "downloads" folder, which is in the same folder this program is.')
                   
    async def process_download(self, ballot, type, browser):
        print("Processing tournament name and the export paths/export file names")
        if ballot['type'] == 'Debate':
            ballotName = re.sub(r"\b(Round|Debate|Court|Flt|Flight|A|B)\b|[,]", '', ballot['round']).replace(' ', '')
            ballotName = ballotName + ": BYE" if ballot.get('bye') else ballotName
        else:
            print(ballot['round'])
            ballotName = re.sub(r'\bSpeech\b|\bRound\b', '', ballot['round'])
            ballotName = re.sub(r'\s+', '', ballotName)
            ballotName = re.sub(r'(\d)[AB]', r'\1', ballotName)
            ballotName = f"{ballot['speechType'][:4]}{ballotName}"
            print(ballotName)
            
        modifyPerson = ballot.get('person', ballot.get('person', ''))
        modifyPerson = re.sub(r"[ a-z]", "", modifyPerson)
        numbering = f"_Ballot#{str(ballot['ballotNum'])}" if ballot['ballotNum'] != 0 else ""
        userFileName = f"{modifyPerson}_{self.currentYearSelected}{ballot['abbreviatedtournament']}_{ballotName}{numbering}"
        serverFileName = ballot['index']
        html_content = ballot['formatted_html']
        if type == 'PDF':
            print("It's a pdf!")
            userExportPath = os.path.join(altering_parent_dir, "downloads", "pdfs", f"{userFileName}.pdf")
            serverExportPath = os.path.join(savedpdfsPath, f"{serverFileName}.pdf")
            if not os.path.exists(userExportPath):
                if os.path.exists(serverExportPath):
                    shutil.copy(serverExportPath, userExportPath)
                else:
                    try:
                        page = await browser.newPage()
                        await page.setContent(html_content)
                        await page.pdf({'path': userExportPath, 'format': 'A4'})
                    finally:
                        await page.close()
                    shutil.copy(userExportPath, serverExportPath)
            self.on_status_update(f"{userFileName} converted to PDF!")
        elif type == 'ETHANJOHN':
            print("It's a JSON (Ethan)")
            userExportPath = os.path.join(altering_parent_dir, "downloads", "jsons", f"{userFileName}.json")
            serverExportPath = os.path.join(savedjsonsPath, f"{serverFileName}.json")
            if not os.path.exists(userExportPath):
                if os.path.exists(serverExportPath):
                    shutil.copy(serverExportPath, userExportPath)
                else:
                    os.makedirs(os.path.dirname(userExportPath), exist_ok=True)
                    os.makedirs(os.path.dirname(serverExportPath), exist_ok=True)
                    variables = {key: val for key, val in ballot.items() if key != 'formatted_html'}
                    data_to_write = {
                        "Variables_Written_To_Html": variables,
                        "Html_Written": html_content
                    } 
                    with open(serverExportPath, 'w') as json_file:
                        json.dump(data_to_write, json_file, indent=4)
                    shutil.copy(serverExportPath, userExportPath)
                self.on_status_update(f"{userFileName} converted to JSON!")
        elif type == 'DOCX':
            print("It's a DOCX!")
            userExportPath = os.path.join(altering_parent_dir, "downloads", "docs", f"{userFileName}.docx")
            serverExportPath = os.path.join(saveddocsPath, f"{serverFileName}.docx")
            if not os.path.exists(userExportPath):
                if os.path.exists(serverExportPath):
                    shutil.copy(serverExportPath, userExportPath)
                else:
                    os.makedirs(os.path.dirname(userExportPath), exist_ok=True)
                    os.makedirs(os.path.dirname(serverExportPath), exist_ok=True)
                    pdf_path = serverExportPath.replace('.docx', '.pdf')
                    if not os.path.exists(pdf_path):
                        try:
                            page = await browser.newPage()
                            await page.setContent(html_content)
                            await page.pdf({'path': pdf_path, 'format': 'A4'})
                        finally:
                            await page.close()
                    cv = Converter(pdf_path)
                    cv.convert(serverExportPath, start=0, end=None)
                    cv.close()
                    os.remove(pdf_path)
                    shutil.copy(serverExportPath, userExportPath)
                self.on_status_update(f"{userFileName} converted to DOCX!")        
    
    
                
        
        
        

        
        
        

    def sortAndAddBallots(self, tournaments, sentBallots, allBallots, download):
        
        if config['settings'][6]['value'] != True:
            print("Writing any new ballot info to file")
            self.on_status_update("Saving ballot info for offline use...")
            if 'years' in savedBallots.get(currentUser, {}) and self.currentYearSelected in savedBallots[currentUser]['years']:
                existing_ids = {ballotID['ballotJudgeId'] for ballotID in savedBallots[currentUser]['years'][self.currentYearSelected].get('savedBallotsIDs', [])}
                existing_ballots = {ballot['ballotJudgeId'] for ballot in savedBallots[currentUser]['years'][self.currentYearSelected].get('savedBallots', [])}
            else:
                existing_ids = set()
                existing_ballots = set()
            newIDsFetched = [ballotID for ballotID in allBallots if (ballotID['ballotJudgeId'] not in existing_ids) and (ballotID['ballotJudgeId'] in {ballot['ballotJudgeId'] for ballot in sentBallots})]
            newBallotsFetched = [ballot for ballot in sentBallots if ballot['ballotJudgeId'] not in existing_ballots]
            
            
            print(self.currentYearSelected)
            savedBallots[currentUser]['years'][self.currentYearSelected]['savedBallotsIDs'].extend(newIDsFetched) 
            savedBallots[currentUser]['years'][self.currentYearSelected]['savedBallots'].extend(newBallotsFetched)
            with open(os.path.join(altering_script_dir, 'data', 'savedBallots.json'), 'w') as file:
                json.dump(savedBallots, file, indent=4)  # Using indent for pretty printing

        
        data = sentBallots
        
        
        prelimGroups = {}
        round_pattern = re.compile(r'\bRound ([1-6])\b')
        for ballot in data:
            if ballot['type'] == 'Debate' and round_pattern.search(ballot['round']):
                key = ballot['tournament']
                if key not in prelimGroups:
                    prelimGroups[key] = []
                prelimGroups[key].append(ballot)
        prelimRoundsWithBye = {tournament: ballots for tournament, ballots in prelimGroups.items() if len(ballots) < 6}
        for ballots in prelimRoundsWithBye.values():
            existing_rounds = {round_pattern.search(ballot['round']).group(1) for ballot in ballots if round_pattern.search(ballot['round'])}
            print(len(ballots))
            for i in range(1, 7):
                if str(i) not in existing_rounds:
                    ballotToAppend = {
                        'bye': 'bye',
                        'type': 'Debate',
                        'tournament': ballots[0]['tournament'],
                        'abbreviatedtournament': ballots[0]['abbreviatedtournament'],
                        'round': re.sub(r'\b[1-6\b]', str(i), ballots[0]['round']),
                        'output_image': "BallotImageBYE.jpg"
                    }
                    ballots.append(ballotToAppend)
                    data.append(ballotToAppend)
            print([str(b['round']) for b in ballots])
            print("Here^")
        tournament_index = {name: index for index, name in enumerate(tournaments)}
        
        def extract_round_details(round_name):
            print("Extracting what kind of round it is")
            round_name = re.sub(r"\b(Debate|Court|Flt|Flight|A|B)\b|[,]", '', round_name)
            round_name = re.sub(r'\s+', ' ', round_name).strip()
            natashasanchez = round_name.split(' ')
            style = natashasanchez[0]
            
            round_detail = ' '.join(natashasanchez[1:])
            style = re.sub(r'\s+', '', style).strip().lower()
            round_detail = re.sub(r'\s+', '', round_detail).strip().lower()
            print(style, round_detail)
            return style, round_detail

        def sort_key(ballot):
            tournament_priority = tournament_index.get(ballot['tournament'], float('inf'))
            if ballot['type'] == 'Debate':
                print("Sorting for debate ballots")
                style, round_detail = extract_round_details(ballot['round'])
                debate_style_priority = {
                    'ld': 0,
                    'tp': 1,
                    'moot': 2
                }    
                round_priority = {
                    'finals': 1,
                    'semifinals': 2,
                    'quarterfinals': 3,
                    'octafinals': 4,
                    'doubleoctafinals': 5,
                    'tripleoctafinals': 6,
                    'round6': 7,
                    'round5': 8,
                    'round4': 9,
                    'round3': 10,
                    'round2': 11,
                    'round1': 12
                }
                return (
                    tournament_priority,  # Primary grouping for debates
                    0,
                    debate_style_priority.get(style, float('inf')),  # Prioritize 'TP' over 'LD'
                    round_priority.get(round_detail, float('inf'))  # Specific round detail priority
                )
            else:
                print("Sorting for speech ballots")
                round_detail = re.sub(r'\s+', '', ballot['round']).strip().lower()
                speech_round_priority = {
                    'speechfinals': 1,
                    'speechsemifinals': 2,
                    'speechquarterfinals': 3,
                    'speechoctafinals': 4,
                    'speechround3b': 5,
                    'speechround3a': 6,
                    'speechround2b': 7,
                    'speechround2a': 8,
                    'speechround1b': 9,
                    'speechround1a': 10
                }
                # Construct sort key for speeches
                return (
                    tournament_priority,  # Primary grouping for speeches
                    1,  # Alphabetically by speech event name
                    ballot['speechType'],
                    speech_round_priority.get(round_detail, float('inf'))
                    
                )
        self.fetchedBallots = sorted(data, key=sort_key)
        
        
        
        print("fetchedBallots has been sorted.")
        finalsGroups = {}
        for ballot in self.fetchedBallots:
            event_key = ballot.get('eventName') or ballot.get('speechType')
            key = (event_key, ballot['tournament'], ballot['round'])
            if key not in finalsGroups:
                finalsGroups[key] = []
            finalsGroups[key].append(ballot)
        finalsRounds = [b for ballots in finalsGroups.values() if len(ballots) == 5 for b in ballots]
        superFinalsRounds = [b for ballots in finalsGroups.values() if len(ballots) == 7 for b in ballots]
        GIGARounds = [b for ballots in finalsGroups.values() if len(ballots) == 9 for b in ballots]
        

            
        
        print(f"Found prelim rounds with a bye. There are {len(prelimRoundsWithBye)} rounds.")
        print(f"Found finals rounds. We have {len(finalsRounds)} finals rounds")
        finalsOrder = [1, 2, 3, 0, 4]  # Fill center, then sides
        superFinalsOrder = [2, 3, 4, 1, 5, 0, 6]
        GIGAFinalsOrder = [3, 4, 5, 2, 6, 1, 7, 0, 8]
        finals_counter = 0
        super_finals_counter = 0
        GIGA_counter = 0
        regular_counter = 0
        for ballot in self.fetchedBallots:
            row_multiplier = 3 * (finals_counter // 5) + 3 * (regular_counter // 3) + 3 * (super_finals_counter // 7) + 3 * (GIGA_counter // 9)
            if ballot in finalsRounds:
                print("Using 5 columns for these finals rounds")
                col_index = finalsOrder[finals_counter % 5]
                finals_counter += 1
            elif ballot in superFinalsRounds:
                col_index = superFinalsOrder[super_finals_counter % 7]
                super_finals_counter += 1
            elif ballot in GIGARounds:
                col_index = GIGAFinalsOrder[GIGA_counter % 9]
                GIGA_counter += 1
                
            else:
                print("Using 3 columns for normal ballots")
                col_index = (regular_counter % 3) + 1
                regular_counter += 1

            print("Processing tournament name and formatting its size")
            if ballot['type'] == 'Debate':
                ballotName = re.sub(r"\b(Round|Debate|Court|Flt|Flight|A|B)\b|[,]", '', ballot['round']).replace(' ', '')
                ballotName = ballotName + ": BYE" if ballot.get('bye') else ballotName
            else:
                ballotName = re.sub(r'\bSpeech\b|\bRound\b', '', ballot['round'])
                ballotName = re.sub(r'\s+', '', ballotName)
                ballotName = re.sub(r'(\d)[AB]', r'\1', ballotName)
                ballotName = ballot['speechType'][:4] + ballotName

            print(ballot)
            tournament_label = QLabel(ballot['abbreviatedtournament'])
            tournament_label.setWordWrap(True)
            tournament_label.setAlignment(Qt.AlignCenter)
            print("Adding button and preview image")
            ballotButton = QPushButton(ballotName)
            ballotButton.setToolTip('View Ballot')
            if not ballot.get('bye'):
                ballotButton.clicked.connect(lambda _, b=ballot['index'], f=ballot['formatted_html'], n=ballotName: self.display_ballot(b, f, n))
            image_label = OriginalQLabel()
            pixmap = QPixmap(ballot['output_image'])
            hundred = int(100 * multiplier)
            image_label.setPixmap(pixmap.scaled(hundred, hundred, Qt.KeepAspectRatio))
            image_label.setFixedSize(hundred, hundred)
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(int(15 * multiplier))
            shadow.setXOffset(int(5 * multiplier))
            shadow.setYOffset(int(5 * multiplier))
            shadow.setColor(Qt.black)
            image_label.setGraphicsEffect(shadow)
            if not ballot.get('bye'):
                image_label.ballot_index = ballot['index']
                image_label.formatted_html = ballot['formatted_html']
                image_label.ballot_name = ballotName
                image_label.installEventFilter(self)
                
                downloadButton = QPushButton()
                downloadButton.setIcon(QIcon(os.path.join(altering_script_dir, 'silaswingate.png')))
                downloadButton.setIconSize(QSize(int(25 * multiplier), int(25 * multiplier)))
                downloadButton.setToolTip('Download individual ballot in PDF format')
                downloadButton.clicked.connect(lambda _, l=[ballot], d='PDF': asyncio.run(self.process_downloading_ballots(l, d)))

            buttonsContainer = QWidget()
            buttonsLayout = QHBoxLayout(buttonsContainer)
            buttonsLayout.setSpacing(0)
            
     
            
            
            buttonsLayout.addWidget(ballotButton, 3)
            if not ballot.get('bye'):
                buttonsLayout.addWidget(downloadButton, 1)

            print("Placing ballot on grid now")
            self.gridLayout.addWidget(tournament_label, row_multiplier, col_index, alignment=Qt.AlignCenter)
            self.gridLayout.addWidget(image_label, row_multiplier + 1, col_index, alignment=Qt.AlignCenter)
            self.gridLayout.addWidget(buttonsContainer, row_multiplier + 2, col_index, alignment=Qt.AlignCenter)                
                    
        self.setup_stats(tournaments)
        self.on_super_status_update('Done!')
        self.on_instruct('Ballots are now in the "View Ballots" and "Stats" pages.')
        
    def eventFilter(self, source, event):
        if event.type() == event.MouseButtonPress:
            if event.button() == Qt.LeftButton and isinstance(source, OriginalQLabel):
                print("Image clicked")
                self.display_ballot(source.ballot_index, source.formatted_html, source.ballot_name)
                return True
        return super().eventFilter(source, event)
    
    def resetGridLayout(self, layout):
        print("Removing all the ballots in the grid")
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()       
            
    def display_ballot(self, ballot_index, formatted_html, ballotName):
        print("Creating a ballot window if there isn't one and adding the ballot clicked.")
        if self.ballotWindow is None:
            self.ballotWindow = BallotDisplayWindow()
        if self.ballotWindow.isMinimized():
            self.ballotWindow.showNormal()
        self.ballotWindow.show()
        self.ballotWindow.addBallot(ballot_index, formatted_html, ballotName)
        
    def closeEvent(self, event):
        print("Closing...")
        if self.ballotWindow:
            self.ballotWindow.close()
        event.accept()
        



if __name__ == '__main__':
    # Define the exception handling function
    def exception_hook(exctype, value, traceback):
        # Print the exception details to the console or log it
        print(f"Unhandled exception: {exctype}, {value}")
        # Display an error message box to the user
        QMessageBox.critical(None, "Application Error", f"""A rare error occurred. The program does not know how to handle it. Usually, you can just close this window and everything will work okay. If that doesn't work, close the app and reload it. Here's the error:
                             
An unexpected error occurred: {value}""")
        # Call the normal exception hook after handling
        sys.__excepthook__(exctype, value, traceback)

    # Set the custom exception hook
    sys.excepthook = exception_hook

    # Create the application instance
    app = QApplication(sys.argv)
    
    screen = QDesktopWidget().screenGeometry()
    setWidth = int(screen.width() * 0.5)
    setHeight = int(screen.height() * 0.75)
    multiplier = int(screen.width() * 0.4) / 1024
    print(multiplier)
    legacyStyles = f"""
#menuBarWidget {{
    background-color: green;
    height: {60 * multiplier}px;
    max-height: {60 * multiplier}px;
    padding: 0;
    margin: 0
}}
#title {{
    color: white;
    margin-left: {20 * multiplier}px;
    font-size: {20 * multiplier}px
}}
#menuButton, #clickedMenuButton {{
    background-color: transparent;
    border: none;
    padding: {5 * multiplier}px
}}
#statsContainer, #viewBallotsContainer, #error_label, #home_label, QScrollArea {{
    border: none;
}}
"""

    defaultStyles = f"""
#mainContainer, QMainWindow {{
    background: qlineargradient(
        spread:pad, x1:0, y1:0, x2:0, y2:1,
        stop:0 #a1c4fd, stop:1 #c2e9fb
    );
    margin: 0;
    padding: 0;
}}
#statsContainer, #viewBallotsContainer, #error_label, #home_label, QScrollArea {{
    background: transparent;
    border: none;
}}
QScrollBar:vertical {{
    background: transparent;
    width: {6 * multiplier}px;
}}
QScrollBar::handle:vertical {{
    background-color: rgba(0,0,0,0.6)
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal,
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: none;
}}
QPushButton, QLineEdit {{
    background: rgba(225,250,255,1);
}}
QPushButton, QLineEdit, QLabel, QWidget {{
    font-size: {int(18 * multiplier)}px;
}}

#menuBarWidget {{
    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, 
stop:0 rgba(0, 0, 0, 255), 
stop:0.36 rgba(14, 0, 138, 255), 
stop:1 rgba(161, 196, 253, 255));
    min-height: {120 * multiplier}px;
    padding: 0;
    margin: 0
}}
#title {{
    font-family: 'Times';
    font-size: {int(40 * multiplier)}px;
    font-weight: bold;
    font-style: italic;
    color: rgba(225,250,255,1);
}}
#menuButton, #clickedMenuButton {{
    color: rgba(225,250,255,1);
    border: none;
    margin: 0px;
    font-size: {int(18 * multiplier)}px;
    padding: {5 * multiplier}px;
}}
#menuButton {{
    background: qlineargradient(
        x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0.92 rgba(2, 0, 36, 0),
        stop: 0.98 rgba(2, 0, 30, 0),
        stop: 1.0 rgba(0, 0, 0, 0)
    );
}}
#menuButton:hover {{
    background: qlineargradient(
        x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0.89 rgba(2, 0, 36, 0),
        stop: 0.96 rgba(2, 0, 30, 255),
        stop: 1.0 rgba(0, 0, 0, 255)
    );
}}
#clickedMenuButton {{
    background: qlineargradient(
        x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0.85 rgba(2, 0, 36, 0),
        stop: 0.95 rgba(2, 0, 30, 255),
        stop: 1.0 rgba(0, 0, 0, 255)
    );
    font-weight: bold;
}}
"""

    
    
    # Instantiate and show your main window
    ex = BallotReader()
    ex.show()
    
    # Execute the application and exit
    sys.exit(app.exec_())

