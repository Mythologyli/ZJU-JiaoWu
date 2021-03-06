import sys
import getopt
from jiaowu import JiaoWu


if __name__=='__main__':

    username = input('学号: ')
    password = input('统一认证密码: ')

    jiaowu = JiaoWu(username, password)

     # 登录
    if jiaowu.login():
        print('登录成功！')
    else: 
        print('登录失败！请检查用户名和密码')
        exit()

    # 查询课表
    year = input('学年（例：2021-2022）: ')
    semester = input('学期（例：1|秋、冬）: ')

    if year == '':
        year = '2021-2022'

    if semester == '':
        semester = '1|秋、冬'

    print('\n您的课表：')
    course_list = jiaowu.get_course(year, semester)

    for i in range(len(course_list)):
        print(course_list[i])
    
    # 查询课程成绩
    print('\n您的课程成绩：')
    course_info_list = jiaowu.get_score()

    for i in range(len(course_info_list)):
        print(course_info_list[i])

    # 查询所有课程均绩
    print('\n您的所有课程均绩为：', jiaowu.get_gpa())

    # 查询主修课程成绩
    print('\n您的主修课程成绩：')
    major_course_info_list = jiaowu.get_major_score()

    for i in range(len(major_course_info_list)):
        print(major_course_info_list[i])

    # 查询主修课程均绩
    print('\n您的主修课程均绩为：', jiaowu.get_mgpa())

    # 查询成绩更正公示
    score_announce_list = jiaowu.get_score_announce()
    if score_announce_list == 0:
        print('\n您没有成绩更正公示！')
    else:
        print('\n您的成绩更正公示为：')
        for i in range(len(score_announce_list)):
            print(score_announce_list[i])
