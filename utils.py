import json
import requests
import urllib
from db import db_mongo
import re
from pymongo import MongoClient
from urllib.parse import urlparse, urlunparse, parse_qs

import urllib
import ssl
import json
import requests

platforms_tin = {
        "freepik.com": "freepik",
        "envato.com": "envato",
        "stock.adobe.com": "adobestock",
        "shutterstock.com": "shutterstock",
        "depositphotos.com": "depositphotos",
        "alamy.com": "alamy"
    }

def get_db_connection(db_name, collection):
    mongodb = db_mongo.MongoDB(
        uri="mongodb+srv://mysteriouscoder:mysteriouscoder@cluster0.agkearu.mongodb.net/?retryWrites=true&w=majority",
        db_name=db_name,
        collection_name=collection
    )
    return mongodb

mongo = get_db_connection("test", "fileprices")  # Define once globally

def get_thumnail_url(image_url):
    apikey = "VuqP6URUZjWD9zCEI57CHWviZdgimx"
    url = urllib.parse.quote(image_url)
    apiurl = "https://nehtw.com/api/stockinfo/null/null?apikey=" + apikey + "&url=" + url

    vpireq = requests.get(url=apiurl)
    jk = json.loads(vpireq.text)
    print("get details from vip")
    print(jk)

    if "data" in jk and "image" in jk["data"]:
        dupimage = jk["data"]["image"]
        source = jk["data"]["source"]
        ext = jk["data"]["ext"]
    else:
        dupimage = "No image found or another default value"
    try:
        er = jk['error']
        if er:
            return "Something error happened.", "", ""
        else:
            return dupimage, source, ext
    except Exception as e:
        return dupimage, source, ext

def getfilesprices_tineye(stock, source):
    try:
        if stock in platforms_tin:
            stock_search = platforms_tin[stock]

            result = mongo.find_documents({"site": stock_search})
            if result:
                if stock_search == source:
                    return result[0]['cost']
                else:
                    result2 = mongo.find_documents({"site": source})
                    pricef = result2[0]['cost']
                    print(type(pricef))

                    # Calculate 30% discount
                    discount = pricef * 0.30
                    # Calculate final price after discount
                    result23 = round(pricef - discount, 2)

                    return result23
            else:
                return "1"

            return price
        else:
            return "1"
    except:
        return "1"

def getfiles_slug_tineye(stock):
        try:
            if stock in platforms_tin:
                stock_search = platforms_tin[stock]
                return stock_search
            else:
                return "less"
        except:
            return "less"

def getfilesprices(stock, source):
    try:
        result = mongo.find_documents({"site": stock})
        if result:
            if stock == source:
                return result[0]['cost']
            else:
                result2 = mongo.find_documents({"site": stock})
                pricef = int(result2[0]['cost'])
                percentage = 40 / 100
                result23 = pricef * percentage
                return result23

        else:
            return "1"

        return price
    except:
        return "1"

def allowed_platforms(slugs: list, source: str):

    allowed_slugs_shutterstock = ["tineye_shutterstock", "adobestock", "freepik"] #"envato" excluded not saving on server thumb issue
    allowed_slugs_istockphoto = ["tineye_istockphoto", "adobestock", "freepik"]
    allowed_slugs_alamy = ["tineye_alamy", "adobestock", "freepik"]
    allowed_slug_depositphotos = ["tineye_depositphotos", "adobestock", "freepik"]

    if source == "shutterstock":
        filtered_data = [item for item in slugs if item["slug"] in allowed_slugs_shutterstock]
        return filtered_data
    elif source == "istockphoto":
        filtered_data = [item for item in slugs if item["slug"] in allowed_slugs_istockphoto]
        return filtered_data
    elif source == "alamy":
        filtered_data = [item for item in slugs if item["slug"] in allowed_slugs_alamy]
        return filtered_data
    elif source == "depositphotos":
        filtered_data = [item for item in slugs if item["slug"] in allowed_slug_depositphotos]
        return filtered_data
    else:
        return slugs

def check_envato_id_exist(url):
    pattern = re.findall(r"[A-Za-z0-9]+", url)
    for x in pattern:
        if x.isupper():
            print(f"Uppercase letters exist in pattern: {x}")
            return True
    return False

def get_envato_id(url):
    pattern = re.findall(r"[A-Za-z0-9]+", url)
    for x in pattern:
        if x.isupper():
            return x.isupper()
    return False

