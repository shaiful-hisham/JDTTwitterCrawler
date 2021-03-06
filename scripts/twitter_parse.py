import json
import collections
from ConfigParser import SafeConfigParser
import sys, os
import glob
from datetime import datetime
import csv


def convert(input):
    if isinstance(input, dict):
        return {convert(key): convert(value) for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [convert(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input

def to_ilan_csv(folder):
	# write the column headers
	csv_writer = csv.writer(out_file, quoting=csv.QUOTE_ALL)
	headers = ["tweet_id", "tweet_text", "favorited", "favoriteCount", "replyToSN", "created", "truncated", "replyToUID", "statusSource", "screenName", "retweetCount", "isRT", "location"]
	csv_writer.writerow(headers)

	# open the JSON files we stored and parse them into the CSV file we're working on
	try:
		json_files = glob.glob(folder)
		print("Parsing %s files." % len(json_files))
		for file in json_files:
			try:
				f = open(file, 'r')
			except:
				print("Couldn't open JSON file for parsing.")
			try:
				for line in f:
					# hack to avoid the trailing \n at the end of the file - sitcking point LH 4/7/16
					if len(line) > 3:
						i = 0
						tweets = convert(json.loads(line))
						for tweet in tweets:
							has_media = False
							is_RT = False
							is_MT = False
							hashtags_list = []
							mentions_list = []
							media_list = []

							entities = tweet["entities"]
							# old tweets don't have key "media" so need a workaround
							if entities.has_key("media"):
								has_media = True
								for item in entities["media"]:
									media_list.append(item["media_url"])

							for hashtag in entities["hashtags"] :
								hashtags_list.append(hashtag["text"])

							for user in entities["user_mentions"]:
								mentions_list.append(user["screen_name"])

							if tweet["text"][:2] == "RT":
								is_RT = True

							if tweet["text"][:2] == "MT":
								is_MT = True

							values = [
								tweet["id_str"],
                                tweet["text"],
                                tweet["favorited"],
                                tweet["favorite_count"],
                                tweet["in_reply_to_screen_name"],
                                datetime.strptime(tweet["created_at"], '%a %b %d %H:%M:%S +0000 %Y').strftime('%Y-%m-%d %H:%M:%S'),
                                tweet["truncated"],
                                tweet["in_reply_to_status_id"],
                                tweet["source"],
                                tweet["user"]["screen_name"],
								tweet["retweet_count"],
								tweet["retweeted"],
                                tweet["user"]["location"]
							]
							csv_writer.writerow(values)
					else:
						continue
			except ValueError as err:
				print("%s in %s" % (err, file))
				continue
			f.close()

	except:
		print("Something went wrong. Quitting.")
		for i in sys.exc_info():
			print(i)

if __name__ == '__main__' :

	config = SafeConfigParser()
	script_dir = os.path.dirname(os.path.abspath(__file__))
	config_file = os.path.join(script_dir, '../settings.cfg')
	config.read(config_file)
	outfolder = config.get('files','outfolder')
	out_filename = config.get('files', 'parsed_file')+"_"+datetime.now().strftime("%Y%m%d%H%M%S")+".csv"

	glob_search = outfolder + "*.json"

	try: # try to open the file for writing
		out_file = open(out_filename, 'wb')
	except:
		print("Couldn't open output file for saving parsed data. Quitting.")
		sys.exit()

	to_ilan_csv(glob_search)

	out_file.close
	print("Done parsing. See your data in %s." % out_filename)

sys.exit()
