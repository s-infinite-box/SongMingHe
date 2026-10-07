---
title: Kubernetes 1.19 升级到 1.32：常用资源 YAML 字段变动整理
description: 整理 Kubernetes 版本升级时常用资源 API、字段和行为的变化记录。
date: '2026-04-14T15:18:15+08:00'
image: img/covers/k8s-flower.svg
categories:
  - 云原生
tags:
  - Kubernetes
  - 版本升级
  - YAML
draft: false
---

## 对比范围

对比了下面这些资源，基本是一些常用的：

* configmap
* cronjob
* daemonset
* deployment
* hpa
* ingress
* job
* namespace
* persistentvolume
* persistentvolumeclaim
* secret
* service
* statefulset
* storageclass

## 资源变化情况

### 普遍修改

* `删除：metadata.clusterName<string>`
* `添加：metadata.managedFields.subresource<string>`

### Pod

* `删除：spec.ephemeralContainers.volumes.ephemeral.readOnly<boolean>`在1.31版本中删除，`ephemeralContainers`卷的只读挂载，卷本身依旧有只读选项
* `添加：`亲和性和反亲和性的软硬匹配

  > * `FIELDS.spec.affinity.podAffinity.requiredDuringSchedulingIgnoredDuringExecution.podAffinityTerm.matchLabelKeys`matchLabelKeys 是一组 Pod 标签键，用于通过计算 Pod 分布方式来选择 Pod；这是一个 Beta 字段，需要启用 MatchLabelKeysInPodTopologySpread 特性门控（默认启用）
  > * `FIELDS.spec.affinity.podAffinity.requiredDuringSchedulingIgnoredDuringExecution.namespaceSelector`对条件所适用的名字空间集合的标签查询。
  >
* `添加：lifecycle`：`postStart`和`preStop`增加字段

  > * FIELDS.spec.template.spec.containers.lifecycle.postStart.sleep 睡眠表示容器在终止之前应该睡眠的持续时间
  >
* `添加：readinessProbe/livenessProbe`/startupProbe增加字段

  > * `FIELDS.spec.template.spec.containers.livenessProbe.grpc` 指定涉及 GRPC 端口的操作。
  > * `FIELDS.spec.template.spec.containers.livenessProbe.terminationGracePeriodSeconds`表示 Pod 需要体面终止的所需的时长（以秒为单位）。
  >
* `添加：FIELDS.spec.template.spec.initContainers.restartPolicy`restartPolicy 定义 Pod 中各个容器的重新启动行为。 该字段仅适用于 Init 容器，唯一允许的值是 "Always"。 将 restartPolicy 设置为 "Always" 会产生以下效果：该 Init 容器将在退出后持续重新启动，直到所有常规容器终止。 一旦所有常规容器已完成，所有具有 restartPolicy 为 "Always" 的 Init 容器将被关闭。 这种生命期与正常的 Init 容器不同，通常被称为 "sidecar" 容器。
* `添加：FIELDS.spec.template.spec.containers.resizePolicy`容器的资源调整策略。
* `添加：FIELDS.spec.template.spec.containers.resources.claims`

> * claims 列出了此容器/POD使用的资源名称，资源名称在 spec.resourceClaims 中定义。 这是一个 Alpha 特性字段，需要启用 DynamicResourceAllocation 功能门控开启此特性。

* `添加：FIELDS.spec.template.spec.ephemeralContainers.securityContext.appArmorProfile`AppArmorProfile 定义了一个POD或容器的 Appdeck 设置。
* `添加：FIELDS.spec.template.spec.ephemeralContainers.securityContext.windowsOptions.hostProcess`HostProcess 确定容器是否应作为 “Host Process” 容器运行。Pod 的所有容器必须具有相同的有效 HostProcess 值 (不允许将 HostProcess 容器和非 HostProcess 容器混合)。此外，如果 HostProcess 为 true，那么 HostNetwork 也必须设置为 true。
* `添加：FIELDS.spec.template.spec.containers.volumeMounts.recursiveReadOnly`指定是否应递归处理只读挂载
* `添加：FIELDS.spec.template.spec.hostUsers`使用主机的用户名称空间
* `添加：FIELDS.spec.template.spec.os`指定POD中容器的操作系统。如果设置了该操作系统，一些POD和容器字段将受到限制。

### DaemonSet

* `添加：FIELDS.spec.updateStrategy.rollingUpdate.maxSurge`对于拥有可用 DaemonSet Pod 的节点而言，在更新期间可以拥有更新后的 DaemonSet Pod 的最大节点数

### Job

* `添加：FIELDS.spec.completionMode` 增加一个JOB完成的判断
* `添加：`三类执行策略
  * `FIELDS.spec.podReplacementPolicy` 指定何时创建替代的 Pod。
  * `FIELDS.spec.podFailurePolicy` 指定处理失效 Pod 的策略。特别是，它允许指定采取关联操作需要满足的一组操作和状况。
  * `FIELDS.spec.successPolicy` 描述何时可以根据某些索引的成功将任务声明为成功

