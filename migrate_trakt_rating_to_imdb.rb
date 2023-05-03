#!/usr/bin/env ruby
require 'json'

def get_id(movie);     movie['site_data']['IMDB']['id'] end
def get_rating(movie); movie['site_data']['IMDB']['my_rating'] end

Dir.chdir __dir__ do 

  `./transfer_ratings.py -s trakt`
  `./transfer_ratings.py -s imdb`

  imdb_file  = Dir['RatS/exports/*IMDB.json'].last
  trakt_file = Dir['RatS/exports/*Trakt.json'].last

  imdb  = JSON.parse File.read(imdb_file)
  trakt = JSON.parse File.read(trakt_file)

  imdb.each do |rated_movie|
   id = get_id rated_movie
   rating = get_rating rated_movie
   trakt.delete_if do |t|
     get_id(t).empty? || (get_id(t) == id && get_rating(t) == rating)
   end
  end

  if trakt.size > 0
    File.write('RatS/exports/new.json', trakt.to_json)
    `./transfer_ratings.py --source imdb --destination imdb --file new.json`
  end

  FileUtils.rm_f Dir.glob('RatS/exports/*')
end
