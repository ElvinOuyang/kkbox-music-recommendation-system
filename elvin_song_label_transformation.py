import numpy as np
import pandas as pd
import gensim
import standardized_import as stanimp
from sklearn.feature_extraction import DictVectorizer
from sklearn.decomposition import TruncatedSVD

file_names = ['../raw_data/members.csv',
              '../raw_data/song_extra_info.csv',
              '../raw_data/songs.csv',
              '../raw_data/test.csv',
              '../raw_data/train.csv']

members, song_extra_info, songs, test, train = [pd.read_csv(x)
                                                for x in file_names]

members, song_extra_info, songs, test, train =\
    stanimp.kkbox_cleaning(members, song_extra_info, songs, test, train)

del members, song_extra_info, test, train
"""
# generate song_id-genre_id matrix
# code will likely take much portion of RAM
songs_genre_long = songs[['song_id', 'genre_ids']].astype(str)
songs_genre_long = pd.DataFrame(songs_genre_long.genre_ids.str.split('|').
                                tolist(),
                                index=songs_genre_long.song_id).stack()
songs_genre_long = songs_genre_long.reset_index()[[0, 'song_id']]
songs_genre_long.columns = ['genre_ids', 'song_id']
songs_genre_long['count'] = 1
songs_genre_wide = songs_genre_long.pivot(index='song_id',
                                          columns='genre_ids',
                                          values='count')
del songs_genre_long

# generate song_id-artist_name matrix
# code will run into RAM problem
songs_artist_long = songs[['song_id', 'artist_name']].astype(str)
songs_artist_long = pd.DataFrame(songs_artist_long.artist_name.str.split('|').
                                 tolist(),
                                 index=songs_artist_long.song_id).stack()
songs_artist_long = songs_artist_long.reset_index()[[0, 'song_id']]
songs_artist_long.columns = ['artist_name', 'song_id']
songs_artist_long['count'] = 1
songs_artist_wide = songs_artist_long.pivot(index='song_id',
                                            columns='artist_name',
                                            values='count')
"""

# MATRIX FACTORIZATION ON SONG ARTIST NAMES
# create list of list for the multilabel variable
artist_names = songs['artist_name'].str.split(' & ').tolist()
# create list of unique identifier for later assembling
song_id = songs.song_id.tolist()
# generate dictionary for the sklearn DictVectorizer
dict_artist = [{name: 1 for name in artist_names[i]} for
               i in range(len(song_id))]
# Train a DictVectorizer based on d_artist_name
vec_artist = DictVectorizer().fit(dict_artist)
# Generate a CSR sparse matrix use the trained DictVectorizer
m_artist = vec_artist.transform(dict_artist)
# Train a TruncatedSVD model with m_artist_name
svd_artist_name = TruncatedSVD(n_components=10,
                               algorithm='randomized',
                               random_state=1122).fit(m_artist)
# Generate a svd matrix for song artist_names
v_artist = svd_artist_name.transform(m_artist)

# Assemble a pd.DataFrame with the artist_svd
artist_svds = ['artist_svd_'+str(i+1) for i in range(10)]
artist_df = pd.DataFrame(v_artist,
                         columns=artist_svds)
artist_df['song_id'] = np.array(song_id)

# TODO: use gensim package to load and write songs table transformation with
# hard disk to bypass RAM issues