def geturlbyidshutterstock(url):
    pattern = r'\b\d{8,10}\b'
    matches = re.findall(pattern, url)
    if matches:
        finalmatch = matches[0]
        return finalmatch
    else:
        return None  # Return None if no match is found

def extract_source_data(url):

    if "shutterstock.com" in url:
        if "/video/clip-" in url:
            # Extract ID for Shutterstock video clip
            clip_id = url.split("/video/clip-")[1].split("/")[0]
            return {'source': 'vshutter', 'id': clip_id, 'url': url}
        elif "/music/track-" in url:
            # Extract ID for Shutterstock music track
            track_id = url.split("/music/track-")[1].split("/")[0]
            return {'source': 'mshutter', 'id': track_id, 'url': url}
        elif "image-vector" in url:
            # Extract ID for Shutterstock images
            img_id = url.split("-")[-1].split("/")[0]
            return {'source': 'shutterstock', 'id': img_id, 'url': url, 'ext': 'eps'}
        elif "image-photo" in url:
            # Extract ID for Shutterstock images
            img_id = url.split("-")[-1].split("/")[0]
            return {'source': 'shutterstock', 'id': img_id, 'url': url, 'ext': 'jpg'}
        elif "image-illustration" in url:
            # Extract ID for Shutterstock images
            img_id = url.split("-")[-1].split("/")[0]
            return {'source': 'shutterstock', 'id': img_id, 'url': url, 'ext': 'jpg'}
        else:
            pattern = r'\b\d{8,10}\b'
            matches = re.findall(pattern, url)
            try:
                finalmatch = matches[0]
                return {'source': 'shutterstock', 'id': finalmatch, 'url': url}
            except:
                array = re.findall(r'[0-9]+', url)
                for ii in range(0, len(array)):
                    check = array[ii]
                    lks = len(check)
                    if lks > 4:
                        return {'source': 'shutterstock', 'id': check, 'url': url}
                    else:
                        continue
    elif "stock.adobe.com" in url:
        if "search/audio?k=" in url:
            # Extract ID for Adobe audio search
            audio_id = url.split("audio?k=")[1].split("&")[0]
            return {'source': 'adobestock', 'id': audio_id, 'url': url}
        elif "asset_id=" in url:
            # Extract ID for Adobe asset
            asset_id = url.split("asset_id=")[1].split("&")[0]
            return {'source': 'adobestock', 'id': asset_id, 'url': url}
        elif "/images/" in url or "/templates/" in url:
            url = clean_url(url)
            # Extract ID for Adobe images or templates
            asset_id = url.split("/")[-1].split("-")[-1]
            return {'source': 'adobestock', 'id': asset_id, 'url': url}
        else:
            url = clean_url(url)
            pattern = r'\b(?:\d{8}|\d{9}|\d{10})\b'
            matches = re.findall(pattern, url)
            try:
                finalmatch = matches[0]
                return {'source': 'adobestock', 'id': finalmatch, 'url': url}
            except:
                array = re.findall(r'[0-9]+', url)
                for ii in range(0, len(array)):
                    check = array[ii]
                    lks = len(check)
                    if lks > 4:
                        return int(check)
                    else:
                        continue
    elif "depositphotos.com" in url:
        if "depositphotos_" in url:
            # Extract ID for Depositphotos
            deposit_id = url.split("depositphotos_")[1].split("_")[0]
            return {'source': 'depositphotos', 'id': deposit_id, 'url': url}
        else:
            deposit_id = url.split("/")[3].split("-")[0]
            return {'source': 'depositphotos', 'id': deposit_id, 'url': url}
    elif "123rf.com" in url:
        if "/photo_" in url:
            # Extract ID for 123rf photo
            photo_id = url.split("/photo_")[1].split("_")[0]
            return {'source': '123rf', 'id': photo_id, 'url': url}
        elif "mediapopup=" in url:
            # Extract ID for 123rf mediapopup
            media_id = url.split("mediapopup=")[1].split("&")[0]
            return {'source': '123rf', 'id': media_id, 'url': url}
        elif "stock-photo" in url:
            # Extract ID for 123rf stock photo
            stock_id = url.split("stock-photo/")[1].split(".html")[0]
            return {'source': '123rf', 'id': stock_id, 'url': url}
    elif "istockphoto.com" in url:
        if "gm" in url:
            # Extract ID for iStockphoto
            img_id = url.split("gm")[1].split("-")[0]
            return {'source': 'istockphoto', 'id': img_id, 'url': url}
    elif "gettyimages.com" in url:
        if "/detail/" in url:
            # Extract ID for Getty images
            getty_id = url.split("/detail/")[1].split("/")[0]
            return {'source': 'istockphoto', 'id': getty_id, 'url': url}

    elif "freepik.com" in url:
        if "_" in url:
            # Extract ID for Freepik
            freepik_id = url.split("_")[-1].split(".")[0]
            return {'source': 'freepik', 'id': freepik_id, 'url': url}

    elif "elements.envato.com" in url:
        # Extract ID for Envato elements
        envato_id = url.split("-")[-1].split("/")[0]
        return {'source': 'envato', 'id': envato_id, 'url': url}

    elif "dreamstime.com" in url:
        if "-image" in url:
            # Extract ID for Dreamstime
            dream_id = url.split("-image")[-1].split(".html")[0]
            return {'source': 'dreamstime', 'id': dream_id, 'url': url}

    elif "pngtree.com" in url:
        if "_" in url:
            # Extract ID for Pngtree
            pngtree_id = url.split("_")[-1].split(".html")[0]
            return {'source': 'pngtree', 'id': pngtree_id, 'url': url}

    elif "vectorstock.com" in url:
        if "/vector/" in url:
            # Extract ID for VectorStock
            vector_id = url.split("-")[-1]
            return {'source': 'vectorstock', 'id': vector_id, 'url': url}

    elif "motionarray.com" in url:
        # Extract ID for MotionArray
        motionarray_id = url.split("-")[-1]
        return {'source': 'motionarray', 'id': motionarray_id, 'url': url}

    elif "alamy.com" in url:
        if "-image" in url:
            # Extract ID for Alamy
            alamy_id = url.split("-image")[-1].split(".html")[0]
            return {'source': 'alamy', 'id': alamy_id, 'url': url}

    elif "motionelements.com" in url:
        if "-video" in url:
            # Extract ID for MotionElements
            motion_id = url.split("-")[-2]
            return {'source': 'motionelements', 'id': motion_id, 'url': url}

    elif "storyblocks.com" in url:
        if "stock/" in url:
            # Extract ID for Storyblocks
            story_id = url.split("stock/")[-1].split("-")[0]
            return {'source': 'storyblocks', 'id': story_id, 'url': url}

    elif "epidemicsound.com" in url:
        if "/track/" in url:
            # Extract ID for Epidemic Sound
            epidemic_id = url.split("/track/")[-1]
            return {'source': 'epidemicsound', 'id': epidemic_id, 'url': url}

    elif "yellowimages.com" in url:
        if "/stock/" in url:
            # Extract ID for Yellow Images
            yellow_id = url.split("/stock/")[-1]
            return {'source': 'yellowimages', 'id': yellow_id, 'url': url}

    elif "vecteezy.com" in url:
        if "/photo/" in url or "/vector-art/" in url or "/video/" in url:
            # Extract ID for Vecteezy
            vecteezy_id = url.split("/")[-1]
            return {'source': 'vecteezy', 'id': vecteezy_id, 'url': url}

    elif "creativefabrica.com" in url:
        if "/product/" in url:
            # Extract ID for Creative Fabrica
            cf_id = url.split("/product/")[-1].split("/")[0]
            return {'source': 'creativefabrica', 'id': cf_id, 'url': url}

    elif "lovepik.com" in url:
        if "-" in url:
            # Extract ID for Lovepik
            lovepik_id = url.split("-")[-1].split("/")[0]
            return {'source': 'lovepik', 'id': lovepik_id, 'url': url}

    elif "rawpixel.com" in url:
        if "/image/" in url:
            # Extract ID for RawPixel
            rawpixel_id = url.split("/image/")[-1]
            return {'source': 'rawpixel', 'id': rawpixel_id, 'url': url}

    elif "deeezy.com" in url:
        if "/product/" in url:
            # Extract ID for Deeezy
            deeezy_id = url.split("/product/")[-1]
            return {'source': 'deeezy', 'id': deeezy_id, 'url': url}

    elif "productioncrate.com" in url or "footagecrate.com" in url:
        # Extract ID for ProductionCrate or FootageCrate
        crate_id = url.split("/")[-1]
        return {'source': 'footagecrate', 'id': crate_id, 'url': url}

    elif "artgrid.io" in url:
        if "/clip/" in url:
            # Extract ID for Artgrid
            artgrid_id = url.split("/clip/")[-1]
            return {'source': 'artgrid_HD', 'id': artgrid_id, 'url': url}

    return False

