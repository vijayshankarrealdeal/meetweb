import psycopg2

host = "meetwebflask-server"
dbname = "postgres"
user = "ncgfeatlso"
password = "PGO0637ETON66601$"
sslmode = "require"
conn_string = "host={0} user={1} dbname={2} password={3} sslmode={4}".format(host, user, dbname, password, sslmode)


def create_table():
    conn = psycopg2.connect(conn_string) 
    cursor = conn.cursor()
    try:
        cursor.execute("CREATE TABLE student (id serial PRIMARY KEY, fname VARCHAR(50), lname VARCHAR(50),pet VARCHAR(50));")
        conn.commit()
        cursor.close()
        return "Success"
    except Exception as e:
        conn.close()
        return str(e)



def insert_data(fname,lname,pet):
    conn = psycopg2.connect(conn_string) 
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO inventory (fname, lname,pet) VALUES (%s, %s,%s);", (fname, lname,pet))
        conn.commit()
        cursor.close()
        return "Success"
    except Exception as e:
        conn.close()
        return str(e)


def read_data():
    conn = psycopg2.connect(conn_string) 
    cursor = conn.cursor()
    try:
        data = []
        rows = cursor.fetchall()
        for row in rows:
            k = {}
            k['fname'] = str(row[0])
            k['lname'] = str(row[1])
            k['pet'] = str(row[2])
            data.append(k)
        conn.commit()
        cursor.close()
        return data
    except Exception as e:
        conn.close()
        return [str(e)]


