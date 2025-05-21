# vlight 虚拟晶光灯应用设计文档 (v0.4.0)

## 一、项目简介

**vlight** 是一个使用 Python 编写的可配置式 MQTT 虚拟晶光灯系统，支持 Home Assistant 的自动发现 (MQTT Discovery)，可以模拟多台灯光设备。

它有如下功能：

* 多台虚拟晶光灯创建（数量可配置）
* 支持 MQTT + Home Assistant Discovery 协议
* 支持独立设备状态管理：开/关、亮度、RGB、色温
* 状态持久化：重启后保持最后状态
* 支持随机状态模拟切换，可配置打开或关闭
* 支持 pip install 安装，使用 CLI 命令 `vlight` 启动

---

## 二、目录结构

```
vlight_v4/
├── vlight/                 应用核心源码
│   ├── __init__.py        
│   ├── main.py            全局进入点
│   ├── config.py          配置文件读取
│   ├── logger.py          日志初始化
│   ├── mqtt_client.py     MQTT 造成器，初始化所有灯设备
│   ├── light_device.py    灯设备实体，包括状态和功能
│   └── state_store.py     将灯的状态持久化 JSON 文件
├── configuration.yaml     用户配置文件
├── setup.py               pip install 设置文件
├── requirements.txt       依赖列表
└── vlight_v4_package.zip  打包成果
```

---

## 三、核心模块

### 1. `light_device.py`

* 设备实体类

  * `self.state` 保存灯的开关、亮度、色温、RGB 状态
  * 接收 Home Assistant 发来的命令 topic，执行状态更新
  * 通过 `publish_state()` 发布当前状态
  * 重启后从 JSON 状态文件恢复

### 2. `mqtt_client.py`

* 初始化 MQTT 连接
* 初始化多个 `LightDevice`
* 每个 device 会:

  * 发送 discovery 描述 topic
  * 订阅 set topic，处理接收命令

### 3. `state_store.py`

* 使用 `~/.vlight/state/` 路径保存灯的名为 light-xxx.json 文件
* 提供 `save_state()` / `load_state()` 两个方法

### 4. 随机状态模拟

* 如果 `simulate_behavior: true` ，则每台灯会自动随机切换（速度 10-30s），包括:

  * 开/关
  * 亮度
  * 色温
  * RGB

---

## 四、MQTT 协议配置

### 1. discovery topic

```text
Topic:
  homeassistant/light/light-001/config
Payload:
{
  "name": "Virtual Light 001",
  "unique_id": "light-001",
  "command_topic": "home/vlight/light-001/set",
  "state_topic": "home/vlight/light-001/state",
  "schema": "json",
  "brightness": true,
  "rgb": true,
  "color_temp": true
}
```

### 2. 接收 topic

```text
Topic: home/vlight/light-001/set
Payload:
{
  "state": "ON",
  "brightness": 150,
  "rgb_color": [0,255,128]
}
```

### 3. 状态发布 topic

```text
Topic: home/vlight/light-001/state
Payload:
{
  "state": "ON",
  "brightness": 150,
  "color_temp": 250,
  "rgb_color": [0,255,128]
}
```

---

## 五、安装和启动

```bash
unzip vlight_v4_package.zip
cd vlight_v4
python3 -m venv venv
source venv/bin/activate
pip install .
vlight
```

---

## 六、配置文件格式 (configuration.yaml)

```yaml
mqtt:
  host: "127.0.0.1"
  port: 1883
  username: ""
  password: ""
  base_topic: "home/vlight"
  discovery_prefix: "homeassistant"

lights:
  count: 2
  simulate_behavior: true
  default_state:
    state: "OFF"
    brightness: 128
    color_temp: 250
    rgb_color: [255, 255, 255]
  definitions:
    - did: "light-001"
      pid: "V1"
    - did: "light-002"
      pid: "V2"

logging:
  level: "info"
  file: "./logs/vlight.log"
```

---

## 七、后续拟增能力

| 功能           | 说明                           |
| ------------ | ---------------------------- |
| 后台服务化        | 支持 systemd 或 runit 形式进程实现长运行 |
| Web UI       | 给虚拟灯设备加上简单前端可视化界面            |
| 独立 MQTT auth | 支持用户名、密码、TLS 配置              |
| 与真实设备进行比对    | 重环真实灯接口行为，帮助模拟测试             |

---

如需要进一步实现上面功能，我可以进行代码实现或打包新版本 v0.5+
