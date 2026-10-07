---
title: "windows与ubuntu双系统主机下ubuntu访问windows磁盘是只读"
date: 2024-11-21T16:10:00+08:00
image: img/covers/Linux-or-Windows.jpg
categories:
  - 系统环境
tags:
  - Linux
  - NTFS
  - Ubuntu
  - Windows
---

## 尝试关闭 Windows 快速启动

看一些博客写的切换windows关闭快速启动，结果到windows系统以后，电源选项里就没有快速启动，这个地方还是跑了一下关闭快速启动的命令，

```powershell
powercfg -h off # 就是禁用休眠模式 同时会删除C盘的hiberfil.sys
```

## 尝试直接运行 ntfsfix

切换ubuntu，还是一样，这个时候尝试第二个方法

```shell
ntfsfix /dev/xxx
# 并无X用
```

## 卸载磁盘后修复并重新挂载

先卸载磁盘，运行：“ntfsfix /dev/xxx” 再挂载，问题解决

```shell
# 卸载已挂载的设备
sudo umount /dev/nvme1n1p3
ntfsfix /dev/nvme1n1p3
sudo mount -t ntfs -w /dev/nvme1n1p3 /root/win_p
```
