#!/usr/bin/env python
# encoding: utf-8
"""
Tweet every Finnish number.
"""
from __future__ import print_function, unicode_literals
import argparse
import fino
import sys
import twitter
import webbrowser
import yaml

HELSINKI_LAT = 60.170833
HELSINKI_LONG = 24.9375

TWITTER = None


# cmd.exe cannot do Unicode so encode first
def print_it(text):
    print(text.encode('utf-8'))


def load_yaml(filename):
    """
    File should contain:
    consumer_key: TODO_ENTER_YOURS
    consumer_secret: TODO_ENTER_YOURS
    oauth_token: TODO_ENTER_YOURS
    oauth_token_secret: TODO_ENTER_YOURS
    If it contains last_number or last_mention_id, don't change it
    """
    f = open(filename)
    data = yaml.safe_load(f)
    f.close()
    if not data.viewkeys() >= {
            'oauth_token', 'oauth_token_secret',
            'consumer_key', 'consumer_secret'}:
        sys.exit("Twitter credentials missing from YAML: " + filename)

    if 'last_number' not in data:
        data['last_number'] = 0

    if 'last_mention_id' not in data:
        data['last_mention_id'] = 1

    return data


def save_yaml(filename, data):
    with open(filename, 'w') as yaml_file:
        yaml_file.write(yaml.safe_dump(data, default_flow_style=False))


def build_tweet(number, reply_to=None):
    tweet = ""
    if reply_to:
        tweet += "@" + reply_to + " "
    tweet += str(number) + " " + fino.to_finnish(number)

    # Truncate?
    if len(tweet) > 140:
        tweet = tweet[:139] + "…"

    return tweet


def tweet_it(string, credentials, in_reply_to_status_id=None):
    global TWITTER
    if len(string) <= 0:
        print("ERROR: trying to tweet an empty tweet!")
        return

    # Create and authorise an app with (read and) write access at:
    # https://dev.twitter.com/apps/new
    # Store credentials in YAML file
    if TWITTER is None:
        TWITTER = twitter.Twitter(auth=twitter.OAuth(
            credentials['oauth_token'],
            credentials['oauth_token_secret'],
            credentials['consumer_key'],
            credentials['consumer_secret']))

    print_it("TWEETING THIS: " + string)

    if args.test:
        print("(Test mode, not actually tweeting)")
    else:
        result = TWITTER.statuses.update(
            status=string,
            lat=HELSINKI_LAT, long=HELSINKI_LONG,
            display_coordinates=True,
            in_reply_to_status_id=in_reply_to_status_id)
        url = "http://twitter.com/" + \
            result['user']['screen_name'] + "/status/" + result['id_str']
        print("Tweeted: " + url)
        if not args.no_web:
            webbrowser.open(url, new=2)  # 2 = open in a new tab, if possible


def check_replies(credentials):
    global TWITTER
    print("Check replies...")
#     TODO remove duplicate
    if TWITTER is None:
        TWITTER = twitter.Twitter(auth=twitter.OAuth(
            credentials['oauth_token'],
            credentials['oauth_token_secret'],
            credentials['consumer_key'],
            credentials['consumer_secret']))

    mentions = TWITTER.statuses.mentions_timeline(since_id=credentials[
                                                  'last_mention_id'])
    for i, m in enumerate(reversed(mentions)):
        print("*"*80)
        print(i)
        print_it("text: " + m['text'])
        print("in_reply_to_screen_name:", m['in_reply_to_screen_name'])
        print("screen_name:", m['user']['screen_name'])
        print("ID:", m['id'])
        number = extract_number_from_tweet(m['text'])
        print("Found a number:", number)
        if number:
            # Does the mention already include the Finnish?
            # If so, it's probably an edited retweet, so don't reply
            if fino.to_finnish(number) in m['text']:
                print("Mention already includes the Finnish, don't reply")
            else:
                tweet = build_tweet(number, reply_to=m['user']['screen_name'])
                # print(tweet)
                tweet_it(tweet, data, in_reply_to_status_id=m['id'])

        data['last_mention_id'] = m['id']
        print("Save last mention ID for next time:", data['last_mention_id'])

        if not args.test:
            save_yaml(args.yaml, data)


def extract_number_from_tweet(text):
    # Remove commas
    text = text.replace(",", "").rstrip("?")

    # http://stackoverflow.com/a/4289557/724176
    ints = [int(s) for s in text.split() if s.isdigit()]
    if len(ints):
        return ints[0]
    else:
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Tweet every Finnish number.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '-y', '--yaml',
        default='C:/Users/hugovk/bin/data/everyfinnishno.yaml',
        help="YAML file location containing Twitter keys and secrets")
    parser.add_argument(
        '-nw', '--no-web', action='store_true',
        help="Don't open a web browser to show the tweeted tweet")
    parser.add_argument(
        '-x', '--test', action='store_true',
        help="Test mode: go through the motions but don't update anything")
    args = parser.parse_args()

    data = load_yaml(args.yaml)

    tweet = build_tweet(data['last_number'])

    # print("Tweet this:\n", tweet)
    tweet_it(tweet, data)

    data['last_number'] += 1
    print("Save new number for next time:", data['last_number'])
    if not args.test:
        save_yaml(args.yaml, data)

    check_replies(data)

# End of file
