import mysql.connector

conn = mysql.connector.connect(
  host="localhost",
  user="root",
  password="password",
  database="allsafe",
  auth_plugin='mysql_native_password'
)