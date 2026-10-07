---
title: 分享一个 WSL 的 IP 总是变化的解决办法
description: 在 WSL 启动时将当前 IP 写入 Windows hosts，并记录通过 Windows OpenSSH 访问 WSL 的方法。
date: '2026-04-14T15:18:15+08:00'
image: img/covers/Linux-or-Windows.jpg
categories:
  - 系统环境
tags:
  - WSL
  - Windows
  - hosts
  - SSH
draft: false
---

## 思路

之前尝试过几次其他办法，可能操作有误都没正常生效
后来修改了思路，每次wsl启动的时候执行一个脚本，直接将wsl当前的ip写进windows宿主机的hosts里

## Bash 代码实现

```shell
# 主机HOST增加WSL_IP
HS=/mnt/c/Windows/System32/drivers/etc/hosts
function replace_host() {
  if ! [ -x "$(which ip)" ]; then return; fi
  # 获取当前wsl的ip
  wsl_ip=$(ip -br a | awk '/eth0/ {print $3}' | grep -o '^[0-9./]*$' | sed 's@/.*@@g')
  if [ -z "${wsl_ip}" ]; then
    wsl_ip="127.0.0.1"
  fi
  # 获取win主机host中的wsl_ip
  current_host_wsl_ip=$(grep '^.* wsl$' ${HS})
  if [ "$current_host_wsl_ip" == "$wsl_ip wsl" ]; then
    # 若本来相同则不做处理
    return
  fi
  echo "replace wsl ip in hosts file"
  echo "remove hosts: $current_host_wsl_ip"
  # 先删后加 分开处理，若直接替换则需考虑首次添加问题更麻烦
  sed -i '/^.* wsl/d' $HS
  echo "add wsl current ip: ${wsl_ip}"
  echo "${wsl_ip} wsl" >>$HS
}
```

可以写到.bashrc，profile里，也可以复制一个单独的脚本，通过配置/etc/wsl.conf添加wsl的启动命令实现
下面是一个demo

```toml
[boot]
command=win_hosts_proc.sh
```

[微软关于wsl.conf的官方文档](https://learn.microsoft.com/zh-cn/windows/wsl/wsl-config#boot-settings)

## 远程访问 WSL

看一些场景是需要远程访问wsl中的docker\k3s等容器的端口，这些场景使用加hosts的方法可能不太灵活，需要搭建代理处理

如果只是需要ssh访问的话，那大可以直接开启windows的ssh服务，然后ssh链接windows后再输入wsl，嫌麻烦可以直接修改下ssh的默认终端程序

```powershell
# 安装 OpenSSH 客户端
Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0
# 安装 OpenSSH 服务器
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
# 修改默认终端
New-ItemProperty -Path "HKLM:\SOFTWARE\OpenSSH" -Name DefaultShell -Value "C:\Windows\System32\wsl.exe" -PropertyType String -Force
```
