from fastapi import FastAPI, File, UploadFile
import time
from quicksand.quicksand import quicksand
import json


app = FastAPI()

class BytesDump(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return obj.decode(errors='replace')
        return json.JSONEncoder.default(self, obj)

# recursive key as string conversion for byte keys
def keys_string(d):
    rval = {}
    if not isinstance(d, dict):
        if isinstance(d,(tuple,list,set)):
            v = [keys_string(x) for x in d]
            return v
        else:
            return d

    for k,v in d.items():
        if isinstance(k,bytes):
            k = k.decode()
        if isinstance(v,dict):
            v = keys_string(v)
        elif isinstance(v,(tuple,list,set)):
            v = [keys_string(x) for x in v]
        rval[k] = v
    return rval


@app.post("/files/")
async def create_file(file: bytes = File()):
    return {"file_size": len(file)}


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File()):
    request_time = str(time.time())
    file_location = f"/tmp/{file.filename}.{request_time}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())

    qs = quicksand(file_location, capture=False )
    qs.process()
    return json.loads(json.dumps(keys_string(qs.results), cls=BytesDump,sort_keys=True))
#    return {"info": f"file '{file.filename}' saved at '{file_location}'","result":keys_string(qs.results)}

