from tqdm import tqdm
import requests
url = 'https://file-examples.com/storage/fef7a0384867fa86095088c/2017/11/file_example_MP3_700KB.mp3'
r = requests.get(url, stream=True)
totalExpectedBytes = int(r.headers['Content-Length'])

bytesReceived = 0

with open("audio.mp3", 'wb') as f:
    for chunk in r.iter_content(chunk_size=128):
        print(f"{bytesReceived} received out of {totalExpectedBytes}") 
        f.write(chunk)
        bytesReceived += 128
    


# aise hi likha hai, isko hata dena baad mein | abhi test ke liye likha hai