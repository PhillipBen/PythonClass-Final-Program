# I certify, that this computer program submitted by me is all of my own work. Signed: Phillip Benson, 12/18/23


########## Beginning of Start-Up Details ##########  
import random
import csv
import os

numberOfTiles = [10, 10] #x, y.
completeTileArray = [] #Complete list of tiles to make calling each one easier
outerEdgeTileArray = [] #Zombies spawn on the outer edge of the map (1 tile ring). This lists all tile positions (An array/list of lists)
entityList = [] #Contains Humans and Zombies.
numberOfTurnsPassed = 0
totalKillCounter = 0 #Zombie deaths
totalDeathsCounter = 0 #Human deaths
totalKDA = 0 #Zombie deaths compared to human deaths 
statisticsSaveFile = "ZombieGameStatistics.csv"


def main(): #This is a summary of the entiry game! Simple functions that split the game into four important parts.
    #Create Tile System
    tileSetup()
    
    
    #Create Entities
    initializeEntities() 
    
    #Run Game
    runGame()
    
    
    #Print Final Stats, and Save Score to File
    printFinalStats()
    
    
########## Ending of Start-Up Details ##########  


########## Beginning of Turn-Based Functions ##########  
def runGame():
    global entityList
    global numberOfHumans
    global numberOfTurnsPassed
    
    """
    Temporary lists are created each round to hold humans and zombies. 
    We want the player to move before the zombies, so we need all humans selected first,
    and we want the user to choose which human they want to move in their own order, so we don't want to call specific humans in the same order,
    we want the user to choose the order (via human IDs).
    """
    #Initial Start Up
    printRules()  
    tempHumanEntityList = []
    tempZombieEntityList = []
    for entity in entityList: #Sort the remaining entities into the two lists
        if entity.faction == "Human":
            tempHumanEntityList.append(entity)
        else:
            tempZombieEntityList.append(entity)
    gridUpdate(tempHumanEntityList) 
    tempHumanEntityList = []
    tempZombieEntityList = []
    #End of Initial Start Up
    
    
    while len(tempHumanEntityList) >= 1 or numberOfTurnsPassed == 0:
        tempHumanEntityList = []
        tempZombieEntityList = []
        for entity in entityList: #Sort Humans into human list
            if entity.faction == "Human":
                tempHumanEntityList.append(entity)
            
        #Human Movement
        tempHumanEntityListCopy = tempHumanEntityList.copy() #For some reason, the moveAllHumans() was changing this base list, even though I sent the list as a parameter. - Reference: https://stackoverflow.com/questions/2612802/how-do-i-clone-a-list-so-that-it-doesnt-change-unexpectedly-after-assignment
        moveAllHumans(tempHumanEntityListCopy)  
        #Zombie Movement
        if len(tempHumanEntityList) <= 0:
            break #Game over
        else:
        
            for entity in entityList: #Sort zombies into zombie list. Need to keep it seperate from initializing human list, because if a zombie dies between turns, it should be removed before having the opportunity to attack / move.
                if entity.faction == "Zombie":
                    tempZombieEntityList.append(entity)
                    
            for entity in tempZombieEntityList: #Once all humans have been moved, move the zombies.
                tempHumanEntityList = HumanListRefresh()   
                if len(tempHumanEntityList) <= 0:
                    break #Game over
                else:
                    voidValue = entity.__moveUnit__(tempHumanEntityList)
            
            tempHumanEntityList = HumanListRefresh()          
            if len(tempHumanEntityList) <= 0:
                break #Game over
            else:
                spawnNewZombies(numberOfTurnsPassed) #Spawn a certain number of zombies each round
                
                numberOfTurnsPassed += 1 #Add 1 to the global turn counter.
                
                gridUpdate(tempHumanEntityList)  #After all movements are done, upgrade the grid.
        
 
def HumanListRefresh():
    global entityList
    
    newHumanList = []
    for entity in entityList: #Sort the remaining entities into the two lists
        if entity.faction == "Human":
            newHumanList.append(entity)
    return newHumanList
    

