#!/bin/bash

# 进入项目目录（根据你的路径修改）
cd /Users/zzw868/PycharmProjects/zzw868.github.io || exit

echo "拉取远程最新代码..."
git pull origin master

echo "添加所有修改..."
git add .

echo "提交修改（自动提交）..."
git commit -m "自动更新博客内容"

echo "推送到远程仓库..."
git push origin master

echo "博客已成功更新并推送到GitHub！"
