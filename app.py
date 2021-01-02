import os

import git
import tweepy

environ = os.environ

repo_dir = ""
repo = git.Repo(repo_dir)

auth = tweepy.OAuthHandler(environ.get("TWITTER_CONSUMER_KEY"),
                           environ.get("TWITTER_CONSUMER_SECRET"))
auth.set_access_token(environ.get("TWITTER_KEY"),
                      environ.get("TWITTER_SECRET"))

api = tweepy.API(auth)

def post_new():
    TO_BE_FILLED = "{sha}: {title}\nBy {author}@\ngh: https://github.com/freebsd/freebsd-src/commit/{sha}\ncgit: https://cgit.freebsd.org/src/commit/?id={sha}"
    commit = {
        "author": "lwhsu",
        "sha": "5ef5f51d",
        "title": "Mark the repository has been converted to Git",
    }

    api.update_status(TO_BE_FILLED.format(**commit), hide_media=True)

def get_last_tweet():
    tweet = api.user_timeline(count=1)[0]
    print(tweet.text)

def get_git_commits():
    repo.remotes.origin.pull()

#post_new()
#get_last_tweet()
