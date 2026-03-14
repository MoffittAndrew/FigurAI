import numpy, csv, sqlite3 as sql

def readFromCSV(fileName):

    weights = {}

    for shape in shapeList:
        weights[shape] = numpy.empty((shapeRes, shapeRes), dtype=int)
        
    weights_file = open(fileName, "r")
    allWeights = []
    read_file = csv.reader(weights_file)
    for record in read_file:
        weightRow = {}
        for i in range(len(shapeList)):
            weightRow[shapeList[i]] = int(record[i])
        allWeights.append(weightRow)
    weights_file.close()
            
    i = 0
    for y in range(shapeRes):
        for x in range(shapeRes):
            for shape in shapeList:
                weights[shape][x, y] = allWeights[i][shape]
            i += 1

    return weights

def createConnection(fileName):

    conn = None
    try:
        conn = sql.connect(fileName)
    except sql.Error as e:
        print(e)
        
    return conn

def writeToDB(fileName, weights):

    print("\nCreating new database file...")
    
    dbConn = createConnection(fileName)
    if dbConn is not None:
        
        cur = dbConn.cursor()
        for shape in shapeList:
            cur.execute("CREATE TABLE IF NOT EXISTS " + shape + " (x INT NOT NULL, y INT NOT NULL, weightVal INT NOT NULL);")
            cur.execute("DELETE FROM " + shape)
            for y in range(shapeRes):
                for x in range(shapeRes):
                    cur.execute("INSERT INTO " + shape + " VALUES (?, ?, ?)", (x, y, int(weights[shape][x, y])))
            
        dbConn.commit()
        cur.close()
        dbConn.close()
        print("Successfully created '" + fileName + "' and transferred CSV contents into it")
        
    else:
        print("Error! Cannot create a connection to '" + fileName + "'")

shapeList = ["Rectangle", "Circle", "Triangle", "Hexagon"]
shapeRes = 256
weights = readFromCSV("weights.csv")
writeToDB("database.db", weights)
