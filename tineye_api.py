import json
import aiohttp  # (Note: aiohttp is no longer used in the synchronous version)
import pydash
import requests
import boto3
from botocore.exceptions import NoCredentialsError
import mimetypes
import utils
import re
from pymongo import MongoClient
from urllib.parse import urlparse
import cloudscraper

class paneltin:
    def __init__(self):
        self.urlqueryhash = "https://tineye.com/api/v1/result_json/"
        self.queryhash = None
        self.urlgetdomains = "https://tineye.com/api/v1/search/get_domains/"
        self.hash = None
        self.allresp = None
        self.ACCESS_KEY_ID = 'AKIA2O46OGO4UZRDUIPY'
        self.SECRET_ACCESS_KEY = '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'
        self.s3 = boto3.client('s3', aws_access_key_id=self.ACCESS_KEY_ID, aws_secret_access_key=self.SECRET_ACCESS_KEY)
        self.proxies = {
            "http": "http://spmhmfozio:ze1sg+sP3n4apXhDV9@isp.decodo.com:10001",
            "https": "http://spmhmfozio:ze1sg+sP3n4apXhDV9@isp.decodo.com:10001",
            #"http": "http://spp8nbtqo1:0bo9dZ7Gv1pDO=pnae@gate.decodo.com:10001",
            #"https": "http://spp8nbtqo1:0bo9dZ7Gv1pDO=pnae@gate.decodo.com:10001",


        }
        self.result_list = []

    def get_query_hash(self, dupimage, source, actual_id, ext_main):
        boundary = "----WebKitFormBoundarymtiGPeOfCaEkU8GC"
        headers = {
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Origin": "https://tineye.com",
            "Pragma": "no-cache",
            "Priority": "u=1, i",
            "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36",
        }

        body = (
            f'--{boundary}\r\n'
            'Content-Disposition: form-data; name="url"\r\n\r\n'
            f'{dupimage}\r\n'
            f'--{boundary}--\r\n'
        )

        try:
            # Create a cloudscraper instance with an Android Chrome signature.
            scraper = cloudscraper.create_scraper(
                browser={'browser': 'chrome', 'platform': 'android', 'mobile': True}
            )

            # First attempt: standard POST
            response = scraper.post(self.urlqueryhash, headers=headers, data=body)
            response_text = response.text
            print("firstipchecktineye")
            print(response_text)
            response_status = response.status_code
            print(response_status)

            if str(response_status) == "400":
                return self.result_list

            elif str(response_status) == "429":
                # Retry with proxy settings if rate limited.
                proxy = {"http": self.proxies["http"], "https": self.proxies["https"]}
                response = scraper.post(self.urlqueryhash, headers=headers, data=body, proxies=proxy)
                response_text = response.text
                print("secondipchecktineye")
                print(response_text)
                response_status = response.status_code
                print(response_status)

                resp = json.loads(response_text)
                print(resp)
                totalmatches = resp.get("num_matches", 0)
                if totalmatches > 0:
                    self.queryhash = resp["query"]["key"]
                    self.hash = resp["query"]["hash"]
                    self.allresp = resp
                    available_domains = self.get_domains_by_hash()
                    get_backlinks_data = self.get_image_path_with_slug(available_domains, source, actual_id, ext_main)
                    return get_backlinks_data
                else:
                    my_json_string = {"status": 200, "message": "No Tineye Image Found"}
                    return self.result_list

            else:
                resp = json.loads(response_text)
                print(resp)
                totalmatches = resp.get("num_matches", 0)
                if totalmatches > 0:
                    self.queryhash = resp["query"]["key"]
                    self.hash = resp["query"]["hash"]
                    self.allresp = resp
                    available_domains = self.get_domains_by_hash()
                    get_backlinks_data = self.get_image_path_with_slug(available_domains, source, actual_id, ext_main)
                    return get_backlinks_data
                else:
                    my_json_string = {"status": 200, "message": "No Tineye Image Found"}
                    return self.result_list

        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def get_domains_by_hash(self):
        url = self.urlgetdomains + self.hash
        headers = {
            "Content-Type": "application/json",
        }
        try:
            response = requests.get(url, headers=headers)
            response_status = response.status_code
            print(response_status)
            if response_status == 200:
                resp = response.json()
                print(resp)
                alldomains = resp['domains']
                result = pydash.map_(alldomains, lambda x: x[0])
                print(result)
                return result
            else:
                print(f"Request failed with status: {response_status}")
                return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def get_image_path_with_slug(self, slugs: list, real_file_slug, actual_id, ext_main):
        for xy in range(len(slugs)):
            slug = slugs[xy]
            matchlen = len(self.allresp['matches'])
            for ny in range(matchlen):
                slugcheck = self.allresp['matches'][ny]['domain']

                if str(slug) == str(slugcheck):
                    percentage = self.allresp['matches'][ny]['score']
                    key = self.allresp['matches'][ny]['key']
                    platformurl = self.allresp['matches'][ny]['domains'][0]['backlinks'][0]['backlink']
                    thumburl = self.allresp['matches'][ny]['domains'][0]['backlinks'][0]['url']
                    if thumburl != '':
                        print(thumburl)
                        res = utils.getfiles_slug_tineye(slug)
                        if res != "less":
                            public_url = self.upload_file_to_server(thumburl, key)
                        else:
                            public_url = ''
                    else:
                        public_url = ''

                    if utils.getfiles_slug_tineye(slug) == "adobestock":
                        ext = utils.get_abobe_info_by_media_get_extension(platformurl, ext_main)
                    else:
                        ext = "N/A"

                    new_entry = {
                        'slug': utils.getfiles_slug_tineye(slug),
                        'price': utils.getfilesprices_tineye(slug, real_file_slug),
                        'percentage': 'other similar',
                        'platformurl': platformurl,
                        'thumburl': public_url,
                        'actual_slug': real_file_slug + "_" + actual_id,
                        'ext': ext
                    }

                    # Generate the check_exist_original_file value
                    check_exist_original_file = "tineye_" + utils.getfiles_slug_tineye(slug)

                    # Check if slug already exists in result_list
                    existing_index = next(
                        (index for (index, d) in enumerate(self.result_list) if d['slug'] == new_entry['slug']), None)

                    # Check if check_exist_original_file exists in result_list
                    existing_index_check_exist_original_file = next(
                        (index for (index, d) in enumerate(self.result_list) if d['slug'] == check_exist_original_file),
                        None)

                    if slugcheck == "envato.com":
                        exist = utils.check_envato_id_exist(platformurl)
                        if exist:
                            if existing_index is not None:
                                if existing_index_check_exist_original_file is not None:
                                    print("Already exist")
                                else:
                                    if new_entry['percentage'] > self.result_list[existing_index]['percentage']:
                                        self.result_list[existing_index] = new_entry
                            else:
                                if existing_index_check_exist_original_file is not None:
                                    print("Already exist")
                                else:
                                    self.result_list.append(new_entry)
                    else:
                        if existing_index is not None:
                            if existing_index_check_exist_original_file is not None:
                                print("Already exist")
                            else:
                                if new_entry['percentage'] > self.result_list[existing_index]['percentage']:
                                    self.result_list[existing_index] = new_entry
                        else:
                            if existing_index_check_exist_original_file is not None:
                                print("Already exist")
                            else:
                                self.result_list.append(new_entry)
        fresult = utils.allowed_platforms(self.result_list, real_file_slug)
        return fresult

    def upload_file_to_s3(self, remote_url, bucket, file_name):
        try:
            imageResponse = requests.get(remote_url, stream=True).raw
            print(imageResponse)
            content_type = imageResponse.headers['content-type']
            metadata = {
                'Content-Type': content_type
            }
            # Upload the file with metadata
            self.s3.upload_fileobj(imageResponse, bucket, file_name + ".jpg", ExtraArgs={
                'Metadata': metadata,
                'ContentType': content_type,
            })
            print("Upload Successful")
            return file_name + ".jpg"
        except Exception as e:
            print(e)

    def upload_file_to_server(self, remote_url, file_name, download_timeout=5, upload_timeout=5):
        try:
            response = requests.get(remote_url, stream=True, timeout=download_timeout)
            if response.status_code == 200:
                upload_url = 'https://bot.webinpocket.com/api/upload'
                files = {'file': (file_name + '.jpg', response.raw, 'image/jpeg')}
                upload_response = requests.post(upload_url, files=files, timeout=upload_timeout)
                if upload_response.status_code == 200:
                    print("File uploaded successfully!")
                    rsk_resp = upload_response.json()
                    return rsk_resp['public_url']
                else:
                    print(f"Failed to upload the file. Status code: {upload_response.status_code}")
                    return upload_response.text
            else:
                print(f"Failed to download image. Status code: {response.status_code}")
        except requests.exceptions.Timeout:
            print("The operation timed out. Please try again later.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def generate_public_url(self, bucket, key):
        url = f'https://{bucket}.s3.amazonaws.com/{key}'
        return url

    def process_original_data(self, slug, public_url, platformurl, source, actual_id, ext, userId):
        accid = source + "_" + actual_id
        checker = utils.check_record_exists(userId, accid)
        if checker:
            slugf = "tineye_" + slug
            self.result_list.append({
                'slug': slugf,
                'price': "0.00",
                'percentage': 100,
                'platformurl': platformurl,
                'thumburl': public_url,
                'actual_slug': source + "_" + actual_id,
                'ext': ext
            })
        else:
            slugf = "tineye_" + slug
            self.result_list.append({
                'slug': slugf,
                'price': utils.getfilesprices(slug, source),
                'percentage': 100,
                'platformurl': platformurl,
                'thumburl': public_url,
                'actual_slug': source + "_" + actual_id,
                'ext': ext
            })
        return self.result_list

    def process_original_data_pcloud(self, slug, public_url, platformurl, source, actual_id, ext, userId):
        accid = source + "_" + actual_id
        checker = utils.check_record_exists(userId, accid)
        if checker:
            slugf = "pcloud_" + slug
            self.result_list.append({
                'slug': slugf,
                'price': "0.00",
                'percentage': 100,
                'platformurl': platformurl,
                'thumburl': public_url,
                'actual_slug': source + "_" + actual_id,
                'ext': ext
            })
        else:
            slugf = "pcloud_" + slug
            self.result_list.append({
                'slug': slugf,
                'price': utils.getfilesprices(slug, source),
                'percentage': 100,
                'platformurl': platformurl,
                'thumburl': public_url,
                'actual_slug': source + "_" + actual_id,
                'ext': ext
            })
        return self.result_list

    def process_original_data_only_original(self, slug, public_url, platformurl, source, actual_id, ext, userId):
        accid = source + "_" + actual_id  # Note - Here we only check if record exists but we also need to check file exist on pcloud or not
        file = utils.search_pcloud_for_files(accid)
        print("file exist in pcloud", file)
        checker = utils.check_record_exists(userId, accid)
        print("file exist in db without downloadlink", checker)
        checker2 = utils.check_record_exists2(userId, accid)
        print("file exist in db with downloadlink", checker2)
        refundedchecker = utils.check_record_exists_withrefunded(userId, accid)
        print("file exist in db with refundchecker", refundedchecker)

        print(checker2)
        if checker:
            print("chla")
            if checker2:
                if slug == "envato":
                    slugf = slug
                    self.result_list.append({
                        'slug': slugf,
                        'price': "0.00",
                        'percentage': 100,
                        'platformurl': platformurl,
                        'thumburl': public_url,
                        'actual_slug': source + "_" + actual_id,
                        'ext': ext
                    })
                else:
                    slugf = "pcloud_" + slug
                    self.result_list.append({
                        'slug': slugf,
                        'price': "0.00",
                        'percentage': 100,
                        'platformurl': platformurl,
                        'thumburl': public_url,
                        'actual_slug': source + "_" + actual_id,
                        'ext': ext
                    })
            else:
                if refundedchecker:
                    if file == "exist":
                        slugf = "pcloud_" + slug
                        self.result_list.append({
                            'slug': slugf,
                            'price': utils.getfilesprices(slug, source),
                            'percentage': 100,
                            'platformurl': platformurl,
                            'thumburl': public_url,
                            'actual_slug': source + "_" + actual_id,
                            'ext': ext
                        })
                    else:
                        slugf = slug
                        self.result_list.append({
                            'slug': slugf,
                            'price': "0.00",
                            'percentage': 100,
                            'platformurl': platformurl,
                            'thumburl': public_url,
                            'actual_slug': source + "_" + actual_id,
                            'ext': ext
                        })
                elif slug == "envato":
                    slugf = "envato"
                    self.result_list.append({
                        'slug': slugf,
                        'price': "0.00",
                        'percentage': 100,
                        'platformurl': platformurl,
                        'thumburl': public_url,
                        'actual_slug': source + "_" + actual_id,
                        'ext': ext
                    })
                else:
                    slugf = "tineye_" + slug
                    self.result_list.append({
                        'slug': slugf,
                        'price': "0.00",
                        'percentage': 100,
                        'platformurl': platformurl,
                        'thumburl': public_url,
                        'actual_slug': source + "_" + actual_id,
                        'ext': ext
                    })
            return self.result_list
        else:
            print("chla2")
            print(slug)
            if refundedchecker:
                if file == "exist":
                    slu2 = "pcloud_" + slug
                else:
                    slu2 = slug
            elif slug == "adobestock":
                slu2 = slug
            elif slug == "freepik":
                slu2 = slug
            elif slug == "envato":
                slu2 = slug
            else:
                slu2 = "tineye_" + slug
            self.result_list.append({
                'slug': slu2,
                'price': utils.getfilesprices(slug, source),
                'percentage': 100,
                'platformurl': platformurl,
                'thumburl': public_url,
                'actual_slug': source + "_" + actual_id,
                'ext': ext
            })
            return self.result_list

    def get_query_hash_others_non_stock(self, dupimage, source, actual_id, ext_main):
        boundary = "----WebKitFormBoundarymtiGPeOfCaEkU8GC"

        headers = {
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Origin": "https://tineye.com",
            "Pragma": "no-cache",
            "Priority": "u=1, i",
            "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36",
        }

        body = (
            f'--{boundary}\r\n'
            'Content-Disposition: form-data; name="url"\r\n\r\n'
            f'{dupimage}\r\n'
            f'--{boundary}--\r\n'
        )

        try:
            response = requests.post(self.urlqueryhash, headers=headers, data=body)
            response_text = response.text
            response_status = response.status_code
            print(response_status)
            if str(response_status) == "400":
                return self.result_list
            elif str(response_status) == "429":
                response = requests.post(self.urlqueryhash, headers=headers, data=body, proxies={"http": self.proxies['http']})
                response_text = response.text
                response_status = response.status_code
                print(response_status)
                resp = json.loads(response_text)
                print(resp)
                totalmatches = resp['num_matches']
                if totalmatches > 0:
                    self.queryhash = resp['query']['key']
                    self.hash = resp['query']['hash']
                    self.allresp = resp
                    available_domains = self.get_domains_by_hash_others_non_stock()
                    get_backlinks_data = self.get_image_path_with_slug_others_non_stock(available_domains, source, actual_id, ext_main)
                    return get_backlinks_data
                else:
                    my_json_string = {"status": 200, "message": "No Tineye Image Found"}
                    return self.result_list
            else:
                resp = json.loads(response_text)
                print(resp)
                totalmatches = resp['num_matches']
                if totalmatches > 0:
                    self.queryhash = resp['query']['key']
                    self.hash = resp['query']['hash']
                    self.allresp = resp
                    available_domains = self.get_domains_by_hash_others_non_stock()
                    get_backlinks_data = self.get_image_path_with_slug_others_non_stock(available_domains, source, actual_id, ext_main)
                    return get_backlinks_data
                else:
                    my_json_string = {"status": 200, "message": "No Tineye Image Found"}
                    return self.result_list
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def get_domains_by_hash_others_non_stock(self):
        url = self.urlgetdomains + self.hash
        headers = {
            "Content-Type": "application/json",
        }
        try:
            response = requests.get(url, headers=headers)
            response_status = response.status_code
            print(response_status)
            if response_status == 200:
                resp = response.json()
                print(resp)
                alldomains = resp['domains']
                result = pydash.map_(alldomains, lambda x: x[0])
                print(result)
                return result
            else:
                print(f"Request failed with status: {response_status}")
                return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def get_image_path_with_slug_others_non_stock(self, slugs: list, real_file_slug, actual_id, ext_main):
        for xy in range(len(slugs)):
            slug = slugs[xy]
            matchlen = len(self.allresp['matches'])
            for ny in range(matchlen):
                slugcheck = self.allresp['matches'][ny]['domain']

                if str(slug) == str(slugcheck):
                    percentage = self.allresp['matches'][ny]['score']
                    key = self.allresp['matches'][ny]['key']
                    platformurl = self.allresp['matches'][ny]['domains'][0]['backlinks'][0]['backlink']
                    thumburl = self.allresp['matches'][ny]['domains'][0]['backlinks'][0]['url']
                    if thumburl != '':
                        print(thumburl)
                        res = utils.getfiles_slug_tineye(slug)
                        if res != "less":
                            public_url = self.upload_file_to_server(thumburl, key)
                        else:
                            public_url = ''
                    else:
                        public_url = ''

                    if utils.getfiles_slug_tineye(slug) == "adobestock":
                        ext = utils.get_abobe_info_by_media_get_extension(platformurl, ext_main)
                    else:
                        ext = "N/A"

                    try:
                        parsed_url = urlparse(thumburl)
                        domain = parsed_url.netloc
                    except:
                        domain = ""

                    new_entry = {
                        'slug': domain,
                        'price': utils.getfilesprices_tineye(slug, real_file_slug),
                        'percentage': 'other similar',
                        'platformurl': platformurl,
                        'thumburl': public_url,
                        'actual_slug': real_file_slug + "_" + actual_id,
                        'ext': ext
                    }

                    check_exist_original_file = "tineye_" + utils.getfiles_slug_tineye(slug)

                    existing_index = next(
                        (index for (index, d) in enumerate(self.result_list) if d['slug'] == new_entry['slug']), None)

                    existing_index_check_exist_original_file = next(
                        (index for (index, d) in enumerate(self.result_list) if d['slug'] == check_exist_original_file),
                        None)

                    if slugcheck == "envato.com":
                        exist = utils.check_envato_id_exist(platformurl)
                        if exist:
                            if existing_index is not None:
                                if existing_index_check_exist_original_file is not None:
                                    print("Already exist")
                                else:
                                    if new_entry['percentage'] > self.result_list[existing_index]['percentage']:
                                        self.result_list[existing_index] = new_entry
                            else:
                                if existing_index_check_exist_original_file is not None:
                                    print("Already exist")
                                else:
                                    self.result_list.append(new_entry)
                    else:
                        if existing_index is not None:
                            if existing_index_check_exist_original_file is not None:
                                print("Already exist")
                            else:
                                if new_entry['percentage'] > self.result_list[existing_index]['percentage']:
                                    self.result_list[existing_index] = new_entry
                        else:
                            if existing_index_check_exist_original_file is not None:
                                print("Already exist")
                            else:
                                self.result_list.append(new_entry)
        return self.result_list

    def get_domain_from_url(self, url):
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        return domain

__api__ = paneltin
__service__ = "Tineye"
__identifier__ = "tineye_apis"
