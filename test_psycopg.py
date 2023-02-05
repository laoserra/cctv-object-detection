import psycopg2

# Connect to your PostgreSQL database on a remote server
conn = psycopg2.connect(host="127.0.0.1", port="5432", dbname="detections", user="postgres", password="")

# Open a cursor to perform database operations
cur = conn.cursor()

# Execute a test query
cur.execute("SELECT * FROM models")

# Retrieve query results
records = cur.fetchall()

# Finally, you may print the output to the console or use it anyway you like
print(records)

