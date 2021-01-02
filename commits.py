META = (
    "PR:",
    "Reviewed by:",
    "Approved by:",
    "Reported by:",
    "Sponsored by:",
    "Differential Revision:",
)


class BSDCommit:
    def __init__(self, commit_log: list):
        self.commit_sha = None
        self.commit_sha_short = None
        self.author = None
        self.author_handle = None
        self.date = None
        self.commit_msg_title = None
        self.commit_msg_body = None
        self.commit_meta = []

        for idx, msg in enumerate(commit_log):
            # "commit 17eba5e32a2cf7a217bb9f1e5dcca351f2b71cfc"
            if msg.startswith("commit ") and not self.commit_sha:
                self.commit_sha = msg.split("commit ")[1].strip()
                self.commit_sha_short = self.commit_sha[:8]
            # "Author: Kyle Evans <ygy@FreeBSD.org>"
            elif msg.startswith("Author: ") and not self.author:
                self.author = msg.split("Author: ")[1].strip()
                self.author_handle = self.author.split("@FreeBSD.org")[0].split("<")[1].strip()
            # "Date:   Fri Jan 1 23:59:21 2021 -0600"
            elif msg.startswith("Date: ") and not self.date:
                self.date = msg.split("Date: ")[1].strip()
            else:
                break

        for idx in range(3, len(commit_log)):
            if not self.commit_msg_title:
                self.commit_msg_title = commit_log[idx].strip()
                continue
            if commit_log[idx].strip().startswith(META):
                self.commit_meta.append(commit_log[idx].strip())
                continue
            if not self.commit_msg_body:
                self.commit_msg_body = ""
            self.commit_msg_body += commit_log[idx]
            self.commit_msg_body += "\n"
