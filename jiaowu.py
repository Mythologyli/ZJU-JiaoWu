import requests
import re
from bs4 import BeautifulSoup


class JiaoWu(object):
    '''浙江大学教务网爬虫库'''

    def __init__(self, username, password):
        # 浙大统一认证平台用户名
        self.username = username 

        # 浙大统一认证平台密码
        self.password = password

        # 浙大统一认证平台登录 url
        self.zjuam_login_url = 'https://zjuam.zju.edu.cn/cas/login?service=http://jwbinfosys.zju.edu.cn'

        # 教务网登录 url
        self.jiaowu_login_url = 'http://jwbinfosys.zju.edu.cn/default2.aspx'

        # 教务网课程查询 url
        self.course_url = 'http://jwbinfosys.zju.edu.cn/xskbcx.aspx?xh='

        # 教务网成绩查询 url
        self.score_url = 'http://jwbinfosys.zju.edu.cn/xscj.aspx?xh='

        # 教务网主修成绩查询 url
        self.major_score_url = 'http://jwbinfosys.zju.edu.cn/xscj_zg.aspx?xh='

        # 教务网成绩更正公示 url
        self.score_announce_url = 'http://jwbinfosys.zju.edu.cn/cjgs.aspx?xh='

        # 请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.67'
        }

        # 请求 session
        self.sess = requests.Session()

    def login(self):
        '''教务网统一认证登录'''

        res = self.sess.get(self.zjuam_login_url, headers=self.headers)
        execution = re.search('name="execution" value="(.*?)"', res.text).group(1)
        res = self.sess.get(url='https://zjuam.zju.edu.cn/cas/v2/getPubKey', headers=self.headers).json()
        n, e = res['modulus'], res['exponent']
        encrypt_password = self._rsa_encrypt(self.password, e, n)

        data = {
            'username': self.username,
            'password': encrypt_password,
            'execution': execution,
            '_eventId': 'submit'
        }

        res = self.sess.post(url=self.zjuam_login_url, data=data, headers=self.headers)
        res.encoding = 'gb2312' # 教务网编码为 gb2312

        if res.text.find('秒钟后将自动进入首页') == -1:
            return 0

        res = self.sess.get(self.jiaowu_login_url, headers=self.headers)
        
        return 1

    def get_course(self, year, semester):
        '''查询课表'''

        # 获取 __VIEWSTATE
        res = self.sess.get(self.course_url + self.username, headers=self.headers)
        res.encoding = 'gb2312'

        soup = BeautifulSoup(res.text, 'html.parser')
        viewstate_part = str(soup.find('form').find_all('input')[2])
        viewstate = viewstate_part[47:(len(viewstate_part) - 3)]

        # 课表查询
        data = {
            '__EVENTTARGET': 'xqd',
            '__EVENTARGUMENT': '',
            '__VIEWSTATE': viewstate,
            'xxms': '列表'.encode(encoding='gb2312'),
            'xnd': year,
            'xqd': semester.encode(encoding='gb2312'),
            'kcxx': ''
        }

        res = self.sess.post(url=(self.course_url + self.username), data=data, headers=self.headers)
        res.encoding = 'gb2312'
        
        soup = BeautifulSoup(res.text.replace('<br>', ' ').replace('&nbsp;', ''), 'html.parser')
        course_grid = soup.find('table', id='xsgrid')
        row_list = course_grid.find_all('tr')
        course_amount = len(row_list) - 1
        course_info_list = []

        for i in range(course_amount):
            row = row_list[i + 1].find_all('td')

            course_info = {
                '课程代码': '',
                '课程名称': '',
                '教师姓名': '',
                '学期': '',
                '上课时间': '',
                '上课地点': '',
                '选课时间': '',
                '选课志愿': ''
            }

            course_info['课程代码'] = row[0].text
            course_info['课程名称'] = row[1].text
            course_info['教师姓名'] = row[2].text
            course_info['学期'] = row[3].text
            course_info['上课时间'] = row[4].text
            course_info['上课地点'] = row[5].text
            course_info['选课时间'] = row[6].text
            course_info['选课志愿'] = row[7].text

            course_info_list.append(course_info)

        return course_info_list

    def get_score(self):
        '''查询课程成绩'''

        # 获取 __VIEWSTATE
        res = self.sess.get(self.score_url + self.username, headers=self.headers)
        res.encoding = 'gb2312'

        soup = BeautifulSoup(res.text, 'html.parser')
        viewstate_part = str(soup.find('form').find('input'))
        viewstate = viewstate_part[47:(len(viewstate_part) - 3)]

        # 在校学习成绩查询
        data = {
            '__VIEWSTATE': viewstate,
            'ddlXN': '',
            'ddlXQ': '',
            'txtQSCJ': '',
            'txtZZCJ': '',
            'Button2': ''
        }

        res = self.sess.post(url=(self.score_url + self.username), data=data, headers=self.headers)
        res.encoding = 'gb2312'

        soup = BeautifulSoup(res.text.replace('&nbsp;', ''), 'html.parser')
        course_grid = soup.find('table', id='DataGrid1')
        row_list = course_grid.find_all('tr')
        course_amount = len(row_list) - 1
        course_info_list = []

        for i in range(course_amount):
            row = row_list[i + 1].find_all('td')

            course_info = {
                '选课课号': '',
                '课程名称': '',
                '成绩': '',
                '学分': '',
                '绩点': '',
                '补考成绩': ''
            }

            course_info['选课课号'] = row[0].text
            course_info['课程名称'] = row[1].text
            course_info['成绩'] = row[2].text
            course_info['学分'] = float(row[3].text)
            course_info['绩点'] = float(row[4].text)

            course_info_list.append(course_info)

        return course_info_list

    def get_gpa(self):
        '''查询所有课程均绩'''

        course_info_list = JiaoWu.get_score(self)
        course_amount = len(course_info_list)
        credit_sum = 0
        credit_get_sum = 0

        # 计算总学分
        for i in range(course_amount):
            credit_sum += course_info_list[i]['学分']

            # 绩点为 0 判断为未获得该学分
            if course_info_list[i]['绩点'] != 0:
                credit_get_sum += course_info_list[i]['学分']

        credit_mul_gp_sum = 0
        # 计算 GPA
        for i in range(course_amount):
            credit_mul_gp_sum += course_info_list[i]['学分'] * course_info_list[i]['绩点']

        return round(credit_mul_gp_sum / credit_sum, 2)

    def get_major_score(self):
        '''查询主修课程成绩'''

        res = self.sess.get(self.major_score_url + self.username, headers=self.headers)
        res.encoding = 'gb2312'
        
        soup = BeautifulSoup(res.text.replace('&nbsp;', ''), 'html.parser')
        major_course_grid = soup.find('table', id='DataGrid1')
        row_list = major_course_grid.find_all('tr')
        major_course_amount = len(row_list) - 1

        major_course_info_list = []

        for i in range(major_course_amount):
            row = row_list[i + 1].find_all('td')

            major_course_info = {
                '选课课号': '',
                '课程名称': '',
                '成绩': '',
                '折算成绩': '',
                '学分': '',
                '绩点': '',
                '学年': ''
            }

            major_course_info['选课课号'] = row[0].text
            major_course_info['课程名称'] = row[1].text
            major_course_info['成绩'] = row[2].text
            major_course_info['折算成绩'] = row[3].text
            major_course_info['学分'] = float(row[4].text)
            major_course_info['绩点'] = float(row[5].text)
            major_course_info['学年'] = row[6].text

            major_course_info_list.append(major_course_info)

        return major_course_info_list

    def get_mgpa(self):
        '''查询主修课程均绩'''

        res = self.sess.get(self.major_score_url + self.username, headers=self.headers)
        res.encoding = 'gb2312'
        
        soup = BeautifulSoup(res.text, 'html.parser')
        text = soup.find('span', id='Label1').text
        
        return float(text[13:17])

    def get_score_announce(self):
        '''查询成绩更正公示'''

        # 获取 __VIEWSTATE
        res = self.sess.get(self.score_announce_url + self.username, headers=self.headers)
        res.encoding = 'gb2312'

        soup = BeautifulSoup(res.text, 'html.parser')
        viewstate_part = str(soup.find('form').find_all('input')[2])
        viewstate = viewstate_part[47:(len(viewstate_part) - 3)]

        # 查询成绩更正公示
        data = {
            '__VIEWSTATE': viewstate,
            'ddlXy': '',
            'txtXs': self.username,
            'txtXkkh': '',
            'btnCx': '查询'.encode(encoding='gb2312')
        }

        res = self.sess.post(url=(self.score_announce_url + self.username), data=data, headers=self.headers)
        res.encoding = 'gb2312'

        soup = BeautifulSoup(res.text.replace('&nbsp;', ''), 'html.parser')
        recording_info = soup.find('fieldset').find('legend')

        # 无记录
        if recording_info.text[10] == '0':
            return 0

        announce_grid = soup.find('fieldset').find('table')

        row_list = announce_grid.find_all('tr')
        announce_amount = len(row_list) - 2
        announce_info_list = []

        for i in range(announce_amount):
            row = row_list[i + 1].find_all('td')

            announce_info = {
                '学年': '',
                '学期': '',
                '小学期': '',
                '开课部门': '',
                '课程名称': '',
                '学号': '',
                '姓名': '',
                '原成绩': '',
                '更正成绩': '',
                '申请人': '',
                '更正原因': ''
            }

            announce_info['学年'] = row[0].text
            announce_info['学期'] = row[1].text
            announce_info['小学期'] = row[2].text
            announce_info['开课部门'] = row[3].text
            announce_info['课程名称'] = row[4].text
            announce_info['学号'] = row[5].text
            announce_info['姓名'] = row[6].text
            announce_info['原成绩'] = row[7].text
            announce_info['更正成绩'] = row[8].text
            announce_info['申请人'] = row[9].text
            announce_info['更正原因'] = row[10].text

            announce_info_list.append(announce_info)

        return announce_info_list

    def _rsa_encrypt(self, password_str, e_str, M_str):
        '''统一认证登录 rsa 计算'''

        password_bytes = bytes(password_str, 'ascii') 
        password_int = int.from_bytes(password_bytes, 'big')
        e_int = int(e_str, 16) 
        M_int = int(M_str, 16) 
        result_int = pow(password_int, e_int, M_int) 

        return hex(result_int)[2:].rjust(128, '0')
