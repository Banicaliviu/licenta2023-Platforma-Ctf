from ctfplatform.kubernetes_interactions import get_db_connection
from ctfplatform.utils import append_new_line
from werkzeug.security import generate_password_hash


########################USERS & GROUPS tables################
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

        password = "admin"
        hashed_password = generate_password_hash(password)
        cur.execute(
            "INSERT INTO UserTable (email, password, username, role) "
            "VALUES (%s, %s, %s, %s);",
            ("admin@gmail.com", hashed_password, "admin", "admin"),
        )

        conn.commit()
    except Exception as e:
        append_new_line("logs.txt", "Error user table: {}".format(e))
        conn.rollback()


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
        conn.rollback()


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
        conn.rollback()


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
        conn.rollback()


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
        conn.rollback()


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
        conn.rollback()


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
        conn.rollback()


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
        append_new_line("logs.txt", "Error imagestoreleasetable: {}".format(e))
        conn.rollback()


def imagestomanifesttable(conn, cur):
    try:
        cur.execute(
            "CREATE TABLE imagestomanifesttable ("
            "id_image INTEGER NOT NULL,"
            "id_manifest INTEGER NOT NULL,"
            "FOREIGN KEY (id_image) REFERENCES imagestable(id),"
            "FOREIGN KEY (id_manifest) REFERENCES manifeststable(id)"
            ");"
        )
        conn.commit()
    except Exception as e:
        append_new_line("logs.txt", "Error imagestomanifesttable: {}".format(e))
        conn.rollback()


#######################Kubernetes MANIFESTS tables##########
def manifeststable(conn, cur):
    try:
        cur.execute(
            "CREATE TABLE manifeststable ("
            "id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,"
            "name VARCHAR(150) NOT NULL,"
            "imageName VARCHAR(150) NOT NULL,"
            "deployment_file_path VARCHAR(150) NOT NULL,"
            "service_file_path VARCHAR(150) NOT NULL,"
            "namespace_file_path VARCHAR(150) NOT NULL,"
            "replicas INTEGER NOT NULL,"
            "status VARCHAR(30) NOT NULL,"
            "nodePort INTEGER NOT NULL,"
            "fullUrl VARCHAR(50) NOT NULL"
            ");"
        )
        conn.commit()
    except Exception as e:
        append_new_line("logs.txt", "Error manifeststable: {}".format(e))
        conn.rollback()


#######################JEOPARDYS tables##########


def jeopardystable(conn, cur):
    try:
        cur.execute(
            "CREATE TABLE jeopardystable ("
            "id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,"
            "name VARCHAR(150) NOT NULL,"
            "description VARCHAR(300) NOT NULL,"
            "status VARCHAR(30) NOT NULL,"
            "fullUrl VARCHAR(150) NOT NULL,"
            "flag VARCHAR(150) NOT NULL,"
            "score INTEGER NOT NULL"
            ");"
        )
        conn.commit()
    except Exception as e:
        append_new_line("logs.txt", "Error jeopardystable: {}".format(e))
        conn.rollback()


def jeopardytoreleasetable(conn, cur):
    try:
        cur.execute(
            "CREATE TABLE jeopardytoreleasetable ("
            "id_jeopardy INTEGER NOT NULL,"
            "id_release INTEGER NOT NULL,"
            "FOREIGN KEY (id_jeopardy) REFERENCES jeopardystable(id),"
            "FOREIGN KEY (id_release) REFERENCES releasestable(id)"
            ");"
        )
        conn.commit()
    except Exception as e:
        append_new_line("logs.txt", "Error jeopardytoreleasetable: {}".format(e))
        conn.rollback()


def jeopardytomanifesttable(conn, cur):
    try:
        cur.execute(
            "CREATE TABLE jeopardytomanifesttable ("
            "id_jeopardy INTEGER NOT NULL,"
            "id_manifest INTEGER NOT NULL,"
            "FOREIGN KEY (id_jeopardy) REFERENCES jeopardystable(id),"
            "FOREIGN KEY (id_manifest) REFERENCES manifeststable(id)"
            ");"
        )
        conn.commit()
    except Exception as e:
        append_new_line("logs.txt", "Error jeopardytomanifesttable: {}".format(e))
        conn.rollback()


def jeopardytousertable(conn, cur):
    try:
        cur.execute(
            "CREATE TABLE jeopardytousertable ("
            "id_jeopardy INTEGER NOT NULL,"
            "id_user INTEGER NOT NULL,"
            "FOREIGN KEY (id_jeopardy) REFERENCES jeopardystable(id),"
            "FOREIGN KEY (id_user) REFERENCES usertable(id)"
            ");"
        )
        conn.commit()
    except Exception as e:
        append_new_line("logs.txt", "Error jeopardytousertable: {}".format(e))
        conn.rollback()


