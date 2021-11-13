#!/usr/bin/env python
# coding: utf-8

# In[1]:


import psycopg2
from configparser import ConfigParser
import json
import re


# In[2]:


def config(filename='../database.ini', section='postgresql'):
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
    return None


def postgres_execute(dbCursor=None, sql=''):
    
    if dbCursor is None:
        print('Bad DB Cursor')
        return False
    
    dbCursor.execute(sql)
    return True


def create_tables():
    commands = (
        """
        CREATE TABLE craigslist_listings (
            listing_id BIGINT PRIMARY KEY,
            listing_title TEXT NOT NULL,
            listing_time TIMESTAMP NOT NULL,
            listing_price INTEGER NOT NULL,
            listing_rooms INTEGER NOT NULL,
            listing_sqft INTEGER NOT NULL,
            listing_area TEXT NOT NULL,
            listing_url TEXT NOT NULL
        )
        """,
        """
        SELECT version()
        """)
    
    conn = None
    try:
        # Read connection parameters
        params = config()
        
        # Connect to PostgreSQL server
        conn = psycopg2.connect(**params)
        
        # Create cursor
        cur = conn.cursor()
        
        # Execute SQL statement
        for command in commands:
            cur.execute(command)
        
        # Close communication to db
        cur.close()
        
        # Commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def drop_tables():
    commands = (
        """
        DROP TABLE craigslist_listings
        """,
        """
        SELECT version()
        """)
    
    conn = None
    try:
        # Read connection parameters
        params = config()
        
        # Connect to PostgreSQL server
        conn = psycopg2.connect(**params)
        
        # Create cursor
        cur = conn.cursor()
        
        # Execute SQL statement
        for command in commands:
            cur.execute(command)
        
        # Close communication to db
        cur.close()
        
        # Commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()    


# In[90]:


#postgres_connect()
#drop_tables()
#create_tables()


# In[4]:


listings = None
with open('../scrapes/craigslist_listings_210910190959.json','r') as f:
    listings = json.load(f)
    


# In[5]:


print('Writing entries to database')
for listingID,listingDetails in listings['listings'].items():
    price = listingDetails['price']
    title = re.sub(r"([\'])", r"'\1", listingDetails['title']) #replace ' with ''
    time = listingDetails['listingTime']
    link = listingDetails['link']
    rooms = listingDetails['rooms']
    sqft = listingDetails['sqft']
    area = re.sub(r"([\'])", r"'\1", listingDetails['area'])
    
    insertStr = f"INSERT INTO craigslist_listings VALUES ({listingID},'{title}','{time}',{price},{rooms},{sqft},'{area}','{link}') ON CONFLICT (listing_id) DO NOTHING;"    
    conn = None
    try:
        # Read connection parameters
        params = config()
        
        # Connect to PostgreSQL server
        conn = psycopg2.connect(**params)
        
        # Create cursor
        cur = conn.cursor()
        
        # Execute SQL statement
        cur.execute(insertStr)
        
        # Close communication to db
        cur.close()
        
        # Commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


# In[ ]:




