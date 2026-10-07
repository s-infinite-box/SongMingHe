---
title: K8s 网络插件 Cilium 相关技术调研总结
description: 整理 Cilium 安装、离线镜像、外部 etcd、Istio 配合、kube-proxy 替换与 Ingress 等调研笔记。
date: '2026-04-14T15:18:15+08:00'
image: img/covers/cilium.jpg
categories:
  - 云原生
tags:
  - Kubernetes
  - Cilium
  - eBPF
  - Istio
draft: false
---

<svg xmlns="http://www.w3.org/2000/svg" width="590" height="210" fill="none" viewBox="0 0 118 42" class="col-span-1 lg:col-span-1"><path fill="#141A1F" d="M23.79 14.344h-7.604l-3.818 6.725 3.8 6.656h7.62l3.8-6.656zM22.775 25.9H17.18l-2.786-4.849 2.789-4.9h5.596l2.788 4.9z"></path><path fill="#E83030" d="M14.392 21.068 17.18 25.9h5.596l2.806-4.832-2.806-4.968H17.18z"></path><path fill="#141A1F" d="M23.79 28.637h-7.604l-3.818 6.707 3.8 6.656h7.62l3.8-6.656zm-1.015 11.607H17.18l-2.786-4.849 2.789-4.9h5.596l2.788 4.9z"></path><path fill="#6B91C7" d="m14.392 35.344 2.788 4.9h5.596l2.806-4.9-2.806-4.9H17.18z"></path><path fill="#141A1F" d="M23.79 0h-7.604l-3.818 6.725 3.818 6.656h7.62l3.8-6.656zm-1.015 11.556H17.18l-2.786-4.849 2.789-4.95h5.596l2.788 4.9z"></path><path fill="#F9C31F" d="m14.392 6.723 2.788 4.833h5.596l2.806-4.833-2.806-4.967H17.18z"></path><path fill="#141A1F" d="M36.159 21.541h-7.543l-3.8 6.725 3.8 6.656h7.62l3.8-6.656zm-1.015 11.585H29.55l-2.789-4.85 2.789-4.9h5.595l2.789 4.9z"></path><path fill="#795AA5" d="m26.747 28.29 2.829 4.85h5.58l2.856-4.85-2.856-4.967h-5.58z"></path><path fill="#141A1F" d="M36.159 7.197h-7.543l-3.8 6.656 3.8 6.656h7.62l3.8-6.656zM35.144 18.77H29.55l-2.789-4.85 2.789-4.9h5.595l2.789 4.9z"></path><path fill="#F17423" d="m26.747 13.924 2.784 4.914h5.625l2.856-4.849-2.856-4.968h-5.625z"></path><path fill="#141A1F" d="M11.355 21.541H3.8L0 28.266l3.8 6.656h7.62l3.8-6.656zM10.34 33.115H4.812l-2.788-4.85 2.788-4.9h5.596l2.789 4.9z"></path><path fill="#97C639" d="m2.023 28.265 2.789 4.849h5.528l2.856-4.85-2.856-4.967H4.812z"></path><path fill="#141A1F" d="M11.355 7.197H3.8L0 13.853l3.8 6.656h7.62l3.8-6.656zM10.34 18.771H4.812l-2.788-4.85 2.788-4.9h5.596l2.789 4.9z"></path><path fill="#C9DB70" d="m2.023 13.92 2.789 4.85h5.528l2.856-4.85-2.856-4.967H4.812z"></path><path fill="#141A1F" d="M57.088 14.074c.62.004 1.239.075 1.844.213.574.124 1.06.35 1.53.587v1.838a16 16 0 0 0-1.6-.498c-.538-.125-1.024-.214-1.564-.214s-1.06.089-1.6.25c-.54.16-.99.462-1.443.888-.417.427-.748.961-1.025 1.637-.243.676-.364 1.512-.364 2.525 0 .7.086 1.398.296 2.027.187.585.482 1.129.869 1.6.383.463.869.801 1.391 1.05q.861.372 1.982.372c.538 0 1.059-.035 1.651-.16q.815-.2 1.6-.498v1.85c-.156.088-.364.213-.608.302-.244.09-.539.16-.869.25-.296.088-.608.124-.99.16l-1.026.088a7.3 7.3 0 0 1-2.556-.427 6.9 6.9 0 0 1-2.105-1.262 6.15 6.15 0 0 1-1.391-2.188c-.342-.889-.539-1.887-.539-3.112 0-.89.087-1.69.296-2.4a6.2 6.2 0 0 1 .749-1.887c.33-.536.683-1.014 1.112-1.398a6.4 6.4 0 0 1 1.355-.925c.486-.249.991-.426 1.478-.55l1.53-.143zm6.904-2.775v-2.49h2.163v2.49zM64.026 28V14.447h2.163v13.564zm6.625.011V7.35h2.164v20.661zM77.23 11.3v-2.49h2.163v2.49zM77.264 28V14.447h2.164v13.564zm11.784.349a8 8 0 0 1-1.844-.213 6.4 6.4 0 0 1-1.443-.622c-.416-.303-.782-.587-1.059-1.014a3.9 3.9 0 0 1-.683-1.262 8 8 0 0 1-.296-1.138l-.087-1.352v-8.287H85.8v8.287c0 .766.087 1.398.296 1.888.209.587.574 1.013 1.06 1.35.484.339 1.147.5 1.894.5.818 0 1.478-.16 1.981-.552.488-.372.87-.836 1.06-1.476.156-.462.243-1.048.243-1.724v-8.293h2.164v8.324q0 .634-.087 1.262a4.3 4.3 0 0 1-.243 1.085c-.156.462-.417.889-.684 1.299-.296.373-.66.699-1.059 1.013-.416.303-.904.499-1.478.676a7.1 7.1 0 0 1-1.895.249zm20.31-.35h-2.164v-8.725a5.4 5.4 0 0 0-.208-1.512c-.122-.427-.296-.766-.539-1.014a2.4 2.4 0 0 0-.869-.587c-.342-.124-.683-.16-1.112-.16a3.76 3.76 0 0 0-2.105.623 6.4 6.4 0 0 0-1.685 1.76v9.641H98.52V14.448h1.685l.417 1.887h.034l.783-.89c.296-.248.608-.498.939-.698a3.7 3.7 0 0 1 1.148-.463c.417-.124.869-.16 1.367-.16.99 0 1.808.25 2.468.7.661.498 1.148 1.138 1.531 1.974h.034c.574-.836 1.27-1.512 2.016-1.974.746-.463 1.651-.7 2.626-.7.452 0 .939.09 1.478.214.538.125.991.373 1.443.699s.782.836 1.059 1.476c.296.622.452 1.423.452 2.437v9.089h-2.086v-8.733a5.5 5.5 0 0 0-.209-1.512c-.122-.426-.296-.765-.539-1.013a2.44 2.44 0 0 0-.868-.587c-.342-.125-.684-.16-1.113-.16-.782 0-1.478.213-2.104.622a7.1 7.1 0 0 0-1.722 1.761z"></path></svg>

