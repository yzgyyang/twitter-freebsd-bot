import re


META = (
    "PR:",
    "Reviewed by:",
    "Reviewed-by:",
    "Requested by:",
    "Requested-by:",
    "Approved by:",
    "Approved-by:",
    "Submitted by:",
    "Submitted-by:",
    "Reported by:",
    "Reported-by:",
    "Obtained from:",
    "Obtained-from:",
    "Discussed with:",
    "Discussed-with:",
    "Sponsored by:",
    "Sponsored-by:",
    "Tested by:",
    "Tested-by:",
    "MFC after:",
    "MFC-after:",
    "Differential Revision:",
    "Differential-Revision:",
)


class BSDCommit:
    def __init__(self, commit_log: list):
        self.commit_sha = ""
        self.commit_sha_short = ""
        self.author = ""
        self.author_email = ""
        self.committer = ""
        self.committer_email = ""
        self.committer_handle = ""
        self.commit_msg_title = ""
        self.commit_msg_body = ""
        self.author_is_committer = None
        self.commit_meta = []

        pattern = "[^:]*:\s([^<]*)\s<([^>]*)>"

        for idx, msg in enumerate(commit_log):
            # "commit 17eba5e32a2cf7a217bb9f1e5dcca351f2b71cfc"
            if msg.startswith("commit ") and not self.commit_sha:
                self.commit_sha = msg.split("commit ")[1].strip()
                self.commit_sha_short = self.commit_sha[:8]
            # "Author: Guangyuan Yang <ygy@FreeBSD.org>"
            elif msg.startswith("Author: ") and not self.author:
                r = re.search(pattern, msg)
                self.author = r.group(1)
                self.author_email = r.group(2)
            # "Commit: Guangyuan Yang <ygy@FreeBSD.org>"
            elif msg.startswith("Commit: ") and not self.committer:
                r = re.search(pattern, msg)
                self.committer = r.group(1)
                self.committer_email = r.group(2)
                self.committer_handle = self.committer_email.split("@")[0]
            else:
                break
        
        self.author_is_committer = self.author_email.lower() == self.committer_email.lower()

        # commit message title and body
        for idx in range(idx, len(commit_log)):
            if not self.commit_msg_title:
                self.commit_msg_title = commit_log[idx].strip()
                continue
            if commit_log[idx].strip().startswith(META):
                break
            self.commit_msg_body += commit_log[idx].strip()
            self.commit_msg_body += "\n"

        # commit meta tags
        for idx in range(idx, len(commit_log)):
            if commit_log[idx].strip():
                self.commit_meta.append(commit_log[idx].strip())
