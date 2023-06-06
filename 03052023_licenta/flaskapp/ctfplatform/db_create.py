from ctfplatform.kubernetes_interactions import get_db_connection
from ctfplatform.utils import append_new_line

# Comment out DROP statements from any related to releases
def user_table(conn, cur):
    try:
        # cur.execute('DROP TABLE IF EXISTS UserTable;')
        cur.execute(
            "CREATE TABLE usertable ("
            "id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,"
            "email VARCHAR(150) NOT NULL,"
            "password VARCHAR(150) NOT NULL,"
            "username VARCHAR(150) NOT NULL,"
            "role VARCHAR(150),"
            "date_added DATE DEFAULT CURRENT_TIMESTAMP"
            ");"
        )

        cur.execute(
            "INSERT INTO UserTable (email, password, username, role) "
            "VALUES (%s, %s, %s, %s);",
            ("admin@gmail.com", "admin", "admin", "admin"),
        )

        conn.commit()
    except Exception as e:
        append_new_line("logs.txt", "Error user table: {}".format(e))


def usertogroup_table(conn, cur):
    try:
        cur.execute(
            "CREATE TABLE usertogrouptable ("
            "id_user INTEGER,"
            "id_group INTEGER,"
            "FOREIGN KEY (id_user) REFERENCES usertable(id),"
            "FOREIGN KEY (id_group) REFERENCES grouptable(id)"
            ");"
        )
        conn.commit()
    except Exception as e:
        append_new_line("logs.txt", "Error jeopardy category table: {}".format(e))


def group_table(conn, cur):
    try:
        cur.execute(
            "CREATE TABLE grouptable ("
            "id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,"
            "name VARCHAR(150) NOT NULL"
            ");"
        )
        conn.commit()
    except Exception as e:
        append_new_line("logs.txt", "Error jeopardy category table: {}".format(e))


# from here
def jeopardycategory_table(conn, cur):
    try:
        # cur.execute('DROP TABLE jeopardycategorytable CASCADE;')
        # conn.commit()
        cur.execute(
            "CREATE TABLE jeopardycategorytable ("
            "id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,"
            "category VARCHAR(150) NOT NULL"
            ");"
        )
        conn.commit()
    except Exception as e:
        append_new_line("logs.txt", "Error jeopardy category table: {}".format(e))


def jeopardyexercise_table(conn, cur):
    try:
        # cur.execute('DROP TABLE jeopardyexercisetable CASCADE;')
        # conn.commit()
        cur.execute(
            "CREATE TABLE jeopardyexercisetable ("
            "id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,"
            "title VARCHAR(150) NOT NULL,"
            "description VARCHAR(600) NOT NULL,"
            "difficulty VARCHAR(10) NOT NULL,"
            "id_category INTEGER NOT NULL,"
            "score_if_completed VARCHAR(10) NOT NULL,"
            "flag VARCHAR(150) NOT NULL,"
            "pod_status VARCHAR(50) NOT NULL,"
            "FOREIGN KEY (id_category) REFERENCES jeopardycategorytable(id)"
            ");"
        )
        conn.commit()
    except Exception as e:
        append_new_line("logs.txt", "Error jeopardy exercise table: {}".format(e))


def jeopardyuserhistory_table(conn, cur):
    try:
        # cur.execute('DROP TABLE jeopardyuserhistorytable;')
        # conn.commit()
        cur.execute(
            "CREATE TABLE jeopardyuserhistorytable ("
            "id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,"
            "id_jepardyexercise INTEGER NOT NULL,"
            "id_user INTEGER NOT NULL,"
            "date_completed DATE DEFAULT CURRENT_TIMESTAMP,"
            "FOREIGN KEY (id_user) REFERENCES usertable(id),"
            "FOREIGN KEY (id_jepardyexercise) REFERENCES jeopardyexercisetable(id)"
            ");"
        )
        conn.commit()
    except Exception as e:
        append_new_line("logs.txt", "Error : {}".format(e))


# to here

#############RELEASES tables###############


