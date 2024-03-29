import datetime
import os
import time

import git
import tweepy

from commits import BSDCommit


environ = os.environ

repo_path = environ.get("GIT_REPO_PATH")
g = git.Git(repo_path)
repo = git.Repo(repo_path)

# Twitter v1 API (deprecated)
#auth = tweepy.OAuthHandler(environ.get("TWITTER_CONSUMER_KEY"),
#                           environ.get("TWITTER_CONSUMER_SECRET"))
#auth.set_access_token(environ.get("TWITTER_KEY"),
#                      environ.get("TWITTER_SECRET"))
#
#api = tweepy.API(auth)

# Twitter v2 API
client = tweepy.Client(
    consumer_key=environ.get("TWITTER_CONSUMER_KEY"),
    consumer_secret=environ.get("TWITTER_CONSUMER_SECRET"),
    access_token=environ.get("TWITTER_KEY"),
    access_token_secret=environ.get("TWITTER_SECRET"),
)

UPDATE_INTERVAL = 180.0 # seconds

TWEET_LIMIT = 270
BASEDIR_LIMIT = 2
BASEDIR_CHAR_LIMIT = 30

TWEET_TEMPLATE = "{author_info}{committer_handle}@ on {basedirs} ({sha}):\n\n"
TWEET_TEMPLATE += "{msg}\n\n"
TWEET_TEMPLATE += "https://cgit.freebsd.org/src/commit/?id={sha}"

LAST_SHA_FILE = "./.last_sha"


# https://stackoverflow.com/questions/17215400/format-string-unused-named-arguments
class SafeDict(dict):
    def __missing__(self, key):
        return '{' + key + '}'


def post_new(commit):
    # find basedirs
    diff_raw = g.diff("--dirstat=files,0", f"{commit.commit_sha}..{commit.commit_sha}^")
    if not diff_raw:
        # only committed to the root directory
        basedirs_list = ["."]
    else:
        basedirs_list = []
        for line_raw in diff_raw.split("\n"):
            line = line_raw.strip().split(" ")[1]
            if line.endswith("/"):
                line = line[:-1]
            basedirs_list.append(line)

    # too many directories
    if len(basedirs_list) > BASEDIR_LIMIT:
        basedirs_list = basedirs_list[:BASEDIR_LIMIT]
        basedirs_list.append("..")

    basedirs = " ".join(basedirs_list)

    # directory path too long
    if len(basedirs) > BASEDIR_CHAR_LIMIT:
        basedirs = basedirs[:BASEDIR_CHAR_LIMIT] + ".."
    
    commit_info = SafeDict(
        author_info="" if commit.author_is_committer else f"{commit.author} via ",
        committer_handle=commit.committer_handle,
        sha=commit.commit_sha_short,
        basedirs=basedirs,
    )

    cur_tweet_limit = TWEET_LIMIT
    while True:
        cur_tweet = TWEET_TEMPLATE.format_map(commit_info)
        char_count_left = cur_tweet_limit - len(cur_tweet)
        commit_msg_body = commit.commit_msg_title + "\n\n" + commit.commit_msg_body
        if len(commit_msg_body) > char_count_left:
            commit_msg_body = commit_msg_body[:char_count_left] + "...\n"
        cur_tweet = cur_tweet.format_map(SafeDict(msg=commit_msg_body))

        try:
            client.create_tweet(text=cur_tweet)
        except tweepy.errors.TooManyRequests:
            print(f"caught 429 too many requests - cooling down")
            return False
        except tweepy.errors.TweepyException:
            print(f"caught exception - shorten the tweet {commit.commit_sha_short} by {commit.committer_handle}")
            cur_tweet_limit -= 1
            continue
        return True


def get_last_commit_sha():
    try:
        with open(LAST_SHA_FILE, "r") as f:
            last_sha = f.read().strip()
    except:
        raise FileNotFoundError(f"Please create a file {LAST_SHA_FILE} with the latest sha in it.")
    
    print(f"latest sha is {last_sha}.")
    return last_sha


def set_last_commit_sha(sha):
    with open(LAST_SHA_FILE, "w") as f:
        f.write(sha)
    print(f"updated latest sha to {sha}")


def get_git_commits_from(commit_sha):
    repo.remotes.origin.pull("main")
    raw_logs = g.log("--reverse", "--ancestry-path", f"{commit_sha}...main", "--pretty=full").split("\n")
    commits = []
    cur_log = []
    for raw_log in raw_logs:
        if raw_log.startswith("commit ") and cur_log:
            commits.append(BSDCommit(commit_log=cur_log))
            cur_log = []
        if raw_log.strip():
            cur_log.append(raw_log)
    if cur_log:
        commits.append(BSDCommit(commit_log=cur_log))
    return commits


def main():
    last_sha = get_last_commit_sha()
    commits = get_git_commits_from(last_sha)

    count = 0
    for commit in commits:
        count += 1
        res = False
        try:
            res = post_new(commit)
            if res:
                set_last_commit_sha(commit.commit_sha_short)
                print(f"({count}/{len(commits)}): tweeted {commit.commit_sha_short} by {commit.committer_handle}")
        except Exception as e:
            print(vars(commit))
            import traceback; traceback.print_exception(type(e), e, e.__traceback__)
            break
        if not res:
            print("post failed, cooling down")
            break
                

if __name__ == "__main__":
    starttime = time.time()
    total, succeeded = 0, 0
    while True:
        print(f"{total - succeeded} failures, tick", datetime.datetime.now())
        total += 1
        try:
            main()
            succeeded += 1
        except Exception as e:
            print(e)
        time.sleep(UPDATE_INTERVAL - ((time.time() - starttime) % UPDATE_INTERVAL))
