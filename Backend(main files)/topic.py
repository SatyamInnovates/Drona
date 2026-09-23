def topic_finding(path):
    name = path.replace("\\", "/").split("/")[-1]   
    return name.rsplit(".", 1)[0]                    



def category_finding(path):
    print("PATH RECEIVED:", repr(path))
    parts = path.replace("\\", "/").split("/")
    
    return parts[-2]   