def releasestable(conn, cur):
    try:
        cur.execute(
            "CREATE TABLE releasestable ("
            "id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,"
            "name VARCHAR(150) NOT NULL,"
            "version VARCHAR(50) NOT NULL,"
            "description VARCHAR(300) NOT NULL,"
            "apiVersion VARCHAR(50) NOT NULL,"
            "appVersion VARCHAR(50) NOT NULL,"
            "type VARCHAR(50) NOT NULL,"
            "created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
            "installed varchar(10) NOT NULL"
            ");"
        )
        conn.commit()
    except Exception as e:
        append_new_line("logs.txt", "Error releasestable table: {}".format(e))


def releasestousertable(conn, cur):
    try:
        cur.execute(
            "CREATE TABLE releasestousertable ("
            "id_release INTEGER NOT NULL,"
            "id_user INTEGER NOT NULL,"
            "FOREIGN KEY (id_release) REFERENCES releasestable(id),"
            "FOREIGN KEY (id_user) REFERENCES usertable(id)"
            ");"
        )
        conn.commit()
    except Exception as e:
        append_new_line("logs.txt", "Error releasestousertable table: {}".format(e))


def releasetogrouptable(conn, cur):
    try:
        cur.execute(
            "CREATE TABLE releasetogrouptable ("
            "id_release INTEGER NOT NULL,"
            "id_group INTEGER NOT NULL,"
            "FOREIGN KEY (id_release) REFERENCES releasestable(id),"
            "FOREIGN KEY (id_group) REFERENCES grouptable(id)"
            ");"
        )
        conn.commit()
    except Exception as e:
        append_new_line("logs.txt", "Error releasetogrouptable table: {}".format(e))


###################IMAGES tables#############


def imagestable(conn, cur):
    try:
        cur.execute(
            "CREATE TABLE imagestable ("
            "id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,"
            "name VARCHAR(150) NOT NULL,"
            "tag VARCHAR(50) NOT NULL,"
            "created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
            "inUse varchar(10) NOT NULL"
            ");"
        )
        conn.commit()
    except Exception as e:
        append_new_line("logs.txt", "Error imagestable table: {}".format(e))


def imagestoreleasetable(conn, cur):
    try:
        cur.execute(
            "CREATE TABLE imagestoreleasetable ("
            "id_image INTEGER NOT NULL,"
            "id_release INTEGER NOT NULL,"
            "FOREIGN KEY (id_image) REFERENCES imagestable(id),"
            "FOREIGN KEY (id_release) REFERENCES releasestable(id)"
            ");"
        )
        conn.commit()
    except Exception as e:
        append_new_line("logs.txt", "Error imagestoreleasetable table: {}".format(e))


