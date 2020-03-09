#coding:utf-8

import requests
from bs4 import BeautifulSoup
import re
import time
# import sys
# import os

class EolHomework():
    """这个类获取eol未完成作业
    """



    def __init__(self, timeout, url):
        """ __init__

        :param timeout: all requests timeout

        :param url: eol url
        """

        self.timeout = timeout
        self.url = url
        self.logintoken = ''

        self.headers = {
            'User-Agent': 'User-Agent:'
                          'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/56.0.2924.87 Safari/537.36'
        }
        self.web = requests.session()

        self.chinesename = ''
        self.username = ''
        self.password = ''

        self.homeworknum = 0
        self.homeworkname = ''
        self.id = ''
        self.idnamedict = []

        self.showcontent = []



    def __main__(self):
        """__main__
        """

        self.username = input("账号：")
        self.password = input("密码：")
        # self.username = ''
        # self.password = ''

        #self.GetUserPwd()
        self.LoginEol()



    # def GetUserPwd(self):
    #     """使用预先文本中的用户账号与密码
    #     """
    #     try:
    #         name = ''
    #         pwd = ''
    #         count = 1
    #
    #         ABSPATH = None
    #         ABSPATH = os.path.abspath(sys.argv[0])
    #         ABSPATH = os.path.dirname(ABSPATH) + "/login.txt"
    #
    #         if not os.path.exists(ABSPATH):
    #             print("login.txt不存在")
    #             input()
    #             os._exit(0)
    #         else:
    #             with open(ABSPATH) as f:
    #                 for line in f.readlines():
    #                     if count == 1:
    #                         name = line.strip()
    #                     else:
    #                         pwd = line.strip()
    #                     count += 1
    #                 self.username = name
    #                 self.password = pwd
    #     except ZeroDivisionError as e:
    #         print('except:', e)



    def GetLoginToken(self):
        """获取LoginToken
        """

        try:
            logintokentext = self.web.get(self.url, headers=self.headers, timeout=self.timeout)
            #print(logintokentext.text)

            if logintokentext.status_code == 200:
                # logintokentext.text to lxml
                soup = BeautifulSoup(logintokentext.text, "lxml")

                # get,save logintoken
                self.logintoken = soup.find('input', {'name':'logintoken'}).get('value')
                # print(self.logintoken)

            else:
                print('logintokentext请求失败')
        except ZeroDivisionError as e:
            print('except:', e)



    def LoginEol(self):
        """LoginEol
        """

        try:
            # self.logintoken saved
            self.GetLoginToken()

            # 网址
            loginurl = 'http://eol.bnuz.edu.cn/meol/loginCheck.do'
            # logintoken,账号,密码
            payload = {
                'logintoken': self.logintoken,
                'IPT_LOGINUSERNAME': self.username,
                'IPT_LOGINPASSWORD': self.password
            }
            # 登录
            logintext = self.web.post(loginurl, data=payload, headers=self.headers, timeout=self.timeout)
            
            # 若请求成功
            if logintext.status_code == 200:
				# 登录成功
				print('登录成功',end="\n\n")
                # 若账号密码正确，登录后网址应为'http://eol.bnuz.edu.cn/meol/personal.do'
                if logintext.url == 'http://eol.bnuz.edu.cn/meol/personal.do':
                    self.chinesename = (re.findall(r'class="login-text">\s*<span>(.*)</span>', logintext.text))[0]
                    print(self.chinesename + '同学：')
                    self.GetHomeworkList()
                else:
                    print('账号或密码错误')
                    input()
            else:
                print('登录失败')

        except ZeroDivisionError as e:
            print('except:', e)



    def GetHomeworkList(self):
        """获取未完成作业列表
        """

        try:
            # “互动提醒”jsp
            homeworkurl = 'http://eol.bnuz.edu.cn/meol/welcomepage/student/interaction_reminder_v8.jsp'
            # payload
            payload = {
                'r':'0.5123454851964999'
            }
            # 请求
            homeworktext = self.web.get(homeworkurl, headers=self.headers, data=payload, timeout=self.timeout)

            # 若请求成功
            if homeworktext.status_code == 200:
                # 未完成作业课程数
                num = re.findall(r'title="点击查看">\s*<span>(\d)</span>\s*门课程有待提交作业', homeworktext.text)

                # 如果有未完成作业
                if num:
                    # 未完成作业课程数
                    self.homeworknum = num[0]
                    # 未完成作业课程名
                    self.homeworkname = re.findall(r'hw"\s*target="_blank">\s*(.*)</a>\s*</li>', homeworktext.text)

                    print("你有" + num[0] + "门课需要提交作业",end="\n\n")

                    # 未完成作业课程id
                    self.id = re.findall(r'id=(\d{5})&t=hw', homeworktext.text)

                    # 未完成作业课程 dict(id : 课程名)
                    self.idnamedict = dict(zip(self.id, self.homeworkname))

                    # get,show未交作业项细节
                    self.GetHomeworkDetail()
                else:
                    print("你没有需要提交的课程作业",end="\n\n")
            else:
                print('homeworktext请求失败')
            self.Loginout()

        except ZeroDivisionError as e:
            print('except:', e)



    def GetHomeworkDetail(self):
        """获取每项作业的具体情况
        """

        try:
            # 请求进入某课程前缀
            lessonurl = 'http://eol.bnuz.edu.cn/meol/lesson/enter_course.jsp'

            # 遍历未交作业课程
            for i in self.id:
                # payload
                payload = {
                    'lid': i,
                    't': 'hw'
                }
                # 请求该课程网页
                lesson = self.web.get(lessonurl, headers=self.headers, params=payload, timeout=self.timeout)

                # 请求成功
                if lesson.status_code == 200:
                    # 该课程课程活动url
                    homeworkdetailurl = 'http://eol.bnuz.edu.cn/meol/common/hw/student/hwtask.jsp'
                    # payload
                    homeworkdetailpayload = {
                        'tagbug': 'client',
                        'strStyle': 'new06'
                    }
                    # 请求该课程课程活动
                    homworkdetail = self.web.get(homeworkdetailurl, headers=self.headers, params=homeworkdetailpayload,
                                                 timeout=self.timeout)

                    # 请求成功
                    if homworkdetail.status_code == 200:
                        #print(homworkdetail.text)

                        # 找到所有作业id
                        hwid = re.findall(r'hwtask.view.jsp\?hwtid=(\d{4,5})', homworkdetail.text)
                        #print('hwid')
                        #print(hwid)

                        # 遍历所有课程id行
                        for newid in hwid:
                            # 这里用两个判断，
                            # 若之后有可以“已经提交作业，未到截止时间，可以更新提交作业提醒”的需求，
                            # 可以修改

                            # 找到存在“提交作业”button的作业行
                            hwenter = re.findall(r'hwtid=%s"\s*class="enter"' % newid, homworkdetail.text)
                            # 找到存在“查看结果”button的作业行
                            hwview = re.findall(r'hwtid=%s"\s*class="view"' % newid, homworkdetail.text)

                            # 可以“提交作业”的作业
                            if hwenter:
                                # 上一个if下，提交过作业，可以“查看结果”的作业
                                if not hwview:
                                    homeworkdetailname = re.findall(r'hwtid=%s"\s*class="infolist">(.*)\s*</a></td>'
                                                                    % newid, homworkdetail.text)
                                    homeworkdetaildate = re.findall(r'hwtid=%s"\s*class="infolist">.*\s*</a></td>\s*'
                                                                    r'<td class="align_c">(.*)\s*</td>'
                                                                    % newid,homworkdetail.text)

                                    detailcontent = "{0:\u3000<20s}{1:\u3000<20s}{2:\u3000<20s}"\
                                        .format(self.idnamedict[i],
                                                '\n作业名称:'+ homeworkdetailname[0],
                                                '\n截止时间:' + homeworkdetaildate[0])

                                    # 加到未完成作业列表
                                    self.showcontent.append(detailcontent)
                        # 每次让课程退出的语句
                        time.sleep(1)
                    else:
                        print('homworkdetail请求失败')
                else:
                    print('lesson请求失败')

            #self.status = 1
            #print(self.showcontent)

            # show未完成作业列表
            for text in self.showcontent:
                print(text+'\n')

        except ZeroDivisionError as e:
            print('except:', e)



    def Loginout(self):
        """Loginout
        """

        try:
            loginouturl = 'http://eol.bnuz.edu.cn/meol/homepage/V8/include/logout.jsp'
            loginout = self.web.get(loginouturl, headers=self.headers)
            # 若登出请求成功
            if loginout.status_code == 200:
                print('登出成功')
            else:
                print('登出失败')
        except ZeroDivisionError as e:
            print('except:', e)



if __name__ == '__main__':
    url = 'http://eol.bnuz.edu.cn/meol/index.do'
    timeout = 10
    eol = EolHomework(timeout, url)
    eol.__main__()


