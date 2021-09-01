#!/usr/bin/env python
# coding: utf-8

# In[1]:


import psycopg2
from configparser import ConfigParser


# In[3]:


def config(filename='database.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)
    
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(f'Section {section} not found in the {filename} file')
        
    return db

def postgres_connect():
    conn = None
    try:
        # Read connection parameters
        params = config()
        
        # Connect to PostgreSQL server
        print('Connecting to Postgres DB...')
        conn = psycopg2.connect(**params)
        
        # Create cursor
        cur = conn.cursor()
        
        # Execute SQL statement
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')
        
        # Get result from last executed SQL command
        db_version = cur.fetchone()
        print(db_version)
        
        # Close communication to db
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed')


# In[5]:


postgres_connect()


# In[ ]:




