import pymysql
import creds
import boto3
from botocore.exceptions import ClientError

def get_conn():
    conn = pymysql.connect(
        host=creds.host,
        user=creds.user,
        password=creds.password,
        db=creds.db,
        cursorclass=pymysql.cursors.DictCursor
    )
    return conn

def execute_query(query, args=()):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(query, args)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def execute_update(query, args=()):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(query, args)
    conn.commit()
    affected = cursor.rowcount
    cursor.close()
    conn.close()
    return affected > 0

def add_artist_with_track(artist_id, artist_name, track_name, unit_price):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT ArtistId FROM Artist WHERE ArtistId = %s", (artist_id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO Artist (ArtistId, Name) VALUES (%s, %s)", (artist_id, artist_name))
    cursor.execute("SELECT MAX(AlbumId) as max_id FROM Album")
    result = cursor.fetchone()
    album_id = (result['max_id'] or 0) + 1
    cursor.execute("INSERT INTO Album (AlbumId, Title, ArtistId) VALUES (%s, %s, %s)", 
                   (album_id, artist_name + " Album", artist_id))
    cursor.execute("SELECT MAX(TrackId) as max_id FROM Track")
    result = cursor.fetchone()
    track_id = (result['max_id'] or 0) + 1
    cursor.execute("SELECT MediaTypeId FROM MediaType LIMIT 1")
    media_type = cursor.fetchone()
    media_type_id = media_type['MediaTypeId'] if media_type else 1
    cursor.execute("""
        INSERT INTO Track (TrackId, Name, AlbumId, MediaTypeId, Milliseconds, UnitPrice) 
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (track_id, track_name, album_id, media_type_id, 200000, unit_price))
    conn.commit()
    cursor.close()
    conn.close()
    return True

def delete_artist_by_id(artist_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT Name FROM Artist WHERE ArtistId = %s", (artist_id,))
    result = cursor.fetchone()
    if not result:
        cursor.close()
        conn.close()
        return None
    artist_name = result['Name']
    cursor.execute("""
        DELETE FROM InvoiceLine WHERE TrackId IN 
        (SELECT TrackId FROM Track WHERE AlbumId IN 
        (SELECT AlbumId FROM Album WHERE ArtistId = %s))
    """, (artist_id,))
    cursor.execute("""
        DELETE FROM PlaylistTrack WHERE TrackId IN 
        (SELECT TrackId FROM Track WHERE AlbumId IN 
        (SELECT AlbumId FROM Album WHERE ArtistId = %s))
    """, (artist_id,))
    cursor.execute("""
        DELETE FROM Track WHERE AlbumId IN 
        (SELECT AlbumId FROM Album WHERE ArtistId = %s)
    """, (artist_id,))
    cursor.execute("DELETE FROM Album WHERE ArtistId = %s", (artist_id,))
    cursor.execute("DELETE FROM Artist WHERE ArtistId = %s", (artist_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return artist_name

def get_all_artists():
    return execute_query("SELECT ArtistId, Name AS ArtistName FROM Artist ORDER BY Name")

def update_artist(old_name, new_name):
    return execute_update("UPDATE Artist SET Name = %s WHERE Name = %s", (new_name, old_name))

def update_artist_by_id(artist_id, artist_name, track_name, unit_price):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT Name FROM Artist WHERE ArtistId = %s", (artist_id,))
    result = cursor.fetchone()
    if not result:
        cursor.close()
        conn.close()
        return None
    old_name = result['Name']
    cursor.execute("UPDATE Artist SET Name = %s WHERE ArtistId = %s", (artist_name, artist_id))
    cursor.execute("SELECT MAX(AlbumId) as max_id FROM Album")
    result = cursor.fetchone()
    album_id = (result['max_id'] or 0) + 1
    cursor.execute("INSERT INTO Album (AlbumId, Title, ArtistId) VALUES (%s, %s, %s)", 
                   (album_id, artist_name + " Album", artist_id))
    cursor.execute("SELECT MAX(TrackId) as max_id FROM Track")
    result = cursor.fetchone()
    track_id = (result['max_id'] or 0) + 1
    cursor.execute("SELECT MediaTypeId FROM MediaType LIMIT 1")
    media_type = cursor.fetchone()
    media_type_id = media_type['MediaTypeId'] if media_type else 1
    cursor.execute("""
        INSERT INTO Track (TrackId, Name, AlbumId, MediaTypeId, Milliseconds, UnitPrice) 
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (track_id, track_name, album_id, media_type_id, 200000, unit_price))
    conn.commit()
    cursor.close()
    conn.close()
    return old_name

def get_dynamodb_table(table_name):
    try:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table(table_name)
        return table
    except ClientError:
        return None

def add_to_dynamodb(table_name, item):
    try:
        table = get_dynamodb_table(table_name)
        if not table:
            return False
        table.put_item(Item=item)
        return True
    except ClientError:
        return False

def get_from_dynamodb(table_name, key):
    try:
        table = get_dynamodb_table(table_name)
        if not table:
            return None
        response = table.get_item(Key=key)
        return response.get('Item')
    except ClientError:
        return None

def update_dynamodb(table_name, key, update_expression, expression_values):
    try:
        table = get_dynamodb_table(table_name)
        if not table:
            return False
        table.update_item(
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values
        )
        return True
    except ClientError:
        return False

def delete_from_dynamodb(table_name, key):
    try:
        table = get_dynamodb_table(table_name)
        if not table:
            return False
        table.delete_item(Key=key)
        return True
    except ClientError:
        return False

def scan_dynamodb(table_name):
    try:
        table = get_dynamodb_table(table_name)
        if not table:
            return []
        response = table.scan()
        return response.get('Items', [])
    except ClientError:
        return []