def create_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT count(*) FROM information_schema.tables WHERE table_name='usertable';"
        )
        result = cur.fetchone()
        if result[0] == 0:
            user_table(conn, cur)
            append_new_line("logs.txt", "UserTable table successfully created !")
        else:
            append_new_line("logs.txt", "UserTable table already exists!")

        ################creation of grouptable
        cur.execute(
            "SELECT count(*) FROM information_schema.tables WHERE table_name='grouptable';"
        )
        result = cur.fetchone()
        if result[0] == 0:
            group_table(conn, cur)
            append_new_line("logs.txt", "grouptable successfully created !")
        else:
            append_new_line("logs.txt", "grouptable already exists!")

        ############### creation of usertogrouptable
        cur.execute(
            "SELECT count(*) FROM information_schema.tables WHERE table_name='usertogrouptable';"
        )
        result = cur.fetchone()
        if result[0] == 0:
            usertogroup_table(conn, cur)
            append_new_line("logs.txt", "usertogrouptable successfully created !")
        else:
            append_new_line("logs.txt", "usertogrouptable already exists!")
        # Delete from here
        # creation of jeopardy category table
        cur.execute(
            "SELECT count(*) FROM information_schema.tables WHERE table_name='jeopardycategorytable';"
        )
        result = cur.fetchone()
        if result[0] == 0:
            # jeopardycategory_table(conn, cur)
            append_new_line(
                "logs.txt", "jeopardycategorytable table successfully created !"
            )
        else:
            # Use below execute command to drop all jeopardy tables(1)
            cur.execute("DROP TABLE jeopardycategorytable CASCADE;")
            conn.commit()
            # jeopardycategory_table(conn, cur)
            append_new_line("logs.txt", "jeopardycategorytable deleted successfuly!")

        # creation of jeopardy exercise table
        cur.execute(
            "SELECT count(*) FROM information_schema.tables WHERE table_name='jeopardyexercisetable';"
        )
        result = cur.fetchone()
        if result[0] == 0:
            # jeopardyexercise_table(conn, cur)
            append_new_line(
                "logs.txt", "jeopardyexercisetable table successfully created !"
            )
        else:
            # Use below execute command to drop all jeopardy tables(2)
            cur.execute("DROP TABLE jeopardyexercisetable  CASCADE;")
            conn.commit()
            # jeopardyexercise_table(conn, cur)
            append_new_line(
                "logs.txt", "jeopardyexercisetable table deleted successfuly!"
            )

        # creation of jeopardy user history table
        cur.execute(
            "SELECT count(*) FROM information_schema.tables WHERE table_name='jeopardyuserhistorytable';"
        )
        result = cur.fetchone()
        if result[0] == 0:
            # jeopardyuserhistory_table(conn, cur)
            append_new_line(
                "logs.txt", "jeopardyuserhistorytable table successfully created !"
            )
        else:
            cur.execute("DROP TABLE jeopardyuserhistorytable  CASCADE;")
            conn.commit()
            append_new_line("logs.txt", "jeopardyuserhistorytable deleted successfuly!")
        # to here
        ################### RELEASES
        # creation of releases table
        cur.execute(
            "SELECT count(*) FROM information_schema.tables WHERE table_name='releasestable';"
        )
        result = cur.fetchone()
        if result[0] == 0:
            releasestable(conn, cur)
            append_new_line("logs.txt", "releasestable table successfully created !")
        else:
            cur.execute("DROP TABLE releasestable  CASCADE;")
            conn.commit()
            append_new_line("logs.txt", "releasestable table already exists!")

        # creation of releases to user table
        cur.execute(
            "SELECT count(*) FROM information_schema.tables WHERE table_name='releasestousertable';"
        )
        result = cur.fetchone()
        if result[0] == 0:
            releasestousertable(conn, cur)
            append_new_line(
                "logs.txt", "releasestousertable table successfully created !"
            )
        else:
            cur.execute("DROP TABLE releasestousertable  CASCADE;")
            conn.commit()
            append_new_line("logs.txt", "releasestousertable table already exists!")

        # creation of releases to group table
        cur.execute(
            "SELECT count(*) FROM information_schema.tables WHERE table_name='releasetogrouptable';"
        )
        result = cur.fetchone()
        if result[0] == 0:
            releasetogrouptable(conn, cur)
            append_new_line(
                "logs.txt", "releasetogrouptable table successfully created !"
            )
        else:
            cur.execute("DROP TABLE releasetogrouptable  CASCADE;")
            conn.commit()
            append_new_line("logs.txt", "releasetogrouptable table already exists!")

        ################ IMAGES
        # creation of imagestable
        cur.execute(
            "SELECT count(*) FROM information_schema.tables WHERE table_name='imagestable';"
        )
        result = cur.fetchone()
        if result[0] == 0:
            imagestable(conn, cur)
            append_new_line("logs.txt", "imagestable table successfully created !")
        else:
            # cur.execute("DROP TABLE imagestable  CASCADE;")
            # conn.commit()
            append_new_line("logs.txt", "imagestable table already exists!")
        # creation of imagestoreleasetable
        cur.execute(
            "SELECT count(*) FROM information_schema.tables WHERE table_name='imagestoreleasetable';"
        )
        result = cur.fetchone()
        if result[0] == 0:
            imagestoreleasetable(conn, cur)
            append_new_line(
                "logs.txt", "imagestoreleasetable table successfully created !"
            )
        else:
            # cur.execute("DROP TABLE imagestable  CASCADE;")
            # conn.commit()
            append_new_line("logs.txt", "imagestoreleasetable table already exists!")

        cur.close()
    except Exception as e:
        append_new_line("logs.txt", "Error : {}".format(e))
        raise e
    finally:
        if conn:
            conn.close()
