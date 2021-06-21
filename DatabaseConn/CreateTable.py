from DatabaseConn.connection import conn
mycursor=conn.cursor()
#Drop Table If Exists
mycursor.execute("DROP TABLE IF EXISTS allsafe")
#Create Table 
mycursor.execute("CREATE TABLE passwords (id INT AUTO_INCREMENT PRIMARY KEY,link VARCHAR(255), answer VARCHAR(255))")