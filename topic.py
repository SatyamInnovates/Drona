def topic_finding(path):
    name = path.replace("\\", "/").split("/")[-1]   
    return name.rsplit(".", 1)[0]                   