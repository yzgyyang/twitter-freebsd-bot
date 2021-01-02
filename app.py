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

TWEET_TEMPLATE = "{author}@ on {basedirs} (commit {sha}):\n\n"
TWEET_TEMPLATE += "{title}\n\n"
TWEET_TEMPLATE += "{body}\n"
TWEET_TEMPLATE += "full: https://cgit.freebsd.org/src/commit/?id={sha}"

def post_new(commit):    
    diff_raw = g.diff("--dirstat=files,0", f"{commit.commit_sha}..{commit.commit_sha}^")
    if not diff_raw:
        # only committed to the root directory
        basedirs = ["."]
    else:
        basedirs = []
        for line_raw in diff_raw.split("\n"):
            line = line_raw.strip().split(" ")[1]
            if line.endswith("/"):
                line = line[:-1]
            basedirs.append(line)

    # too many directories
    if len(basedirs) >= 4:
        basedirs = basedirs[:3]
        basedirs.append("..")
    
    commit_info = {
        "author": commit.author_handle,
        "sha": commit.commit_sha_short,
        "title": commit.commit_msg_title,
        "body": commit.commit_msg_body[:150] + "...\n" if len(commit.commit_msg_body) > 151 else commit.commit_msg_body,
        "basedirs": " ".join(basedirs),
    }

    api.update_status(TWEET_TEMPLATE.format(**commit_info), hide_media=True)

def get_last_tweet_commit_sha():
    tweet = api.user_timeline(count=1)[0].text
    return tweet.split("\n")[0].split("(commit ")[1].split(")")[0]

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
