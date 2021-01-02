META = (
    "PR:",
    "Reviewed by:",
    "Reviewed-by:",
    "Approved by:",
    "Approved-by:",
    "Submitted by:",
    "Submitted-by:",
    "Reported by:",
    "Reported-by:",
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
        self.author_handle = ""
        self.date = ""
        self.commit_msg_title = ""
        self.commit_msg_body = ""
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
