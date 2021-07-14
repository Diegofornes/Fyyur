#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
from models import Venue, Artist, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#----------------------------------------------------------------------------#
#  Venues
#----------------------------------------------------------------------------#

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[]
  cityes = db.session.query(Venue.city).group_by(Venue.city).order_by(Venue.city).all()
  for city in (cityes):
        city_venue= Venue.query.filter_by(city=city[0]).all()
        venue_list = []
        for venue in city_venue:
           upcoming_shows = (
             Show.query.join(Venue, Venue.id==Show.venue)
             .filter(Venue.id==venue.id)
             .filter(Show.start_time>=datetime.now())
             .all()
             )
           venue_list.append({
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": len(upcoming_shows),
           })
        data.append({
          "city": city[0],
          "state": city_venue[0].state,
          "venues": venue_list,
        })
  return render_template('pages/venues.html', areas=data);

#----------------------------------------------------------------------------#
#  Venues search
#----------------------------------------------------------------------------#

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search = request.form.get('search_term')
  venues = Venue.query.filter(Venue.name.ilike('%'+search+'%')).all()
  for venue in venues:
      upcoming_shows = (
        Show.query.join(Venue, Venue.id==Show.venue)
        .filter(Venue.id==venue.id)
        .filter(Show.start_time>=datetime.now())
        .all()
        )
      data.append({
      "id":venue.id,
      "name":venue.name,
      "num_upcoming_shows": len(upcoming_shows),
      })
  response={
    "count": len(venues),
    "data": data,
    }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

#----------------------------------------------------------------------------#
#  Venues id show
#----------------------------------------------------------------------------#

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  shows = (
            Show.query.join(Venue, Venue.id==Show.venue)
            .filter(Venue.id==venue_id)
            .all()
            )
  past_show = []
  upcoming_show = []
  for show in shows:
      data_show = {
        "artist_id": show.artist,
        "artist_name": Artist.query.get(show.artist).name,
        "artist_image_link": Artist.query.get(show.artist).image_link,
        "start_time": str(show.start_time)
        }
      if show.start_time < datetime.now():
          past_show.append(data_show)
      else:
          upcoming_show.append(data_show)
  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_show,
    "upcoming_shows": upcoming_show,
    "past_shows_count": len(past_show),
    "upcoming_shows_count": len(upcoming_show),
  }
  return render_template('pages/show_venue.html', venue=data)

#----------------------------------------------------------------------------#
#  Create Venue
#----------------------------------------------------------------------------#

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
      venue = Venue(name = request.form.get('name'),
      address = request.form.get('address'),
      city = request.form.get('city'),
      state = request.form.get('state'),
      phone = request.form.get('phone'),
      genres = request.form.getlist('genres'),
      website_link = request.form.get('website_link'),
      facebook_link = request.form.get('facebook_link'),
      seeking_talent = True if 'seeking_talent' in request.form else False,
      image_link = request.form.get('image_link'),
      seeking_description = request.form.get('seeking_description'))
      db.session.add(venue)
      db.session.commit()
      db.session.close()
      # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
      db.session.rollback()
       # TODO: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
      db.session.close()
  return render_template('pages/home.html')

#----------------------------------------------------------------------------#
#  Venues Dalete
#----------------------------------------------------------------------------#

@app.route('/venues/<venue_id>', methods=['POST'])
def delete_venue(venue_id):
  venue = Venue.query.filter_by(id=venue_id)
  name = venue.first().name
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue.delete()
    db.session.commit()
    flash('Venue ' + name + ' was successfully deleted!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + name + ' could not be deleted.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

#----------------------------------------------------------------------------#
#  Artist Dalete
#----------------------------------------------------------------------------#

@app.route('/artists/<artist_id>', methods=['POST'])
def delete_artist(artist_id):
  artist = Artist.query.filter_by(id=artist_id)
  name = artist.first().name
  try:
    artist.delete()
    db.session.commit()
    flash('Artist ' + name + ' was successfully deleted!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + name + ' could not be deleted.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepag
  #Both done, I also created a delete Artist button

#----------------------------------------------------------------------------#
#  Artist
#----------------------------------------------------------------------------#

@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data=[]
  artists = Artist.query.all()
  for artist in artists:
      data.append({
        "id": artist.id,
        "name": artist.name,
      })
  return render_template('pages/artists.html', artists=data)

#----------------------------------------------------------------------------#
#  Artist Search
#----------------------------------------------------------------------------#

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search = request.form.get('search_term')
  artists = Artist.query.filter(Artist.name.ilike('%'+search+'%')).all()
  for artist in artists:
      upcoming_shows = (
        Show.query.join(Artist, Artist.id==Show.artist)
        .filter(artist.id==artist.id)
        .filter(Show.start_time>=datetime.now())
        .all()
        )
      data.append({
      "id":artist.id,
      "name":artist.name,
      "num_upcoming_shows": len(upcoming_shows),
      })
  response={
    "count": len(artists),
    "data": data,
    }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

#----------------------------------------------------------------------------#
#  Artist id show
#----------------------------------------------------------------------------#

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)
  shows = Show.query.filter_by(artist=artist_id).all()
  past_show = []
  upcoming_show = []
  for show in shows:
      data_show={
        "venue_id": show.venue,
        "venue_name": Venue.query.get(show.venue).name,
        "venue_image_link": Venue.query.get(show.venue).image_link,
        "start_time": str(show.start_time)
        }
      if show.start_time < datetime.now():
          past_show.append(data_show)
      else:
          upcoming_show.append(data_show)
  data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_show,
    "upcoming_shows": upcoming_show,
    "past_shows_count": len(past_show),
    "upcoming_shows_count": len(upcoming_show),
    }
  return render_template('pages/show_artist.html', artist=data)

