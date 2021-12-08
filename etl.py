import configparser
from datetime import datetime
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col
from pyspark.sql.functions import (
    year, 
    month, 
    dayofmonth, 
    hour, 
    weekofyear, 
    dayofweek, 
    date_format, 
    monotonically_increasing_id
)
from pyspark.sql.types import (
    StructType, 
    StructField, 
    StringType, 
    IntegerType, 
    DoubleType, 
    TimestampType
)
from schema import SONG_DATA_SCHEMA, LOG_DATA_SCHEMA

# config = configparser.ConfigParser()
# config.read('dl.cfg')

# os.environ['AWS_ACCESS_KEY_ID']=config['AWS_ACCESS_KEY_ID']
# os.environ['AWS_SECRET_ACCESS_KEY']=config['AWS_SECRET_ACCESS_KEY']


def create_spark_session():
    spark = SparkSession \
        .builder \
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:2.7.0") \
        .getOrCreate()
    return spark


def process_song_data(spark, input_data, output_data):
    # get filepath to song data file
    song_data = os.path.join(input_data, "song-data", "*", "*", "*", "*.json")
    
    # read song data file
    df = spark.read.json(song_data, schema=SONG_DATA_SCHEMA)

    # extract columns to create songs table
    songs_table = df.select('song_id', 'title', 'artist_id', 'year', 'artist_name', 'duration').distinct()
    
    # write songs table to parquet files partitioned by year and artist
    songs_table.write.mode('overwrite').partitionBy(
        "year", "artist_id").parquet(output_data + "songs_table.parquet")

    # extract columns to create artists table
    artists_table = df.select(
    "artist_id",
    col("artist_name").alias("name"),
    col("artist_location").alias("location"),
    col("artist_latitude").alias("latitude"),
    col("artist_longitude").alias("longitude")
    ).drop_duplicates()
    
    # write artists table to parquet files
    artists_table.write.mode('overwrite').parquet(output_data + "artist_table.parquet")


def process_log_data(spark, input_data, output_data):
    # get filepath to log data file
    # log_data = os.path.join(input_data, "log-data", "*.json") # LOCAL PATH ON MY MACHINE
    log_data = os.path.join(input_data, "log-data", "*", "*", "*.json")

    # read log data file
    df = spark.read.json(log_data, schema=LOG_DATA_SCHEMA)
    
    # filter by actions for song plays
    df = df.filter(df.page == 'NextSong')

    # create timestamp column from original timestamp column
    get_timestamp = udf(lambda ts: datetime.utcfromtimestamp(ts / 1000.0).
        strftime("%Y-%m-%d %H:%M:%S"), 
        StringType()
         )
    df = df.withColumn('timestamp', get_timestamp("ts"))
    
    # create datetime column from original timestamp column
    get_datetime = udf(
        lambda x: datetime.utcfromtimestamp(x / 1000),
        TimestampType()
    )
    df = df.withColumn("start_time", get_datetime("ts"))
    
    # extract columns to create time table
    time_table = (
        df
        .withColumn("hour", hour("start_time"))
        .withColumn("day", dayofmonth("start_time"))
        .withColumn("week", weekofyear("start_time"))
        .withColumn("month", month("start_time"))
        .withColumn("year", year("start_time"))
        .withColumn("weekday", dayofweek("start_time"))
        .select(
            "start_time",
            "hour",
            "day",
            "week",
            "month",
            "year",
            "weekday"
        )
        .drop_duplicates(["year", "month", "day", "hour"])
    )
    
    # write time table to parquet files partitioned by year and month
    time_table.write.parquet(
        os.path.join(output_data, "time_table.parquet"),
        mode="overwrite",
        partitionBy=["year", "month"]
    )

    # read in song data to use for songplays table
    songs = spark.read.parquet(
        os.path.join(output_data, "songs_table.parquet")
    )

    # extract columns from joined song and log datasets to create songplays table 
    songplays_table = (
        df
        .join(songs, [
            df.song == songs.title,
            df.artist == songs.artist_name,
            df.length == songs.duration
        ], "left")
    )

    songplays_table = (
        songplays_table
        .select(
            monotonically_increasing_id().alias("songplay_id"),
            "start_time",
            col("userID").alias("user_id"),
            "level",
            "song_id",
            "artist_id",
            col("sessionId").alias("session_id"),
            "location",
            col("userAgent").alias("user_agent"),
            month("start_time").alias("month"),
            year("start_time").alias("year")
        )
    )

    # write songplays table to parquet files partitioned by year and month
    songplays_table.write.parquet(
        os.path.join(output_data, "songplays_table.parquet"),
        mode="overwrite",
        partitionBy=["year", "month"]
    )


def main():
    spark = create_spark_session()

    # input_data = 'data/'
    # output_data = 'data/output_data/'

    input_data = "s3a://udacity-dend/"
    output_data = "s3a://drggfish-spark-udacity-dend/"
    
    process_song_data(spark, input_data, output_data)    
    process_log_data(spark, input_data, output_data)


if __name__ == "__main__":
    main()
