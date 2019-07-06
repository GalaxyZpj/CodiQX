from django.http import HttpResponse
from django.shortcuts import render

from os import system
from base64 import b64decode
import requests, json

def compiler_view(request):
    return render(request, 'web.html', {'output': ''})

def result(request):
    # Global
    URL = ''
    language_d = {}
    data_d = {}
    result = None
    use_base64 = False

    URL = 'https://api.judge0.com/submissions/'

    testcases = {
    'Layout_test': {'stdin': 'str', 'expected_output': 'str', 'description': 'comment_result'},
    1: {'stdin': '4\n16\n', 'expected_output': '20', 'description': 'comment_result'},
    2: {'stdin': '300000\n100000\n', 'expected_output': '400000', 'description': 'comment_result'},
    3: {'stdin': '600\n100000\n', 'expected_output': '10060', 'description': 'comment_result'}
    }   

    languages = [
    {"id": 1,"name": "C (gcc 7.2.0)"},
    {"id": 2,"name": "C++ (g++ 7.2.0)"},
    {"id": 3,"name": "C# (mono 5.4.0.167)"},
    {"id": 4,"name": "Java (OpenJDK 9 with Eclipse OpenJ9)"},
    {"id": 5,"name": "JavaScript (nodejs 8.5.0)"},
    {"id": 6,"name": "Python (3.6.0)"},
    ]
    data = {
        "source_code": None,
        "language_id": None,
        "number_of_runs": "1",
        "stdin": None,
        "expected_output": None,
        "cpu_time_limit": "2",
        "cpu_extra_time": "0.5",
        "wall_time_limit": "5",
        "memory_limit": "128000",
        "stack_limit": "64000",
        "max_processes_and_or_threads": "30",
        "enable_per_process_and_thread_time_limit": False,
        "enable_per_process_and_thread_memory_limit": True,
        "max_file_size": "1024"
    }


    # Functions
    def initialize(url, language, data, testcases=None):
        global URL
        global language_d
        global data_d
        URL = url
        language_d = language
        data_d = data

    def code_string():
        """print('Enter your code:-')
        with open('Sample.txt', 'w') as f:
            while True:
                s = input()
                if s == '': break
                f.write(s)
                f.write('\n')
        with open('Sample.txt', 'r') as f:
            data_s = f.read()
        return data_s"""
        code = request.GET['code']
        return code

    def language_id(l):
        global use_base64
        """for x in l:
            print('{}: {}'.format(x['id'], x['name']))
        i = int(input('Choose amoung following languages: '))
        if i == 1: s = str(4)
        elif i == 2: s = str(10)
        elif i == 3: s = str(16)
        elif i == 4: s = str(26)
        elif i == 5: s = str(29)
        elif i == 6: s = str(34)
        else: s = str(i)"""
        s = request.GET['language']
        if s == '4' or s == '10' or s == '16' or s == '26': use_base64 = True
        return s

    def prep_submissionDict():
        data_d["language_id"] = language_id(language_d)
        data_d["source_code"] = code_string()
        return data_d

    def generate_token(data):
        r = requests.post(URL, data)
        if r.status_code == 201: return r.json()
        elif r.status_code == 401:
            print('Authentication Failed')
            quit()
        elif r.status_code == 422:
            print('Language ID invalid')
            quit()

    def fetch_server(token):
        while True:
            global use_base64
            print('OUTPUT:-')
            print('Processing...')
            if use_base64 == True: useb64 = 'true'
            else: useb64 = 'false'
            r = requests.get(URL + token['token'] + '?base64_encoded=' + useb64)
            if r.status_code != 200: break
            else:
                r = r.json()
                if r['status']['id'] == 1 or r['status']['id'] == 2: continue
                else:
                    if use_base64 == True:
                        if r['stdout'] != None: r['stdout'] = decrypt(r['stdout'])
                        if r['compile_output'] != None: r['compile_output'] = decrypt(r['compile_output'])
                        if r['message'] != None: r['message'] = decrypt(r['message'])
                        if r['stderr'] != None: r['stderr'] = decrypt(r['stderr'])
                    return [1, r]
        x = r.status_code
        if x == 401: return [0, {'error': 'Authentication Failed', 'exception': 'Unknown'}]
        elif x == 500:
            return [0, {'error': 'Authentication Failed', 'exception': 'Unknown'}]

    def display_output(o):
        """if o[0] == 1:
            print('::: ',o[1]['status']['description'].upper(),' :::')
            if o[1]['stdout'] != None: print('STDOUT:\n', o[1]['stdout'])
            if o[1]['time'] != None: print('TIME:\n', o[1]['time'])
            if o[1]['memory'] != None: print('MEMORY:\n', o[1]['memory'])
            if o[1]['stderr'] != None: print('STDERR:\n', o[1]['stderr'])
            if o[1]['compile_output'] != None: print('COMPILE OUTPUT:\n', o[1]['compile_output'])
            if o[1]['message'] != None: print('MESSAGE:\n', o[1]['message'])
        elif o[0] == 0:
            print('\nError: ', o[1]['error'])
            print('Exception: ',o[1]['exception'])"""
        #print(o)
        return o[1]

    def decrypt(s):
        return b64decode(s).decode()

    # Compiler.py
    initialize(URL, languages, data)
    s_dict = prep_submissionDict()
    token = generate_token(s_dict)
    response = fetch_server(token)
    s = display_output(response)
    return render(request, 'web.html', {'output': s})
