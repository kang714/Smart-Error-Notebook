# AI智能错题本系统（竞赛获奖顶配版·本地大模型版）

## 项目简介

一款 Python桌面端AI智能错题本，主打炫酷科技感可视化界面+硬核本地AI功能，适配中小学生/中学生使用，全程本地运行、无付费接口、无需联网、不依赖云端API。

### 核心亮点
- 接入本地部署DeepSeek-R1:7B大模型，实现AI错题深度剖析
- 科技风卡片式布局，支持暗黑/明亮双主题
- 多模态智能录入（手动、粘贴、OCR识别）
- 艾宾浩斯自适应复习引擎
- 多维分类与数据统计
- 纯本地离线运行，零部署成本

## 技术栈

- **开发语言**：Python 3.10+
- **界面框架**：ttkbootstrap+Tkinter
- **本地OCR**：pytesseract+PIL
- **本地大模型**：ollama+deepseek-r1:7b
- **数据存储**：本地JSON文件

## 环境搭建

### 1. 安装Python依赖

```bash
pip install -r requirements.txt
```

### 2. 安装OCR依赖

- 下载并安装Tesseract OCR：https://github.com/UB-Mannheim/tesseract/wiki
- 确保Tesseract已添加到系统环境变量

### 3. 安装并配置ollama

1. 下载并安装ollama：https://ollama.ai/download
2. 拉取DeepSeek-R1:7B模型：
   ```bash
   ollama pull deepseek-r1:7b
   ```
3. 启动ollama服务（默认端口11434）

## 运行项目

```bash
python main.py
```

## 功能模块

1. **多模态智能录入**：支持手动录入、复制粘贴、图片OCR识别
2. **本地大模型分析**：DeepSeek-R1:7B深度诊断错题
3. **艾宾浩斯复习引擎**：自适应复习计划
4. **多维分类统计**：按学科、知识点、错误原因筛选
5. **AI答疑互动**：针对错题实时解答

## 注意事项

- 确保ollama服务正常运行
- 首次运行会自动创建data.json数据文件
- 所有数据存储在本地，无需联网
- 大模型调用可能会占用较多系统资源

## 竞赛亮点

1. **颜值碾压**：科技风双主题界面
2. **技术硬核**：融合OCR、本地大模型、NLP、遗忘曲线算法
3. **AI能力升级**：真正的AI辅导能力
4. **实用性拉满**：解决学生核心痛点
5. **完整交付**：本地运行、零部署成本