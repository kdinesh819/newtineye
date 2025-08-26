from fastapi import FastAPI, Request, HTTPException
from tineye_api import paneltin
import utils
import urllib.parse
import random
import string
from urllib.parse import urlparse, urlunparse, unquote

app = FastAPI()

allow_tineye = ['shutterstock', 'depositphotos', 'alamy', 'istockphoto']


@app.get('/tineye')
def tineye_api(request: Request):
    dupimagess = request.query_params.get('dupimage', '')
    dupimages = dupimagess.replace("refunded", "")
    userId = request.query_params.get('userId')
    if "freepik" in dupimagess:
        # Decode the URL
        decoded_url = unquote(dupimagess)
        parsed_url = urlparse(decoded_url)
        dupimage = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))
    elif "stock.adobe" in dupimagess:
        dupid = utils.extract_source_data(dupimagess)['id']
        dupimage = "https://stock.adobe.com/in/" + dupid
    else:
        dupimage = urllib.parse.unquote(dupimages)



    if not dupimage:
        raise HTTPException(status_code=400, detail="dupimage parameter is required")

    image_thumb, source, ext = utils.get_thumnail_url(dupimage)
    tin = paneltin()

    if image_thumb == "Something error happened.":
        parsed_url = urlparse(dupimages)
        domain = parsed_url.netloc

        characters = string.ascii_letters + string.digits  # A-Z, a-z, 0-9
        random_string = ''.join(random.choices(characters, k=8))
        fslugn = domain + "_" + random_string

        queryhash = tin.get_query_hash(dupimages, 'ss', fslugn, ext)
        return {"query_hash": queryhash}
    else:
        actual_id = utils.extract_source_data(dupimage)['id']
        if source == "shutterstock":
            ext = utils.get_shutterstock_predictor_extension(dupimage)

        if source in allow_tineye:
            checker_id = source + "_" + actual_id
            file = utils.search_pcloud_for_files(checker_id)
            if file == "not exist":
                tin.process_original_data(source, image_thumb, dupimage, source, actual_id, ext, userId)
                queryhash = tin.get_query_hash(image_thumb, source, actual_id, ext)
            else:
                queryhash = tin.process_original_data_pcloud(source, image_thumb, dupimage, source, actual_id, ext,
                                                             userId)
        else:
            queryhash = tin.process_original_data_only_original(source, image_thumb, dupimage, source, actual_id, ext,
                                                                userId)

        if queryhash is None:
            raise HTTPException(status_code=500, detail="Error in processing the image")
        print(queryhash)
        return {"query_hash": queryhash}


if __name__ == "__main__":
    import uvicorn, os
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)

