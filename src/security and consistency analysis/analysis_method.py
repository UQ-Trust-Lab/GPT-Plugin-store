import random
import re
import string
import time
import json

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
import yaml
from urllib.parse import urljoin, urlparse

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
}
class Json:
    def __init__(self,execl_path):
        self.execl_path = execl_path
        self.df = pd.read_excel(self.execl_path)
    def inital_excel(self):
        self.df['json_info'] = [None] * len(self.df)
        self.df['urlnum'] = [None] * len(self.df)
        self.df['json_url'] = [None] * len(self.df)
        self.df['url_state'] = [None] * len(self.df)
        self.df['url_parsed'] = [None] * len(self.df)
        self.df['api_url'] = [None] * len(self.df)
        self.df['apiurl_state'] = [None] * len(self.df)
        self.df['api_info'] = [None] * len(self.df)
        self.df['api_info_state'] = [None] * len(self.df)
        self.df['request_result'] = [None] * len(self.df)
        self.df['auth'] = [None] * len(self.df)
        for idx in range(1,28):
            self.df[f'response_{idx}'] = [None] * len(self.df)
            self.df[f'request_{idx}'] = [None] * len(self.df)
        self.save_changes()
    def write_down(self):
        infos= self.df['info']

        for idx,info in enumerate(infos,start=0,):
            url1=self.clean_urls(info)
            url2=self.clean_urls_2(info)
            url3=self.clean_url_3(info)
            url4=self.clear_urls_4(info)
            url5=self.clear_urls_5(info)
            self.write_to_excel(idx,"url1",url1)
            self.write_to_excel(idx, "url2", url2)
            self.write_to_excel(idx, "url3", url3)
            self.write_to_excel(idx, "url4", url4)
            self.write_to_excel(idx, "url5", url5)

    def clean_urls(self,url):
        stop_words_pattern = re.compile(r'/(terms|home|legal|policy|privacy|about)[/\w-]*', re.IGNORECASE)
        cleaned_urls = stop_words_pattern.sub('', url)
        cleaned_urls = re.sub(r'\.(html|htm|php)$', '', cleaned_urls)
        cleaned_urls = re.sub(r'\.html$', '', cleaned_urls)
        cleaned_urls = re.sub(r'/(static|tos|term).*$', '', cleaned_urls)
        cleaned_urls = re.sub(r'\/?$', '', cleaned_urls)
        cleaned_urls = re.sub(r'/.*term.*$', '', cleaned_urls)
        return cleaned_urls

    def clean_urls_2(self,url):
        stop_words_pattern = re.compile(r'/(terms|home|legal|policy|privacy|about)[/\w-]*', re.IGNORECASE)
        cleaned_urls = stop_words_pattern.sub('', url)
        cleaned_urls = re.sub(r'\/?$', '', cleaned_urls)
        cleaned_urls = re.sub(r'\.html$', '', cleaned_urls)
        cleaned_urls = re.sub(r'/(static|tos|term).*$', '', cleaned_urls)
        return cleaned_urls

    def clean_url_3(self,url):
        cleaned_urls = re.sub(r'\.(htm|php|txt|pdf)$', '', url)
        cleaned_urls = re.sub(r'/(policies|.well-known|us|en|pages|page|#legal|.well-knonw|terms|api|%|live).*$',
                              '', cleaned_urls)
        cleaned_urls = re.sub(r'/.*(term|static|=sharing|=en|terms).*$', '', cleaned_urls)
        return cleaned_urls

    def clear_urls_4(self,url):
        match = re.match(r'(https?)://([^/]+)/?', url)
        if match:
            protocol, domain = match.groups()
            extracted_url = f"{protocol}://{domain}"
            return extracted_url
        else:
            return ' '

    def clear_urls_5(self,url):
        match = re.match(r'(https?)://([^/]+)/([^/]+)', url)
        if match:
            protocol, domain, path1 = match.groups()
            extracted_url = f"{protocol}://{domain}/{path1}"
            extracted_url = re.sub(r'\.(html|htm|pdf|php|txt)$', '', extracted_url)
            return extracted_url
        else:
            return ''
    def parse_json(self,new_url):
        api_1 = f"{new_url}/{'.well-known/ai-plugin.json'}"
        api_2 = f"{new_url}/{'api/ai.chatgpt.get-plugin-config'}"
        api_3 = f"{new_url}/{'.well-known'}"
        result=[]
        try:
            response_1 = requests.get(api_1,timeout = 10)
            if response_1.status_code == 200:
                soup = BeautifulSoup(response_1.text, 'html.parser')
                result = (('success',api_1,soup),)
                return result
            else:
                result.append(('state',  response_1.status_code))
        except requests.exceptions.Timeout as e2:
            result.append(('timeout', api_1))
        except requests.exceptions.RequestException as e:
            result.append((False,e))
        try:
            response_2 = requests.get(api_2,timeout = 10)
            if response_2.status_code == 200:
                json_txt = response_2.text
                soup = BeautifulSoup(json_txt, 'html.parser')
                result = (('success',api_2, soup),)
                return result
            else:
                result.append(
                    ('state', response_2.status_code))
        except requests.exceptions.Timeout as e2:
            result.append(('timeout', api_2))
        except requests.exceptions.RequestException as e:
            result.append((False, e))

        try:
            response_3 = requests.get(api_3,timeout = 10)

            if response_3.status_code == 200:

                json_txt = response_3.text
                soup = BeautifulSoup(json_txt, 'html.parser')
                result = (('success',api_3, soup),)
                return result
            else:
               result.append(('state', response_3.status_code))
        except requests.exceptions.Timeout as e2:
            result.append(('timeout', api_3))
        except requests.exceptions.RequestException as e:
            result.append((False, e))
        return result

    def write_to_excel(self, row_index: int, column: str, txt):
        if column not in self.df.columns:
            self.df[column] = [np.nan] * len(self.df)
        if txt is not None:
            self.df.at[row_index, column] = str(txt)
        else:
            self.df.at[row_index, column] = np.nan
    def get_api(self, num):
        url_parsed =self.df['url_parsed']
        url_state =self.df['url_state']
        urls =self.df['json_url'].tolist()
        count = num
        for url in urls[num:]:
            if url_state[count] == 'Y':
                try:
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        try:
                            data = json.loads(response.text)
                            api_url = data.get("api")
                            if api_url is None:
                                self.write_to_excel(count, 'api_url', 'W3')
                                count +=1
                                continue
                            api_url = api_url.get("url")
                            if urlparse(api_url).scheme == "":
                                api_url = urljoin(url_parsed[count], api_url)
                            self.write_to_excel(count,'apiurl_state','Y')
                            self.write_to_excel(count, 'api_url',api_url )

                        except json.decoder.JSONDecodeError as e:
                            self.write_to_excel(count, 'apiurl_state','W3')
                    else:
                        self.write_to_excel(count, 'apiurl_state', response.status_code)
                except requests.exceptions.Timeout as e1:
                    self.write_to_excel(count, 'apiurl_state', 'timeout')
                except requests.exceptions.RequestException as e2:
                    self.write_to_excel(count, 'apiurl_state', e2)
            count += 1
        self.save_changes()

    def get_api_info(self,num):
        urls=self.df['api_url']
        apiurl_state=self.df['apiurl_state']
        for count,api in enumerate(urls[num:],start=num):
            if apiurl_state[count] != 'Y':
                continue

            try:
                response = requests.get(api,timeout=10)
                time.sleep(random.randint(1,3))
                if response.status_code==200:
                    content_type = response.headers.get('Content-Type')

                    if response.text.strip() == '':
                        self.write_to_excel(count,'api_info_state', "W3")
                        continue
                    if api.endswith('.yaml') or api.endswith('.yml'):
                        response_text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', response.text)
                        try:
                            api_info = yaml.safe_load(response_text)
                        except Exception as e1:
                            self.write_to_excel(count,'api_info_state',"W3")
                            continue
                    elif 'application/json' in content_type:
                        try:
                            api_info = response.json()
                        except Exception as e1:
                            self.write_to_excel(count,'api_info_state',"W3")
                            continue
                    elif 'application/x-yaml' in content_type or 'text/yaml' in content_type:
                        try:
                            api_info = yaml.safe_load(response.text)
                        except Exception as e1:
                            self.write_to_excel(count, 'api_info_state', "W3")
                            continue
                    else:
                        api_info = response.json()
                    if api_info is None:
                        continue

                    if str(api_info).strip().startswith('<') or "'code': 'file_not_found' " in str(api_info) or "'error': 'No account found.'" in str(api_info):
                        self.write_to_excel(count, 'api_info_state', "W4")
                        continue
                    self.write_to_excel(count,'api_info',str(api_info))
                    self.write_to_excel(count, 'api_info_state', 'Y')
                else:
                    self.write_to_excel(count, 'api_info_state', response.status_code)
            except requests.exceptions.Timeout as e:
                self.write_to_excel(count,'api_info_state', 'overtime')
            except requests.exceptions.RequestException as e2:
                self.write_to_excel(count,'api_info_state', e2)
            count += 1
        self.save_changes()

    def save_changes(self):
        with pd.ExcelWriter(self.execl_path, engine='openpyxl', mode='a',if_sheet_exists='replace') as writer:
            self.df.to_excel(writer, index=False)
        print("Changes have been saved to the file.")

    def handle_list_2(self,num,urlnum):
        url_state=self.df['url_state']
        #detect different url
        urls = self.df[urlnum].tolist()
        for count,url in enumerate(urls[num:],start=num):
            time.sleep(1)
            if url_state[count] == "Y":
                continue
            new_url = url
            result = self.parse_json(new_url)
            if result[0][0] is False or result[0][0] == 'state' or result[0][0] == 'timeout':
                api_state = result
                self.write_to_excel(count,'state',str(api_state))
                self.write_to_excel(count, 'url_state', "W1")
            else:
                json_url = result[0][1]
                json_info = result[0][2]
                self.write_to_excel(count, 'json_info',str(json_info))
                self.write_to_excel(count, 'json_url', json_url)
                info_string=str(json_info)
                info_string=info_string.lstrip()
                if info_string.startswith('<'):
                    self.write_to_excel(count,'url_state',"W2")
                    continue
                print('json_info', count,url)
                self.write_to_excel(count, 'url_state', "Y")
                self.write_to_excel(count, 'state', '')
                self.write_to_excel(count, 'url_parsed', url)


    def clear_path(self,num):

        api_url = self.df['api_url']
        count = num
        api_info_state=self.df['api_info_state']
        for api in api_url[num:]:
            if api_info_state[count] != 'Y':
                count += 1
                continue
            try:
                response = requests.get(api,timeout=10)
                time.sleep(random.randint(1,3))
                if response.status_code==200:
                    content_type = response.headers.get('Content-Type')

                    if api.endswith('.yaml') or api.endswith('.yml'):
                        response_text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', response.text)
                        api_info = yaml.safe_load(response_text)
                    elif 'application/json' in content_type:
                        api_info = response.json()
                    elif 'application/x-yaml' in content_type or 'text/yaml' in content_type:
                        api_info = yaml.safe_load(response.text)
                    else:
                        api_info = response.json()
                    if api_info is None:
                        count += 1
                        continue
                    self.handle_get(api_info, count)
                else:
                    self.write_to_excel(count, 'request_status', response.status_code)  
            except requests.exceptions.Timeout as e:
                self.write_to_excel(count,'request_status',"W1")
            except requests.exceptions.RequestException as e2:
                self.write_to_excel(count, 'request_status', "W2")
            count += 1
        self.save_changes()

    def handle_get(self,body,count):
        urls = {"GET": [], "POST": []}
        try:
            base_url = body['servers'][0]['url']
        except (KeyError, IndexError):
            base_url =self.df['url_parsed'][count]
        api_endpoints = []
        idx = 1
        if body.get('paths') is None:
            return

        for path, path_item in body['paths'].items():
            for http_method in ['get', 'post']:
                if http_method in path_item:
                    full_url = f"{base_url}{path}"
                    params = None
                    data = None

                    if http_method == 'get':
                        params = path_item[http_method].get('parameters', {})
                        if params is not None:
                            params = self.construct_params(params)

                    elif http_method == 'post':
                        request_body = path_item[http_method].get('requestBody', {})
                        if 'content' in request_body and 'application/json' in request_body['content']:
                            data = request_body['content']['application/json'].get('schema', {})
                    elif http_method in ['patch', 'put']:
                        request_body = path_item[http_method].get('requestBody', {})
                        if 'content' in request_body and 'application/json' in request_body['content']:
                            data = request_body['content']['application/json'].get('schema', {})
                    elif http_method == 'delete':
                        pass

                    request_1={
                        'method': http_method.upper(),
                        'path': path,
                        'full_url': full_url,
                        'params': params,
                        'data': data
                    }
                    api_endpoints.append(request_1)
                    response = self.send_api_request(http_method.upper(), full_url, params, data)
                    response_text=response.text

                    if response.headers.get('Content-Type') == 'image/png':
                        response_text='picture!'
                    self.write_to_excel(count,f'request_{idx}', json.dumps(request_1))
                    self.write_to_excel(count,f'response_{idx}',f'{response.status_code}{response_text}')
                    idx += 1

    def send_api_request(self,method, url, params=None, data=None):
        headers = {
            'Content-Type': 'application/json',
        }
        # send request
        if method == 'GET':
            response = requests.get(url, params=params, headers=headers,verify=False,timeout=10)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers,verify=False,timeout=10)
        elif method == 'PUT':
            response = requests.put(url, json=data, headers=headers,verify=False,timeout=10)
        elif method == 'PATCH':
            response = requests.patch(url, json=data, headers=headers,verify=False,timeout=10)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers,verify=False,timeout=10)
        else:
            raise ValueError("only  'GET'、'POST'、'PUT'、'PATCH' or 'DELETE'。acceptable")
        return response

    def construct_params(self,param_definition):
        params = {}
        for param in param_definition:
            param_name = param['name']
            param_required = param.get('required',False)
            if param_required:
                param_value = 'default_value'
                params[param_name] = param_value
        return params

    def request_result(self,num):
        count = num
        api_info_state=self.df['api_info_state']
        for state in api_info_state[count:]:
            if state != 'Y':
                count += 1
                continue
            success = False

            for idx in range(1,27):
                response =self.df[f'response_{idx}'][count]
                if str(response).strip().lower() == 'nan':
                    continue
                try:
                    res_code = response[:3]
                    res_content = response[3:]
                    res_2 = res_content.strip()
                    if res_code == '200':
                        try:
                            json_dict = json.loads(res_content)
                            if (res_2 == "3" or res_2 == "[]" or res_2 == "{}"
                                    or res_2 == ''
                                    or res_2 == "null"
                                    or "Sorry, plugin does not work" in res_2):
                                continue
                            if isinstance(json_dict, dict) and 'error' in json_dict:
                                continue
                            if json_dict.get('code') == "jwt_token_invalid":
                                continue
                            success = True
                        except ValueError:
                            success = True
                            pass
                        except Exception as e:
                            success = True
                            pass
                except Exception as e:
                    success = True
                    pass
                if success is True:
                    self.write_to_excel(count,'request_result','success')
                    break
            if success is False:
                self.write_to_excel(count, 'request_result', 'unsuccess')
            count += 1
        self.save_changes()

    def normalize_url(self,url):
        url = re.sub(r'^https?://', '', url, flags=re.IGNORECASE)
        url = re.sub(r'\.html?$', '', url, flags=re.IGNORECASE)
        url = url.rstrip('/')
        return url

    def check_auth(self,num):
        json_info=self.df['json_info']
        api_info_state=self.df['api_info_state']
        count=num
        for api in json_info[num:]:
            if api_info_state[count]!='Y':
                count += 1
                continue
            try:
                json_dict = json.loads(api)
                if 'auth' in json_dict:
                    auth_info = json_dict['auth']
                else:
                    auth_info = "not exist"  
                self.write_to_excel(count,'auth',str(auth_info))
            except json.decoder.JSONDecodeError:
                self.write_to_excel(count, 'auth', 'cannot parse')
            count += 1
        self.save_changes()

    def detect_token(self,num):
        dls=self.df['auth']
        count =num
        url_parsed=self.df['url_parsed']
        api_info_state=self.df['api_info_state']
        request_result=self.df['request_result']
        for dl in dls[count:]:
            if api_info_state[count] != 'Y':
                count += 1
                continue
            if request_result[count] != 'success':
                count += 1
                continue
            dl = str(dl).replace("'", '"')
            load_url = json.loads(dl)
            if load_url.get('type') == "none":
                count += 1
                continue
            for idx in range(1, 27):
                requests_data=self.df[f'request_{idx}'][count]
                if str(requests_data).strip().lower() =='nan':
                    continue
                requests_data=json.loads(requests_data)
                if requests_data.get("full_url") is not None:
                    if 'http' not in requests_data.get('full_url'):
                        requests_data['full_url']=f'{url_parsed[count]}{ requests_data['full_url']}'
                response=self.send_api_request_token(requests_data.get("method"),requests_data.get("full_url")
                                                      ,load_url['verification_tokens']['openai'],requests_data.get("params"),
                                                     requests_data.get("data"))
                self.write_to_excel(count,f'response_{idx}', f'{response.status_code}{response.text}')
            count += 1
        self.save_changes()

    def send_api_request_token(self, method, url, token, params=None, data=None):
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        }
        if method == 'GET':
            response = requests.get(url, params=params, headers=headers)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers)
        elif method == 'PUT':
            response = requests.put(url, json=data, headers=headers)
        elif method == 'PATCH':
            response = requests.patch(url, json=data, headers=headers)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError("Method must be 'GET', 'POST', 'PUT', 'PATCH', or 'DELETE'.")
        return response

    def check_legal(self,num):
        json_info =self.df['json_info']
        url_state =self.df['url_state']
        infos =self.df['info']
        count = num
        for api in json_info[count:]:
            if url_state[count] != 'Y':
                count += 1
                continue
            try:
                api_dict = json.loads(api)
                if type(api_dict)!=dict or api_dict.get('legal_info_url') is None:
                    self.write_to_excel(count,'legal_state','No legal information')
                    count+=1
                    continue
                legal_url = api_dict.get('legal_info_url')
                legal_url = self.normalize_url(legal_url)
                legal_info = self.normalize_url(infos[count])
                self.write_to_excel(count, 'legal',legal_url)
                self.write_to_excel(count, 'legal_state',legal_url==legal_info)
            except json.decoder.JSONDecodeError:
                self.write_to_excel(count, 'legal_state', "W")
            except Exception as e:
                self.write_to_excel(count, 'name_issue', 'Other Exception: ' + str(e))

            count += 1
        self.save_changes()
    def check_name(self,num):
        json_info=self.df['json_info']
        titles=self.df['title']
        count=num
        url_state=self.df['url_state']
        for api in json_info[count:]:
            try:
                if url_state[count]!='Y':
                    count += 1
                    continue

                api_dict = json.loads(api)
                name = api_dict.get('name_for_human')
                name=self.normalize_url(name)
                title=self.normalize_url(titles[count])

                self.write_to_excel(count, 'name_for_human',name)
                self.write_to_excel(count,'name_issue',name == title)
            except json.decoder.JSONDecodeError:
                self.write_to_excel(count,'name_issue','_cannot parse')
            except Exception as e:
                self.write_to_excel(count, 'name_issue', 'Other Exception: ' + str(e))
            count += 1

        self.save_changes()
