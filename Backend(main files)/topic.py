import re


def topic_finding(path):
    name = path.replace("\\", "/").split("/")[-1]   
    return name.rsplit(".", 1)[0]                    



def category_finding(path, repo_path=None):
    path = path.strip('"')
    parts = path.replace("\\", "/").split("/")
    full_path = " ".join(
        part.replace("_", " ").replace("-", " ")
        for part in [str(repo_path) if repo_path is not None else "", path]
    )
    if re.search(r"\b(machine\s+learning|ml|aiml)\b", full_path, re.IGNORECASE):
        return "Machine learning"
    if len(parts) < 2:
        return parts[-1]
    return parts[-2]   
