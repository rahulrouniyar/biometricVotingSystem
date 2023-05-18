import mysql.connector
import mimetypes

dbname = "election_database"


def convertToBinaryData(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData


def insertBlob(partyName, photo):
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user = "root",
            password="",
            database = dbname
        )

        mycursor = mydb.cursor()
        sql = """ UPDATE party_symbol SET symbol = %s, mime_type = %s WHERE political_party = %s"""

        partySymbol = convertToBinaryData(photo)

        mycursor.execute(sql, (partySymbol, mimetypes.guess_type(photo)[0], partyName))
        mydb.commit()

    except mysql.connector.Error as error:
        print("Failed inserting BLOB data into MySQL table {}".format(error))

    finally:
        if mydb.is_connected():
            mycursor.close()
            mydb.close()

def readBlob(partyName):
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user = "root",
            password="",
            database = dbname
        )

        mycursor = mydb.cursor()
        sql = """ SELECT * FROM party_symbol WHERE political_party = %s"""

        mycursor.execute(sql, (partyName,))
        myresult = mycursor.fetchone()

        storeFilePath = "icons/{0}{1}".format(myresult[0], mimetypes.guess_extension(myresult[2]))
        with open(storeFilePath, 'wb') as file:
            file.write(myresult[1])
            file.close

    except mysql.connector.Error as error:
        print("Failed inserting BLOB data into MySQL table {}".format(error))

    finally:
        if mydb.is_connected():
            mycursor.close()
            mydb.close()
            print("MySQL connection is closed")
        return storeFilePath
