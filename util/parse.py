
def parse_headers(data: str):
    dic = {}
    for i in range(len(data)):
        if data[i].endswith(":"):
            if data[i+1].endswith(";"):
                j = i + 1
                val = data[j]
                while data[j].endswith(";"):
                    val += " " + data[j+1]
                    j += 1  
                dic[data[i].strip()] = val
            else: 
                dic[data[i].strip()] = data[i+1].strip()
    return dic