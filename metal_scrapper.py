#!/usr/bin/env python
import re
import json
from urllib import urlopen, urlencode

site_url = 'https://www.metal-archives.com/'
url_search_songs = 'search/ajax-advanced/searching/songs?'
url_search_bands = 'search/ajax-advanced/searching/bands?'
url_lyrics = 'release/ajax-view-lyrics/id/'
lyrics_not_available = '(lyrics not available)'
lyric_id_re = re.compile(r'id=.+[a-z]+.(?P<id>\d+)')
band_name_re = re.compile(r'title="(?P<name>.*)\"')
tags_re = re.compile(r'<[^>]+>')


def get_songs_data(band_name="", song_title=""):
    """Search on metal-archives for song coincidences"""
    params = dict(bandName = band_name, songTitle = song_title)
    url = site_url + url_search_songs + urlencode(params)

    return json.load(urlopen(url))['aaData']


def get_bands_data(band_name="", genre="", num=0):
    """Search on metal-archives for band coincidences, starting at result num """
    params = dict(bandName = band_name, genre = genre, iDisplayStart=num)
    url = site_url + url_search_bands + urlencode(params)
    return json.load(urlopen(url))['aaData'], json.load(urlopen(url))["iTotalRecords"]


def get_lyrics_by_song_id(song_id):
    """Search on metal-archives for lyrics based on song_id"""
    url = site_url + url_lyrics + song_id
    return tags_re.sub('', urlopen(url).read().strip()).decode('utf-8')


def iterate_lyrics(songs):
    '''Iterate over returned song matches. If the lyrics are different than\
    "(lyrics not available)" then save them.'''
    total_lyrics = {}
    for song in songs:
        song_title = song[3]
        song_id = lyric_id_re.search(song[4]).group("id")
        lyrics = get_lyrics_by_song_id(song_id)
        if lyrics != lyrics_not_available:
            total_lyrics[song_title] = lyrics

    return total_lyrics


def iterate_bands(songs):
    '''Iterate over returned song matches. If the lyrics are different than\
    "(lyrics not available)" then save them.'''
    total_bands = []
    for song in songs:
        song=song[0]
        song = song[:song.find('</a')]
        band_name = song[song.find('>')+1:]
        if band_name not in total_bands:
            total_bands.append(band_name)
    return total_bands


def iterate_songs(songs):
    '''Iterate over returned song matches. If the lyrics are different than\
    "(lyrics not available)" then save them.'''
    total_names = []
    for song in songs:
        song_title = song[3]
        total_names.append(song_title)
    return total_names


def get_all_bands(genre="black metal", band_name=""):
    # songs_data = get_songs_data(band_name, song_title)
    all = []
    i = 0
    bands, total = get_bands_data(band_name, genre, i)
    print "total bands: " + str(total)
    end = False
    while not end:
        all.extend(iterate_bands(bands))
        bands, num = get_bands_data(band_name, genre, i)
        print len(all)
        if i + 200 > total:
            end = True
        else:
            i += 200
        print i
    return all


def scrap_bands(filename="black_metal_bands.txt", genre="black metal"):
    print "scrapping bands"
    try:
        with open(filename, "r") as f:
            bands = f.readlines()
    except:
        bands = get_all_bands()
        with open(filename, "w") as f:
            for band in bands:
                try:
                    f.write(band+"\n")
                except:
                    continue
    print "scrapped", len(bands), "band names"
    return bands


def scrap_lyrics(bands=[], filename="black_metal_lyrics.txt", genre="black metal"):
    print "scrapping lyrics"
    try:
        with open(filename, "r") as f:
            lyrics = f.readlines()
    except:
        lyrics = {}
        if not len(bands):
            bands = scrap_bands()
        for band in bands:
            try:
                songs_data = get_songs_data(band)
                if len(songs_data):
                    lyrics.update(iterate_lyrics(songs_data))
                    print len(lyrics)
            except:
                continue
        with open(filename, "w") as f:
            for lyric in lyrics:
                try:
                    f.writelines(lyrics[lyric])
                except:
                    pass
    print "scrapped", len(lyrics), "lyrics"
    return lyrics


def scrap_songs(bands=[], filename="black_metal_songs.txt", genre="black metal"):
    print "scrapping songs"
    try:
        with open(filename, "r") as f:
            songs = f.readlines()
    except:
        songs = []
        if not len(bands):
            bands = scrap_bands()
        i = len(bands)
        for band in bands:
            i -= 1
            try:
                songs_data = get_songs_data(band)
                if len(songs_data):
                    new = iterate_songs(songs_data)
                    songs.extend(new)
                    print str(len(new)) + " songs from " + band.replace("\n","")
                    print "total songs: " + str(len(songs)), "bands missing: " + str(i)
            except:
                pass
        with open(filename, "w") as f:
            for song in songs:
                try:
                    f.writelines(songs[song])
                except:
                    pass
    print "scrapped " + str(len(songs)) + " song names from " + str(len(bands)) + " bands"
    return songs


def get_song_names_from_lyrics(lyrics_dict):
    song_names = lyrics.keys()
    with open("black_metal_songs", "w") as f:
        for song in song_names:
            song = song.lower().replace("live", "").replace("cover",
                                                            "").replace("intro",
                                                                        "").replace(
                "outro", "").replace("(", "").replace(")", "").replace("-", "")
            try:
                if song != "":
                    f.write(song + "\n")
            except:
                continue
    return song_names


if __name__ == '__main__':
    genre = "black metal"
    filename = "black_metal_bands.txt"
    bands = scrap_bands(genre=genre, filename=filename)
    filename = "black_metal_songs.txt"
    song_names = scrap_songs(bands=bands, genre=genre, filename=filename)
    filename = "black_metal_lyrics.txt"
    lyrics = scrap_lyrics(bands=bands, genre=genre, filename=filename)
