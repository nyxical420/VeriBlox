# DataEdit
# VeriBlox Package for Editing Data
import sqlite3
from packages.Logging import log

# Add Data
def addUserData(userid: int):
    data = sqlite3.connect(r"data/data.db")
    cursor = data.cursor()
    
    cursor.execute(f'INSERT INTO users VALUES ({userid}, 0, "", "False")')
    
    data.commit()
    data.close()
    log(f"DataEdit: Added User Data for ID: {userid}")

def addGuildData(guildid: int):
    data = sqlite3.connect(r"data/data.db")
    cursor = data.cursor()
    
    cursor.execute(f'INSERT INTO guilds VALUES ({guildid}, 0, "", "0", 0, 0, 1, 0, 0, "<robloxUsername> - <robloxDisplay>", 0)')
    
    data.commit()
    data.close()
    log(f"DataEdit: Added Guild Data for ID: {guildid}")

# Edit Data
def editUserData(userid: int, set: str, setValue):
    data = sqlite3.connect(r"data/data.db")
    cursor = data.cursor()
    
    cursor.execute(f"UPDATE users SET {set} = {setValue} WHERE UserID = {userid}")
    
    data.commit()
    data.close()
    log(f"DataEdit: Edited User Data {set} to {setValue} from User ID: {userid}")

def editGuildData(guildid: int, set: str, setValue):
    data = sqlite3.connect(r"data/data.db")
    cursor = data.cursor()
    
    cursor.execute(f"UPDATE guilds SET {set} = {setValue} WHERE GuildID = {guildid}")
    
    data.commit()
    data.close()
    log(f"DataEdit: Edited Guild Data {set} to {setValue} from Guild ID: {guildid}")

# Delete Data
def deleteUserData(userid: int):
    data = sqlite3.connect(r"data/data.db")
    cursor = data.cursor()

    cursor.execute(f"DELETE FROM users WHERE UserID = '{userid}'")
    data.commit()
    data.close()
    log(f"DataEdit: Deleted User Data for ID: {userid}")

def deleteGuildData(guildid: int):
    data = sqlite3.connect(r"data/data.db")
    cursor = data.cursor()

    cursor.execute(f"DELETE FROM guilds WHERE GuildID = '{guildid}'")
    data.commit()
    data.close()
    log(f"DataEdit: Deleted Guild Data for ID: {guildid}")

def deleteDuplicateData():
    data = sqlite3.connect(r"data/data.db")
    cursor = data.cursor()

    cursor.executescript("DELETE FROM users WHERE rowid NOT IN (SELECT min(rowid) FROM users GROUP BY UserID)")
    cursor.executescript("DELETE FROM guilds WHERE rowid NOT IN (SELECT min(rowid) FROM guilds GROUP BY GuildID)")
    data.commit()
    data.close()
    log(f"DataEdit: Deleted Duplicate User and Guild Data from Database.")

# Get Data
def getUserData(userid: int):
    data = sqlite3.connect(r"data/data.db")
    cursor = data.cursor()
    
    cursor.execute(f"SELECT * FROM users WHERE UserID = '{userid}'")
    result = cursor.fetchone()
    cursor.close()
    data.close()
    return result

def getGuildData(guildid: int):
    data = sqlite3.connect(r"data/data.db")
    cursor = data.cursor()
    
    cursor.execute(f"SELECT * FROM guilds WHERE GuildID = '{guildid}'")
    result = cursor.fetchone()

    if result:
        cursor.close()
        data.close()
        return result
    else:
        addGuildData(guildid)
        cursor.execute(f"SELECT * FROM guilds WHERE GuildID = '{guildid}'")
        result = cursor.fetchone()
        cursor.close()
        data.close()
        return result

# Get Lists
def getUserList():
    data = sqlite3.connect(r"data/data.db")
    cursor = data.cursor()
    cursor.execute("SELECT * FROM users")
    
    tempUsers = []
    for users in cursor.fetchall():
        tempUsers.append(users[0])

    cursor.close()
    data.close()
    return tempUsers

def getGuildList():
    data = sqlite3.connect(r"data/data.db")
    cursor = data.cursor()
    cursor.execute("SELECT * FROM guilds")

    tempGuilds = []
    for guilds in cursor.fetchall():
        tempGuilds.append(guilds[0])
    
    cursor.close()
    data.close()
    return tempGuilds