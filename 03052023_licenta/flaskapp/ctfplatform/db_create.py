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
        #append_new_line("logs.txt", "UserTable table successfully created !")
    except(Exception) as e:
        append_new_line("logs.txt", "Error user table: {}".format(e))


def jeopardycategory_table(conn, cur):
    try:
        # cur.execute('DROP TABLE jeopardycategorytable CASCADE;')
        # conn.commit()
        cur.execute('CREATE TABLE jeopardycategorytable ('
                    'id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,'
                    'category VARCHAR(150) NOT NULL'
                ');'
        )        
        conn.commit()
    except(Exception) as e:
        append_new_line("logs.txt", "Error jeopardy category table: {}".format(e))

def jeopardyexercise_table(conn, cur):
    try:
        # cur.execute('DROP TABLE jeopardyexercisetable CASCADE;')
        # conn.commit()
        cur.execute('CREATE TABLE jeopardyexercisetable ('
                    'id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,'
                    'title VARCHAR(150) NOT NULL,'
                    'description VARCHAR(600) NOT NULL,'
                    'difficulty VARCHAR(10) NOT NULL,'
                    'id_category INTEGER NOT NULL,'
                    'score_if_completed VARCHAR(10) NOT NULL,'
                    'flag VARCHAR(150) NOT NULL,'
                    'pod_status VARCHAR(50) NOT NULL,'
                    'FOREIGN KEY (id_category) REFERENCES jeopardycategorytable(id)'
                ');'
        )        
        conn.commit()
    except(Exception) as e:
        append_new_line("logs.txt", "Error jeopardy exercise table: {}".format(e))

def jeopardyuserhistory_table(conn, cur):
    try:
        # cur.execute('DROP TABLE jeopardyuserhistorytable;')
        # conn.commit()
        cur.execute('CREATE TABLE jeopardyuserhistorytable ('
                    'id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,'
                    'id_jepardyexercise INTEGER NOT NULL,'
                    'id_user INTEGER NOT NULL,'
                    'date_completed DATE DEFAULT CURRENT_TIMESTAMP,'
                    'FOREIGN KEY (id_user) REFERENCES usertable(id),'
                    'FOREIGN KEY (id_jepardyexercise) REFERENCES jeopardyexercisetable(id)'
                ');'
        )        
        conn.commit()
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
        
        #creation of jeopardy category table
        cur.execute("SELECT count(*) FROM information_schema.tables WHERE table_name='jeopardycategorytable';")
        result = cur.fetchone()
        if result[0] == 0:
            jeopardycategory_table(conn, cur)
            append_new_line("logs.txt", "jeopardycategorytable table successfully created !")
        else:
            # Use below execute command to drop all jeopardy tables(1)
            # cur.execute('DROP TABLE jeopardycategorytable CASCADE;')
            # conn.commit()
            # jeopardycategory_table(conn, cur)
            append_new_line("logs.txt", "jeopardycategorytable table already exists!")
        
        #creation of jeopardy exercise table
        cur.execute("SELECT count(*) FROM information_schema.tables WHERE table_name='jeopardyexercisetable';")
        result = cur.fetchone()
        if result[0] == 0:
            jeopardyexercise_table(conn, cur)
            append_new_line("logs.txt", "jeopardyexercisetable table successfully created !")
        else:
            # Use below execute command to drop all jeopardy tables(2)
            # cur.execute('DROP TABLE jeopardyexercisetable  CASCADE;')
            # conn.commit()
            # jeopardyexercise_table(conn, cur)
            append_new_line("logs.txt", "jeopardyexercisetable table already exists!")
    
        #creation of jeopardy user history table
        cur.execute("SELECT count(*) FROM information_schema.tables WHERE table_name='jeopardyuserhistorytable';")
        result = cur.fetchone()
        if result[0] == 0:
            jeopardyuserhistory_table(conn, cur)
            append_new_line("logs.txt", "jeopardyuserhistorytable table successfully created !")
        else:
            append_new_line("logs.txt", "jeopardyuserhistorytable table already exists!")
        cur.close()
    except(Exception) as e:
        append_new_line("logs.txt", "Error : {}".format(e))
        raise e
    finally:
        if(conn):
            conn.close()
            