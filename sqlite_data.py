'''
Description: Manipulates DB with separate functionalities in api.py
'''
import os
import sqlite3
import boto3

BUCKET_NAME = ''
FILE_NAME = ''
AWS_FOLDER = f'cloudflare_monthlyFacts/{FILE_NAME}'

s3 = boto3.resource('s3',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'))
bucket = s3.Bucket(BUCKET_NAME)

# Create a new file (dangerous - could overwrite data) (.back extension if existing file)


def create_file(requests, bandwidth, visits, views, date):
    '''Purpose: Create new database using paramaters'''
    c.execute("""CREATE TABLE http_data (
    	requests real,
    	bandwidth real,
    	visits real,
    	views real,
        date text)""")

    add_entry(requests, bandwidth, visits, views, date)

def get_file():
    '''Purpose: Get the database file from S3'''
    # check if file exists
    # iterator = bucket.objects.all()

    # files = []
    # for file in iterator:
    #     files.append(file.key)
    #     print({"files": files})

    # pull s3 object from bucket
    s3.Bucket(BUCKET_NAME).download_file(AWS_FOLDER, FILE_NAME)

# push db file into s3 object


def push_file():
    '''Purpose: Push existing database in S3'''
    s3.Bucket(BUCKET_NAME).upload_file(FILE_NAME, AWS_FOLDER)

# add entry to database if a new date


def add_entry(requests, bandwidth, visits, views, date):
    '''Purpose: Add a new entry into database with above parameters'''
    with conn:
        c.execute("INSERT INTO http_data VALUES (:requests, :bandwidth, :visits, :views, :date)",
        {'requests': requests, 'bandwidth': bandwidth, 'visits': visits, 'views': views,\
         'date': (str)(date)})
    conn.commit()

# pull all the data correlated to the first date specified


def get_data_by_date(date):
    '''Purpose: `date` data from the DB'''
    c.execute("SELECT * FROM http_data WHERE date=:date",
              {'date': (str)(date)})
    return c.fetchone()

# delete an entry from the database (use if db is incorrect)


def delete_entry(date):
    '''Purpose: Delete row from database with param specification'''
    c.execute('DELETE FROM http_data WHERE date =:date', {'date': (str)(date)})
    conn.commit()

# close sqlite connection


def close():
    '''Purpose: Close connection to DB'''
    conn.close()


# get file before opening connection to aws
get_file()

conn = sqlite3.connect(FILE_NAME)
c = conn.cursor()