#----------------------------------------------------------------------------#
#  Artist Update
#----------------------------------------------------------------------------#

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # TODO: populate form with fields from artist with ID <artist_id>
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  data={
    "id": artist_id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link
    }
  return render_template('forms/edit_artist.html', form=form, artist=data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist = Artist.query.get(artist_id)
  artist.name = request.form.get('name')
  artist.genres = request.form.getlist('genres')
  artist.city = request.form.get('city')
  artist.state = request.form.get('state')
  artist.phone = request.form.get('phone')
  artist.website_link = request.form.get('website')
  artist.facebook_link = request.form.get('facebook_link')
  artist.seeking_venue = True if 'seeking_venue' in request.form else False
  artist.seeking_description = request.form.get('seeking_description')
  artist.image_link = request.form.get('image_link')
  db.session.commit()

  return redirect(url_for('show_artist', artist_id=artist_id))

#----------------------------------------------------------------------------#
#  Venue Update
#----------------------------------------------------------------------------#

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # TODO: populate form with values from venue with ID <venue_id>
  venue = Venue.query.get(venue_id)
  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
  }
  return render_template('forms/edit_venue.html', form=form, venue=data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.get(venue_id)
  venue.name = request.form.get('name')
  venue.genres = request.form.getlist('genres')
  venue.address = request.form.get('address')
  venue.city = request.form.get('city')
  venue.state = request.form.get('state')
  venue.phone = request.form.get('phone')
  venue.website_link = request.form.get('website')
  venue.facebook_link = request.form.get('facebook_link')
  venue.seeking_talent = True if 'seeking_venue' in request.form else False
  venue.seeking_description = request.form.get('seeking_description')
  venue.image_link = request.form.get('image_link')
  db.session.commit()

  return redirect(url_for('show_venue', venue_id=venue_id))
#----------------------------------------------------------------------------#
#  Create Artist
#----------------------------------------------------------------------------#

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
      artist = Artist(name = request.form.get('name'),
      city = request.form.get('city'),
      state = request.form.get('state'),
      phone = request.form.get('phone'),
      genres = request.form.getlist('genres'),
      website_link = request.form.get('website_link'),
      facebook_link = request.form.get('facebook_link'),
      seeking_venue = True if 'seeking_venue' in request.form else False,
      image_link = request.form.get('image_link'),
      seeking_description = request.form.get('seeking_description'))
      db.session.add(artist)
      db.session.commit()
      db.session.close()
      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
      db.session.rollback()
      # TODO: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
      db.session.close()

  return render_template('pages/home.html')


#----------------------------------------------------------------------------#
#  Show
#----------------------------------------------------------------------------#

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[]
  venues = db.session.query(Show.venue).filter(Show.start_time>=datetime.now()).group_by(Show.venue).order_by(Show.venue).all()
  for venue in venues:
      venue_shows = db.session.query(Show).filter(Show.start_time>=datetime.now(), Show.venue==venue[0]).all()
      for show in venue_shows:
          data.append({
            "venue_id": show.venue,
            "venue_name": Venue.query.get(show.venue).name,
            "artist_id": show.artist,
            "artist_name": Artist.query.get(show.artist).name,
            "artist_image_link": Artist.query.get(show.artist).image_link,
            "start_time": str(show.start_time)
          })

  return render_template('pages/shows.html', shows=data)

#----------------------------------------------------------------------------#
#  Show Create
#----------------------------------------------------------------------------#

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
      show = Show(artist = request.form.get('artist_id'),
      venue = request.form.get('venue_id'),
      start_time = request.form.get('start_time'))
      db.session.add(show)
      db.session.commit()
      db.session.close()
      # on successful db insert, flash success
      flash('Show was successfully listed!')
  except:
      db.session.rollback()
      # TODO: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Show could not be listed.')
  finally:
      db.session.close()
  return render_template('pages/home.html')

#----------------------------------------------------------------------------#
# Error handle
#----------------------------------------------------------------------------#

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