### CronJob

* 修改：Version: `batch/v1beta1`==>`batch/v1`
* `添加：FIELDS.spec.timeZone`给定时间表的时区名称
* `添加：FIELDS.status.lastSuccessfulTime`上次成功完成作业的时间信息。

### HorizontalPodAutoscaler（V2修改较大）

* 修改：Version: `autoscaling/v1`==>`autoscaling/v2`
* `删除：spec.targetCPUUtilizationPercentage`字段删除，V2提供了更丰富的指标选项，不仅仅局限于 CPU 利用率
* `添加：FIELDS.spec.behavior`基于策略来扩缩POD：指定扩缩策略来限制扩缩速度。可以通过指定稳定窗口来防止抖动，可以制定绝对数量/相对数量等
* `添加：FIELDS.spec.metrics`基于指标的扩缩：Kubernetes 的container指标，不与任何 Kubernetes 对象关联、基于来自集群外部运行组件的指标，单个 Kubernetes 对象的指标，当前扩缩目标中每个 Pod 的指标， Kubernetes 已知的resource资源指标
* `添加：FIELDS.status.conditions`conditions 是此自动扩缩器扩缩其目标所需的一组条件，并指示是否满足这些条件。
* `添加：FIELDS.status.currentMetrics` 是此自动扩缩器使用的指标的最后读取状态。

### Ingress

* 修改：Version: `autoscaling/v1`==>`autoscaling/v2`
* `删除：spec.targetCPUUtilizationPercentage`字段删除，V2提供了更丰富的指标选项，不仅仅局限于 CPU 利用率
* `添加：FIELDS.spec.behavior`基于策略来扩缩POD：指定扩缩策略来限制扩缩速度。可以通过指定稳定窗口来防止抖动，可以制定绝对数量/相对数量等
* `添加：FIELDS.spec.metrics`基于指标的扩缩：Kubernetes 的container指标，不与任何 Kubernetes 对象关联、基于来自集群外部运行组件的指标，单个 Kubernetes 对象的指标，当前扩缩目标中每个 Pod 的指标， Kubernetes 已知的resource资源指标
* `添加：FIELDS.status.conditions`conditions 是此自动扩缩器扩缩其目标所需的一组条件，并指示是否满足这些条件。
* `添加：FIELDS.status.currentMetrics` 是此自动扩缩器使用的指标的最后读取状态。

### Service

* `修改：spec.ipFamily<string>`==>`spec.ipFamilies<[]string>` 有效值为 “IPv4” 和 “IPv6”。通常根据集群配置和 ipFamilyPolicy 字段自动设置
* `删除：spec.topologyKeys`
* `添加：FIELDS.spec.internalTrafficPolicy `描述节点如何分发它们在 ClusterIP 上接收到的服务流量。 如果设置为 “Local”，代理将假定 Pod 只想与在同一节点上的服务端点通信，如果没有本地端点，它将丢弃流量。 “Cluster” 默认将流量路由到所有端点（可能会根据拓扑和其他特性进行修改）。
* `添加：FIELDS.spec.loadBalancerClass` 是此 Service 所属的负载均衡器实现的类
* `添加：FIELDS.spec.ipFamilyPolicy` 表示此服务请求或要求的双栈特性
* `添加：FIELDS.spec.trafficDistribution` 提供了一种流量如何被分配到 Service 端点的偏好表达方式
* `添加：FIELDS.status.conditions`当前状态

### PersistentVolume

* 添加：`FIELDS.spec.csi.nodeExpandSecretRef` 是对包含敏感信息的 Secret 对象的引用， 从而传递到 CSI 驱动以完成 CSI NodeExpandVolume 调用。

### PersistentVolumeClaim

* `删除：spec.volumeName`
* 添加：`FIELDS.spec.volumes.image`镜像作为卷挂载到POD
* `添加：FIELDS.spec.dataSourceRef` 允许任意名字空间中的任何非核心对象作为数据源

### StatefulSet

* `添加：FIELDS.spec.minReadySeconds`新创建的 Pod 应准备就绪（其任何容器都未崩溃）的最小秒数，以使其被视为可用
* `添加：FIELDS.spec.ordinals`ordinals 控制 StatefulSet 中副本索引的编号。 默认序数行为是将索引 "0" 设置给第一个副本，对于每个额外请求的副本，该索引加一。
* `添加：FIELDS.spec.persistentVolumeClaimRetentionPolicy` 描述从 VolumeClaimTemplates 创建的持久卷申领的生命周期。
* `添加FIELDS.spec.updateStrategy.rollingUpdate.maxUnavailable` 更新期间不可用的 Pod 个数上限。取值可以是绝对数量（例如：5）或所需 Pod 的百分比（例如：10%）
