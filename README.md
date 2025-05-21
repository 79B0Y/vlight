# vlight 虚拟灯光应用设计文档 (v0.4.3)

## 一、项目简介

**vlight** 是一个使用 Python 编写的可配置式 MQTT 虚拟灯光系统，支持 Home Assistant 的自动发现 (MQTT Discovery)，可以模拟多台灯光设备。

它有如下功能：

* 多台虚拟灯光创建（数量可配置）
* 支持 MQTT + Home Assistant Discovery 协议（符合 iSG 扩展格式）
* 支持独立设备状态管理：开/关、亮度、RGB、色温
* 状态持久化：重启后保持最后状态
* 支持随机状态模拟切换，可配置打开或关闭
* ✅ 从 v0.4.3 开始，Discovery Payload 中增加 `device` 信息，使设备可在 HA 中显示为“设备页”
* 支持 pip install 安装，使用 CLI 命令 `vlight` 启动

---

## 二、目录结构

```
vlight_v043/
├── vlight/                 应用核心源码
│   ├── __init__.py        
│   ├── main.py            全局进入点
│   ├── config.py          配置文件读取
│   ├── logger.py          日志初始化
│   ├── mqtt_client.py     MQTT 管理器，初始化所有灯设备
│   ├── light_device.py    灯设备实体，包括状态和功能
│   └── state_store.py     将灯的状态持久化 JSON 文件
├── configuration.yaml     用户配置文件
├── setup.py               pip 安装设置文件
├── requirements.txt       依赖列表
└── vlight_v043_full_package.zip  打包成果
```

---

## 三、核心模块

### 1. `light_device.py`

* 设备实体类，支持多个子指令 topic 控制：

  * `/switch` 控制开关
  * `/brightness` 控制亮度
  * `/rgb` 控制 RGB 颜色
  * `/colortemp` 控制色温
* `self.state` 保存设备状态，并通过 `status` topic 发布
* 支持 `availability_topic` 表示设备在线状态（发布 `online`）
* ✅ 在 discovery payload 中加入 `device` 字段

### 2. `mqtt_client.py`

* 初始化 MQTT 连接
* 初始化多个 `LightDevice`
* 每个 device 会:

  * 发布 discovery 描述 topic
  * 订阅各功能控制 topic
  * 接收指令后更新状态并发布反馈

### 3. `state_store.py`

* 使用 `~/.vlight/state/` 路径保存每盏灯的 JSON 状态文件
* 重启后自动恢复最近状态

### 4. 随机状态模拟

* 如果 `simulate_behavior: true`，每盏灯每隔 10\~30 秒随机变化状态：

  * 开/关
  * 亮度
  * 色温
  * RGB

---

## 四、MQTT 协议配置（支持 iSG 结构）

### 1. Discovery Topic

```text
Topic:
  homeassistant/light/<pid>/<did>/config
Payload:
{
  "name": "light-001",
  "unique_id": "light-001",
  "availability_topic": "home/vlight/light-001/availability",
  "state_topic": "home/vlight/light-001/status",
  "command_topic": "home/vlight/light-001/switch",
  "brightness_command_topic": "home/vlight/light-001/brightness",
  "rgb_command_topic": "home/vlight/light-001/rgb",
  "color_temp_command_topic": "home/vlight/light-001/colortemp",
  "brightness": true,
  "rgb": true,
  "color_temp": true,
  "schema": "json",
  "device": {
    "identifiers": ["vlight-hub"],
    "name": "vLight 虚拟灯控制器",
    "manufacturer": "LinknLink",
    "model": "vlight-sim",
    "sw_version": "0.4.3"
  }
}
```

### 2. 状态 Topic

```text
Topic: home/vlight/light-001/status
Payload:
{
  "state": "ON",
  "brightness": 150,
  "color_temp": 250,
  "rgb_color": [0,255,128]
}
```

### 3. 控制 Topics

```text
home/vlight/light-001/switch → "1" / "0"
home/vlight/light-001/brightness → 0~255
home/vlight/light-001/rgb → "255,0,0"
home/vlight/light-001/colortemp → 153~500
```

### 4. Availability Topic

```text
home/vlight/light-001/availability → "online"
```

---

## 五、安装与使用

### 安装步骤

```bash
unzip vlight_v043_full_package.zip
cd vlight_v043
python3 -m venv venv
source venv/bin/activate
pip install .
```

### 启动程序

```bash
vlight
```

程序将：

* 读取配置
* 启动所有设备并发布 discovery 信息
* 与 MQTT broker 建立连接
* 将实体注册进 Home Assistant
* 启动灯光模拟逻辑（如配置启用）

---

## 六、配置文件格式 (configuration.yaml)

> 以下是配置文件中用于控制虚拟灯功能的说明：
>
> * `simulate_behavior: true/false`：是否启用随机状态变化模拟（开/关、亮度、颜色、色温）
> * `default_state`：每台灯启动时的默认状态（如果无状态持久化文件）
> * `definitions`：定义多个虚拟灯的设备 ID（did）和产品 ID（pid）

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
      pid: "vlight"
    - did: "light-002"
      pid: "vlight"

logging:
  level: "debug"
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