def printRules():
    print("Hello, and welcome to our Human VS Zombie game! This game was made by me, Phillip Benson.")
    print("The goal of this game is to survive as many turns as possible against the zombies. The zombies will continue spawning until you die.")
    print("You will first decide how many humans to fight for your team. Choose between 1 and 4 humans. Then the game will begin.")
    print("Zombies will slowly start to spawn. They are denoted as X#. The # stands for their ID number, so you can identify each one quickly.")
    print("During each turn, you will be able to move each human on the board. If you are next to a zombie, move towards the zombie, and the human will attack it.")
    print("Zombies will continue spawning, slowly growing more and more until you have too many to keep up with.")
    print("After all your humans died, you will be printed a score, showing how many zombies you killed, and other interesting information.")
    print("You will also be exported a .csv file to the local folder. This will show all your games, and all your data.")
    print("Thanks for reading! Now get out there, and good luck survivng!")
    print("\n\n")
            
    
def moveAllHumans(humanList):
    
    while len(humanList) > 0:
        movedTF = False
        userInput = input("Type a human ID (number) to move that human.")
        
        try:
            userInput = int(userInput)
            
            for entity in humanList:
                if entity.ID == userInput:
                    movedTF = entity.__moveUnit__(humanList)
                    break
                
            if movedTF == True:
                humanList.remove(entity)
                if len(humanList) >= 1:
                    gridUpdate(humanList) #Print a new grid every move so you can keep up with what you moved.
        except:
            print("Your input was not a valid number. Try again.")
        

