#!usr/bin/env python3
# coding=utf-8
"""
此Python脚本可批量更新Python库，请确保您已安装pip
"""
from os import popen, system

print('正在扫描需要更新的库...')

# 定义需要更新的第三方库列表
outdated = popen('pip list -o').read().split('\n')[2:-1]
outdatedLibs = [(i.split()[0], i.split()[1], i.split()[2]) for i in outdated]

if len(outdatedLibs) == 0:  # 判断需要更新的库是否为空
    print('没有需要更新的库！')
else:
    # 列出需要更新的库
    print('以下库需要更新：')
    print('格式：库名: (当前版本, 最新版本)')
    for i in outdatedLibs:
        print(f'{i[0]}: ({i[1]}, {i[2]})')
    while True:
        opt = input('是否更新？[Y/n] ')  # 判断是否更新库
        if opt.lower() == 'y':
            fail = False

            # 更新库
            for i in range(len(outdatedLibs)):
                print(f'正在更新{outdatedLibs[i][0]}...（第{i+1}项，共{len(outdatedLibs)}项）')
                if outdatedLibs[i][0] == "pip":
                    upgradeLib = system(f'python -m pip install --upgrade pip')
                else:
                    upgradeLib = system(f'pip install {outdatedLibs[i][0]} -U')
                if upgradeLib == 0:
                    print(f'{outdatedLibs[i][0]}更新完成！')
                else:
                    print(f'{outdatedLibs[i][0]}更新失败！')
                    fail = True
                    break

            if not fail:
                print('所有库更新完成！')
                break
            else:
                print('部分库更新失败！')
                break
        elif opt.lower() == 'n':
            break
        else:
            print('无效输入！')

system('pause')
