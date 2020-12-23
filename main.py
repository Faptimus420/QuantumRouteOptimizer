#Quantum Route Optimizer - logic core. Supplement to bachelor thesis made as part of the Business Economics & IT programme at KEA, by Patrik Žori and Kieran Olivier Holm, for A.P. Møller - Mærsk, 2020

#----------Settings----------
debug=True  #Set variable to 'True' to enable debug mode. Default: False
sapiToken=''  #The API token used to access the D-Wave annealer. Default: None
apiURL='https://cloud.dwavesys.com/sapi'  #The URL to access the D-Wave annealer. Default: https://cloud.dwavesys.com/sapi
solver=''  #The quantum annealer to be used to solve the problem. Default: None
#----------------------------

#----------Start initialization----------
print('Initializing, please wait...\n')
if not sapiToken or not solver: #Tests whether the API access has been preconfigured or if it will need to be configured as part of initialization
    presetAPI=False
else:
    presetAPI=True

#Loading libraries
import datetime,os
from time import sleep
from csv import reader
from sys import exit,executable

from platform import system
user_os=system()  #Reads the user's OS
print('Built-in libraries loaded') if debug==True else ''

from subprocess import check_output #Adapted from StackExchange (Answer by Artur Barseghyan, https://stackoverflow.com/questions/1051254/check-if-python-package-is-installed)
required_pkgs = ['dwave-ocean-sdk','numpy','xlrd']  #List of required external libraries
reqs = check_output([executable, '-m', 'pip', 'freeze'])
installed_pckgs = [r.decode().split('==')[0] for r in reqs.split()] #Tests if required libraries are installed
for package in required_pkgs:   #Prints information that a required library is missing and how to install it, based on user's OS
    if package not in installed_pckgs:
        print(f'The package "{package}" is required to run the Quantum Route Optimizer.')
        if user_os == 'Windows':
            print(f'Open the Anaconda Prompt (or the Command Prompt, if you are not using the Anaconda Distribution), and run the following command: "pip install {package}" without the quotes to install the {package} package.')
        else:
            print(f'Open the Anaconda Prompt (or the Terminal, if you are not using the Anaconda Distribution), and run the following command: "pip install {package}" without the quotes to install the {package} package.')
            exit('The program will now terminate.')
from dwave.cloud import Client
import xlrd
print('External libraries loaded') if debug == True else ''


#Testing modules
if os.path.isfile('./calculations.py')==True:   #Tests if the calculations module is present
    if debug==True:
        print('Calculations module OK')
else:
    exit('calculations.py module missing. The module is responsible for preparing and performing calculations on the quantum annealer. Make sure the calculations.py file is located in the same folder as the main.py file.\nThe program will now terminate.')
import calculations


#Testing databases
if os.path.isfile('./distances.xlsx')==True:    #Tests if the distance dataset is present
    if debug==True:
        print('Distance dataset OK')
else:
    exit('distances.xlsx not found. The distances.xlsx dataset is required to proceed, as it contains the distances between the sea ports. Make sure the distances.xlsx file is located in the same folder as the main.py file.\nThe program will now terminate.')
print('Building the distance database...')
distanceBook = xlrd.open_workbook('./distances.xlsx')   #Lines 61 to 67 will build a dictionary of sea distances between ports. Structure: a dictionary where the keys are tuples of country A (first column of sheet), country B (second column of sheet), and the values are the appropriate distance between them (third column of sheet)
distanceSheet = distanceBook.sheet_by_index(0)
distances = {}
for row in range(1,distanceSheet.nrows):
    locations = (distanceSheet.cell(row,0).value,distanceSheet.cell(row,1).value)
    distanceVal = int(distanceSheet.cell(row,2).value)
    distances[locations] = distanceVal

if os.path.isfile('./countries.csv')==True: #Tests if the country code database is present
    if debug==True:
        print('Country database OK')
else:
    exit('countries.csv not found. The countries.csv database contains a list of countries with access to the sea, along with their ISO 3116 alpha-3 shortcodes. Make sure the countries.csv file is located in the same folder as the main.py file.\nThe program will now terminate.')
