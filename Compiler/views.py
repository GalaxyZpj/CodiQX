from django.http import HttpResponse
from django.shortcuts import render
import pymysql as sql
from datetime import datetime
from random import choice

from os import system
from base64 import b64decode
import requests, json, threading

use_base64 = False
testcases = {}
question = []
returnResult = []
rootCode = ''

def homepage(request):
    return render(request, 'base.html')

def redirect(request):
    if request.GET['goto'] == 'Login': return render(request, 'login.html', {'login': ''})
    elif request.GET['goto'] == 'Register': return render(request, 'register.html')
    elif request.GET['goto'] == 'RegisterQ': return render(request, "addquestion.html", {'wall': ['True', '', ''], 'output': '', 'setType': '', 'setList': [], 'set_no': '', 'qID': ''})
    elif request.GET['goto'] == 'RegisterTestcase': return render(request, 'addtestcase.html')

def loginCheck(request):
    conn = sql.connect(host = 'localhost', port = 3306, user = 'root', password = '12345678', db = 'Practice')
    cmd = conn.cursor()
    # Password Check
    q = f"select password from Compiler where email = '{request.GET['email']}'"
    cmd.execute(q)
    row = cmd.fetchone()

    # Question Title Fetch
    q = "select * from OrganizationRecord"
    cmd.execute(q)
    qBank = cmd.fetchall()
    if row == None: return render(request, 'login.html', {'login': 'Email not found.   Please consider registering first.'})
    conn.close()
    if row[0] == request.GET['pass']: return render(request, 'questionView.html', {'qBank': qBank})
    else: return render(request, 'login.html', {'login': 'Invalid Password'})

def register(request):
    conn = sql.connect(host = 'localhost', port = 3306, user = 'root', password = '12345678', db = 'Practice')
    cmd = conn.cursor()
    q = f"insert into Compiler (first_name, last_name, email, mobile, password, create_date, update_date, status) values('{request.GET['fn']}', '{request.GET['ln']}', '{request.GET['email']}', '{request.GET['mob']}', '{request.GET['pass']}', '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}', '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}', 'Not Verified')"
    cmd.execute(q)
    print('Record Added.')
    conn.commit()
    conn.close()
    return HttpResponse("<html><h1>User Registered.</h1></html>")

# OLD
"""def result(request):
    global testcases, question, rootCode

    URL = 'https://api.judge0.com/submissions/' 

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
        global rootCode
        code = request.GET['code']
        rootCode = code
        return code

    def language_id(l):
        global use_base64
        s = request.GET['language']
        if s == '4' or s == '10' or s == '16' or s == '26': use_base64 = True
        return s

    def prep_submissionDict(stdin, exp):
        data_d["language_id"] = language_id(language_d)
        data_d["source_code"] = code_string()
        data_d["stdin"] = stdin
        data_d["expected_output"] = exp
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
        return o[1]

    def decrypt(s):
        return b64decode(s).decode()

    # Compiler.py
    returnResult = []
    for x in testcases.keys():
        initialize(URL, languages, data)
        s_dict = prep_submissionDict(testcases[x]['stdin'], testcases[x]['expected_output'])
        token = generate_token(s_dict)
        response = fetch_server(token)
        s = display_output(response)
        print('\n\n\n', s, '\n\n\n')
        returnResult.append(s)
        print('\n\n\n', returnResult, '\n\n\n')
    d = []
    t = []
    for x in testcases.keys(): t.append(x)
    for i, r in enumerate(returnResult):
        d.append([i+1,testcases[t[i]]['stdin'], r['stdout'], r['status']['description']])
    # print('\n\n\n', returnResult, '\n\n\n')
    # print('\n\n\n', testcases, '\n\n\n')
    #print('\n\n\n\n\n\n\n\n',rootCode)
    return render(request, 'compiler.html', {'d': d, 'question': question, 'code': rootCode})
    # return render(request, 'compiler_extended.html', {'d': d, 'question': question, 'code': rootCode})
    # return render(request, 'compiler_extended.html', d)
"""
# NEW
def result(request):
    def evaluate(test_no, testcase):
        global returnResult
        URL = 'https://api.judge0.com/submissions/' 

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
            global rootCode
            code = request.GET['code']
            rootCode = code
            return code

        def language_id(l):
            global use_base64
            s = request.GET['language']
            if s == '4' or s == '10' or s == '16' or s == '26': use_base64 = True
            return s

        def prep_submissionDict(stdin, exp):
            data_d["language_id"] = language_id(language_d)
            data_d["source_code"] = code_string()
            data_d["stdin"] = stdin
            data_d["expected_output"] = exp
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
            return o[1]

        def decrypt(s):
            return b64decode(s).decode()
        initialize(URL, languages, data)
        s_dict = prep_submissionDict(testcase['stdin'], testcase['expected_output'])
        token = generate_token(s_dict)
        response = fetch_server(token)
        s = display_output(response)
        print('\n\n\n', s, '\n\n\n')
        for x in returnResult:
            if x[0] == test_no:
                returnResult[test_no-1].append(s)

    global testcases, question, returnResult, rootCode

    returnResult = []    
    testcase_Threads = []
    
    # Storing the threads
    for x in testcases.keys():
        returnResult.append([x])
        t = threading.Thread(target = evaluate, args=(x, testcases[x]))
        testcase_Threads.append((x, t))

    # Starting the threads
    for x in testcase_Threads: x[1].start()

    # Waiting for all threads to finish up
    for x in testcase_Threads: x[1].join()
    
    d = []
    t = []
    for x in testcases.keys(): t.append(x)
    for r in returnResult:
        d.append([r[0],testcases[t[r[0]-1]]['stdin'], r[1]['stdout'], r[1]['status']['description']])
    return render(request, 'compiler.html', {'d': d, 'question': question, 'code': rootCode})