def jeopardytogrouptable(conn, cur):
    try:
        cur.execute(
            "CREATE TABLE jeopardytogrouptable ("
            "id_jeopardy INTEGER NOT NULL,"
            "id_group INTEGER NOT NULL,"
            "FOREIGN KEY (id_jeopardy) REFERENCES jeopardystable(id),"
            "FOREIGN KEY (id_group) REFERENCES grouptable(id)"
            ");"
        )
        conn.commit()
    except Exception as e:
        append_new_line("logs.txt", "Error jeopardytogrouptable: {}".format(e))
        conn.rollback()


###
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

        ################### MANIFESTS

        cur.execute(
            "SELECT count(*) FROM information_schema.tables WHERE table_name='manifeststable';"
        )
        result = cur.fetchone()
        if result[0] == 0:
            manifeststable(conn, cur)
            append_new_line("logs.txt", "manifeststable table successfully created !")
        else:
            # cur.execute("DROP TABLE releasestable  CASCADE;")
            # conn.commit()
            append_new_line("logs.txt", "manifeststable table already exists!")

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
            # cur.execute("DROP TABLE releasestable  CASCADE;")
            # conn.commit()
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
            # cur.execute("DROP TABLE releasestousertable  CASCADE;")
            # conn.commit()
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
            # cur.execute("DROP TABLE releasetogrouptable  CASCADE;")
            # conn.commit()
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
        # creation of images to manifest table
        cur.execute(
            "SELECT count(*) FROM information_schema.tables WHERE table_name='imagestomanifesttable';"
        )
        result = cur.fetchone()
        if result[0] == 0:
            imagestomanifesttable(conn, cur)
            append_new_line(
                "logs.txt", "imagestomanifesttable table successfully created !"
            )
        else:
            # cur.execute("DROP TABLE imagestable  CASCADE;")
            # conn.commit()
            append_new_line("logs.txt", "imagestomanifesttable table already exists!")

        ################JEOPARDYS
        # creation of jeopardys table
        conn.rollback()
        cur.execute(
            "SELECT count(*) FROM information_schema.tables WHERE table_name='jeopardystable';"
        )
        result = cur.fetchone()
        if result[0] == 0:
            jeopardystable(conn, cur)
            append_new_line("logs.txt", "jeopardystable table successfully created !")
        else:
            # cur.execute("DROP TABLE jeopardystable  CASCADE;")
            # conn.commit()
            append_new_line("logs.txt", "jeopardystable table already exists!")

        # creation of jeopardy to release table
        cur.execute(
            "SELECT count(*) FROM information_schema.tables WHERE table_name='jeopardytoreleasetable';"
        )
        result = cur.fetchone()
        if result[0] == 0:
            jeopardytoreleasetable(conn, cur)
            append_new_line(
                "logs.txt", "jeopardytoreleasetable table successfully created !"
            )
        else:
            # cur.execute("DROP TABLE jeopardystable  CASCADE;")
            # conn.commit()
            append_new_line("logs.txt", "jeopardytoreleasetable table already exists!")

        # creation of jeopardy to manifest table
        cur.execute(
            "SELECT count(*) FROM information_schema.tables WHERE table_name='jeopardytomanifesttable';"
        )
        result = cur.fetchone()
        if result[0] == 0:
            jeopardytomanifesttable(conn, cur)
            append_new_line(
                "logs.txt", "jeopardytomanifesttable table successfully created !"
            )
        else:
            # cur.execute("DROP TABLE jeopardystable  CASCADE;")
            # conn.commit()
            append_new_line("logs.txt", "jeopardytomanifesttable table already exists!")

        # creation of jeopardy to user table
        cur.execute(
            "SELECT count(*) FROM information_schema.tables WHERE table_name='jeopardytousertable';"
        )
        result = cur.fetchone()
        if result[0] == 0:
            jeopardytousertable(conn, cur)
            append_new_line("logs.txt", "jeopardytousertable  successfully created !")
        else:
            # cur.execute("DROP TABLE jeopardystable  CASCADE;")
            # conn.commit()
            append_new_line("logs.txt", "jeopardytousertable table already exists!")

        # creation of jeopardy to group table
        cur.execute(
            "SELECT count(*) FROM information_schema.tables WHERE table_name='jeopardytogrouptable';"
        )
        result = cur.fetchone()
        if result[0] == 0:
            jeopardytogrouptable(conn, cur)
            append_new_line("logs.txt", "jeopardytogrouptable  successfully created !")
        else:
            # cur.execute("DROP TABLE jeopardystable  CASCADE;")
            # conn.commit()
            append_new_line("logs.txt", "jeopardytogrouptable table already exists!")

        ###
        cur.close()
    except Exception as e:
        append_new_line("logs.txt", "Error : {}".format(e))
        conn.rollback()
    finally:
        if conn:
            conn.close()
