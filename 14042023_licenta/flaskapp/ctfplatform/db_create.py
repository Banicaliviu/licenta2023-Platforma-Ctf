from ctfplatform.kubernetes_interactions import get_db_connection
from ctfplatform.utils import append_new_line

def user_table(conn, cur):
    try:
        #cur.execute('DROP TABLE IF EXISTS UserTable;')
        cur.execute('CREATE TABLE usertable ('
                    'id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,'
                    'email VARCHAR(150) NOT NULL,'
                    'password VARCHAR(150) NOT NULL,'
                    'username VARCHAR(150) NOT NULL,'
                    'role VARCHAR(150),'
                    'date_added DATE DEFAULT CURRENT_TIMESTAMP'
                ');'
        )        

        conn.commit()
        append_new_line("logs.txt", "UserTable table successfully created !")
    except(Exception) as e:
        append_new_line("logs.txt", "Error : {}".format(e))

def create_db():    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM information_schema.tables WHERE table_name='usertable';")
        result = cur.fetchone()
        if result[0] == 0:
            user_table(conn, cur)
            append_new_line("logs.txt", "UserTable table successfully created !")
        else:
            append_new_line("logs.txt", "UserTable table already exists!")


    except(Exception) as e:
        append_new_line("logs.txt", "Error : {}".format(e))
    finally:
        append_new_line("logs.txt", "Database up and running !")
        cur.close()
        conn.close()
            