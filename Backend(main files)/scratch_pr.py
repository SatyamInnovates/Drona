
# # {"2026-10-04": [21256,20185]} to {"ms": 17863, "project": "Unassigned"}

def normalize(sessions):
   
    if isinstance(sessions,(int,float)):
        return {"ms":sessions,"project":"Unassigned"}
    return sessions
        
day = [17863, 116570, {"ms": 5000, "project": "Drona"}]

# print([normalize(s) for s in day])

# session = 17863
# box = {"ms":session,"project":"Unassigned"}
# print(box)


def total_by_project(sessions):
    totals = {}
    for s in sessions:
        box = normalize(s)
        name = box['project']
        totals[name] = totals.get(name,0) + box["ms"]
    return totals

print(total_by_project(day))

