def topic_finding(path):
    name = path.replace("\\", "/").split("/")[-1]   
    return name.rsplit(".", 1)[0]                    

path = "C:\Drona\Backend(main files)\main.py"

def category_finding(path):
    print("PATH RECEIVED:", repr(path))
    parts = path.replace("\\", "/").split("/")
    return parts[-2]   

print(category_finding(path))