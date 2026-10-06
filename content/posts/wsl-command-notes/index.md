---
title: WSL 相关命令的一些分享
description: 整理 WSL 发行版安装、导入导出、时间同步、图形应用和字体配置等常用操作。
date: '2026-04-14T15:18:15+08:00'
image: img/covers/Linux-or-Windows.jpg
categories:
  - 系统环境
tags:
  - WSL
  - Windows
  - Linux
draft: false
---

# 设置wsl2为默认内核版本

wsl --set-default-version 2

# curl安装wsl发行版

curl.exe -L -o ubuntu-2004.appx https://aka.ms/wsl-ubuntu-2004

# 下载了发行版后，导航到包含下载内容的文件夹，并在该目录中运行以下命令，其中app-name是 Linux 发行版 .appx 文件的名称。

Add-AppxPackage .\app_name.appx

# 立即终止所有正在运行的发行版和 WSL 2 轻量级实用工具虚拟机。 在需要重启 WSL 2 虚拟机环境的情形下，例如更改内存使用限制或更改 .wslconfig 文件，可能必须使用此命令。

# 根据我的理解，如果有多个wsl的分发版（场景情况是一个自己用的分发+docker-desktop的情况），wsl --shutdown会关闭所有分发，也就是wsl内核其实是所有分发公用的，各个分发版实质只是一个用户态的文件系统

wsl --shutdown

# 卸载发行版

wsl --unregister ub

# 指定默认发行版

wsl -s ub

# 导入wsl wsl --import <名称> <wsl虚拟磁盘位置> <导入源文件> [Options]

wsl --import ub P:\vm\wsl\ubd\ P:\vm\wsl\ub\source.tar --version 2

## 导入这个命令也支持tar.gz格式，根据分发版只是一个用户态文件系统的理解，依据这个命令可以玩一个比较骚的操作：直接下载一个[ubuntu25.04](https://cdimage.ubuntu.com/ubuntu-base/releases/25.04/release/ubuntu-base-25.04-base-amd64.tar.gz)的rootfs，然后直接使用wsl --import这个文件，那就可以得到一个干干净净，几乎没有任何附加的wsl分发，然后再自己装一装库包

# 导出wsl

wsl --export ub P:\vm\wsl\ub\ub20-231009.tar

# 将指定的 .vhdx 文件作为新分发版导入。  必须使用 ext4 文件系统类型设置此虚拟硬盘的格式。

wsl --import-in-place <Distro> <FileName>

## 其实WSL安装好都是一个ext4.vhdx的虚拟磁盘，如果重装电脑啥的要还原之前的WSL只需将这个文件备份；

# 同步宿主机时间，解决有时候时间不一致的问题

hwclock -s

# wsl systemd，这个现在应该用不上了，wsl-config默认有相关配置，[官方文档](https://learn.microsoft.com/zh-cn/windows/wsl/systemd#how-to-enable-systemd)

wsl --update

```Bash
curl -L -O "https://raw.githubusercontent.com/nullpo-head/wsl-distrod/main/install.sh"
chmod +x install.sh
./install.sh install
/opt/distrod/bin/distrod enable --start-on-windows-boot
```

# wslg 应用缩放调整

echo "export GDK_DPI_SCALE=1.5" >> /etc/profile

## 如果使用wsl中的vscode或其他图形化应用字体显示过小可以用这个；wsl打开linux图形化这个功能主要问题是输入中文需要在linux上安装中文输入法，用起来真一言难尽

# 中文安装好依赖后方框，给windows的字体加个软连接连到wsl里，需不需要重启有点忘了，这个大家实际操作视具体情况

sudo mkdir -p /usr/share/fonts/win11 # to differentiate self-built font links from system font files
sudo ln -s /mnt/c/Windows/Fonts/* /usr/share/fonts/win11
重启wsl

# wsl 卸载，winserver上只关闭wsl功能不会卸载wsl组件，需要执行下面命令

wsl --uninstall