def process_thum_url(url, platform):
    if platform == "envato.com":
        enid = get_envato_id(url)
        thumby = "https://i2.pngimg.me/stock/envato/"+enid+".jpg"
        return thumby
    elif platform == "shutterstock.com":
        shuid = geturlbyidshutterstock(url)
        thumby = "https://image.shutterstock.com/image-vector/-250nw-"+shuid+".jpg"
        return thumby
    else:
        return url

def search_pcloud_for_files(filenamen):
    API_ACCESS_TOKENs = ["otGUZzTBLD10Yy1fZcBRFykZzEjpJwaEHNpSDN6cIiOjCuF7cgvV"]
    for tkn in API_ACCESS_TOKENs:
        urlgetfileid = 'https://api.pcloud.com/search'

        # Define headers for the request
        headers = {
            "Authorization": "Bearer {}".format(tkn)
        }

        # Define parameters for the request
        params = {
            "query": filenamen
        }

        # Make the API request
        response = requests.get(urlgetfileid, headers=headers, params=params)

        if response.status_code == 200:
            rksns = response.json()
            val = rksns.get('total', 0)

            if val > 0:
                # Iterate through the items to find an exact match
                for item in rksns['items']:
                    spli = item['name'].split(".")
                    if spli[0].lower() == filenamen:  # Check for exact match
                        fileidfinal = item['fileid']

                        share_link_url = "https://api.pcloud.com/getfilepublink"
                        share_data = {
                            "access_token": tkn,
                            "fileid": fileidfinal
                        }

                        share_response = requests.get(share_link_url, params=share_data, verify=False)
                        if share_response.status_code == 200:
                            share_result = share_response.json()
                            share_link = share_result.get('link', None)
                            return "exist"
        else:
            print(f"Failed to search for files. Status code: {response.status_code}")

    # Return None if no exact match is found
    return "not exist"