def spawnNewZombies(numberOfTurnsPassed): #Make sure this is BEFORE the turn passed, not after.
    """
    Spawn 4 Zombies initially, around 1 per turn to start
    1, 2, 3, 4, 5, 6, etc
    This is how many zombies are spawned every round. Increases to a new spawn number every 4 rounds
    """
    global outerEdgeTileArray
    
    numberOfZombiesToSpawn = (numberOfTurnsPassed // 4) + 1
    
    for i in range(0, numberOfZombiesToSpawn):
        zombieAdded = False
        while zombieAdded == False:
            newZombiePosIndex = random.randrange(0, len(outerEdgeTileArray))
            newZombiePos = outerEdgeTileArray[newZombiePosIndex]
            if checkIfTileIsTaken(newZombiePos[0], newZombiePos[1])[0] == False:
                zombie = Entity("Zombie", newZombiePos)
                zombieAdded = True
########## Ending of Turn-Based Functions ##########  
    
   
########## Beginning of Map Details ##########   
class Tile:
    #The basic tile an entity can move on.
    
    ID = -1 #ID used to individualize each tile.
    x = -1 #Basic x and y pos, set to negative 1 as a placeholder. The grid here is only ++, so no negative positions to deal with.
    y = -1
    entityOnTile = "Null" #Null if there is no entity currently on tile, entity instance if there is one.
    def __init__(self, position, ID):
        global completeTileArray
        
        self.x = position[0]
        self.y = position[1]
        completeTileArray.append(self)
        self.ID = ID

def tileSetup():
    global numberOfTiles
    global outerEdgeTileArray
    
    tileID = 0
    for y in range(0,numberOfTiles[0]): #includes 0, stops at one before final number
        for x in range(0,numberOfTiles[1]):
            newTile = Tile([x,y], tileID)
            tileID += 1
            
            if x == 0: #outerEdgeTileArray determining. Finds smallest and largest x values, then adds there. Use elif instead of if to not add duplicate submissions, for instance on 0,0, and 10,10
                outerEdgeTileArray.append([x,y])
            elif x == numberOfTiles[0] - 1:
                outerEdgeTileArray.append([x,y])
            elif y == 0:
                outerEdgeTileArray.append([x,y])
            elif y == numberOfTiles[1] - 1:
                outerEdgeTileArray.append([x,y])

def gridUpdate(humanList): #The graphics that are displayed each turn. Make sure this happens AFTER the turn number increases by one.
    global completeTileArray
    global numberOfTiles
    
    """NOTE: This usage of index as increasing per call and autoselecting each tile in order is ONLY because of the way this program works.
    In a real use case scenario, we would either be calling the tiles by ID, by position, or by sorting the list first. However, because there
    are no obstacles, or no changing tile length/widths as the game changes, there is no need for a complex function like that. That is the
    difference between my program and real programs.
    """
    index = 0
    for y in range(0,numberOfTiles[1]): 
        for x in range(0,numberOfTiles[0]):
            if completeTileArray[index].entityOnTile != "Null":
                #print(str(completeTileArray[index].x) + str(completeTileArray[index].y), end="")
                #print(str(completeTileArray[index].entityOnTile.tileForEntity.x) + str(completeTileArray[index].entityOnTile.tileForEntity.y), end="")
                stringToPrint = "+"
                if completeTileArray[index].entityOnTile.faction == "Human":
                    stringToPrint = "O" + str(completeTileArray[index].entityOnTile.ID)
                else:
                    stringToPrint = "X" + str(completeTileArray[index].entityOnTile.ID)
                print(f'|{stringToPrint : ^5}', end='')
            else:
                print("|  +  ", end='')
            index += 1
        print("|")
    
    print("\nYour Team:")
    for entity in humanList:
        print("- Human" + str(entity.ID) + " can still be moved. They have " + str(entity.currentHealth) + " HP remaining. ")
        
def stepsToRange(userInput, entity): #Can't make a multi-tile move because we don't have a gui to click on.
    returnValue = [False, 0, 0, False]
    #print("Entity Selected: " + str(entity.ID))
    #print("Begining x and y: " + str(entity.tileForEntity.x) + str(entity.tileForEntity.y))
    entityPosX = entity.tileForEntity.x #Initial X and Y Pos
    entityPosY = entity.tileForEntity.y
    if userInput == "w": #The four classic movement keys. Inverse because of how we display the grid.
        entityPosY -= 1 
    if userInput == "s": 
        entityPosY += 1 
    if userInput == "a": 
        entityPosX -= 1 
    if userInput == "d": 
        entityPosX += 1 
    #print("Ending x and y: " + str(entityPosX) + str(entityPosY))
        
    isTileTakenData = checkIfTileIsTaken(entityPosX, entityPosY)
    #print("StepsToRange Return: " + str(isTileTakenData[0]))
    if isTileTakenData[0] == False:
        returnValue = [True, entityPosX, entityPosY, False]
    elif isTileTakenData[0] == True and isTileTakenData[1] != "Null": #isTileTakenData[1] != "Null" only when an enemy has been detected.
        entity.__attack__(isTileTakenData[1])
        returnValue = [True, entityPosX, entityPosY, True]
        
    return returnValue #If [0] is True, the tile is open to be taken. If False, it is filled, or doesn't exist (edge of map). If [3] is true, it attacked instead of moving.

def moveToNewTile(newPos, entityToMove):
    global completeTileArray
    
    instanceNumber = xAndYToTileArrayIndex(newPos[0], newPos[1])
    #print("Old Tile Pos: " + str(entityToMove.tileForEntity.x) + str())
    entityToMove.currentPos = newPos
    completeTileArray[instanceNumber].entityOnTile = entityToMove   #Add entity to new tile
    completeTileArray[xAndYToTileArrayIndex(entityToMove.tileForEntity.x, entityToMove.tileForEntity.y)].entityOnTile = "Null"          #Remove entity from old tile
    entityToMove.tileForEntity = completeTileArray[instanceNumber]  #Replace tile on this entity
    
def xAndYToTileArrayIndex(tileX, tileY):
    global numberOfTiles
    return int((tileY * numberOfTiles[0]) + tileX) 
    #Since the tile creation function loops through all values on y before going up an x, x is the multiplied value, and y is the single value
    
def xAndYToTotalDistance(entityOneX, entityOneY, entityTwoX, entityTwoY):
    """
    -NOTE: Because two entities can never be in the same tile, one of the axis may be the same for both entities, but the second axis NEVER will.
    -This means you will either have two different x and y distances, at lease one is 0 and one is +-1, or they will be the same, both +-1,
    but they will NEVER be both 0.
    -Therefore, when testing distance, we only have to check which wether the distance (no abs) is less than or greater than 0, because we are
    always testing the larger number [abs(totalXDistance) > abs(totalYDistance)], and since on is always 1+, the initial direction 
    we will move will always be based off a number greater than 0. 
    -However, if total distance equals one, this means the target is right next to the enemy, and can therefore attack. This means they won't
    move, but instead attack.
    """
    #print("X and Y Checked: Orig, New: " + str(entityOneX) + str(entityOneY) + str(entityTwoX) + str(entityTwoY))
    totalXDistance = entityOneX - entityTwoX
    totalYDistance = entityOneY - entityTwoY
    totalDistance = abs(totalXDistance) + abs(totalYDistance)
    return [totalDistance, totalXDistance, totalYDistance]
    
    
def checkIfTileIsTaken(inputX, inputY, *args): #Checks if the specific tile is currently occupied or not. Returns False if tile is not taken
    global completeTileArray
    returnValue = [True, "Null"]
    
    instanceNumber = xAndYToTileArrayIndex(inputX, inputY) 
    if instanceNumber <= len(completeTileArray): #If x or y is too high, it's like trying to walk off the map.
        #print("Tile Checked" + str(completeTileArray[instanceNumber].ID) + "-" + str(completeTileArray[instanceNumber].x) + str(completeTileArray[instanceNumber].y))
        if completeTileArray[instanceNumber].entityOnTile == "Null":
            returnValue = [False, "Null"]
        elif completeTileArray[instanceNumber].entityOnTile.faction == "Zombie": #Only using this for humans trying to attack zombies. Not built for both.
            returnValue = [True, completeTileArray[instanceNumber].entityOnTile] #Returns the entity so the human can attack that zombie.
        #else:
        #    returnValue = [False, "Null"] #If the tile is taken and it's not an enemy, then it has to be a friendly.
    return returnValue
    
def findNearestEntity(humanList, currentlyMovingEntity):
    """
    This function returns the direction that the entity should move to approach it's target. It returns in w,a,s,d.
    Currently this imports the human list, and finds the closest from that. This could be attached to entityList to find any entity.
    """
    entityListToExamine = humanList
    closestEntity = "Null"
    closestEntityDistance = -1
    distanceList = []
    finalDistanceList = []
    for entity in entityListToExamine: #Determine the closest entity
        distanceList = xAndYToTotalDistance(currentlyMovingEntity.currentPos[0], currentlyMovingEntity.currentPos[1], entity.currentPos[0], entity.currentPos[1])
        
        if closestEntity == "Null" or closestEntityDistance > distanceList[0]:
            closestEntity = entity
            closestEntityDistance = distanceList[0]
            finalDistanceList = distanceList
    #Use values 2 and 3 of the distanceList to determine which direction to take 
    #print("Zombie ID: " + str(currentlyMovingEntity.ID))
    #print("Zombie Current Pos: " + str(currentlyMovingEntity.currentPos[0]) + str(currentlyMovingEntity.currentPos[1]))
    #print("Distance from Human: " + str(finalDistanceList[0]))
    newX = currentlyMovingEntity.currentPos[0]
    newY = currentlyMovingEntity.currentPos[1]
    if finalDistanceList[0] == 1: #Close enough to attack
        print("Zombie attacks!")
        currentlyMovingEntity.__attack__(closestEntity) #Zombie attack!
    else:
        """
        Explaining the following lines:
        -If the entity cannot attack, then it is more than one tile away, and should move. If the x distance is bigger than the y distance,
        it should move closer on the x axis, and vise versa if the y is greater. 
        -Next, we check if the tile we want to move to is available. If it is, move. All done. If not, we need to try other options.
        -If we cannot move forewards, we must randomly choose an up or down direction. This makes things feel realistic, rather than always going
        up or always going down if another entity is in the way. This also allows the entity to circle around the human, making it harder for them, so they can be more easily be attacked by multiple zombies that are moving towards them from the same direction.
        -Therefore, a random value +1 or -1 will be chosen to move first. Then, if not available, try the other way. If both are blocked, the
        zombie is stuck, and should stay where it is. Since there is no obstacles in this game, it is better for the zombie to wait for the
        ahead obstacles to clear, rather than to backtrack and loose ground.
        
        #NOTE: if distancex = distancey, it will always choose to move y. This can cause back and forth looping (up 1, down 1, down 1, up 1, up 1, down 1, down 1, etc)
        """
        changedAxis = "Null"
        #print("X Distance: " + str(finalDistanceList[1]))
        #print("Y Distance: " + str(finalDistanceList[2]))
        if abs(finalDistanceList[1]) > abs(finalDistanceList[2]): #Distance in x is farther than distance in y.
            #print("Distance Further in x")
            if finalDistanceList[1] < 0: #See note in xAndYToTotalDistance function to see why we never have to check if the values both = zero.
                newX += 1
            else:
                newX -= 1
        else: #y > x or y = x
            #print("Distance Further in y")
            if finalDistanceList[2] < 0:
                newY += 1
            else:
                newY -= 1
        
        if checkIfTileIsTaken(newX, newY)[0] == False:
            #print("Moved")
            #print("Old Tile Pos" + str(currentlyMovingEntity.currentPos[0]) + str(currentlyMovingEntity.currentPos[1]))
            moveToNewTile([newX, newY], currentlyMovingEntity)
            #print("New Tile Pos" + str(currentlyMovingEntity.currentPos[0]) + str(currentlyMovingEntity.currentPos[1]))
        else:
        
            newX = currentlyMovingEntity.currentPos[0]
            newY = currentlyMovingEntity.currentPos[1]
            #If it can't move to the best spot, move to the alternate best spot.
            if abs(finalDistanceList[1]) > abs(finalDistanceList[2]): #Distance in x is farther than distance in y.
                if finalDistanceList[2] < 0: #See note in xAndYToTotalDistance function to see why we never have to check if the values both = zero.
                    newY += 1
                else:
                    newY -= 1
            else: #y > x or y = x
                if finalDistanceList[1] < 0:
                    newX += 1
                else:
                    newX -= 1
            
                if checkIfTileIsTaken(newX, newY)[0] == False:
                    moveToNewTile([newX, newY], currentlyMovingEntity)
                    """
                    If none of these options are available, then the zombie will just stay put. This means that the zombie cannot move
                    forwards or side to side when compared to it's target. Therefore, it is better to just stay put and wait for one of
                    the entities in front of it to move. There are no obstacles in this game, so it cannot get stuck and need to backtrack.
                    """
                
########## Ending of Map Details ########## 


########## Beginning of Entity Details ########## 

def initializeEntities():#Called before the game begins, the number of humans (1-9) is chosen by the player.
    global numberOfTiles
    global outerEdgeTileArray
    
    print("Welcome to the humans vs zombies simulator! Your task is to survive as long as possible against the waves of zombies.")
    humanNumber = 0
    while humanNumber < 1:
        try:
            humanNumber = int(input("Please input a number (preferably 1-9) of Humans. This is your army you can control."))
            if humanNumber <= 1:
                print("You entered too few number of humans.")
        except:
            print("Your input was not a valid number. Try again.")
    zombieNumber = 4 #Initial number of zombies to spawn
    completePos = []
    
    for i in range(0, humanNumber): #Generate new human positions. Start around the middle tiles.
        positionTaken = True
        completePos = []
        
        while positionTaken == True:
            newXPos = random.randrange(-1, 2) #Can choose between -1, 0, and 1 (3 options * 2 axis = 9 possible locations. There should be no way for all positions to be filled as long as 9 or less humans are initially spawned. 
            newYPos = random.randrange(-1, 2)
            completePos = [(numberOfTiles[0]/2) + newXPos, (numberOfTiles[1]/2) + newYPos] #Finds the middle number of x and y tiles + a randomly generated number as the full position.
            if checkIfTileIsTaken(completePos[0], completePos[1])[0] == False:
                positionTaken = False
        
        human = Entity("Human", completePos)     #Technically creates 'human' as a list, but this works easier creating a seperate team list (humanEntityList), especially if we wanted to add singular entities later.
        print()
    
    for i in range(0, zombieNumber): #This is the only time I spawn them manually. Every other time I use the spawnNewZombies function.
        zombieAdded = False
        while zombieAdded == False:
            newZombiePosIndex = random.randrange(0, len(outerEdgeTileArray))
            newZombiePos = outerEdgeTileArray[newZombiePosIndex]
            if checkIfTileIsTaken(newZombiePos[0], newZombiePos[1])[0] == False:
                zombie = Entity("Zombie", newZombiePos)
                zombieAdded = True
        
class Entity:
    """ A class that represents a generic entity.
    Variables on this indent line are 'global' in relation to their class. Every object entity has these same values for these variables."""
    currentPos = [-1, -1]
    ID = 0 
    maxHealth = 100 #Zombies get 10 HP (2 hits)
    damage = 5
    cooldownTimer = 2
    faction = "None" #Zombie or Human. NORMALLY, xD, they only attack the opposite faction, not each other.
    tileForEntity = "Null"
    
    def __init__(self, factionTF, newPos): #When an instance is initialized, all global variabes are given to the instance as local variables. We can then change the local variables from there to reflect individual differences among a group.
        global entityList
        global completeTileArray
        
        self.faction = factionTF
        self.currentPos = newPos
        self.ID = Entity.ID #Set the instance's ID to the current available ID
        Entity.ID += 1 #Then change it by one for the future instance.
        self.currentCooldownTimer = 0 #Don't need a 'readyToAttackTF variable, as currentCooldownTimer == 0 gives us the same result
        entityList.append(self) #Adds itself to the list, that way in the Main function we can call every object easier
        
        if self.faction == "Zombie":
            self.maxHealth = 10
        self.currentHealth = self.maxHealth #Set the instance's HP to full.
            
        
        completeTileArray[xAndYToTileArrayIndex(self.currentPos[0], self.currentPos[1])].entityOnTile = self   #Add entity to new tile
        self.tileForEntity = completeTileArray[xAndYToTileArrayIndex(self.currentPos[0], self.currentPos[1])]  #Add tile on this entity
        
    def __attack__(self, enemy):
        enemy.currentHealth -= self.damage
        print("Entity " + str(self.faction) + str(self.ID) + " attacked " + str(enemy.faction) + str(enemy.ID) + ". "  + str(enemy.faction) + str(enemy.ID) + " has " + str(enemy.currentHealth) + " HP remaining.")
        if enemy.currentHealth <= 0:
            enemy.__entityDie__()
        
    def __entityDie__(self):
        global totalKillCounter
        global totalDeathsCounter
        
        print(str(self.faction) + str(self.ID) + "died")
        #Remove from the lists so it can't be attacked or attack anymore. I don't technically know how to delete instances, and this doesn't need it right now either.
        if self.faction == "Zombie":
            totalKillCounter += 1
        else:
            totalDeathsCounter += 1
        if self in entityList:
            entityList.remove(self)
        completeTileArray[xAndYToTileArrayIndex(self.currentPos[0], self.currentPos[1])].entityOnTile = "Null"

    def __moveUnit__(self, humanList): #Moves an individiual entity, the humanList variable is only needed for zombies.
        returnValue = False
        if self.faction == "Human":#If the entitiy is a human, we want to move them manually.
            playerInput = input("Input a direction you would like to move this human. Enter w, a, s, or d. You can also enter 'skip' to skip that human's movement turn.")
            playerInput = playerInput.lower()
            if playerInput == "skip":
                returnValue = True
            else:
                if (playerInput == "w") or (playerInput == "s") or (playerInput == "a") or (playerInput == "d"):
                    
                    newPos = stepsToRange(playerInput, self)
                    if newPos[0] == True:
                        if newPos[3] == False:
                            moveToNewTile([newPos[1],newPos[2]], self)
                        returnValue = True
                    else:
                        print("You cannot move onto that tile. Either that tile is currently occupied, or you are trying to walk off the map.")
                        returnValue = False
                else:
                    print("You did not enter the right key. Please enter w for moving upwards, s for downwards, a for left, or d for right.")
                    returnValue = False
        else: #Otherwise move them automatically.
            zombieInput = findNearestEntity(humanList, self) #This is specifically for the AI zombies, so it takes care of itself.
            #returnValue = False
        return returnValue #IF true, the entity made a move. if false, they did not. Used for humans
            
            
########## Ending of of Entity Details ########## 


########## Beginning of End-Game Functions ########## 
 
def printFinalStats():
    global totalKillCounter
    global totalDeathsCounter
    global totalKDA
    
    totalKDA = totalKillCounter / totalDeathsCounter
    print("That was tough! I hope you had fun :)")
    print("Statistics:")
    print("Total Zombie Kills:" + str(totalKillCounter))
    print("Total Player Deaths:" + str(totalDeathsCounter))
    print("Total KDA (Zombie to Human)" + str(totalKDA))
    print("Thanks for playing!")
    saveToCSV() 
    
    
def saveToCSV():
    global totalKillCounter
    global totalDeathsCounter
    global totalKDA
    global numberOfTurnsPassed
    
    csvRowTitle = ["Total KDA", "Total Zombie Kills", "Total Human Deaths", "Total Turns Survived"]
    csvRow = [totalKDA, totalKillCounter, totalDeathsCounter, numberOfTurnsPassed]
    
    if not os.path.isfile(statisticsSaveFile): #Reference: https://www.freecodecamp.org/news/how-to-check-if-a-file-exists-in-python/#:~:text=Thankfully%2C%20Python%20has%20multiple%20built,a%20symlink%20to%20a%20file.
        print("Warning. The CSV file to save the statistics has not been found. However, if this is your first time playing this game, this is normal, and you can ignore this error.") #If csv not found, print a warning, then save to a new csv
        with open (statisticsSaveFile, 'a', encoding="utf-8", newline='') as csv_file: #If the file doesn't currently exist, create a new file with the statistic titles added in.
            csvwriter = csv.writer(csv_file)  
            csvwriter.writerow(csvRowTitle)   
            csvwriter.writerow(csvRow)   
    else:
        with open (statisticsSaveFile, 'a', encoding="utf-8", newline='') as csv_file:
            csvwriter = csv.writer(csv_file)  
            csvwriter.writerow(csvRow)   
    
    
########## Ending of End-Game Functions ########## 














































































































































































main()
