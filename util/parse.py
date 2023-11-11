
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

def parse_multipart(buff: bytes, boundary: bytes):
    dic = {}
    while len(buff.split(boundary, 1)) > 1:
        [bound,buff] = buff.split(boundary, 1)
        [headers,buff] = buff.split(b"\r\n\r\n", 1)
        headers = parse_headers(headers.decode().split())
        print(headers)
        name = headers["Content-Disposition:"].split()[1].split('=')[1].strip('\"')
        if name == 'upload";':
            [body,buff] = buff.split(b"\r\n", 1)
            name = name.strip('\";')
            filename = headers["Content-Disposition:"].split()[2].split('=')[1].strip('\"')
            filetype = headers["Content-Type:"].split('/')[1]
            dic['filename'] = filename
            dic['filetype'] = filetype
        else:
            [body,buff] = buff.split(b"\r\n", 1)
            body = body.decode()
        dic[name] = body

    return dic