def check_record_exists(user_id, actual_slug):
    client = MongoClient(
        'mongodb+srv://mysteriouscoder:mysteriouscoder@cluster0.agkearu.mongodb.net/?retryWrites=true&w=majority')  # Update with your MongoDB URI
    db = client['test']
    history_collection = db['history']

    exist = history_collection.find_one({'userid': user_id, 'actual_slug': actual_slug})
    if exist:
        return True
    else:
        return False

def check_record_exists_withrefunded(user_id, actual_slug):
    client = MongoClient(
        'mongodb+srv://mysteriouscoder:mysteriouscoder@cluster0.agkearu.mongodb.net/?retryWrites=true&w=majority')  # Update with your MongoDB URI
    db = client['test']
    history_collection = db['history']

    exist = history_collection.find_one({'userid': user_id, 'actual_slug': actual_slug + "_refunded"})
    if exist:
        return True
    else:
        return False

def check_record_exists2(user_id, actual_slug):
    from pymongo import MongoClient

    client = MongoClient(
        'mongodb+srv://mysteriouscoder:mysteriouscoder@cluster0.agkearu.mongodb.net/?retryWrites=true&w=majority')  # Update with your MongoDB URI
    db = client['test']
    history_collection = db['history']

    # Query to check if the record exists with a download_link
    exist = history_collection.find_one(
        {'userid': user_id, 'actual_slug': actual_slug, 'download_link': {'$exists': True}})

    if exist:
        return True
    else:
        return False

def clean_url(url):
    # Parse the URL
    parsed_url = urlparse(url)

    # Remove query parameters that are not needed
    query_params = parse_qs(parsed_url.query)
    allowed_query_params = {}
    new_query = '&'.join(f"{key}={value[0]}" for key, value in query_params.items() if key in allowed_query_params)

    # Reconstruct the URL without unwanted query parameters
    cleaned_url = urlunparse(parsed_url._replace(query=new_query))

    return cleaned_url

def get_abobe_info_by_media_get_extension(url, ext):
    try:
        searchid = extract_source_data(url)['id']
        urllincense = "https://stock.adobe.com/Ajax/MediaData/" + searchid + "?full=1"
        request = urllib.request.Request(url=urllincense, method='GET')
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        with urllib.request.urlopen(request, context=ssl_context) as response:
            data = response.read()
            response_str = data.decode('utf-8')
            print(response_str)
            newext = json.loads(response_str)
            extension = newext['file_extension']
            if "ai" in extension:
                return "eps"
            elif "jpeg" in extension:
                return "jpg"
            else:
                return extension
    except:
        return ext

def get_shutterstock_predictor_extension(url):
    try:
        imageid = extract_source_data(url)['ext']
        return imageid
    except:
        return "N/A"


























