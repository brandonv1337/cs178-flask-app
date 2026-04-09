from flask import Flask, render_template, request, redirect, url_for, flash, session
from dbCode import *

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
# Home page route
def home():
    return render_template('home.html')

@app.route('/add-user', methods=['GET', 'POST'])
# Add new artist with track
def add_user():
    if request.method == 'POST':
        artist_id = request.form['artist_id']
        artist_name = request.form['artist_name']
        track_name = request.form['track_name']
        unit_price = request.form['unit_price']
        
        if add_artist_with_track(int(artist_id), artist_name, track_name, float(unit_price)):
            item = {
                'ArtistName': artist_name,
                'TrackName': track_name,
                'UnitPrice': unit_price
            }
            add_to_dynamodb('ArtistPreferences', item)
            session['current_artist'] = artist_name
            flash('Artist added successfully', 'success')
            return redirect(url_for('home'))
        else:
            flash('Failed to add artist', 'error')
            return render_template('add_user.html')
    else:
        return render_template('add_user.html')

@app.route('/delete-user', methods=['GET', 'POST'])
# Delete artist by ID
def delete_user():
    if request.method == 'POST':
        artist_id = request.form['artist_id']

        artist_name = delete_artist_by_id(int(artist_id))
        if artist_name:
            delete_from_dynamodb('ArtistPreferences', {'ArtistName': artist_name})
            if session.get('current_artist') == artist_name:
                session.pop('current_artist', None)
            flash('Artist deleted successfully', 'warning')
            return redirect(url_for('home'))
        else:
            flash('Failed to delete artist', 'error')
            return render_template('delete_user.html')
    else:
        return render_template('delete_user.html')

@app.route('/update-user', methods=['GET', 'POST'])
# Update artist with new track
def update_user():
    if request.method == 'POST':
        artist_id = request.form['artist_id']
        artist_name = request.form['artist_name']
        track_name = request.form['track_name']
        unit_price = request.form['unit_price']

        old_name = update_artist_by_id(int(artist_id), artist_name, track_name, float(unit_price))
        if old_name:
            delete_from_dynamodb('ArtistPreferences', {'ArtistName': old_name})
            add_to_dynamodb('ArtistPreferences', {
                'ArtistName': artist_name,
                'TrackName': track_name,
                'UnitPrice': unit_price
            })
            if session.get('current_artist') == old_name:
                session['current_artist'] = artist_name
            flash('Artist updated successfully', 'info')
            return redirect(url_for('home'))
        else:
            flash('Failed to update artist', 'error')
            return render_template('update_user.html')
    else:
        return render_template('update_user.html')

@app.route('/display-users')
# Display all artists and tracks
def display_users():
    users_list = execute_query("""
        SELECT ArtistId, Artist.Name AS ArtistName, Track.Name AS TrackName, UnitPrice
        FROM Artist
        LEFT JOIN Album USING (ArtistId)
        LEFT JOIN Track USING (AlbumId)
        ORDER BY Artist.Name
    """)
    return render_template('display_users.html', users=users_list)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
