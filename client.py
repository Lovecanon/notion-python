# -*- coding:utf-8 -*-
import os
from urllib.parse import urljoin
import requests
from pprint import pprint
from errors import ApiKeyError, RequestError, ApiError, JsonDecodeError, ParameterError

NOTION_API_KEY = "******"
NOTION_VERSION = "2021-05-13"
DEFAULT_BASE_URL = "https://api.notion.com/v1/"


class Clint(object):
    def __init__(self, api_key=None, request_kwargs=None, base_url=DEFAULT_BASE_URL):
        if api_key is None:
            api_key = os.environ.get("NOTION_API_KEY")
            if api_key is None:
                raise ApiKeyError()
        self.api_key = api_key
        self.base_url = base_url

        self.session = requests.Session()
        # 设置Notion的API TOKEN
        self.session.headers = {
            "Authorization": "Bearer {}".format(NOTION_API_KEY),
            "Notion-Version": NOTION_VERSION
        }
        self.request_kwargs = request_kwargs or {}

    def _do_request(self, method, url, params=None, data=None, json=None):
        try:
            resp = self.session.request(method, url, params=params, data=data, json=json, **self.request_kwargs)
        except Exception as e:
            raise RequestError(str(e))
        else:
            try:
                json_data = resp.json()
            except Exception as e:
                raise JsonDecodeError(resp.status_code, str(e))
            if resp.status_code != 200:
                raise ApiError(resp.status_code, json_data.get("message"))

            return json_data

    def _do_get(self, url, params=None):
        return self._do_request("GET", url, params=params)

    def _do_post(self, url, data=None, json=None):
        return self._do_request("POST", url, data=data, json=json)

    def _do_patch(self, url, data):
        return self._do_request("PATCH", url, data=data)

    def list_database(self):
        """获取所有数据库列表"""
        data = self._do_get(urljoin(self.base_url, "databases"))
        return data

    def retrieve_database(self, database_id):
        """获取某个数据库信息，包括标题、列信息等"""
        json_data = self._do_get(urljoin(self.base_url, "databases/{}".format(database_id)))
        return json_data

    def query_database(self, database_id, filter=None, sorts=None, start_cursor=None, page_size=20):
        """查询某个数据库"""
        url = urljoin(self.base_url, "databases/{}/query".format(database_id))
        data = {
            "filter": filter,
            "sorts": sorts,
            "start_cursor": start_cursor,
            "page_size": page_size
        }
        json_data = self._do_post(url, data)
        return json_data

    def retrieve_page(self, page_id):
        """获取某个page详情"""
        url = urljoin(self.base_url, "pages/{}".format(page_id))
        json_data = self._do_get(url)
        return json_data

    def create_page(self, database_id=None, page_id=None, properties=None):
        """创建一个page，类似于在关系型数据库中创建一条记录"""
        if database_id is None and page_id is None:
            raise ParameterError("parent database id or page id required")

        if database_id:
            parent_type = "database_id"
            parent_id = database_id
        else:
            parent_type = "page_id"
            parent_id = page_id

        data = {
            "parent": {parent_type: parent_id},
            "properties": properties,
            "children": []
        }
        return self._do_post(urljoin(self.base_url, "pages"), json=data)

    def update_page(self, page_id, properties):
        """更新某个page"""
        url = urljoin(self.base_url, "pages/{}".format(page_id))
        return self._do_patch(url, data=properties)


if __name__ == '__main__':
    client = Clint(NOTION_API_KEY)
    # ret = client.list_database()
    # for database in ret["results"]:
    #     database_id = database["id"]
    #     title = database["title"][0]["text"]["content"]
    #     properties = ", ".join(database["properties"].keys())
    #
    #     print("database id: {}".format(database_id))
    #     print("database title: {}".format(title))
    #     print("database properties: {}".format(properties))

    database_id = "******"

    properties = {
        '创建时间': {'created_time': None},
        '单词': {
            'title': [{'text': {'content': 'invocations'}}],
        },
        '来源': {
            'rich_text': [{'text': {'content': '通过Notion API添加'}}],
        },
        '示例': {'rich_text': []},
        '释义': {
            'rich_text': [{'text': {'content': '祈祷、调用'}}],
        }
    }
    ret = client.create_page(database_id=database_id, properties=properties)
    pprint(ret)
