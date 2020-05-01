import bs4
import lxml

from bs4 import BeautifulSoup as bs
content = []

#Read the XML files
type = "tripinfo_" + input("type of file: default(def), source density(sou), congestion Boolean(con), lagging Boolean(lag) = ") + "_"
print("Reading file: " + type)
for i in range(1, 6):
    # read non traffic files
    name = type + str(i) + ".xml"
    with open(name, "r") as file:
        content = file.readlines()
        content = "".join(content)
        bs_content = bs(content, "lxml")
        result = bs_content.find_all("tripinfo")
    
        count = 0
        total_wait = float(0)
        # parse each item in result
        for r in result:
            count += 1
            total_wait += float(r["waitingtime"])
    file.close()

    # read traffic files
    name = type + "traf_" + str(i) + ".xml"
    with open(name, "r") as file:
        content = file.readlines()
        content = "".join(content)
        bs_content = bs(content, "lxml")
        result = bs_content.find_all("tripinfo")
    
        total_wait_traf = float(0)
        # parse each item in result
        for r in result:
            total_wait_traf += float(r["waitingtime"])
    file.close()

    print("i: " + str(i))
    print("Count: " + str(count))
    print("Total wait time without traffic: " + str(total_wait))
    print("Total wait time with traffic: " + str(total_wait_traf))
