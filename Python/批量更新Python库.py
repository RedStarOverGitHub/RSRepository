from os import popen, system
print('正在扫描需要更新的库...')
try:
    # 定义需要更新的第三方库列表
    outdated = popen('pip list -o').read().split('\n')[2:-1]
    outdatedLibs = [(i.split()[0], i.split()[1], i.split()[2]) for i in outdated]
except:
    print('没有需要更新的库！')
else:
    print('以下库需要更新：')
    print('格式：库名: (当前版本, 最新版本)')
    for i in outdatedLibs:
        print(f'{i[0]}: ({i[1]}, {i[2]})')
    while True:
        opt = input('是否更新？[Y/n]')
        if opt.lower() == 'y':
            for i in range(len(outdatedLibs)):
                print(f'正在更新{outdatedLibs[i][0]}...（第{i+1}项，共{len(outdatedLibs)}）')
                system(f'pip install {outdatedLibs[i][0]} -U')
                print(f'{outdatedLibs[i][0]}更新完成！')
            print('所有库更新完成！')
            break
        elif opt.lower() == 'n':
            break
        else:
            print('无效输入！')
