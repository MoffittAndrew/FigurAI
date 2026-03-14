import sqlite3 as sql
from init import dbFileName, weightRes, numpy

# Database functions

def connectToDB():

    conn = None
    try:
        conn = sql.connect(dbFileName)
    except sql.Error as e:
        print(e)

    if conn is None:
        print("Error! Cannot create a connection to '" + dbFileName + "'")
                
    return conn

def readWeights(tableName):

    weightmap = numpy.full((weightRes, weightRes), 0, dtype=int)
    dbConn = connectToDB()
    if dbConn is not None:
        
        cur = dbConn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS " + tableName + " (xIndex INT NOT NULL, yIndex INT NOT NULL, weightValue INT NOT NULL);")
        cur.execute("SELECT * FROM " + tableName)
        results = cur.fetchall()

        if len(results) == weightRes ** 2:
            for row in results:
                weightmap[row[0], row[1]] = row[2]
                
        else:
            if len(results) == 0:
                print("Error! '" + dbFileName + "' Unable to find " + tableName + " weights! Creating new weights...")
            else:
                print("Error! '" + dbFileName + "' " + tableName + " weights are not formatted to " + str(weightRes) + " x " + str(weightRes) + "! Resetting weights...")
                
            cur.execute("DELETE FROM " + tableName)
            for y in range(weightRes):
                for x in range(weightRes):
                    cur.execute("INSERT INTO " + tableName + " VALUES (?, ?, ?)", (x, y, 0))
            dbConn.commit()
            print("Successfully created new " + tableName + " weights\n")
                
        cur.close()
        dbConn.close()

    return weightmap

def updateDB(tableName, weightmap):

    print("\nSaving " + tableName + " weights...")
    dbConn = connectToDB()
    if dbConn is not None:
        
        cur = dbConn.cursor()
        cur.execute("DELETE FROM " + tableName)
        for y in range(weightRes):
            for x in range(weightRes):
                cur.execute("INSERT INTO " + tableName + " VALUES (?, ?, ?)", (x, y, int(weightmap[x, y])))
                    
        dbConn.commit()
        cur.close()
        dbConn.close()
        print("Successfully saved " + tableName + " weights")
