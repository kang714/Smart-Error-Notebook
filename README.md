# AI智能错题本 - 使用说明

## 一、Web版使用（推荐）

直接用浏览器打开 `index.html` 即可使用，无需安装任何依赖。

**访问AI功能前请确保：**
1. 已安装 Ollama：https://ollama.com
2. 已下载 DeepSeek-R1:7B 模型：
   ```bash
   ollama pull deepseek-r1:7b
   ```
3. Ollama 服务正在运行（默认 http://localhost:11434）

---

## 二、桌面版使用

### 1. 安装Python依赖

```bash
pip install -r requirements.txt
```

### 2. 安装Tesseract OCR（可选，用于图片识别）

- 下载地址：https://github.com/UB-Mannheim/tesseract/wiki
- 安装后将路径添加到系统PATH

### 3. 运行桌面版

```bash
python main.py
```

---

## 三、AI功能配置

AI功能使用 Ollama 本地大模型，请确保：

1. **安装 Ollama**
   - Windows: https://ollama.com/download/windows
   - 启动后默认监听 http://localhost:11434

2. **下载模型**
   ```bash
   # 下载 DeepSeek-R1:7B（约4.7GB）
   ollama pull deepseek-r1:7b
   
   # 或者使用其他模型
   ollama pull qwen2.5:7b
   ollama pull llama3:8b
   ```

3. **验证运行**
   ```bash
   ollama list     # 查看已安装模型
   ollama run deepseek-r1:7b  # 测试运行
   ```

---

## 四、Web版功能

- 📝 **录入错题** - 手动、复制粘贴
- 📚 **复习计划** - 卡片模式复习
- 🔍 **错题分析** - AI智能分析
- 📊 **统计分析** - 多维度数据展示
- 💬 **AI答疑** - 实时问答

---

## 五、故障排除

**AI显示离线：**
1. 检查 Ollama 是否运行中
2. 确认模型已下载：`ollama list`
3. 检查端口 11434 是否被占用

**无法保存数据：**
- 浏览器版本需要支持 localStorage

**图片识别失败：**
- 桌面版需要安装 Tesseract OCR