<br>

## 安装参考

[参考文档](https://docs.cilium.io/en/v1.12/gettingstarted/k8s-install-advanced/)

### CLI 命令行安装

```
# 获取最新CLI文件
CILIUM_CLI_VERSION=$(wget -qO- -t1 -T2 "https://api.github.com/repos/cilium/cilium-cli/releases/latest" | jq -r '.tag_name')
while [ -z "$CILIUM_CLI_VERSION" ]; do
  CILIUM_CLI_VERSION=$(wget -qO- -t1 -T2 "https://api.github.com/repos/cilium/cilium-cli/releases/latest" | jq -r '.tag_name')
done
CLI_ARCH=amd64
curl -L --fail --remote-name-all https://github.com/cilium/cilium-cli/releases/download/${CILIUM_CLI_VERSION}/cilium-linux-${CLI_ARCH}.tar.gz
tar xzvfC cilium-linux-${CLI_ARCH}.tar.gz /usr/local/bin && rm -rf cilium-linux-${CLI_ARCH}.tar.gz
# 使用内网镜像则在这里参考使用内网镜像处理
# 安装
cilium install --set kubeProxyReplacement=false --set hubble.relay.enabled=true --set hubble.ui.enabled=true
# 参数说明：
# kubeProxyReplacement=false 关闭替换kubeProxy，二进制安装kubeproxy不能被检测到，cilium会默认开启替换kube-proxy模式
# hubble.relay.enabled=true 开启hubble，用于流量监控
# hubble.ui.enabled=true 开启hubble的web服务
# 查看安装状态
cilium status
kubectl get po -Aw
```

### Helm 安装 Cilium

**安装 Helm：**

```
latest_release_url="https://get.helm.sh/helm-latest-version"
latest_release_response=""
latest_release_response=$( curl -L --silent --show-error --fail "$latest_release_url" 2>&1 || true )
TAG=$( echo "$latest_release_response" | grep '^v[0-9]' )
ARCH=amd64
OS=$(echo `uname`|tr '[:upper:]' '[:lower:]')
HELM_DIST="helm-$TAG-$OS-$ARCH.tar.gz"
DOWNLOAD_URL="https://get.helm.sh/$HELM_DIST"
wget $DOWNLOAD_URL
```

**添加 Helm 仓库：**

```
helm repo add cilium https://helm.cilium.io/
```

**安装 Cilium：** 参数配置及格式同 CLI 模式。

```
helm install cilium cilium/cilium --namespace kube-system --set kubeProxyReplacement=false --set hubble.relay.enabled=true --set hubble.ui.enabled=true
```

### 内网离线安装镜像处理

目前cilium的CLI工具没有提供统一的离线安装参数，但是可以在安装时指定组件镜像
默认镜像源：quay.io，目前在国内可以正常下载，无需梯子

#### CRI 镜像仓库代理

在CRI（containerd/docker）替换镜像仓库代理：quay.io/cilium ==》 harbor.my.cn/devops(替换为自己的内网镜像仓库地址)

- containerd，参考文档：[https://github.com/containerd/containerd/blob/main/docs/hosts.md#cri](https://github.com/containerd/containerd/blob/main/docs/hosts.md#cri)
- 查看版本：ctr -v

  - 如果是1.x版本可以使用方式一配置较简单，但是会有waring报警
  - 方式二是官方建议配置方式，稍微麻烦一点
- 方式一，适用1.x版本：

  配置文件 /etc/containerd/config.toml  添加，

  ```toml
  [plugins."io.containerd.grpc.v1.cri".registry.mirrors]
  [plugins."io.containerd.grpc.v1.cri".registry.mirrors."'quay.io/cilium'"] # 代理仓库配置
   endpoint = ["'https://harbor.my.cn/devops'"]
  [plugins."io.containerd.grpc.v1.cri".registry.configs] # 可选：关闭tls校验，可以使用http，便于本地测试
  [plugins."io.containerd.grpc.v1.cri".registry.configs."'harbor.my.cn/devops'".tls]
   insecure_skip_verify = true
  ```
- 方式二，适用2.x版本：

  1. /etc/containerd/config.toml  添加

     ```toml
     [plugins."io.containerd.cri.v1.images".registry]
     config_path = "/etc/containerd/certs.d"
     ```

  2. config\_path内具体路径，registry\_host\_name为代理的repo地址：域名或端口号，hosts为具体配置内容
     `/etc/containerd/certs.d/[registry_host_name|IP address][:port]/hosts.toml`

  3. hosts.toml配置

     ```toml
     # server指定此 Registry Host 命名空间的默认服务器。
     #指定 （s） 后，将按列出的顺序首先尝试主机。 如果 （s） 都已尝试，则 将用作回退。hosthostserver
     #如果未指定，则将自动使用映像的注册表主机命名空间。server
     server = "https://registry-1.docker.io"

     [host."https://mirror.registry"]
     # 是用于指定主机操作的可选设置 能够执行。仅包含适用的值。
     capabilities =  ["pull", "resolve", "push"]
     # ca（证书颁发机构认证）可以设置为路径或 paths 每个路径都指向一个 CA 文件，用于对 Registry 进行身份验证 Namespace。
     ca = "/etc/certs/mirror.pem"
     # skip_verify跳过对注册表证书链的验证，并且 host name （设置为 .这应该仅用于测试或 与其他验证连接的方法结合使用。（默认为true)
     skip_verify = false
     [host."https://mirror.registry".header]
     x-custom-2 = ["value1", "value2"]

     [host."https://non-compliant-mirror.registry/v2/upstream"]
     capabilities = ["pull"]
     # override_path用于指示已定义主机的 API 根端点 在 URL 路径中，而不是按 API 规范。这可以与 缺少前缀的不合规 OCI 注册表。 （默认为/false)
     override_path = true
     ```

#### 通过 Helm 指定组件镜像

helm/cilium 创建时通过参数指定组件的镜像，[参考文档](https://docs.cilium.io/en/stable/helm-reference/#id1)

基本使用镜像 注意修改镜像版本信息，可以直接helm拉chart下来，然后自己看value.yaml

image: [quay.io/cilium/cilium:v1.16.4@sha256:d55ec38938854133e06739b1af237932b9c4dd4e75e9b7b2ca3acc72540a44bf](http://quay.io/cilium/cilium:v1.16.4@sha256:d55ec38938854133e06739b1af237932b9c4dd4e75e9b7b2ca3acc72540a44bf)

envoy.image: [quay.io/cilium/cilium-envoy:v1.30.7-1731393961-97edc2815e2c6a174d3d12e71731d54f5d32ea16@sha256:0287b36f70cfbdf54f894160082f4f94d1ee1fb10389f3a95baa6c8e448586ed](http://quay.io/cilium/cilium-envoy:v1.30.7-1731393961-97edc2815e2c6a174d3d12e71731d54f5d32ea16@sha256:0287b36f70cfbdf54f894160082f4f94d1ee1fb10389f3a95baa6c8e448586ed)

operator.image: [quay.io/cilium/operator-generic:v1.16.4@sha256:c55a7cbe19fe0b6b28903a085334edb586a3201add9db56d2122c8485f7a51c5](http://quay.io/cilium/operator-generic:v1.16.4@sha256:c55a7cbe19fe0b6b28903a085334edb586a3201add9db56d2122c8485f7a51c5)

hubble.relay.image: [quay.io/cilium/hubble-relay:v1.16.4@sha256:fb2c7d127a1c809f6ba23c05973f3dd00f6b6a48e4aee2da95db925a4f0351d2](http://quay.io/cilium/hubble-relay:v1.16.4@sha256:fb2c7d127a1c809f6ba23c05973f3dd00f6b6a48e4aee2da95db925a4f0351d2)

hubble.ui.frontend.image: [quay.io/cilium/hubble-ui-backend:v0.13.1@sha256:0e0eed917653441fded4e7cdb096b7be6a3bddded5a2dd10812a27b1fc6ed95b](http://quay.io/cilium/hubble-ui-backend:v0.13.1@sha256:0e0eed917653441fded4e7cdb096b7be6a3bddded5a2dd10812a27b1fc6ed95b)

#### 镜像参数参考列表

helm/cilium 安装设计镜像参数参考列表：

<table class="relative-table wrapped confluenceTable" style="width: 190.636%;"><colgroup><col style="width: 9.01714%;"><col style="width: 12.669%;"><col style="width: 2.75023%;"><col style="width: 75.5186%;"></colgroup><tbody><tr><td colspan="1" rowspan="1" style="vertical-align: top;" class="confluenceTd"><p>image</p></td><td colspan="1" rowspan="1" style="vertical-align: top;" class="confluenceTd"><p>Agent container image.</p></td><td colspan="1" rowspan="1" style="vertical-align: top;" class="confluenceTd"><p>object</p></td><td colspan="1" rowspan="1" style="vertical-align: top;" class="confluenceTd"><p><code>{"digest":"","override":null,"pullPolicy":"IfNotPresent","repository":"quay.io/cilium/cilium","tag":"v1.16.5","useDigest":false}</code></p></td></tr><tr><td colspan="1" rowspan="1" style="vertical-align: top;" class="confluenceTd"><p>imagePullSecrets</p></td><td colspan="1" rowspan="1" style="vertical-align: top;" class="confluenceTd"><p>Configure image pull secrets for pulling container images</p></td><td colspan="1" rowspan="1" style="vertical-align: top;" class="confluenceTd"><p>list</p></td><td colspan="1" rowspan="1" style="vertical-align: top;" class="confluenceTd"><p><code>[]</code></p></td></tr><tr><td colspan="1" rowspan="1" style="vertical-align: top;" class="confluenceTd"><p>preflight.image</p></td><td colspan="1" rowspan="1" style="vertical-align: top;" class="confluenceTd"><p>Cilium pre-flight image.</p></td><td colspan="1" rowspan="1" style="vertical-align: top;" class="confluenceTd"><p>object</p></td><td colspan="1" rowspan="1" style="vertical-align: top;" class="confluenceTd"><p><code>{"digest":"","override":null,"pullPolicy":"IfNotPresent","repository":"quay.io/cilium/cilium","tag":"v1.16.5","useDigest":false}</code></p></td></tr><tr><td colspan="1" rowspan="1" style="vertical-align: top;" class="confluenceTd"><p>certgen</p></td><td colspan="1" rowspan="1" style="vertical-align: top;" class="confluenceTd"><p>Configure certificate generation for Hubble integration. If hubble.tls.auto.method=cronJob, these values are used for the Kubernetes CronJob which will be scheduled regularly to (re)generate any certificates not provided manually.</p></td><td colspan="1" rowspan="1" style="vertical-align: top;" class="confluenceTd"><p>object</p></td><td colspan="1" rowspan="1" style="vertical-align: top;" class="confluenceTd"><p><code>{"affinity":{},"annotations":{"cronJob":{},"job":{}},"extraVolumeMounts":[],"extraVolumes":[],"image":{"digest":"sha256:169d93fd8f2f9009db3b9d5ccd37c2b753d0989e1e7cd8fe79f9160c459eef4f","override":null,"pullPolicy":"IfNotPresent","repository":"quay.io/cilium/certgen","tag":"v0.2.0","useDigest":true},"podLabels":{},"tolerations":[],"ttlSecondsAfterFinished":1800}</code></p></td></tr><tr><td colspan="1" rowspan="1" style="vertical-align: top;" class="confluenceTd"><p>clustermesh.apiserver.image</p></td><td colspan="1" rowspan="1" style="vertical-align: top;" class="confluenceTd"><p>Clustermesh API server image.</p></td><td colspan="1" rowspan="1" style="vertical-align: top;" class="confluenceTd"><p>object</p></td><td colspan="1" rowspan="1" style="vertical-align: top;" class="confluenceTd"><p><code>{"digest":"","override":null,"pullPolicy":"IfNotPresent","repository":"quay.io/cilium/clustermesh-apiserver","tag":"v1.16.5","useDigest":false}</code></p></td></tr><tr><td colspan="1" rowspan="1" style="vertical-align: top;" class="confluenceTd"><p>envoy.image</p></td><td colspan="1" rowspan="1" style="vertical-align: top;" class="confluenceTd"><p>Envoy container image.</p></td><td colspan="1" rowspan="1" style="vertical-align: top;" class="confluenceTd"><p>object</p></td><td colspan="1" rowspan="1" style="vertical-align: top;" class="confluenceTd"><p><code>{"digest":"sha256:709c08ade3d17d52da4ca2af33f431360ec26268d288d9a6cd1d98acc9a1dced","override":null,"pullPolicy":"IfNotPresent","repository":"quay.io/cilium/cilium-envoy","tag":"v1.30.8-1733837904-eaae5aca0fb988583e5617170a65ac5aa51c0aa8","useDigest":true}</code></p></td></tr><tr><td colspan="1" rowspan="1" style="vertical-align: top;" class="confluenceTd"><p>hubble.relay.image</p></td><td colspan="1" rowspan="1" style="vertical-align: top;" class="confluenceTd"><p>Hubble-relay container image.</p></td><td colspan="1" rowspan="1" style="vertical-align: top;" class="confluenceTd"><p>object</p></td><td colspan="1" rowspan="1" style="vertical-align: top;" class="confluenceTd"><p><code>{"digest":"","override":null,"pullPolicy":"IfNotPresent","repository":"quay.io/cilium/hubble-relay","tag":"v1.16.5","useDigest":false}</code></p></td></tr><tr><td colspan="1" rowspan="1" style="vertical-align: top;" class="confluenceTd"><p>hubble.ui.backend.image</p></td><td colspan="1" rowspan="1" style="vertical-align: top;" class="confluenceTd"><p>Hubble-ui backend image.</p></td><td colspan="1" rowspan="1" style="vertical-align: top;" class="confluenceTd"><p>object</p></td><td colspan="1" rowspan="1" style="vertical-align: top;" class="confluenceTd"><p><code>{"digest":"sha256:0e0eed917653441fded4e7cdb096b7be6a3bddded5a2dd10812a27b1fc6ed95b","override":null,"pullPolicy":"IfNotPresent","repository":"quay.io/cilium/hubble-ui-backend","tag":"v0.13.1","useDigest":true}</code></p></td></tr><tr><td colspan="1" rowspan="1" style="vertical-align: top;" class="confluenceTd"><p>hubble.ui.frontend.image</p></td><td colspan="1" rowspan="1" style="vertical-align: top;" class="confluenceTd"><p>Hubble-ui frontend image.</p></td><td colspan="1" rowspan="1" style="vertical-align: top;" class="confluenceTd"><p>object</p></td><td colspan="1" rowspan="1" style="vertical-align: top;" class="confluenceTd"><p><code>{"digest":"sha256:e2e9313eb7caf64b0061d9da0efbdad59c6c461f6ca1752768942bfeda0796c6","override":null,"pullPolicy":"IfNotPresent","repository":"quay.io/cilium/hubble-ui","tag":"v0.13.1","useDigest":true}</code></p></td></tr><tr><td colspan="1" rowspan="1" style="vertical-align: top;" class="confluenceTd"><p>nodeinit.image</p></td><td colspan="1" rowspan="1" style="vertical-align: top;" class="confluenceTd"><p>node-init image.</p></td><td colspan="1" rowspan="1" style="vertical-align: top;" class="confluenceTd"><p>object</p></td><td colspan="1" rowspan="1" style="vertical-align: top;" class="confluenceTd"><p><code>{"digest":"sha256:8d7b41c4ca45860254b3c19e20210462ef89479bb6331d6760c4e609d651b29c","override":null,"pullPolicy":"IfNotPresent","repository":"quay.io/cilium/startup-script","tag":"c54c7edeab7fde4da68e59acd319ab24af242c3f","useDigest":true}</code></p></td></tr><tr><td colspan="1" rowspan="1" style="vertical-align: top;" class="confluenceTd"><p>operator.image</p></td><td colspan="1" rowspan="1" style="vertical-align: top;" class="confluenceTd"><p>cilium-operator image.</p></td><td colspan="1" rowspan="1" style="vertical-align: top;" class="confluenceTd"><p>object</p></td><td colspan="1" rowspan="1" style="vertical-align: top;" class="confluenceTd"><p><code>{"alibabacloudDigest":"","awsDigest":"","azureDigest":"","genericDigest":"","override":null,"pullPolicy":"IfNotPresent","repository":"quay.io/cilium/operator","suffix":"","tag":"v1.16.5","useDigest":false}</code></p></td></tr><tr><td colspan="1" rowspan="1" style="vertical-align: top;" class="confluenceTd"><p>preflight.image</p></td><td colspan="1" rowspan="1" style="vertical-align: top;" class="confluenceTd"><p>Cilium pre-flight image.</p></td><td colspan="1" rowspan="1" style="vertical-align: top;" class="confluenceTd"><p>object</p></td><td colspan="1" rowspan="1" style="vertical-align: top;" class="confluenceTd"><p><code>{"digest":"","override":null,"pullPolicy":"IfNotPresent","repository":"quay.io/cilium/cilium","tag":"v1.16.5","useDigest":false}</code></p></td></tr></tbody></table>

## Cilium 与 Kata 配合使用

暂未详细调研。

参考文档：[https://docs.cilium.io/en/stable/network/kubernetes/kata/#kata-containers-with-cilium](https://docs.cilium.io/en/stable/network/kubernetes/kata/#kata-containers-with-cilium)

## 使用外部 etcd 存储 Cilium 元数据

### 指定外部 etcd 端点

helm install cilium cilium/cilium \--version 1.14.4
\--namespace kube-system
\--set etcd.enabled=true
\--set "etcd.endpoints\[0\]\=[http://etcd-endpoint1:2379](http://etcd-endpoint1:2379/)"
\--set "etcd.endpoints\[1\]\=[http://etcd-endpoint2:2379](http://etcd-endpoint2:2379/)"
\--set "etcd.endpoints\[2\]\=[http://etcd-endpoint3:2379](http://etcd-endpoint3:2379/)"
\--set identityAllocationMode=kvstore

### 创建 TLS 证书 Secret

使用根证书权限、客户端密钥和 etcd 证书创建一个secret

kubectl create secret generic \-n kube-system cilium-etcd-secrets
\--from-file=etcd-client-ca.crt=ca.crt
\--from-file=etcd-client.key=client.key
\--from-file=etcd-client.crt=client.crt

### 启用 SSL

为 etcd 启用 SSL， etcd 端点 URL 修改为 https

helm install cilium cilium/cilium \--version 1.14.4
\--namespace kube-system
\--set etcd.enabled=true
\--set etcd.ssl=true
\--set "etcd.endpoints\[0\]\=[https://etcd-endpoint1:2379](https://etcd-endpoint1:2379/)"
\--set "etcd.endpoints\[1\]\=[https://etcd-endpoint2:2379](https://etcd-endpoint2:2379/)"
\--set "etcd.endpoints\[2\]\=[https://etcd-endpoint3:2379](https://etcd-endpoint3:2379/)"

## 与 Istio 共同使用

[参考文档](https://docs.cilium.io/en/stable/network/servicemesh/istio/#gsg-istio)

### Cilium 适配配置

istio会将POD的流量通过iptable代理到边车容器或者节点代理cilium在开启kubeProxyReplacement时，可能会中断相关代理流量

```
helm upgrade cilium cilium/cilium --version 1.16.4 \
   --namespace kube-system \
   --reuse-values \
   --set socketLB.hostNamespaceOnly true \
   --set cni.exclusive false
```

### Istio 相关配置

[参考文档](https://docs.cilium.io/en/stable/network/servicemesh/istio/#istio-configuration)

- Sidecar: 通过在 Istio 的 PeerAuthentication 下配置 mTLS.mode = DISABLE，为希望用 Cilium L7 策略管理的工作负载禁用 Istio mTLS，Istio [PeerAuthentication](https://istio.io/latest/docs/reference/config/security/peer_authentication/#PeerAuthentication).
- Ambient: 通过从名称空间中移除 Istio.io/dataplane-mode 标签，或者在你希望用 Cilium l7 管理的 pods 上标注 “禁用”，从而从 Istio 环境中移除你希望用 Cilium l7 管理的工作负载 ambient.Istio.io/redirection

## 替换 kube-proxy

[参考文档](https://docs.cilium.io/en/stable/network/kubernetes/kubeproxy-free/#kube-proxy-hybrid-modes)

### 安装与状态检查

安装cilium 开启替换kube-proxy特性：

```bash
helm install cilium cilium/cilium --set kubeProxyReplacement=true --namespace kube-system cilium install --set kubeProxyReplacement=true --set=ipam.operator.clusterPoolIPv4PodCIDRList="10.244.0.0/16"
```

查看cilium状态 KubeProxyReplacement: Strict：

```bash
kubectl -n kube-system exec ds/cilium -- cilium status | grep KubeProxyReplacement
```

状态详情：

```bash
kubectl -n kube-system exec ds/cilium -- cilium status --verbose
```

### 查看转发规则

idtable查看是否有kube-proxy转发的service：

```bash
iptables-save | grep KUBE-SVC
```

bpf转发的service 列表：

```bash
kubectl -n kube-system exec ds/cilium -- cilium service list
```

## Cilium Ingress

[参考文档](https://docs.cilium.io/en/v1.14/network/servicemesh/ingress/)

前置条件：需开启kube-proxy替换

### Helm 安装参数

```
helm upgrade cilium cilium/cilium --version 1.16.4 \
    --namespace kube-system \
    --reuse-values \
    --set ingressController.enabled=true \
    --set ingressController.loadbalancerMode=dedicated

helm upgrade cilium cilium/cilium \
    --namespace kube-system \
    --reuse-values \
    --set ingressController.enabled=true \
    --set ingressController.loadbalancerMode=shared
```

### 升级与配置

cilium upgrade 会覆盖之前的参数 注意保存之前的安装命令

`cilium upgrade --version 1.14.17 \ --set kubeProxyReplacement=true \ --set ingressController.enabled=true \   --set ingressController.loadbalancerMode=dedicated`

通过 `kube-system / cilium-config`（configmap），配置ingressclass的Name，tls开启等

## 故障排查

注意看agent启动日志，可以看到agent的所有参数

### 无法识别路由设备

```text
failed to start: daemon creation failed: failed to detect devices: unable to determine direct routing device. Use --direct-routing-device to specify it\\nfailed to stop: unable to find controller ipcache-inject-labels
```

在  kube-system / cilium-config （configmap）指定主网卡

```
direct-routing-device: "eth0"
devices: "eth0
```

## 其他参考文档

- [agent启动参数参考](https://docs.cilium.io/en/stable/cmdref/cilium-agent/#cilium-agent)

- [helm安装参数参考](https://docs.cilium.io/en/stable/helm-reference/)

- [元数据KV存储参考](https://docs.cilium.io/en/stable/kvstore/)

## 内核情况整理

### CentOS 内核升级

主要考虑centos内核升级

[el官方内核库](http://mirrors.coreix.net/elrepo-archive-archive/kernel/el7/x86_64/RPMS/)

kernel-ml 中的ml是英文【 mainline stable 】的缩写，是最新的稳定主线版本。

- 目前较新的版本：5.4.278

kernel-lt 中的lt是英文【 long term support 】的缩写，是长期支持版本。

- 6.1.12
- 6.6.9

### Cilium 功能对应内核版本

<table class="wrapped confluenceTable"><colgroup><col style="width: 54.0pt;"> <col style="width: 145.5pt;"> <col style="width: 100.25pt;"> <col style="width: 296.25pt;"></colgroup><tbody><tr><td class="confluenceTd"><span class="font0">功能</span></td><td class="confluenceTd"><span class="font0">说明</span></td><td class="confluenceTd"><span class="font0">建议内核版本</span></td><td class="confluenceTd"><br></td></tr><tr><td class="confluenceTd"><span class="font0">cilium</span></td><td class="confluenceTd"><span class="font0">基础ebpf功能</span></td><td class="confluenceTd">4.15</td><td class="confluenceTd"><br></td></tr><tr><td class="confluenceTd"><span class="font0">replace kube-proxy</span></td><td class="confluenceTd">替换kube-proxy</td><td class="confluenceTd">v4.19.57<br>v5.1.16<br>v5.2.0<br>以上版本<br>---<br>v5.3<br>v5.8<br>以上性能更好</td><td class="confluenceTd"><a class="external-link" href="https://docs.cilium.io/en/stable/network/kubernetes/kubeproxy-free/#kubernetes-without-kube-proxy" rel="nofollow">Kubernetes Without kube-proxy</a></td></tr><tr><td class="confluenceTd"><span class="font0">ingress</span></td><td class="confluenceTd">需开启kube-proxy替换</td><td style="text-align: center;" class="confluenceTd">-</td><td class="confluenceTd"><a class="external-link" href="https://docs.cilium.io/en/stable/network/servicemesh/ingress/" rel="nofollow">Kubernetes Ingress Support</a></td></tr><tr><td class="confluenceTd">Gateway API</td><td class="confluenceTd">需开启kube-proxy替换</td><td style="text-align: center;" class="confluenceTd">-</td><td class="confluenceTd"><a class="external-link" href="https://docs.cilium.io/en/stable/network/servicemesh/gateway-api/gateway-api/" rel="nofollow">Gateway API Support</a></td></tr><tr><td class="confluenceTd">7层流量处理</td><td class="confluenceTd">需开启kube-proxy替换</td><td style="text-align: center;" class="confluenceTd">-</td><td class="confluenceTd"><a class="external-link" href="https://docs.cilium.io/en/stable/network/servicemesh/envoy-circuit-breaker/#l7-circuit-breaking" rel="nofollow">熔断</a></td></tr><tr><td class="confluenceTd"><span class="font0">IP透传</span></td><td class="confluenceTd"><br></td><td style="text-align: center;" class="confluenceTd">-</td><td class="confluenceTd"><br></td></tr><tr><td class="confluenceTd">node-ipam</td><td class="confluenceTd"><br></td><td style="text-align: center;" class="confluenceTd">-</td><td class="confluenceTd"><br></td></tr><tr><td class="confluenceTd">整合istio</td><td class="confluenceTd"><br></td><td style="text-align: center;" class="confluenceTd">-</td><td class="confluenceTd"><a class="external-link" href="https://docs.cilium.io/en/stable/network/servicemesh/istio/" rel="nofollow">Integration with Istio</a></td></tr></tbody></table>