print('Building the country code database...')
with open('./countries.csv',encoding='utf-8') as f:  #The with loop builds the dictionary of country names and their ISO 3116 shortcodes. Structure: a dictionary where the keys are the full country names and the values their appropriate shortcodes
    next(f)
    reader = reader(f, skipinitialspace=True)
    countries = dict(reader)
print('Databases OK') if debug == True else ''


#Global functions
def func_MainMenu():    #The main menu text function
    sleep(3) if debug == False else ''
    print('\n\n***Quantum Route Optimizer***')
    print('Current time: '+datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
    print('\nDebug mode active\n' if debug==True else '\n')
    print(f'Selected solver: {solver}')
    print(f'API token: {sapiToken}\n')
    print('Write 1 to compute an optimal route.')
    print('Write 2 to re-do the API access setup.')
    print('Write 3 to view the About and the Licence agreements.')
    print('Leave empty to quit.')

def func_setup():  #Function used to configure access to the quantum annealers
    global sapiToken,solver,setupRedo,presetAPI
    skipRestSetup=0
    if not sapiToken or setupRedo==1:   #Asks for API access token if one is not preconfigured, or if reconfiguration has been initialized
        tokenOld=sapiToken if setupRedo==1 else ''
        sapiToken=str(input('\nIn order to access the D-Wave annealers, you need to have a valid API token. If you do not have one, create a free account at https://cloud.dwavesys.com/leap/ to get it.\nEnter your token now: '))
    if not solver or setupRedo==1:  #Asks to select D-Wave solver if one is not preconfigured, or it reconfiguration has been initialized
        print("You must select which quantum annealer you'd like to use to solve the problem. Fetching a list of available solvers...")
        if setupRedo==1 and presetAPI!=True:    #If reconfiguration is taking place, saves old configuration to restore it in case reconfiguration fails
            clientOld,solverOld=client,solver
            client,solvers=None,None
        client=Client.from_config(token=sapiToken,endpoint=apiURL)  #Fetching a list of avialable solvers from the D-Wave API. The next line filters them to online-only, standalone QPUs (no hybrid solvers) only.
        solvers=client.get_solvers(online=True,qpu=True,hybrid=False)
        print('\nAvailable solvers:')
        if not solvers and setupRedo!=1:
            print("There are no solvers available. This means that the D-Wave cloud access system is under maintenance, you don't have an active internet connection, or you have entered an invalid API token. Please try again.")
            func_setup()
        elif not solvers and setupRedo==1:
            print("There are no solvers available. This means that the D-Wave cloud access system is under maintenance, you don't have an active internet connection, or you have entered an invalid API token. Reverting to previous configuration.")
            solver,client,sapiToken=solverOld,clientOld,tokenOld
            skipRestSetup=1
        if skipRestSetup!=1:
            for x in solvers:
                print(x)
            solver=str(input("\nEnter the solver ID without apostrophes ('). Make sure to enter the ID correctly, otherwise calculations will fail: ")).strip()
    setupRedo=0
    print('API access configured successfully.')

def func_prepare(): #Function used to prepare an instance of the TSP to be solved on the annealer. In this function, the countries to be visited are selected.
    global solver,countries
    print('Select the countries that should be visited along the route. Each country should only be visited once.')
    print('Please select at least 3 countries, with a maximum of 9 for the 2000Q system, or 16 for the Advantage system.')
    print('List of available countries:')
    sleep(5)
    print(', '.join('{}'.format(k) for k in countries.keys()))  #Prints a list of available countries using the shortcode dictionary
    while True:
        try:    #Only integers are allowed
            selectionCount=abs(int(input('\nHow many countries will be visited? Please note that the larger the amount, the less accurate the result may be: ')))
        except ValueError:
            print("That's not a number. Please try again.")
            continue
        else:
            if selectionCount < 3:
                print('You need to select at least 3 countries. Please try again.')
                continue
            elif selectionCount > 9 and '2000Q' in solver:
                print('That is too many countries for the 2000Q system. The maximum is 9. Please try again.')
                continue
            elif selectionCount > 16 and 'Advantage' in solver:
                print('That is too many countries for the Advantage system. The maximum is 16. Please try again.')
                continue
            break
    selectionCurrent=1
    selection=[]    #This list will hold the selected countries which are to be visited
    while selectionCurrent <= selectionCount:
        selectionNew=input(str(f'\nEnter the full name of a country to be visited, based on the above list (special characters included, matching case). Selection {selectionCurrent} of {selectionCount}: '))
        if selectionNew not in list((k) for k in countries.keys()):
            print('Invalid country. Please try again.')
            continue
        elif selectionNew in selection:
            print(f'{selectionNew} is already on the list. Please try again.')
            continue
        selection.append(selectionNew)
        selectionCurrent+=1
        print(f'{selectionNew} added to selection.')
    print('\nCountry selection finished. The final list is: '+', '.join(str(x) for x in selection))
    while True: #Confirms whether to proceed with the selected countries
        proceedSelection=str(input("Would you like to proceed? If not, the operation will be cancelled and you'll return to the main menu [Y/N]: ")).upper().strip()
        if proceedSelection[0] not in ['Y','N']:
            print('Invalid choice. Try again.\n')
            continue
        elif proceedSelection[0]=='N':
            return None,True
        break
    selectionTemp = []
    for i,x in enumerate(selection):    #Translates the selected countries into the appropriate shortcodes
        selection[i] = countries[x]
    return selection,None

print('Global functions OK') if debug == True else ''


setupRedo=0
func_setup()
print('\nIntialization complete. Ready!')
#----------End initialization----------

callMenu=True
print("DISCLAIMER: This script serves only as a proof of concept. While it does attempt to solve an instance of the Traveling Salesman Problem using D-Wave's annealers, the results should not be taken as definitive.\nQuantum annealing technology is still under development, and this script would require much more tweaking and optimization to produce truly reliable results. Some outcomes may be nonsensical, and due to the probabilistic nature of quantum mechanics, re-running the calculation on the same set of countries can produce entirely different results each time.\nFurther development is required to improve result accuracy - some suggestions on how the accuracy may be improved are presented in the thesis this code is a supplement to.")
while True:
    func_MainMenu() if callMenu==True else ''
    menuChoice = str(input('What would you like to do?: ' if callMenu == True else '\nWhat would you like to do now?: '))
    callMenu=True
    if menuChoice == '' or menuChoice == None:  #If menu choice is blank, the program will quit
        print('Attempting to quit...') if debug==True else ''
        break
    elif menuChoice == '1': #If menu choice is 1, creating an instance of the TSP will begin
        selection=[]
        print('\nSTEP 1 OF 5: Country selection:')
        cancel=None
        selection,cancel = func_prepare()  #Calls the func_prepare global function to select countries to be visited
        if cancel == True:
            continue
        inputMatrix = []
        sleep(2)
        print('\nSTEP 2 OF 5: Generating the distance matrix...')
        inputMatrix = calculations.func_CreateDistanceMatrix(selection,distances)
        qubo,distanceMatrixLength = None,None
        sleep(2)
        print('\nSTEP 3 OF 5: Encoding distance matrix as QUBO problem and adding constraints...')
        qubo,distanceMatrixLength = calculations.func_createQUBO(inputMatrix)
        timeStart,exception=None,None
        sleep(2)
        print('\nSTEP 4 OF 5: Performing calculation on D-Wave annealer. Please wait for response...')
        binaryResult,timeStart,exception = calculations.func_solveTSPdwave(distanceMatrixLength,sapiToken,apiURL,solver,qubo)
        if exception == True:   #If there was an error getting a result from the annealer, cancel the calculation and return to menu
            continue
        decodedResult = None
        sleep(2)
        print('\nSTEP 5 OF 5: Decoding solution...')
        decodedResult,distribution,timeEnd = calculations.func_decodeResult(binaryResult)
        calcTime = (timeEnd - timeStart) - 2    #Subtracts 2 seconds from the calculation time to account for the 2 second sleep. The timer includes sending the problem to the annealer, the annealer performing the calculation, and receiving the response.
        costs = [(sol, calculations.func_calculateCost(inputMatrix, sol), distribution[sol]) for sol in distribution]   #Lines 215 and 216 have been adapted from M. Stęchły's code; this creates a list of costs for each individual possible solution
        strList = [selection[i] for i in decodedResult]
        for i,x in enumerate(strList):  #Translates the resulting country sequence from their shortcodes back to full names by reversing the countries dictionary
            strList[i] = {v:k for k,v in countries.items()}[x]
        sleep(2)
        print('\n----------|RESULT|----------')
        print(f'According to the D-Wave {solver} annealer, the optimal route based on the sea distance between the selected countries is: {" -> ".join(map(str,strList))}')
        print(f'Calculation time: {round(calcTime,2)} seconds')
        if debug == True:
            print(f'\nFull distribution list: {distribution}')
            print('\nFull cost list:')
            for cost in costs:
                print(cost)
        while True:
            proceedClassical = str(input("\n\nFor time comparison, would you like to perform the same calculation using a classical, brute force search algorithm? Note: Can take a very long time to finish, depending on number of countries and your computer's performance [Y/N]: ")).upper().strip()
            if proceedClassical=='Y':
                print('Performing brute force calculation. Please wait, or close the program to cancel...')
                bestBrute,bestBruteCost,bruteTime = calculations.func_solveTSPbruteforce(distanceMatrixLength,inputMatrix)
                strBruteList = [selection[i] for i in bestBrute]
                for i,x in enumerate(strBruteList):  #Translates the resulting country sequence from their shortcodes back to full names by reversing the countries dictionary
                    strBruteList[i] = {v:k for k,v in countries.items()}[x]
                print(f'\nBrute force result: The optimal route is {" -> ".join(map(str,strBruteList))}.\tCalculation time: {round(bruteTime,2)} seconds\t\tCost: {bestBruteCost}')
                break
            elif proceedClassical=='N':
                break
            else:
                print('Invalid choice. Try again.\n')
                continue
        continue
    elif menuChoice == '2': #If menu choice is 2, will reconfigure API access
        setupRedo=1
        func_setup()
        callMenu=False
        continue
    elif menuChoice == '3': #If menu choice is 3, will display the About
        print('\nQuantum Route Optimizer, v0.1.0')
        print('Scripted in Python 3.7.6 (Anaconda Individual distribution), built in Atom')
        print('Uses of variable-modified code snippets made by Michał Stęchły, Jan Osch, et. al; and by Michał Stęchły, Petar Korponaić, have been denoted by comments.\nApache 2.0 license, respectively © 2018 Bohr Technology; and © 2019 Witold Kowalczyk, Michał Stęchły. https://github.com/BOHRTECHNOLOGY/quantum_tsp https://github.com/BOHRTECHNOLOGY/tsp-demo-unitary-fund')
        print("\nUses D-Wave Ocean Tools SDK to access the D-Wave quantum annealers. Apache 2.0 license, © D-Wave Systems Inc. https://github.com/dwavesystems/dwave-ocean-sdk/")
        print("Also uses a modified CERDI seadistance database as the dataset of port distances. Simone Bertoli et. al. https://hal.archives-ouvertes.fr/halshs-01288748v1")
        print("Also uses a filtered database of countries and their ISO 3116 alpha-3 shortcodes by Luke Duncalfe et. al. CC BY-SA 4.0. https://github.com/lukes/ISO-3166-Countries-with-Regional-Codes")
        print('\nAuthors: Patrik Žori, Kieran Olivier Holm')
        print('Made as a supplement to bachelor thesis written as part of the Business Economics & IT programme at KEA, Copenhagen, Denmark')
        print('Proof of concept made for demonstration at A.P. Møller - Mærsk HQ')
        print('v0.1.0: 2020; latest revision: 2020')
        callMenu=False
        sleep(7) if debug == False else ''
        continue
    else:   #Invalid menu choice
        print("\nYou've entered an invalid choice. Please try again.")
        callMenu=False
        continue
print('Main menu loop end') if debug == True else ''

print('\nThank you for using the Quantum Route Optimizer. Have a nice day!')
