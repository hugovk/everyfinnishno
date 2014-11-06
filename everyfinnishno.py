#!/usr/bin/env python
# encoding: utf-8
"""
Tweet every Finnish number.
"""
from __future__ import print_function, unicode_literals
import argparse
import sys
import twitter
import webbrowser
import yaml

HELSINKI_LAT = 60.170833
HELSINKI_LONG = 24.9375


def load_yaml(filename):
    """
    File should contain:
    consumer_key: TODO_ENTER_YOURS
    consumer_secret: TODO_ENTER_YOURS
    oauth_token: TODO_ENTER_YOURS
    oauth_token_secret: TODO_ENTER_YOURS
    If it contains last_number, don't change it
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

    return data


def save_yaml(filename, data):
    with open(filename, 'w') as yaml_file:
        yaml_file.write(yaml.safe_dump(data, default_flow_style=False))


def build_tweet(number):
    import fino
    tweet = str(number) + " " + fino.to_finnish(number)
    return tweet


def tweet_it(string, credentials):
    if len(string) <= 0:
        print("ERROR: trying to tweet an empty tweet!")
        return

    # Create and authorise an app with (read and) write access at:
    # https://dev.twitter.com/apps/new
    # Store credentials in YAML file
    t = twitter.Twitter(auth=twitter.OAuth(
        credentials['oauth_token'],
        credentials['oauth_token_secret'],
        credentials['consumer_key'],
        credentials['consumer_secret']))

    print("TWEETING THIS:", string)

    if args.test:
        print("(Test mode, not actually tweeting)")
    else:
        result = t.statuses.update(
            status=string,
            lat=HELSINKI_LAT, long=HELSINKI_LONG,
            display_coordinates=True)
        url = "http://twitter.com/" + \
            result['user']['screen_name'] + "/status/" + result['id_str']
        print("Tweeted: " + url)
        if not args.no_web:
            webbrowser.open(url, new=2)  # 2 = open in a new tab, if possible


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

# End of file
