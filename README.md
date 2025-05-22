# vlight 虚拟灯光应用设计文档 (v0.4.4)

## 一、项目简介

**vlight** 是一个使用 Python 编写的可配置式 MQTT 虚拟灯光系统，支持 Home Assistant 的自动发现 (MQTT Discovery)，可以模拟多台灯光设备。

它有如下功能：

* 多台虚拟灯光创建（数量可配置）
* 支持 MQTT + Home Assistant Discovery 协议（符合 iSG 扩展格式）
* 支持独立设备状态管理：开/关、亮度、RGB、色温
* 状态持久化：重启后保持最后状态
* 支持随机状态模拟切换，可配置打开或关闭
* ✅ 从 v0.4.3 开始，Discovery Payload 中增加 `device` 信息，使设备可在 HA 中显示为“设备页”
* ✅ 从 v0.4.4 开始，支持通过 `count/prefix/pid` 自动生成设备定义，无需手写 1000 条
* ✅ 每个灯设备对应 Home Assistant 中一个独立设备页（通过唯一 `device.identifiers` 实现）
* 支持 pip install 安装，使用 CLI 命令 `vlight` 启动

---

## 二、目录结构

```
vlight_v044/
├── vlight/                 应用核心源码
│   ├── __init__.py        
│   ├── main.py            全局进入点
│   ├── config.py          配置文件读取与自动生成逻辑
│   ├── logger.py          日志初始化
│   ├── mqtt_client.py     MQTT 管理器，初始化所有灯设备
│   ├── light_device.py    灯设备实体，包括状态和功能
│   └── state_store.py     将灯的状态持久化 JSON 文件
├── configuration.yaml     用户配置文件
├── setup.py               pip 安装设置文件
├── requirements.txt       依赖列表
└── vlight_v044_full_package.zip  打包成果
```

---

## 三、核心模块说明

### 1. `light_device.py`

* 每个设备为一个实例，具备完整状态控制能力
* 发布 discovery topic（含分 topic 控制、availability、device 信息）
* 接收来自 MQTT 的控制命令，更新本地状态
* 状态持久化到本地 JSON 文件
* 支持模拟行为（随机变化）
* ✅ 每个灯的 `device.identifiers` 使用 `{did}`，确保 Home Assistant 创建独立设备页

### 2. `mqtt_client.py`

* 初始化所有设备并连接 MQTT Broker
* 按设备订阅分 topic 控制指令
* 接收指令时按 topic 末段映射指令类型：switch、brightness、rgb、colortemp

### 3. `state_store.py`

* 所有灯状态持久化到 `~/.vlight/state/` 目录
* 使用 `save_state()` 与 `load_state()` 管理状态文件

### 4. `logger.py`

* 支持日志等级配置
* 写入 `./logs/vlight.log`

### 5. `config.py`

* ✅ 若未定义 `definitions:`，自动根据 `count/prefix/pid` 生成虚拟灯列表：

```yaml
lights:
  count: 1000
  prefix: "light"
  pid: "vlight"
```

---

## 四、MQTT 协议配置（iSG Discovery 兼容）

### 1. Discovery Topic

```
homeassistant/light/<pid>/<did>/config
```

### Payload 示例：

```json
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
    "identifiers": ["light-001"],
    "name": "vLight 虚拟灯 light-001",
    "manufacturer": "LinknLink",
    "model": "vlight-sim",
    "sw_version": "0.4.4"
  }
}
```

### 2. 状态发布 Topic

```
home/vlight/light-001/status
```

```json
{
  "state": "ON",
  "brightness": 150,
  "color_temp": 250,
  "rgb_color": [0,255,128]
}
```

### 3. 控制 Topics

* `home/vlight/light-001/switch` → "1"/"0"
* `home/vlight/light-001/brightness` → 0\~255
* `home/vlight/light-001/rgb` → "255,255,0"
* `home/vlight/light-001/colortemp` → 153\~500

### 4. Availability

* `home/vlight/light-001/availability` → `"online"`

---

## 五、安装与使用

```bash
unzip vlight_v044_full_package.zip
cd vlight_v044
python3 -m venv venv
source venv/bin/activate
pip install .
vlight
rm -rf ~/.vlight/state #如果异常退出，导致空或非法的 JSON，从而在 json.load() 时出错
```

---

## 六、配置文件格式 (configuration.yaml)

> v0.4.4 起，推荐使用自动生成方式：

```yaml
mqtt:
  host: "127.0.0.1"
  port: 1883
  username: ""
  password: ""
  base_topic: "home/vlight"
  discovery_prefix: "homeassistant"

lights:
  count: 4
  prefix: "light"
  pid: "vlight"
  simulate_behavior: true
  default_state:
    state: "OFF"
    brightness: 128
    color_temp: 250
    rgb_color: [255, 255, 255]

logging:
  level: "info"
  file: "./logs/vlight.log"
```

> 如仍需手动指定部分设备，可直接写入 `definitions:` 字段，系统将跳过自动生成。

---

## 七、后续拟增能力

| 功能          | 说明                       |
| ----------- | ------------------------ |
| 后台服务部署      | 支持 systemd/runit 等守护运行模式 |
| Web 控制界面    | 提供页面查看与控制灯状态             |
| MQTT TLS 支持 | 安全连接验证                   |
| 状态同步 API    | 提供外部读取虚拟灯状态的接口           |
| 自定义模板输出     | 兼容更复杂的 HA Discovery 模板结构 |
