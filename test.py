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