def addQuestion(request):
    def insertQuestion():
        x = 1
        while True:
            question_id = set_no + 'q' + str(x)
            print('\n\n\n', question_id)
            try:
                q = f"insert into OrganizationRecord values ({transaction_id}, '{org_id}', '{set_no}', '{question_id}', '{question_title}','{question}')"
                cmd.execute(q)
                return question_id
            except Exception as e:
                print(e, '\n\nQuestion Exists\n\n')
            x += 1
    def insertSet():
        x = 1
        while True:
            set_no = org_id + '_s' + str(x)
            question_id = set_no + 'q' + str(1)
            print('\n\n\n', question_id)
            try:
                q = f"insert into OrganizationRecord values ({transaction_id}, '{org_id}', '{set_no}', '{question_id}', '{question_title}','{question}')"
                cmd.execute(q)
                return set_no, question_id
            except Exception as e:
                print(e, '\nSet Exists\n\n')
            x += 1
    conn = sql.connect(host = 'localhost', port = 3306, user = 'root', password = '12345678', db = 'Practice')
    cmd = conn.cursor()
    wall = ['True', '', '']
    transaction_id = 1
    setList = []
    question_id = ''
    question = ''
    question_title = ''
    try:
        set_no = request.GET['set_no']
    except:
        set_no = ''
    org_id = request.GET['org_id']
    try:
        setType = request.GET['setType']
    except:
        setType = ''
    if setType == 'existing':
        q = f"select set_no from OrganizationRecord where organization_id = '{org_id}'"
        cmd.execute(q)
        setTemp = cmd.fetchall()
        if len(setTemp) == 0: return render(request, "addquestion.html", {'wall': wall, 'output': 'No Entries for your Organization, Please Select \'New\' for Set Type.', 'org_id': org_id, 'setType': setType, 'setList': setList, 'set_no': set_no, 'qID': question_id})
        print('\n\n\n\n\n', setTemp)
        for x in setTemp: 
            for y in x:
                if y not in setList: setList.append(y)
        wall[0], wall[1] = '', 'True'
        return render(request, "addquestion.html", {'wall': wall, 'output': '', 'org_id': org_id, 'setType': setType, 'setList': setList, 'set_no': set_no, 'qID': question_id})
    elif setType == 'new':
        set_no, question_id = insertSet()
        wall[0], wall[1] = '', 'True'
        return render(request, "addquestion.html", {'wall': wall, 'output': '', 'org_id': org_id, 'setType': setType, 'setList': setList, 'set_no': set_no, 'qID': question_id})

    question_title = request.GET['ques_title']
    question = request.GET['ques']
    question_id = insertQuestion()
    conn.commit()
    conn.close()
    if request.GET['send'] == "Submit":
        return render(request, "addquestion.html", {'wall': wall, 'output': 'Question Added Successfully with ID: ', 'org_id': org_id,  'setType': setType, 'setList': setList, 'set_no': set_no, 'qID': question_id})

def questionView(request):
    global testcases, question
    qid = request.GET['qid']
    conn = sql.connect(host = 'localhost', port = 3306, user = 'root', password = '12345678', db = 'Practice')
    cmd = conn.cursor()
    q = f"select question_title, question from OrganizationRecord where question_id = '{qid}'"
    cmd.execute(q)
    question = cmd.fetchone()
    q = f"select testcase_no, stdin, expected_output from Testcases where question_id = '{qid}'"
    cmd.execute(q)
    testcases_list = cmd.fetchall()
    testcases = {}
    print('\n\n\n',testcases)
    for i, x in enumerate(testcases_list): testcases[i+1] = {'stdin': x[1], 'expected_output': x[2], 'description': 'comment_result'}
    print('\n\n\n\n\n\n\n',testcases, '\n\n\n\n\n\n\n')
    return render(request, "compiler.html", {'question': question})

def addTestcase(request):
    conn = sql.connect(host = 'localhost', port = 3306, user = 'root', password = '12345678', db = 'Practice')
    cmd = conn.cursor()
    transaction_id = 1
    output = ''
    qNo = ''
    stdin = ''
    expected_output = ''
    orgID = request.POST['orgID']
    op = request.POST['send']
    orgList = []

    if op == 'orgID':
        q = f"select question_id, question_title from OrganizationRecord where organization_id = '{orgID}'"
        cmd.execute(q)
        orgList = cmd.fetchall()
        if len(orgList) == 0:
            output = 'Organization Not Registered.'
            return render(request, "addtestcase.html", {'orgID': orgID, 'orgList': orgList, 'qNo': qNo, 'stdin': stdin, 'expected_output': expected_output, 'output': output})
    if op == 'Submit':
        qNo = request.POST['qNo']
        stdin = request.POST['stdin']
        expected_output = request.POST['expected_output']
        output = 'Data Inserted Successfully'
        x = 1
        while True:
            testcase_id = str(qNo)+ '_' + str(x)
            try:
                q = f"insert into Testcases values ({transaction_id}, '{qNo}', '{testcase_id}', '{stdin}', '{expected_output}')"
                cmd.execute(q)
                break
            except:
                print('\n\nTestcase Exists\n\n')
            x += 1
        conn.commit()
    conn.close()
    return render(request, "addtestcase.html", {'orgID': orgID, 'orgList': orgList, 'qNo': qNo, 'stdin': stdin, 'expected_output': expected_output, 'output': output})
