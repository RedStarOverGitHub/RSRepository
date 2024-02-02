echo off
chcp 65001
rem 输出注意事项
echo "注意事项："
echo "1.请确保您是在Windows环境运行此脚本，且errorlever变量在指令执行成功后值为0"
echo "2.请确保您已安装git，本文件在本地仓库根目录，并已连接云端仓库"
echo "3.请确保您已安装pause.vbs"
echo "4.请确保您已配置用户名和邮箱"
echo "5.请您在弹出默认编辑器后，在第九行去掉注释符号（#）"
echo "6.请确保您的远程主机名是origin，若不是，请修改脚本中第31行origin部分"
echo "7.请确保您的本地仓库名是main，若不是，请修改脚本中第31行main部分"
echo "8.请确保您有push到异名云端分支的需求，若有，请在第31行后加上':分支名'"
echo "阅读完毕请按任意键"
pause > nul
rem 提交代码
echo "开始提交代码..."
set /p commitMessage="请输入提交信息："
if %commitMessage% == "" (
    set commitMessage="已提交文件"
)
git commit -a -m %commitMessage%
if %errorlevel% == 0 (
    echo "提交代码成功"
) else (
    echo "提交代码失败，请按任意键退出"
    pause > nul
    exit /b
)
rem push代码
echo "开始push代码..."
git push origin main
if %errorlevel% == 0 (
    echo "push代码成功，请按任意键退出"
    pause > nul
    exit /b
) else (
    echo "push代码失败，请按任意键退出"
    pause > nul
    exit /b
)
