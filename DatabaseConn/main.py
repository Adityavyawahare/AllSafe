from typing_extensions import ParamSpecArgs
from DatabaseConn.connection import conn
mycursor = conn.cursor()

#Get passwords
def get_passwords():
    mycursor.execute("SELECT * FROM passwords")
    result=mycursor.fetchall()
    print(result)
    return result

#Add data to database
def add(mail,passwrd):
    val=(mail,passwrd)
    query="INSERT INTO passwords (link,answer) VALUES (%s,%s)"
    mycursor.execute(query,val)
    conn.commit()

def get_id(mail,password):
    val=(mail,password)
    query="SELECT id FROM passwords WHERE link=%s AND answer=%s"
    mycursor.execute(query,val)
    given_id=mycursor.fetchall()
    return given_id[0][0]

def delete(val):
    query="DELETE FROM passwords WHERE id="
    mycursor.execute(query+str(val))
    conn.commit()

def update(mail,password,id):
    val=(mail,password,str(id))
    print(val)
    query="UPDATE passwords SET link = %s, answer= %s WHERE id = %s"
    mycursor.execute(query,val)
    conn.commit()


