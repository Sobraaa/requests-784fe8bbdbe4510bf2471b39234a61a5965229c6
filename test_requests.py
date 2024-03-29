#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement

import unittest
import cookielib

import omnijson as json

import requests



HTTPBIN_URL = 'http://httpbin.org/'
HTTPSBIN_URL = 'https://httpbin.ep.io/'

# HTTPBIN_URL = 'http://staging.httpbin.org/'
# HTTPSBIN_URL = 'https://httpbin-staging.ep.io/'


def httpbin(*suffix):
    """Returns url for HTTPBIN resource."""

    return HTTPBIN_URL + '/'.join(suffix)


def httpsbin(*suffix):
    """Returns url for HTTPSBIN resource."""

    return HTTPSBIN_URL + '/'.join(suffix)



class RequestsTestSuite(unittest.TestCase):
    """Requests test cases."""


    def setUp(self):
        pass


    def tearDown(self):
        """Teardown."""
        pass


    def test_invalid_url(self):
        self.assertRaises(ValueError, requests.get, 'hiwpefhipowhefopw')


    def test_HTTP_200_OK_GET(self):
        r = requests.get(httpbin('/'))
        self.assertEqual(r.status_code, 200)


    def test_HTTPS_200_OK_GET(self):
        r = requests.get(httpsbin('/'))
        self.assertEqual(r.status_code, 200)


    def test_HTTP_200_OK_GET_WITH_PARAMS(self):
        heads = {'User-agent': 'Mozilla/5.0'}

        r = requests.get(httpbin('user-agent'), headers=heads)

        assert heads['User-agent'] in r.content
        self.assertEqual(r.status_code, 200)


    def test_HTTP_200_OK_GET_WITH_MIXED_PARAMS(self):
        heads = {'User-agent': 'Mozilla/5.0'}

        r = requests.get(httpbin('get') + '?test=true', params={'q': 'test'}, headers=heads)
        self.assertEqual(r.status_code, 200)


    def test_user_agent_transfers(self):
        """Issue XX"""

        heads = {
            'User-agent':
                'Mozilla/5.0 (github.com/kennethreitz/requests)'
        }

        r = requests.get(httpbin('user-agent'), headers=heads);
        self.assertTrue(heads['User-agent'] in r.content)

        heads = {
            'user-agent':
                'Mozilla/5.0 (github.com/kennethreitz/requests)'
        }

        r = requests.get(httpbin('user-agent'), headers=heads);
        self.assertTrue(heads['user-agent'] in r.content)


    def test_HTTP_200_OK_HEAD(self):
        r = requests.head(httpbin('/'))
        self.assertEqual(r.status_code, 200)


    def test_HTTPS_200_OK_HEAD(self):
        r = requests.head(httpsbin('/'))
        self.assertEqual(r.status_code, 200)


    def test_HTTP_200_OK_PUT(self):
        r = requests.put(httpbin('put'))
        self.assertEqual(r.status_code, 200)


    def test_HTTPS_200_OK_PUT(self):
        r = requests.put(httpsbin('put'))
        self.assertEqual(r.status_code, 200)


    def test_HTTP_200_OK_PATCH(self):
        r = requests.patch(httpbin('patch'))
        self.assertEqual(r.status_code, 200)


    def test_HTTPS_200_OK_PATCH(self):
        r = requests.patch(httpsbin('patch'))
        self.assertEqual(r.status_code, 200)


    def test_AUTH_HTTPS_200_OK_GET(self):
        auth = ('user', 'pass')
        url = httpsbin('basic-auth', 'user', 'pass')
        r = requests.get(url, auth=auth)

        self.assertEqual(r.status_code, 200)

        r = requests.get(url)
        self.assertEqual(r.status_code, 200)

        # reset auto authentication
        requests.auth_manager.empty()


    def test_POSTBIN_GET_POST_FILES(self):
        url = httpbin('post')
        post = requests.post(url).raise_for_status()

        post = requests.post(url, data={'some': 'data'})
        self.assertEqual(post.status_code, 200)

        post2 = requests.post(url, files={'some': open('test_requests.py')})
        self.assertEqual(post2.status_code, 200)

        post3 = requests.post(url, data='[{"some": "json"}]')
        self.assertEqual(post3.status_code, 200)


    def test_POSTBIN_GET_POST_FILES_WITH_PARAMS(self):

        url = httpbin('post')
        post = requests.post(url, files={'some': open('test_requests.py')}, data={'some': 'data'})
        self.assertEqual(post.status_code, 200)


    def test_POSTBIN_GET_POST_FILES_WITH_HEADERS(self):

        url = httpbin('post')

        post2 = requests.post(url, files={'some': open('test_requests.py')},
            headers = {'User-Agent': 'requests-tests'})

        self.assertEqual(post2.status_code, 200)


    def test_nonzero_evaluation(self):
        r = requests.get(httpbin('status', '500'))
        self.assertEqual(bool(r), False)

        r = requests.get(httpbin('/'))
        self.assertEqual(bool(r), True)


    def test_request_ok_set(self):
        r = requests.get(httpbin('status', '404'))
        self.assertEqual(r.ok, False)


    def test_status_raising(self):
        r = requests.get(httpbin('status', '404'))
        self.assertRaises(requests.HTTPError, r.raise_for_status)

        r = requests.get(httpbin('status', '200'))
        self.assertFalse(r.error)
        r.raise_for_status()


    def test_cookie_jar(self):

        jar = cookielib.CookieJar()
        self.assertFalse(jar)

        url = httpbin('cookies', 'set', 'requests_cookie', 'awesome')
        r = requests.get(url, cookies=jar)
        self.assertTrue(jar)

        cookie_found = False
        for cookie in jar:
            if cookie.name == 'requests_cookie':
                self.assertEquals(cookie.value, 'awesome')
                cookie_found = True
        self.assertTrue(cookie_found)

        r = requests.get(httpbin('cookies'), cookies=jar)
        self.assertTrue('awesome' in r.content)


    def test_decompress_gzip(self):

        r = requests.get(httpbin('gzip'))
        r.content.decode('ascii')


    def test_autoauth(self):

        http_auth = ('user', 'pass')
        requests.auth_manager.add_auth('httpbin.org', http_auth)

        r = requests.get(httpbin('basic-auth', 'user', 'pass'))
        self.assertEquals(r.status_code, 200)


    def test_unicode_get(self):

        url = httpbin('/')

        requests.get(url, params={'foo': u'føø'})
        requests.get(url, params={u'føø': u'føø'})
        requests.get(url, params={'føø': 'føø'})
        requests.get(url, params={'foo': u'foo'})
        requests.get(httpbin('ø'), params={'foo': u'foo'})


    def test_httpauth_recursion(self):
        http_auth = ('user', 'BADpass')

        r = requests.get(httpbin('basic-auth', 'user', 'pass'), auth=http_auth)
        self.assertEquals(r.status_code, 401)


    def test_settings(self):

        def test():
            r = requests.get(httpbin(''))
            r.raise_for_status()

        with requests.settings(timeout=0.0000001):
            self.assertRaises(requests.Timeout, test)

        with requests.settings(timeout=100):
            requests.get(httpbin(''))


    def test_urlencoded_post_data(self):
        r = requests.post(httpbin('post'), data=dict(test='fooaowpeuf'))
        self.assertEquals(r.status_code, 200)
        self.assertEquals(r.headers['content-type'], 'application/json')
        self.assertEquals(r.url, httpbin('post'))
        rbody = json.loads(r.content)
        self.assertEquals(rbody.get('form'), dict(test='fooaowpeuf'))
        self.assertEquals(rbody.get('data'), '')


    def test_nonurlencoded_post_data(self):
        r = requests.post(httpbin('post'), data='fooaowpeuf')
        self.assertEquals(r.status_code, 200)
        self.assertEquals(r.headers['content-type'], 'application/json')
        self.assertEquals(r.url, httpbin('post'))
        rbody = json.loads(r.content)
        # Body wasn't valid url encoded data, so the server returns None as
        # "form" and the raw body as "data".
        self.assertEquals(rbody.get('form'), None)
        self.assertEquals(rbody.get('data'), 'fooaowpeuf')


    def test_urlencoded_post_querystring(self):
        r = requests.post(httpbin('post'), params=dict(test='fooaowpeuf'))
        self.assertEquals(r.status_code, 200)
        self.assertEquals(r.headers['content-type'], 'application/json')
        self.assertEquals(r.url, httpbin('post?test=fooaowpeuf'))
        rbody = json.loads(r.content)
        self.assertEquals(rbody.get('form'), {}) # No form supplied
        self.assertEquals(rbody.get('data'), '')


    def test_nonurlencoded_post_querystring(self):
        r = requests.post(httpbin('post'), params='fooaowpeuf')
        self.assertEquals(r.status_code, 200)
        self.assertEquals(r.headers['content-type'], 'application/json')
        self.assertEquals(r.url, httpbin('post?fooaowpeuf'))
        rbody = json.loads(r.content)
        self.assertEquals(rbody.get('form'), {}) # No form supplied
        self.assertEquals(rbody.get('data'), '')


    def test_urlencoded_post_query_and_data(self):
        r = requests.post(httpbin('post'), params=dict(test='fooaowpeuf'),
                          data=dict(test2="foobar"))
        self.assertEquals(r.status_code, 200)
        self.assertEquals(r.headers['content-type'], 'application/json')
        self.assertEquals(r.url, httpbin('post?test=fooaowpeuf'))
        rbody = json.loads(r.content)
        self.assertEquals(rbody.get('form'), dict(test2='foobar'))
        self.assertEquals(rbody.get('data'), '')


    def test_nonurlencoded_post_query_and_data(self):
        r = requests.post(httpbin('post'), params='fooaowpeuf',
                          data="foobar")
        self.assertEquals(r.status_code, 200)
        self.assertEquals(r.headers['content-type'], 'application/json')
        self.assertEquals(r.url, httpbin('post?fooaowpeuf'))
        rbody = json.loads(r.content)
        self.assertEquals(rbody.get('form'), None)
        self.assertEquals(rbody.get('data'), 'foobar')



if __name__ == '__main__':
    unittest.main()
