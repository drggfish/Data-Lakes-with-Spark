## Data Lakes with Spark

In this project, you'll apply what you've learned on Spark and data lakes to build an ETL pipeline for a data lake hosted on S3. To complete the project, you will need to load data from S3, process the data into analytics tables using Spark, and load them back into S3. You'll deploy this Spark process on a cluster using AWS.

## Song Dataset
The first dataset is a subset of real data from the Million Song Dataset.
Each file is in JSON format and contains metadata about a song and the artist of that song.
The files are partitioned by the first three letters of each song's track ID.
For example, here are filepaths to two files in this dataset.
```
song_data/A/B/C/TRAACCG128F92E8A55.json
song_data/A/A/B/TRAACER128F4290F96.json
```

Here is an example of the contents of a single song file, TRAACCG128F92E8A55.json:
```
{
    "num_songs": 1,
    "artist_id": "AR5KOSW1187FB35FF4",
    "artist_latitude": 49.80388,
    "artist_longitude": 15.47491,
    "artist_location": "Dubai UAE",
    "artist_name": "Elena",
    "song_id": "SOZCTXZ12AB0182364",
    "title": "Setanta matins",
    "duration": 269.58322,
    "year": 0
}
```

## Log dataset

The second dataset consists of log files in JSON format generated by this event simulator based on the songs in the dataset above. These simulate activity logs from a music streaming app based on specified configurations.

The log files in the dataset you'll be working with are partitioned by year and month. For example, here are filepaths to two files in this dataset.
```
log_data/2018/11/2018-11-01-events.json
log_data/2018/11/2018-11-02-events.json
```

Here is an example of the contents of a single log file, 2018-11-01-events.json:
```
{
	"artist": null,
	"auth": "Logged In",
	"firstName": "Walter",
	"gender": "M",
	"itemInSession": 0,
	"lastName": "Frye",
	"length": null,
	"level": "free",
	"location": "San Francisco-Oakland-Hayward, CA",
	"method": "GET",
	"page": "Home",
	"registration": 1540919166796.0,
	"sessionId": 38,
	"song": null,
	"status": 200,
	"ts": 1541105830796,
	"userAgent": "\"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.143 Safari/537.36\"",
	"userId": "39"
}
```
## Table Design

### Fact Tables
- songplays - records in log data associated with song plays i.e. records with page NextSong
### Dimension Tables
- users - users in the app
- songs - songs in music database
- artists - artists in music database
- time - timestamps of records in songplays broken down into specific units

 The **songplays table** schema and data types:

 | Field        | Data Type          |
 | ------------- | ------------- |
 | songplay_id      | int |
 | start_time      | int    |  
 | user_id | int  | 
 | level |  varchar |
 | song_id | varchar      |  
 | artist_id | varchar     |  
 | session_id | int  |
 | location | varchar      |
 | user_agent | varchar    |

 The **users table** which contains:

 | Field        | Data Type          |
 | ------------- | ------------- |
 | user_id      | int |
 | first_name      | varchar      |
 | last_name | varchar      |
 | gender | varchar      |
 | level | varchar |

The **songs table** which contains:

 | Field        | Data Type          |
 | ------------- | ------------- |  
 | song_id      | varchar |
 | title      | varchar      |
 | artist_id | varchar      |
 | artist_name | varchar      | 
 | year | int     |
 | duration | float     |

  The **artists table** which contains:

 | Field        | Data Type          |
 | ------------- | ------------- |  
 | artist_id      | varchar |
 | name      | varchar      |
 | location | varchar      |  
 | latitude | varchar      |
 | longitude | varchar   |

 
The **time table** which contains:

 | Field        | Data Type          |
 |-------------  | ------------- |
 | start_time      |int |
 | hour      | int     |
 | day | int      |
 | week | int     |
 | month | int      |
 | year | int     |  
 | weekday | int     |