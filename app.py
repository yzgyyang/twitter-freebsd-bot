import os

import git
import tweepy

from commits import BSDCommit

environ = os.environ

repo_path = environ.get("GIT_REPO_PATH")
g = git.Git(repo_path)
repo = git.Repo(repo_path)

auth = tweepy.OAuthHandler(environ.get("TWITTER_CONSUMER_KEY"),
                           environ.get("TWITTER_CONSUMER_SECRET"))
auth.set_access_token(environ.get("TWITTER_KEY"),
                      environ.get("TWITTER_SECRET"))

api = tweepy.API(auth)

def post_new(commit):
    TO_BE_FILLED = "{sha}: {title}\n{body}\nBy {author}@\ngh: https://github.com/freebsd/freebsd-src/commit/{sha}\ncgit: https://cgit.freebsd.org/src/commit/?id={sha}"
    commit_info = {
        "author": commit.author_handle,
        "sha": commit.commit_sha_short,
        "title": commit.commit_msg_title,
        "body": commit.commit_msg_body,
    }

    api.update_status(TO_BE_FILLED.format(**commit_info), hide_media=True)

def get_last_tweet_commit_sha():
    tweet = api.user_timeline(count=1)[0]
    return tweet.text.split(":")[0]

def get_git_commits_from(commit_sha):
    repo.remotes.origin.pull()
    raw_logs = g.log("--reverse", "--ancestry-path", f"{commit_sha}...main").split("\n")
    commits = []
    cur_log = []
    for raw_log in raw_logs:
        if raw_log.startswith("commit ") and cur_log:
            commits.append(BSDCommit(commit_log=cur_log))
            cur_log = []
        if raw_log.strip():
            cur_log.append(raw_log)
    return commits

if __name__ == "__main__":
    last_sha = get_last_tweet_commit_sha()
    commit = get_git_commits_from(last_sha)[0]
    post_new(commit)
