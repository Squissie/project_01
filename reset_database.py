import sqlite3 as sql
import os
os.chdir(os.path.dirname(__file__))

with sql.connect("db.sqlite3") as con:
    c = con.cursor()
    c.execute("DELETE FROM svmApp_patientmodel")
    c.execute("DELETE FROM svmApp_consultationmodel")
    c.execute("DELETE FROM svmApp_imagemodel")
    c.execute("DELETE FROM login_system_user WHERE id >= 4")
    c.execute("DELETE FROM django_session")
    con.commit()
