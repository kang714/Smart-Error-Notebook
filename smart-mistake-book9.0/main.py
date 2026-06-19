import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import ttkbootstrap as ttkb
import datetime
import threading
import random
from utils import (
    load_data, save_data, generate_mistake_id, update_statistics,
    get_today_review_list, update_review_status, find_similar_mistakes,
    calculate_next_review_time, backup_data
)
from ocr_module import ocr_image
from ai_model import (
    analyze_mistake, generate_similar_questions, answer_question,
    check_model_availability
)

class SmartMistakeBook:
    def __init__(self, root):
        self.root = root
        self.root.title("AI智学错题本")
        self.root.geometry("1000x700")
        
        # 设置主题
        self.style = ttkb.Style(theme="darkly")
        self.current_theme = "darkly"
        
        # 创建主框架
        self.main_frame = ttkb.Frame(root, padding=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建导航栏
        self.create_navbar()
        
        # 创建内容区域
        self.content_frame = ttkb.Frame(self.main_frame, padding=20)
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        # 显示主界面
        self.show_main_page()
    
    def create_navbar(self):
        """创建导航栏"""
        navbar = ttkb.Frame(self.main_frame, padding=15, bootstyle="primary")
        navbar.pack(fill=tk.X, pady=10)
        
        # 导航按钮 - 增强设计和交互
        nav_buttons = [
            ("🏠 主界面", self.show_main_page, "primary"),
            ("📝 录入错题", self.show_input_page, "info"),
            ("🤖 错题分析", self.show_analysis_page, "warning"),
            ("📚 复习计划", self.show_review_page, "success"),
            ("📊 统计分析", self.show_statistics_page, "danger"),
            ("💬 AI答疑", self.show_ai_qa_page, "secondary")
        ]
        
        for text, command, style in nav_buttons:
            btn = ttkb.Button(
                navbar, 
                text=text, 
                command=command,
                bootstyle=f"{style}-outline",
                width=16
            )
            # 添加悬停效果
            btn.bind("<Enter>", lambda e, b=btn, s=style: self.on_nav_hover(b, s, True))
            btn.bind("<Leave>", lambda e, b=btn: self.on_nav_hover(b, None, False))
            btn.pack(side=tk.LEFT, padx=8)
        
        # 分隔符
        ttkb.Separator(navbar, orient=tk.VERTICAL, bootstyle="light").pack(side=tk.LEFT, fill=tk.Y, padx=15)
        
        # 主题选择下拉框 - 增强设计
        self.theme_var = tk.StringVar(value="暗夜黑")
        self.themes = {
            "暗夜黑": "darkly",
            "明亮白": "flatly",
            "星空蓝": "superhero"
        }
        
        theme_label = ttkb.Label(navbar, text="🎨 主题:", font=("Microsoft YaHei", 12, "bold"), bootstyle="inverse")
        theme_label.pack(side=tk.RIGHT, padx=10)
        
        theme_combo = ttkb.Combobox(
            navbar, 
            textvariable=self.theme_var, 
            values=list(self.themes.keys()),
            state="readonly",
            width=14,
            font=("Microsoft YaHei", 11, "bold")
        )
        theme_combo.pack(side=tk.RIGHT, padx=10)
        theme_combo.bind("<<ComboboxSelected>>", self.change_theme)
        
        # 备份按钮 - 增强设计
        backup_btn = ttkb.Button(
            navbar, 
            text="💾 备份数据", 
            command=self.backup_data,
            bootstyle="success"
        )
        # 添加悬停效果
        backup_btn.bind("<Enter>", lambda e, b=backup_btn: self.on_nav_hover(b, "success", True))
        backup_btn.bind("<Leave>", lambda e, b=backup_btn: self.on_nav_hover(b, None, False))
        backup_btn.pack(side=tk.RIGHT, padx=10)
    
    def on_nav_hover(self, button, style, enter):
        """导航按钮悬停效果"""
        if enter:
            # 鼠标进入时的效果
            button.config(bootstyle=style)
            # 按钮放大效果
            button.update_idletasks()
            button_width = button.winfo_width()
            button.config(width=button_width + 2)
        else:
            # 鼠标离开时的效果
            button.config(bootstyle=f"{style}-outline" if style else "success-outline")
            # 恢复原始大小
            button.config(width=16 if style else 12)
    
    def change_theme(self, event=None):
        """切换主题"""
        selected_theme_name = self.theme_var.get()
        if selected_theme_name in self.themes:
            self.current_theme = self.themes[selected_theme_name]
            self.style.theme_use(self.current_theme)
            self.root.update()
    
    def toggle_theme(self):
        """切换主题（旧方法，保留兼容性）"""
        theme_names = list(self.themes.keys())
        current_index = theme_names.index(self.theme_var.get())
        next_index = (current_index + 1) % len(theme_names)
        self.theme_var.set(theme_names[next_index])
        self.change_theme()
    
    def clear_content(self):
        """清空内容区域"""
        # 直接销毁所有子控件
        for widget in self.content_frame.winfo_children():
            try:
                widget.destroy()
            except:
                pass
    
    def show_main_page(self):
        """显示主界面"""
        self.clear_content()
        
        # 装饰性横幅 - 添加渐变效果
        banner_frame = ttkb.Frame(self.content_frame, bootstyle="primary")
        banner_frame.pack(fill=tk.X, pady=10)
        
        # 随机学习名言
        study_quotes = [
            "📖 书山有路勤为径，学海无涯苦作舟",
            "💪 失败是成功之母，错题是进步之源",
            "🎯 每天进步一点点，成绩提升看得见",
            "🚀 错题本在手，高分我有",
            "✨ 今日错题，明日满分"
        ]
        
        quote = random.choice(study_quotes)
        
        # 动态名言标签
        quote_label = ttkb.Label(
            banner_frame, 
            text=f"📢 {quote}", 
            font=("Microsoft YaHei", 14, "bold"),
            bootstyle="inverse"
        )
        quote_label.pack(pady=10)
        
        # 标题 - 添加动画效果
        title_frame = ttkb.Frame(self.content_frame)
        title_frame.pack(pady=15)
        
        title = ttkb.Label(
            title_frame, 
            text="✨ AI智能错题本 ✨", 
            font=("Microsoft YaHei", 40, "bold"),
            bootstyle="primary"
        )
        title.pack()
        
        # 添加标题动画
        self.animate_title(title)
        
        # 副标题
        subtitle = ttkb.Label(
            self.content_frame, 
            text="🎓 科技赋能学习 · 📝 错题成就进步 · 🚀 成绩步步高升", 
            font=("Microsoft YaHei", 18)
        )
        subtitle.pack(pady=15)
        
        # 核心功能卡片 - 增强设计
        cards_frame = ttkb.Frame(self.content_frame)
        cards_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        features = [
            ("📝 多模态录入", "支持手动、粘贴、OCR识别\n🖼️ 拍照秒变文字", "primary", "🎨"),
            ("🤖 AI深度分析", "本地DeepSeek-R1:7B模型\n💡 智能错题诊断", "info", "🔍"),
            ("📚 艾宾浩斯复习", "智能自适应复习计划\n⏰ 科学记忆规律", "success", "📅"),
            ("📊 多维统计", "学科、知识点、错误原因\n📈 学习数据可视化", "warning", "🎯"),
            ("💬 AI答疑", "实时解答疑惑\n👨‍🏫 一对一辅导", "danger", "❓"),
            ("🔒 本地运行", "无需联网，零成本\n🛡️ 数据安全无忧", "secondary", "💰")
        ]
        
        for i, (title, desc, style, emoji) in enumerate(features):
            card = ttkb.Frame(
                cards_frame, 
                bootstyle=f"{style}-card",
                relief="raised",
                borderwidth=3
            )
            card.grid(row=i//2, column=i%2, padx=10, pady=10, sticky="nsew")
            
            # 添加卡片悬停效果
            card.bind("<Enter>", lambda e, c=card: self.on_card_hover(c, True))
            card.bind("<Leave>", lambda e, c=card: self.on_card_hover(c, False))
            
            card_inner = ttkb.Frame(card, padding=15)
            card_inner.pack(fill=tk.BOTH, expand=True)
            
            # Emoji图标 - 添加动画
            emoji_label = ttkb.Label(
                card_inner, 
                text=emoji, 
                font=("Microsoft YaHei", 32)
            )
            emoji_label.pack(pady=8)
            
            # 添加图标动画
            self.animate_emoji(emoji_label)
            
            card_title = ttkb.Label(
                card_inner, 
                text=title, 
                font=("Microsoft YaHei", 16, "bold"),
                bootstyle=style
            )
            card_title.pack(pady=8)
            
            card_desc = ttkb.Label(
                card_inner, 
                text=desc, 
                font=("Microsoft YaHei", 11),
                wraplength=280
            )
            card_desc.pack(pady=8)
        
        # 底部装饰 - 增强效果
        footer_frame = ttkb.Frame(self.content_frame, bootstyle="success")
        footer_frame.pack(pady=20, fill=tk.X)
        
        footer_text = "💪 加油！坚持使用，你一定能成为学霸！ 🌟"
        footer_label = ttkb.Label(
            footer_frame, 
            text=footer_text, 
            font=("Microsoft YaHei", 16, "bold"),
            bootstyle="inverse"
        )
        footer_label.pack(pady=15)
        
        # 添加底部文字动画
        self.animate_footer(footer_label)
        
        # 调整网格布局
        cards_frame.grid_columnconfigure(0, weight=1)
        cards_frame.grid_columnconfigure(1, weight=1)
    
    def animate_title(self, label):
        """标题动画"""
        # 简化动画，直接使用固定大小变化
        current_size = 40
        
        def animate():
            nonlocal current_size
            # 检查控件是否仍然存在
            try:
                label.winfo_exists()
            except:
                return
            if not label.winfo_exists():
                return
            if current_size < 42:
                current_size += 1
                label.config(font=("Microsoft YaHei", current_size, "bold"))
                self.root.after(50, animate)
            else:
                def shrink():
                    nonlocal current_size
                    # 检查控件是否仍然存在
                    try:
                        label.winfo_exists()
                    except:
                        return
                    if not label.winfo_exists():
                        return
                    if current_size > 38:
                        current_size -= 1
                        label.config(font=("Microsoft YaHei", current_size, "bold"))
                        self.root.after(50, shrink)
                self.root.after(500, shrink)
        animate()
    
    def animate_emoji(self, label):
        """图标动画"""
        # 简化动画，直接使用固定大小变化
        current_size = 40
        
        def animate():
            nonlocal current_size
            # 检查控件是否仍然存在
            try:
                label.winfo_exists()
            except:
                return
            if not label.winfo_exists():
                return
            if current_size < 45:
                current_size += 1
                label.config(font=("Microsoft YaHei", current_size))
                self.root.after(30, animate)
            else:
                def shrink():
                    nonlocal current_size
                    # 检查控件是否仍然存在
                    try:
                        label.winfo_exists()
                    except:
                        return
                    if not label.winfo_exists():
                        return
                    if current_size > 35:
                        current_size -= 1
                        label.config(font=("Microsoft YaHei", current_size))
                        self.root.after(30, shrink)
                self.root.after(300, shrink)
        animate()
    
    def animate_footer(self, label):
        """底部文字动画 - 已禁用闪烁效果以避免页面闪烁问题"""
        # 禁用闪烁动画，改为静态样式
        pass
    
    def animate_stat_value(self, label, start, end):
        """统计数值动画"""
        duration = 1000  # 动画持续时间（毫秒）
        steps = 20  # 动画步数
        step_time = duration // steps
        step_value = (end - start) / steps
        current = start
        
        def animate(step=0):
            nonlocal current
            # 检查控件是否仍然存在
            try:
                if not label.winfo_exists():
                    return
            except:
                return
            
            if step < steps:
                current += step_value
                label.config(text=f"{int(current)}")
                self.root.after(step_time, lambda: animate(step + 1))
            else:
                label.config(text=f"{end}")
        
        animate()
    
    def animate_progress(self, progress, start, end):
        """进度条动画"""
        duration = 800  # 动画持续时间（毫秒）
        steps = 20  # 动画步数
        step_time = duration // steps
        step_value = (end - start) / steps
        current = start
        
        def animate(step=0):
            nonlocal current
            # 检查控件是否仍然存在
            try:
                if not progress.winfo_exists():
                    return
            except:
                return
            
            if step < steps:
                current += step_value
                progress.config(value=current)
                self.root.after(step_time, lambda: animate(step + 1))
            else:
                progress.config(value=end)
        
        animate()
    
    def on_card_hover(self, card, enter):
        """卡片悬停效果"""
        if enter:
            # 鼠标进入时的效果
            card.config(relief="sunken", borderwidth=4)
            # 卡片放大效果
            card.update_idletasks()
            card_width = card.winfo_width()
            card_height = card.winfo_height()
            card.config(width=card_width + 10, height=card_height + 10)
        else:
            # 鼠标离开时的效果
            card.config(relief="raised", borderwidth=3)
            # 恢复原始大小
            card.config(width=0, height=0)
    
    def show_input_page(self):
        """显示录入界面"""
        self.clear_content()
        
        # 装饰性横幅 - 增强设计
        banner_frame = ttkb.Frame(self.content_frame, bootstyle="info")
        banner_frame.pack(fill=tk.X, pady=10)
        
        input_tips = [
            "💡 提示：详细的信息有助于AI更好地分析错题",
            "📌 建议：填写完整的知识点，便于分类管理",
            "🎯 技巧：OCR识别可以快速录入纸质题目"
        ]
        
        tip = random.choice(input_tips)
        
        tip_label = ttkb.Label(
            banner_frame, 
            text=tip, 
            font=("Microsoft YaHei", 12, "bold"),
            bootstyle="inverse"
        )
        tip_label.pack(pady=8)
        
        # 标题 - 添加动画
        title = ttkb.Label(
            self.content_frame, 
            text="📝 录入错题", 
            font=("Microsoft YaHei", 32, "bold"),
            bootstyle="primary"
        )
        title.pack(pady=20)
        
        # 添加标题动画
        self.animate_title(title)
        
        # 录入方式选择
        input_mode_frame = ttkb.Frame(self.content_frame)
        input_mode_frame.pack(fill=tk.X, pady=10)
        
        self.input_mode = tk.StringVar(value="manual")
        modes = [
            ("手动录入", "manual"),
            ("复制粘贴", "paste"),
            ("图片识别", "ocr")
        ]
        
        for text, value in modes:
            ttkb.Radiobutton(
                input_mode_frame, 
                text=text, 
                variable=self.input_mode, 
                value=value,
                command=self.update_input_mode
            ).pack(side=tk.LEFT, padx=20)
        
        # 录入表单
        form_frame = ttkb.LabelFrame(self.content_frame, text="错题信息")
        form_frame.pack(fill=tk.BOTH, expand=True, pady=20, padx=20, ipady=20)
        
        # 题目输入
        ttkb.Label(form_frame, text="题目:").pack(anchor=tk.W, pady=5)
        self.question_text = tk.Text(form_frame, height=6, wrap=tk.WORD)
        self.question_text.pack(fill=tk.X, pady=5)
        
        # 学科选择
        ttkb.Label(form_frame, text="学科:").pack(anchor=tk.W, pady=5)
        self.subject_var = tk.StringVar()
        subjects = ["数学", "语文", "英语", "物理", "化学", "生物", "历史", "地理", "政治"]
        ttkb.Combobox(
            form_frame, 
            textvariable=self.subject_var, 
            values=subjects,
            state="readonly"
        ).pack(fill=tk.X, pady=5)
        
        # 知识点
        ttkb.Label(form_frame, text="知识点:").pack(anchor=tk.W, pady=5)
        self.knowledge_entry = ttkb.Entry(form_frame)
        self.knowledge_entry.pack(fill=tk.X, pady=5)
        ttkb.Label(form_frame, text="多个知识点用逗号分隔").pack(anchor=tk.W, pady=2)
        
        # 正确答案
        ttkb.Label(form_frame, text="正确答案:").pack(anchor=tk.W, pady=5)
        self.correct_answer_entry = ttkb.Entry(form_frame)
        self.correct_answer_entry.pack(fill=tk.X, pady=5)
        
        # 错误答案
        ttkb.Label(form_frame, text="错误答案:").pack(anchor=tk.W, pady=5)
        self.wrong_answer_entry = ttkb.Entry(form_frame)
        self.wrong_answer_entry.pack(fill=tk.X, pady=5)
        
        # 错误原因
        ttkb.Label(form_frame, text="错误原因:").pack(anchor=tk.W, pady=5)
        error_reasons = [
            "概念混淆", "计算失误", "审题不清", 
            "逻辑漏洞", "方法错误", "步骤遗漏"
        ]
        self.error_reasons_vars = []
        error_frame = ttkb.Frame(form_frame)
        error_frame.pack(fill=tk.X, pady=5)
        
        for i, reason in enumerate(error_reasons):
            var = tk.BooleanVar()
            self.error_reasons_vars.append((reason, var))
            ttkb.Checkbutton(
                error_frame, 
                text=reason, 
                variable=var
            ).grid(row=i//3, column=i%3, sticky=tk.W, padx=10)
        
        # 操作按钮
        button_frame = ttkb.Frame(self.content_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        ttkb.Button(
            button_frame, 
            text="保存错题", 
            command=self.save_mistake,
            bootstyle="primary"
        ).pack(side=tk.LEFT, padx=10)
        
        ttkb.Button(
            button_frame, 
            text="清空", 
            command=self.clear_form,
            bootstyle="secondary"
        ).pack(side=tk.LEFT, padx=10)
        
        # OCR按钮（仅在OCR模式下显示）
        self.ocr_button = ttkb.Button(
            button_frame, 
            text="选择图片", 
            command=self.select_image,
            bootstyle="info"
        )
        self.ocr_button.pack(side=tk.LEFT, padx=10)
        self.ocr_button.pack_forget()
    
    def update_input_mode(self):
        """更新录入模式"""
        if hasattr(self, 'ocr_button'):
            if self.input_mode.get() == "ocr":
                self.ocr_button.pack(side=tk.LEFT, padx=10)
            else:
                self.ocr_button.pack_forget()
    
    def select_image(self):
        """选择图片进行OCR识别"""
        file_path = filedialog.askopenfilename(
            filetypes=[("图片文件", "*.jpg *.jpeg *.png *.bmp")]
        )
        
        if file_path:
            # 显示加载中
            loading_window = ttkb.Toplevel(self.root)
            loading_window.title("识别中")
            loading_window.geometry("300x100")
            loading_window.transient(self.root)
            
            ttkb.Label(
                loading_window, 
                text="正在识别图片...", 
                font=("微软雅黑", 12)
            ).pack(pady=20)
            
            # 启动线程进行OCR
            def ocr_thread():
                result = ocr_image(file_path)
                loading_window.destroy()
                
                # 填充识别结果
                self.question_text.delete(1.0, tk.END)
                self.question_text.insert(tk.END, result["question"])
                
                if result["options"]:
                    self.question_text.insert(tk.END, "\n\n选项:\n")
                    for i, option in enumerate(result["options"]):
                        self.question_text.insert(tk.END, f"{chr(65+i)}. {option}\n")
            
            threading.Thread(target=ocr_thread).start()
    
    def save_mistake(self):
        """保存错题"""
        question = self.question_text.get(1.0, tk.END).strip()
        subject = self.subject_var.get()
        knowledge_text = self.knowledge_entry.get().strip()
        correct_answer = self.correct_answer_entry.get().strip()
        wrong_answer = self.wrong_answer_entry.get().strip()
        
        # 验证输入
        if not question:
            messagebox.showerror("错误", "请输入题目")
            return
        if not subject:
            messagebox.showerror("错误", "请选择学科")
            return
        if not correct_answer:
            messagebox.showerror("错误", "请输入正确答案")
            return
        if not wrong_answer:
            messagebox.showerror("错误", "请输入错误答案")
            return
        
        # 处理知识点
        knowledge_points = [kp.strip() for kp in knowledge_text.split(",") if kp.strip()]
        
        # 处理错误原因
        error_reasons = [reason for reason, var in self.error_reasons_vars if var.get()]
        
        # 生成错题ID
        mistake_id = generate_mistake_id()
        
        # 创建错题记录
        mistake = {
            "id": mistake_id,
            "question": question,
            "subject": subject,
            "knowledge_points": knowledge_points,
            "correct_answer": correct_answer,
            "wrong_answer": wrong_answer,
            "error_reasons": error_reasons,
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "review_count": 0,
            "last_review": "",
            "ai_analysis": ""
        }
        
        # 保存到数据文件
        data = load_data()
        data["mistakes"].append(mistake)
        
        # 计算首次复习时间 - 设置为今天，让新录入的错题立即出现在复习计划中
        next_review = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data["next_review"][mistake_id] = next_review
        
        if save_data(data):
            # 更新统计信息
            update_statistics()
            
            # 自动调用AI分析
            self.auto_analyze_mistake(mistake)
            
            messagebox.showinfo("成功", "错题保存成功，正在进行AI分析...")
            self.clear_form()
        else:
            messagebox.showerror("错误", "保存失败")
    
    def clear_form(self):
        """清空表单"""
        self.question_text.delete(1.0, tk.END)
        self.subject_var.set("")
        self.knowledge_entry.delete(0, tk.END)
        self.correct_answer_entry.delete(0, tk.END)
        self.wrong_answer_entry.delete(0, tk.END)
        for _, var in self.error_reasons_vars:
            var.set(False)
    
    def auto_analyze_mistake(self, mistake):
        """自动分析错题"""
        # 检查模型可用性
        if not check_model_availability():
            return
        
        # 启动线程进行分析
        def analysis_thread():
            # 调用大模型分析
            analysis = analyze_mistake(
                mistake["question"],
                mistake["correct_answer"],
                mistake["wrong_answer"]
            )
            
            # 保存分析结果
            data = load_data()
            for i, m in enumerate(data.get("mistakes", [])):
                if str(m["id"]) == str(mistake["id"]):
                    data["mistakes"][i]["ai_analysis"] = analysis
                    break
            save_data(data)
        
        threading.Thread(target=analysis_thread).start()
    
    def show_analysis_page(self):
        """显示错题分析界面"""
        self.clear_content()
        
        # 装饰性横幅 - 增强设计
        banner_frame = ttkb.Frame(self.content_frame, bootstyle="info")
        banner_frame.pack(fill=tk.X, pady=10)
        
        analysis_tips = [
            "🔍 深入分析错题，找出知识漏洞",
            "💡 理解错因，举一反三",
            "📚 同类题练习，巩固知识点"
        ]
        
        tip = random.choice(analysis_tips)
        
        tip_label = ttkb.Label(
            banner_frame, 
            text=tip, 
            font=("Microsoft YaHei", 12, "bold"),
            bootstyle="inverse"
        )
        tip_label.pack(pady=8)
        
        # 标题 - 添加动画
        title = ttkb.Label(
            self.content_frame, 
            text="🤖 错题分析", 
            font=("Microsoft YaHei", 32, "bold"),
            bootstyle="info"
        )
        title.pack(pady=20)
        
        # 添加标题动画
        self.animate_title(title)
        
        # 加载错题数据
        data = load_data()
        mistakes = data.get("mistakes", [])
        
        if not mistakes:
            ttkb.Label(self.content_frame, text="暂无错题", font=("Microsoft YaHei", 14)).pack(pady=50)
            return
        
        # 获取所有学科
        subjects = list(set(mistake["subject"] for mistake in mistakes))
        subjects.sort()
        
        # 学科筛选
        filter_frame = ttkb.Frame(self.content_frame)
        filter_frame.pack(fill=tk.X, pady=10, padx=20)
        
        ttkb.Label(
            filter_frame, 
            text="选择学科：", 
            font=("Microsoft YaHei", 12, "bold")
        ).pack(side=tk.LEFT, padx=10)
        
        self.analysis_subject_var = tk.StringVar(value="全部学科")
        subject_options = ["全部学科"] + subjects
        
        subject_combo = ttkb.Combobox(
            filter_frame, 
            textvariable=self.analysis_subject_var, 
            values=subject_options,
            state="readonly",
            width=20,
            font=("Microsoft YaHei", 11)
        )
        subject_combo.pack(side=tk.LEFT, padx=10)
        
        # 刷新按钮
        refresh_btn = ttkb.Button(
            filter_frame, 
            text="刷新", 
            command=lambda: self.refresh_analysis_tree(tree, mistakes),
            bootstyle="info-outline"
        )
        refresh_btn.pack(side=tk.LEFT, padx=10)
        
        # 错题列表框架
        list_frame = ttkb.LabelFrame(self.content_frame, text="错题列表")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=20, ipady=10)
        
        # 创建树状视图
        columns = ("id", "subject", "question", "created_at")
        tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # 设置表头
        tree.heading("id", text="ID", anchor=tk.CENTER)
        tree.heading("subject", text="学科", anchor=tk.CENTER)
        tree.heading("question", text="题目", anchor=tk.W)
        tree.heading("created_at", text="创建时间", anchor=tk.CENTER)
        
        # 设置列宽和对齐
        tree.column("id", width=100, anchor=tk.CENTER)
        tree.column("subject", width=120, anchor=tk.CENTER)
        tree.column("question", width=500, anchor=tk.W)
        tree.column("created_at", width=180, anchor=tk.CENTER)
        
        # 添加滚动条
        scrollbar_y = ttkb.Scrollbar(list_frame, orient=tk.VERTICAL, command=tree.yview)
        scrollbar_x = ttkb.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # 布局
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 填充数据
        self.refresh_analysis_tree(tree, mistakes)
        
        # 绑定学科筛选事件
        subject_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_analysis_tree(tree, mistakes))
        
        # 分析按钮
        button_frame = ttkb.Frame(self.content_frame)
        button_frame.pack(fill=tk.X, pady=20, padx=20)
        
        ttkb.Button(
            button_frame, 
            text="📊 分析选中错题", 
            command=lambda: self.analyze_selected_mistake(tree),
            bootstyle="primary",
            width=20
        ).pack(side=tk.LEFT, padx=10)
    
    def refresh_analysis_tree(self, tree, all_mistakes):
        """刷新错题分析列表"""
        # 清空现有数据
        for item in tree.get_children():
            tree.delete(item)
        
        # 获取选中的学科
        selected_subject = self.analysis_subject_var.get()
        
        # 筛选错题
        filtered_mistakes = all_mistakes
        if selected_subject != "全部学科":
            filtered_mistakes = [m for m in all_mistakes if m["subject"] == selected_subject]
        
        # 填充数据
        for mistake in filtered_mistakes:
            tree.insert("", tk.END, values=(
                mistake["id"],
                mistake["subject"],
                mistake["question"][:60] + "..." if len(mistake["question"]) > 60 else mistake["question"],
                mistake["created_at"]
            ))
    
    def analyze_selected_mistake(self, tree):
        """分析选中的错题"""
        selected_items = tree.selection()
        if not selected_items:
            messagebox.showinfo("提示", "请选择要分析的错题")
            return
        
        item = selected_items[0]
        mistake_id = tree.item(item, "values")[0]
        
        # 查找错题
        data = load_data()
        mistake = None
        for m in data.get("mistakes", []):
            if str(m["id"]) == mistake_id:
                mistake = m
                break
        
        if not mistake:
            messagebox.showerror("错误", "未找到错题")
            return
        
        # 检查模型可用性
        if not check_model_availability():
            messagebox.showwarning("警告", "ollama服务未启动，无法使用AI分析功能")
            return
        
        # 显示分析窗口
        analysis_window = ttkb.Toplevel(self.root)
        analysis_window.title("AI错题分析")
        analysis_window.geometry("800x600")
        analysis_window.transient(self.root)
        
        # 显示加载中
        loading_label = ttkb.Label(
            analysis_window, 
            text="AI正在分析，请稍候...", 
            font=("微软雅黑", 14)
        )
        loading_label.pack(pady=50)
        
        # 启动线程进行分析
        def analysis_thread():
            # 调用大模型分析
            analysis = analyze_mistake(
                mistake["question"],
                mistake["correct_answer"],
                mistake["wrong_answer"]
            )
            
            # 生成同类题
            similar_questions = generate_similar_questions(
                mistake["question"],
                mistake["subject"],
                mistake["knowledge_points"]
            )
            
            # 查找相似错题
            similar_mistakes = find_similar_mistakes(mistake)
            
            # 更新界面
            loading_label.pack_forget()
            
            # 创建分析结果界面
            result_frame = ttkb.Frame(analysis_window)
            result_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # 错题信息
            info_frame = ttkb.LabelFrame(result_frame, text="错题信息")
            info_frame.pack(fill=tk.X, pady=10, padx=10, ipady=10)
            
            ttkb.Label(info_frame, text=f"学科: {mistake['subject']}").pack(anchor=tk.W)
            ttkb.Label(info_frame, text=f"知识点: {', '.join(mistake['knowledge_points'])}").pack(anchor=tk.W)
            ttkb.Label(info_frame, text=f"错误原因: {', '.join(mistake['error_reasons'])}").pack(anchor=tk.W)
            ttkb.Label(info_frame, text=f"正确答案: {mistake['correct_answer']}").pack(anchor=tk.W)
            ttkb.Label(info_frame, text=f"错误答案: {mistake['wrong_answer']}").pack(anchor=tk.W)
            
            # AI分析结果
            analysis_frame = ttkb.LabelFrame(result_frame, text="AI分析结果")
            analysis_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10, ipady=10)
            
            analysis_text = tk.Text(analysis_frame, wrap=tk.WORD)
            analysis_text.insert(tk.END, analysis)
            analysis_text.config(state=tk.DISABLED)
            
            scrollbar = ttkb.Scrollbar(analysis_frame, command=analysis_text.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            analysis_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
            analysis_text.config(yscrollcommand=scrollbar.set)
            
            # 同类变式题
            if similar_questions:
                similar_frame = ttkb.LabelFrame(result_frame, text="同类变式题")
                similar_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10, ipady=10)
                
                similar_text = tk.Text(similar_frame, wrap=tk.WORD)
                similar_text.insert(tk.END, similar_questions)
                similar_text.config(state=tk.DISABLED)
                
                scrollbar2 = ttkb.Scrollbar(similar_frame, command=similar_text.yview)
                scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)
                similar_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
                similar_text.config(yscrollcommand=scrollbar2.set)
            
            # 相似错题
            if similar_mistakes:
                similar_mistakes_frame = ttkb.LabelFrame(result_frame, text="相似错题")
                similar_mistakes_frame.pack(fill=tk.X, pady=10, padx=10, ipady=10)
                
                for i, sim_mistake in enumerate(similar_mistakes):
                    ttkb.Label(
                        similar_mistakes_frame, 
                        text=f"{i+1}. {sim_mistake['question'][:100]}...",
                        wraplength=700
                    ).pack(anchor=tk.W, pady=5)
            
            # 保存分析结果
            mistake["ai_analysis"] = analysis
            data = load_data()
            for i, m in enumerate(data.get("mistakes", [])):
                if str(m["id"]) == mistake_id:
                    data["mistakes"][i] = mistake
                    break
            save_data(data)
        
        threading.Thread(target=analysis_thread).start()
    
    def show_review_page(self):
        """显示复习计划界面"""
        self.clear_content()
        
        # 装饰性横幅 - 增强设计
        banner_frame = ttkb.Frame(self.content_frame, bootstyle="success")
        banner_frame.pack(fill=tk.X, pady=10)
        
        review_tips = [
            "⏰ 艾宾浩斯记忆法，科学复习",
            "💪 坚持复习，成绩提升",
            "📅 今日事今日毕，复习要及时"
        ]
        
        tip = random.choice(review_tips)
        
        tip_label = ttkb.Label(
            banner_frame, 
            text=tip, 
            font=("Microsoft YaHei", 12, "bold"),
            bootstyle="inverse"
        )
        tip_label.pack(pady=8)
        
        # 标题 - 添加动画
        title = ttkb.Label(
            self.content_frame, 
            text="📚 复习计划", 
            font=("Microsoft YaHei", 32, "bold"),
            bootstyle="success"
        )
        title.pack(pady=20)
        
        # 添加标题动画
        self.animate_title(title)
        
        # 加载所有错题数据
        data = load_data()
        all_mistakes = data.get("mistakes", [])
        next_review_dict = data.get("next_review", {})
        
        if not all_mistakes:
            ttkb.Label(self.content_frame, text="暂无错题", font=("Microsoft YaHei", 14)).pack(pady=50)
            return
        
        # 今日待复习 - 重新加载数据确保获取最新的AI解析
        today_review_list = get_today_review_list()
        
        # 复习模式选择
        mode_frame = ttkb.Frame(self.content_frame)
        mode_frame.pack(fill=tk.X, pady=10, padx=20)
        
        ttkb.Label(mode_frame, text="复习模式:", font=("Microsoft YaHei", 12, "bold")).pack(side=tk.LEFT, padx=10)
        
        mode_var = tk.StringVar(value="card")
        modes = [
            ("卡片模式", "card"),
            ("列表模式", "list"),
            ("沉浸式模式", "immersive")
        ]
        
        for text, value in modes:
            ttkb.Radiobutton(
                mode_frame, 
                text=text, 
                variable=mode_var, 
                value=value,
                command=lambda: self.show_review_mode(mode_var.get(), today_review_list, all_mistakes, next_review_dict)
            ).pack(side=tk.LEFT, padx=20)
        
        # 显示默认模式
        self.show_review_mode("card", today_review_list, all_mistakes, next_review_dict)
    
    def show_review_mode(self, mode, today_review_list, all_mistakes, next_review_dict):
        """显示不同的复习模式"""
        # 清空内容区域（保留标题和模式选择）
        for widget in self.content_frame.winfo_children():
            if widget.winfo_class() not in ['Label', 'Frame'] or '模式' not in widget.winfo_children()[0].cget('text'):
                if widget.winfo_class() != 'Label' or '复习计划' not in widget.cget('text'):
                    widget.destroy()
        
        # 重新加载数据确保获取最新的AI解析
        updated_today_review_list = get_today_review_list()
        updated_data = load_data()
        updated_all_mistakes = updated_data.get("mistakes", [])
        updated_next_review_dict = updated_data.get("next_review", {})
        
        if mode == "card":
            self.show_card_mode(updated_today_review_list, updated_all_mistakes, updated_next_review_dict)
        elif mode == "list":
            self.show_list_mode(updated_today_review_list, updated_all_mistakes, updated_next_review_dict)
        elif mode == "immersive":
            self.show_immersive_mode(updated_today_review_list)
    
    def show_card_mode(self, today_review_list, all_mistakes, next_review_dict):
        """显示卡片模式"""
        # 今日待复习卡片
        today_frame = ttkb.LabelFrame(self.content_frame, text="📅 今日待复习")
        today_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=20, ipady=10)
        
        if not today_review_list:
            # 显示今日无复习任务，但仍然显示统计信息
            self.show_no_review_summary(today_frame)
            return
        
        # 卡片容器
        cards_frame = ttkb.Frame(today_frame)
        cards_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 卡片翻页控制
        self.current_card_index = 0
        self.review_list = today_review_list
        
        # 翻页按钮（先创建，再显示卡片）
        nav_frame = ttkb.Frame(today_frame)
        nav_frame.pack(fill=tk.X, pady=10)
        
        ttkb.Button(
            nav_frame, 
            text="上一题", 
            command=lambda: self.navigate_card(-1, cards_frame),
            bootstyle="info-outline"
        ).pack(side=tk.LEFT, padx=10)
        
        self.card_status = ttkb.Label(
            nav_frame, 
            text=f"1/{len(self.review_list)}",
            font=("Microsoft YaHei", 12, "bold")
        )
        self.card_status.pack(side=tk.LEFT, padx=20)
        
        ttkb.Button(
            nav_frame, 
            text="下一题", 
            command=lambda: self.navigate_card(1, cards_frame),
            bootstyle="info-outline"
        ).pack(side=tk.LEFT, padx=10)
        
        ttkb.Button(
            nav_frame, 
            text="标记已掌握", 
            command=lambda: self.mark_mastered(cards_frame),
            bootstyle="success"
        ).pack(side=tk.RIGHT, padx=10)
        
        ttkb.Button(
            nav_frame, 
            text="需要重学", 
            command=lambda: self.mark_need_relearn(cards_frame),
            bootstyle="danger"
        ).pack(side=tk.RIGHT, padx=10)
        
        # 显示当前卡片（在创建card_status之后）
        self.show_review_card(cards_frame, 0)
    
    def show_review_card(self, parent, index):
        """显示复习卡片"""
        # 清空卡片区域
        for widget in parent.winfo_children():
            widget.destroy()
        
        if 0 <= index < len(self.review_list):
            mistake = self.review_list[index]
            
            # 卡片容器 - 增强设计
            card = ttkb.Frame(
                parent, 
                bootstyle="primary-card",
                relief="raised",
                borderwidth=2
            )
            # 使用place布局以便能够拖拽
            card.place(relx=0, rely=0, relwidth=1, relheight=1)
            
            # 添加鼠标拖拽事件
            card.bind("<Button-1>", self.on_card_press)
            card.bind("<B1-Motion>", lambda e, c=card: self.on_card_drag(e, c, parent))
            card.bind("<ButtonRelease-1>", lambda e, c=card: self.on_card_release(e, c, parent))
            
            # 卡片内容
            card_inner = ttkb.Frame(card, padding=25)
            card_inner.pack(fill=tk.BOTH, expand=True)
            
            # 卡片头部 - 学科和知识点
            header_frame = ttkb.Frame(card_inner)
            header_frame.pack(fill=tk.X, pady=10)
            
            subject_label = ttkb.Label(
                header_frame, 
                text=f"📚 {mistake['subject']}",
                font=("Microsoft YaHei", 12, "bold"),
                bootstyle="primary"
            )
            subject_label.pack(side=tk.LEFT, padx=10)
            
            knowledge_label = ttkb.Label(
                header_frame, 
                text=f"🎯 {', '.join(mistake['knowledge_points'])}",
                font=("Microsoft YaHei", 11)
            )
            knowledge_label.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
            
            # 题目
            question_frame = ttkb.LabelFrame(card_inner, text="题目")
            question_frame.pack(fill=tk.X, pady=10)
            
            question_label = ttkb.Label(
                question_frame, 
                text=mistake["question"],
                font=("Microsoft YaHei", 14, "bold"),
                wraplength=750,
                justify=tk.LEFT
            )
            question_label.pack(anchor=tk.W, pady=10, padx=10)
            
            # 错误分析
            error_frame = ttkb.LabelFrame(card_inner, text="错误分析")
            error_frame.pack(fill=tk.X, pady=10)
            
            error_reasons = mistake.get("error_reasons", [])
            if error_reasons:
                error_text = "、".join(error_reasons)
            else:
                error_text = "未记录"
            
            error_label = ttkb.Label(
                error_frame, 
                text=f"❌ 错误原因: {error_text}",
                font=("Microsoft YaHei", 12),
                bootstyle="danger"
            )
            error_label.pack(anchor=tk.W, pady=5, padx=10)
            
            # 答题区域
            answer_frame = ttkb.LabelFrame(card_inner, text="答题")
            answer_frame.pack(fill=tk.X, pady=10)
            
            answer_inner = ttkb.Frame(answer_frame, padding=10)
            answer_inner.pack(fill=tk.X)
            
            ttkb.Label(answer_inner, text="你的答案:", font=("Microsoft YaHei", 12)).pack(side=tk.LEFT, padx=5, pady=5)
            self.answer_entry = ttkb.Entry(answer_inner, width=60, font=("Microsoft YaHei", 12))
            self.answer_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True, pady=5)
            
            ttkb.Button(
                answer_inner, 
                text="✓ 提交", 
                command=lambda mid=mistake['id']: self.check_answer_card(mid),
                bootstyle="success"
            ).pack(side=tk.LEFT, padx=10, pady=5)
            
            # AI解析和操作按钮区域
            action_frame = ttkb.Frame(card_inner)
            action_frame.pack(fill=tk.X, pady=10)
            
            # AI解析按钮
            if mistake.get("ai_analysis"):
                ttkb.Button(
                    action_frame, 
                    text="📝 查看AI解析", 
                    command=lambda m=mistake: self.show_ai_analysis(m),
                    bootstyle="info-outline",
                    width=15
                ).pack(side=tk.LEFT, padx=10, pady=5)
            
            # 知识点关联按钮
            ttkb.Button(
                action_frame, 
                text="🔗 知识点关联", 
                command=lambda m=mistake: self.show_knowledge_relations(m),
                bootstyle="warning-outline",
                width=15
            ).pack(side=tk.LEFT, padx=10, pady=5)
            
            # 卡片底部 - 复习信息
            footer_frame = ttkb.Frame(card_inner)
            footer_frame.pack(fill=tk.X, pady=10)
            
            review_count = mistake.get("review_count", 0)
            last_review = mistake.get("last_review", "从未")
            
            footer_label = ttkb.Label(
                footer_frame, 
                text=f"📖 复习次数: {review_count} | 🕒 上次复习: {last_review}",
                font=("Microsoft YaHei", 10)
            )
            footer_label.pack(anchor=tk.W, padx=10)
            
            # 更新卡片状态
            self.card_status.config(text=f"{index + 1}/{len(self.review_list)}")
            self.current_card_index = index
    
    def navigate_card(self, direction, parent):
        """导航到上一题或下一题"""
        new_index = self.current_card_index + direction
        if 0 <= new_index < len(self.review_list):
            self.show_review_card(parent, new_index)
    
    def check_answer_card(self, mistake_id):
        """检查答案"""
        user_answer = self.answer_entry.get().strip()
        if not user_answer:
            messagebox.showinfo("提示", "请输入答案")
            return
        
        data = load_data()
        correct_answer = ""
        for m in data.get("mistakes", []):
            if str(m["id"]) == mistake_id:
                correct_answer = m["correct_answer"]
                break
        
        is_correct = user_answer == correct_answer
        update_review_status(mistake_id, is_correct)
        
        if is_correct:
            messagebox.showinfo("正确", "✅ 回答正确！")
        else:
            messagebox.showinfo("错误", f"❌ 回答错误，正确答案是: {correct_answer}")
    
    def mark_mastered(self, parent):
        """标记为已掌握"""
        if 0 <= self.current_card_index < len(self.review_list):
            mistake = self.review_list[self.current_card_index]
            update_review_status(str(mistake["id"]), True)
            messagebox.showinfo("成功", "✅ 已标记为已掌握")
            # 移除已掌握的题目
            self.review_list.pop(self.current_card_index)
            if self.review_list:
                new_index = min(self.current_card_index, len(self.review_list) - 1)
                self.show_review_card(parent, new_index)
            else:
                parent.pack_forget()
                self.show_review_completion_summary(parent.master)
    
    def mark_need_relearn(self, parent):
        """标记为需要重学"""
        if 0 <= self.current_card_index < len(self.review_list):
            mistake = self.review_list[self.current_card_index]
            update_review_status(str(mistake["id"]), False)
            messagebox.showinfo("成功", "⚠️ 已标记为需要重学")
    
    def show_no_review_summary(self, parent):
        """显示今日无复习任务时的统计信息"""
        self._show_review_summary(parent, completed=False)
    
    def show_review_completion_summary(self, parent):
        """显示复习完成后的统计信息"""
        self._show_review_summary(parent, completed=True)
    
    def _show_review_summary(self, parent, completed=True):
        """显示复习统计信息的通用方法"""
        from datetime import datetime, timedelta
        
        # 清空父容器
        for widget in parent.winfo_children():
            widget.destroy()
        
        # 加载数据
        data = load_data()
        all_mistakes = data.get("mistakes", [])
        next_review_dict = data.get("next_review", {})
        
        # 创建完成总结框架
        summary_frame = ttkb.Frame(parent, padding=30)
        summary_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题 - 根据是否完成显示不同内容
        if completed:
            title_text = "🎉 恭喜完成今日复习！"
            title_style = "success"
        else:
            title_text = "📋 今日暂无复习任务"
            title_style = "info"
        
        title_label = ttkb.Label(
            summary_frame,
            text=title_text,
            font=("Microsoft YaHei", 20, "bold"),
            bootstyle=title_style
        )
        title_label.pack(pady=20)
        
        # 统计信息
        stats_frame = ttkb.LabelFrame(summary_frame, text="📊 复习统计")
        stats_frame.pack(fill=tk.X, pady=15, padx=20)
        
        # 计算统计信息
        total_mistakes = len(all_mistakes)
        reviewed_today = sum(1 for m in all_mistakes if m.get("last_review") == datetime.now().strftime("%Y-%m-%d"))
        mastered_count = sum(1 for m in all_mistakes if m.get("review_count", 0) >= 6)  # 6次复习后视为掌握
        
        stats_text = f"""
总错题数: {total_mistakes} 道
今日已复习: {reviewed_today} 道
已完全掌握: {mastered_count} 道
        """.strip()
        
        ttkb.Label(
            stats_frame,
            text=stats_text,
            font=("Microsoft YaHei", 12),
            justify=tk.LEFT
        ).pack(anchor=tk.W, pady=10)
        
        # 下次复习时间表
        schedule_frame = ttkb.LabelFrame(summary_frame, text="📅 下次复习计划")
        schedule_frame.pack(fill=tk.BOTH, expand=True, pady=15, padx=20)
        
        # 创建表格
        columns = ("题目", "下次复习时间", "剩余次数")
        tree = ttkb.Treeview(schedule_frame, columns=columns, show="headings", height=10)
        
        # 设置列
        tree.heading("题目", text="题目")
        tree.heading("下次复习时间", text="下次复习时间")
        tree.heading("剩余次数", text="剩余复习次数")
        
        tree.column("题目", width=400)
        tree.column("下次复习时间", width=150, anchor=tk.CENTER)
        tree.column("剩余次数", width=100, anchor=tk.CENTER)
        
        # 添加滚动条
        scrollbar = ttkb.Scrollbar(schedule_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 填充数据
        for mistake in all_mistakes:
            mistake_id = str(mistake["id"])
            next_review_date = next_review_dict.get(mistake_id, "未知")
            review_count = mistake.get("review_count", 0)
            remaining = max(0, 6 - review_count)  # 假设总共6次复习
            
            # 截断题目文本
            question_text = mistake["question"][:50] + "..." if len(mistake["question"]) > 50 else mistake["question"]
            
            tree.insert("", tk.END, values=(
                question_text,
                next_review_date,
                f"{remaining} 次"
            ))
        
        # 按钮
        button_frame = ttkb.Frame(summary_frame)
        button_frame.pack(pady=20)
        
        ttkb.Button(
            button_frame,
            text="返回主界面",
            command=self.show_main_page,
            bootstyle="primary",
            width=15
        ).pack(side=tk.LEFT, padx=10)
        
        ttkb.Button(
            button_frame,
            text="查看完整统计",
            command=self.show_statistics_page,
            bootstyle="info-outline",
            width=15
        ).pack(side=tk.LEFT, padx=10)
    
    def on_card_press(self, event):
        """鼠标按下事件"""
        self.card_press_x = event.x
        self.card_press_y = event.y
    
    def on_card_drag(self, event, card, parent):
        """鼠标拖拽事件"""
        dx = event.x - self.card_press_x
        
        # 限制拖拽距离
        if abs(dx) > 300:
            return
        
        # 移动卡片
        card.place_configure(x=dx)
    
    def on_card_release(self, event, card, parent):
        """鼠标释放事件"""
        dx = event.x - self.card_press_x
        
        # 重置卡片位置
        card.place_configure(x=0)
        
        # 检测滑动方向
        if abs(dx) > 100:  # 滑动阈值
            if dx > 0:  # 向右滑动
                # 标记为已掌握
                self.mark_mastered(parent)
            else:  # 向左滑动
                # 标记为需要重学
                self.mark_need_relearn(parent)
    
    def show_ai_analysis(self, mistake):
        """显示AI解析"""
        analysis_window = ttkb.Toplevel(self.root)
        analysis_window.title("AI解析")
        analysis_window.geometry("850x650")
        analysis_window.transient(self.root)
        analysis_window.grab_set()  # 模态窗口
        
        analysis_frame = ttkb.Frame(analysis_window, padding=20)
        analysis_frame.pack(fill=tk.BOTH, expand=True)
        
        # 错题信息
        info_frame = ttkb.LabelFrame(analysis_frame, text="错题信息")
        info_frame.pack(fill=tk.X, pady=10)
        
        info_inner = ttkb.Frame(info_frame, padding=10)
        info_inner.pack(fill=tk.X)
        
        ttkb.Label(info_inner, text=f"学科: {mistake['subject']}", font=("Microsoft YaHei", 12)).pack(anchor=tk.W, pady=2)
        ttkb.Label(info_inner, text=f"知识点: {', '.join(mistake['knowledge_points'])}", font=("Microsoft YaHei", 12)).pack(anchor=tk.W, pady=2)
        ttkb.Label(info_inner, text=f"错误原因: {', '.join(mistake['error_reasons'])}", font=("Microsoft YaHei", 12), bootstyle="danger").pack(anchor=tk.W, pady=2)
        ttkb.Label(info_inner, text=f"正确答案: {mistake['correct_answer']}", font=("Microsoft YaHei", 12), bootstyle="success").pack(anchor=tk.W, pady=2)
        ttkb.Label(info_inner, text=f"错误答案: {mistake['wrong_answer']}", font=("Microsoft YaHei", 12), bootstyle="danger").pack(anchor=tk.W, pady=2)
        
        # AI分析结果
        analysis_frame = ttkb.LabelFrame(analysis_frame, text="AI深度解析")
        analysis_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        analysis_inner = ttkb.Frame(analysis_frame, padding=10)
        analysis_inner.pack(fill=tk.BOTH, expand=True)
        
        analysis_text = tk.Text(analysis_inner, wrap=tk.WORD, font=("Microsoft YaHei", 12), spacing1=5, spacing2=3, spacing3=5)
        analysis_text.insert(tk.END, mistake.get("ai_analysis", "暂无分析结果"))
        analysis_text.config(state=tk.DISABLED)
        
        scrollbar = ttkb.Scrollbar(analysis_inner, command=analysis_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        analysis_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        analysis_text.config(yscrollcommand=scrollbar.set)
        
        # 操作按钮
        button_frame = ttkb.Frame(analysis_window)
        button_frame.pack(fill=tk.X, pady=10, padx=20)
        
        ttkb.Button(
            button_frame, 
            text="🔗 查看知识点关联", 
            command=lambda m=mistake: self.show_knowledge_relations(m),
            bootstyle="warning-outline",
            width=18
        ).pack(side=tk.LEFT, padx=10)
        
        ttkb.Button(
            button_frame, 
            text="关闭", 
            command=analysis_window.destroy,
            bootstyle="secondary",
            width=10
        ).pack(side=tk.RIGHT, padx=10)
    
    def show_knowledge_relations(self, mistake):
        """显示知识点关联内容"""
        knowledge_window = ttkb.Toplevel(self.root)
        knowledge_window.title("知识点关联")
        knowledge_window.geometry("800x600")
        knowledge_window.transient(self.root)
        
        knowledge_frame = ttkb.Frame(knowledge_window, padding=20)
        knowledge_frame.pack(fill=tk.BOTH, expand=True)
        
        # 知识点列表
        knowledge_points = mistake.get("knowledge_points", [])
        
        if not knowledge_points:
            ttkb.Label(knowledge_frame, text="暂无知识点关联", font=("Microsoft YaHei", 14)).pack(pady=50)
            return
        
        # 查找相关错题
        data = load_data()
        all_mistakes = data.get("mistakes", [])
        
        for knowledge in knowledge_points:
            # 知识点标题
            knowledge_label = ttkb.Label(
                knowledge_frame, 
                text=f"🔗 知识点: {knowledge}",
                font=("Microsoft YaHei", 14, "bold"),
                bootstyle="primary"
            )
            knowledge_label.pack(anchor=tk.W, pady=10)
            
            # 相关错题
            related_mistakes = []
            for m in all_mistakes:
                if knowledge in m.get("knowledge_points", []) and str(m["id"]) != str(mistake["id"]):
                    related_mistakes.append(m)
            
            if related_mistakes:
                related_frame = ttkb.LabelFrame(knowledge_frame, text="相关错题")
                related_frame.pack(fill=tk.X, pady=5, padx=10)
                
                for i, related_mistake in enumerate(related_mistakes[:3]):  # 最多显示3个相关错题
                    ttkb.Label(
                        related_frame, 
                        text=f"{i+1}. {related_mistake['question'][:100]}...",
                        font=("Microsoft YaHei", 11),
                        wraplength=700
                    ).pack(anchor=tk.W, pady=3, padx=10)
            else:
                ttkb.Label(
                    knowledge_frame, 
                    text="暂无相关错题",
                    font=("Microsoft YaHei", 12),
                    bootstyle="info"
                ).pack(anchor=tk.W, pady=5, padx=10)
            
            # 分隔线
            ttkb.Separator(knowledge_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
    
    def show_list_mode(self, today_review_list, all_mistakes, next_review_dict):
        """显示列表模式"""
        # 今日待复习
        today_review_frame = ttkb.LabelFrame(self.content_frame, text="📅 今日待复习")
        today_review_frame.pack(fill=tk.X, pady=10, padx=20, ipady=10)
        
        if not today_review_list:
            ttkb.Label(today_review_frame, text="今日暂无待复习错题", font=("Microsoft YaHei", 12)).pack(pady=15)
        else:
            # 创建今日复习列表
            for i, mistake in enumerate(today_review_list):
                card = ttkb.Frame(
                    today_review_frame, 
                    bootstyle="success-card"
                )
                card.pack(fill=tk.X, pady=8, padx=5)
                card_inner = ttkb.Frame(card, padding=12)
                card_inner.pack(fill=tk.X)
                
                ttkb.Label(
                    card_inner, 
                    text=f"{i+1}. {mistake['question'][:80]}...",
                    font=("Microsoft YaHei", 12, "bold"),
                    wraplength=800
                ).pack(anchor=tk.W, pady=3)
                
                ttkb.Label(
                    card_inner, 
                    text=f"学科: {mistake['subject']} | 知识点: {', '.join(mistake['knowledge_points'])}",
                    font=("Microsoft YaHei", 11)
                ).pack(anchor=tk.W, pady=2)
                
                ttkb.Label(
                    card_inner, 
                    text="⚠️ 今日必须复习！",
                    font=("Microsoft YaHei", 10, "bold"),
                    bootstyle="danger"
                ).pack(anchor=tk.W, pady=3)
                
                # 答题区域
                answer_frame = ttkb.Frame(card_inner)
                answer_frame.pack(fill=tk.X, pady=8)
                
                ttkb.Label(answer_frame, text="你的答案:", font=("Microsoft YaHei", 11)).pack(side=tk.LEFT, padx=5)
                answer_entry = ttkb.Entry(answer_frame, width=50)
                answer_entry.pack(side=tk.LEFT, padx=10)
                
                # 判分按钮
                def check_answer(mistake_id, entry):
                    user_answer = entry.get().strip()
                    if not user_answer:
                        messagebox.showinfo("提示", "请输入答案")
                        return
                    
                    data = load_data()
                    correct_answer = ""
                    for m in data.get("mistakes", []):
                        if str(m["id"]) == mistake_id:
                            correct_answer = m["correct_answer"]
                            break
                    
                    is_correct = user_answer == correct_answer
                    update_review_status(mistake_id, is_correct)
                    
                    if is_correct:
                        messagebox.showinfo("正确", "✅ 回答正确！")
                    else:
                        messagebox.showinfo("错误", f"❌ 回答错误，正确答案是: {correct_answer}")
                    
                    # 刷新页面
                    self.show_review_page()
                
                ttkb.Button(
                    answer_frame, 
                    text="✓ 判分", 
                    command=lambda mid=mistake['id'], e=answer_entry: check_answer(mid, e),
                    bootstyle="success",
                    width=10
                ).pack(side=tk.LEFT, padx=10)
        
        # 所有错题复习状态
        all_review_frame = ttkb.LabelFrame(self.content_frame, text="📊 所有错题复习状态")
        all_review_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=20, ipady=10)
        
        # 创建树状视图显示所有错题
        columns = ("id", "subject", "question", "days_left", "review_count")
        tree = ttk.Treeview(all_review_frame, columns=columns, show="headings", height=10)
        
        tree.heading("id", text="ID", anchor=tk.CENTER)
        tree.heading("subject", text="学科", anchor=tk.CENTER)
        tree.heading("question", text="题目", anchor=tk.W)
        tree.heading("days_left", text="距下次复习", anchor=tk.CENTER)
        tree.heading("review_count", text="复习次数", anchor=tk.CENTER)
        
        tree.column("id", width=80, anchor=tk.CENTER)
        tree.column("subject", width=100, anchor=tk.CENTER)
        tree.column("question", width=450, anchor=tk.W)
        tree.column("days_left", width=120, anchor=tk.CENTER)
        tree.column("review_count", width=100, anchor=tk.CENTER)
        
        # 添加滚动条
        scrollbar_y = ttkb.Scrollbar(all_review_frame, orient=tk.VERTICAL, command=tree.yview)
        scrollbar_x = ttkb.Scrollbar(all_review_frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 计算距离下次复习的天数
        now = datetime.datetime.now()
        
        for mistake in all_mistakes:
            mistake_id = str(mistake["id"])
            next_review_str = next_review_dict.get(mistake_id, "")
            
            days_left = "未安排"
            bootstyle = ""
            
            if next_review_str:
                try:
                    next_review_time = datetime.datetime.strptime(next_review_str, "%Y-%m-%d %H:%M:%S")
                    delta = next_review_time - now
                    
                    if delta.days < 0:
                        days_left = "已逾期"
                        bootstyle = "danger"
                    elif delta.days == 0:
                        days_left = "今日"
                        bootstyle = "warning"
                    else:
                        days_left = f"{delta.days} 天"
                        bootstyle = "success"
                except:
                    pass
            
            tree.insert("", tk.END, values=(
                mistake["id"],
                mistake["subject"],
                mistake["question"][:50] + "..." if len(mistake["question"]) > 50 else mistake["question"],
                days_left,
                mistake.get("review_count", 0)
            ))
    
    def show_immersive_mode(self, today_review_list):
        """显示沉浸式复习模式"""
        # 创建全屏窗口
        immersive_window = ttkb.Toplevel(self.root)
        immersive_window.title("沉浸式复习")
        immersive_window.geometry("1200x800")
        immersive_window.transient(self.root)
        immersive_window.grab_set()  # 模态窗口
        
        # 设置护眼模式柔和背景色
        immersive_window.configure(bg="#f8f9fa")
        
        # 护眼模式提示
        ttkb.Label(
            immersive_window, 
            text="🎯 沉浸式复习模式 - 护眼模式已开启",
            font=("Microsoft YaHei", 14, "bold"),
            bootstyle="info"
        ).pack(pady=20)
        
        if not today_review_list:
            ttkb.Label(
                immersive_window, 
                text="今日暂无待复习错题", 
                font=("Microsoft YaHei", 16)
            ).pack(pady=100)
            ttkb.Button(
                immersive_window, 
                text="关闭", 
                command=immersive_window.destroy,
                bootstyle="secondary",
                width=15
            ).pack(pady=20)
            return
        
        # 卡片容器 - 减少干扰
        card_frame = ttkb.Frame(immersive_window, padding=40, bootstyle="light")
        card_frame.pack(fill=tk.BOTH, expand=True, padx=80, pady=40)
        
        # 卡片翻页控制
        self.immersive_index = 0
        self.immersive_list = today_review_list
        
        # 显示当前卡片
        self.show_immersive_card(card_frame, 0)
        
        # 翻页按钮 - 简洁设计
        nav_frame = ttkb.Frame(immersive_window, bg="#f8f9fa")
        nav_frame.pack(fill=tk.X, pady=20, padx=80)
        
        ttkb.Button(
            nav_frame, 
            text="上一题", 
            command=lambda: self.navigate_immersive(-1, card_frame),
            bootstyle="info-outline",
            width=12
        ).pack(side=tk.LEFT, padx=20)
        
        self.immersive_status = ttkb.Label(
            nav_frame, 
            text=f"{self.immersive_index + 1}/{len(self.immersive_list)}",
            font=("Microsoft YaHei", 14, "bold"),
            bg="#f8f9fa"
        )
        self.immersive_status.pack(side=tk.LEFT, padx=40)
        
        ttkb.Button(
            nav_frame, 
            text="下一题", 
            command=lambda: self.navigate_immersive(1, card_frame),
            bootstyle="info-outline",
            width=12
        ).pack(side=tk.LEFT, padx=20)
        
        # 快捷操作按钮
        action_frame = ttkb.Frame(nav_frame, bg="#f8f9fa")
        action_frame.pack(side=tk.RIGHT, padx=20)
        
        ttkb.Button(
            action_frame, 
            text="✅ 标记已掌握", 
            command=lambda: self.mark_immersive_mastered(card_frame, immersive_window),
            bootstyle="success",
            width=12
        ).pack(side=tk.RIGHT, padx=10)
        
        ttkb.Button(
            action_frame, 
            text="⚠️ 需要重学", 
            command=lambda: self.mark_immersive_relearn(card_frame),
            bootstyle="danger",
            width=12
        ).pack(side=tk.RIGHT, padx=10)
        
        ttkb.Button(
            action_frame, 
            text="完成复习", 
            command=immersive_window.destroy,
            bootstyle="secondary",
            width=12
        ).pack(side=tk.RIGHT, padx=10)
    
    def show_immersive_card(self, parent, index):
        """显示沉浸式复习卡片"""
        # 清空卡片区域
        for widget in parent.winfo_children():
            widget.destroy()
        
        if 0 <= index < len(self.immersive_list):
            mistake = self.immersive_list[index]
            
            # 卡片容器 - 沉浸式设计
            card = ttkb.Frame(
                parent, 
                bootstyle="light-card",
                relief="raised",
                borderwidth=2
            )
            card.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
            
            # 卡片内容
            card_inner = ttkb.Frame(card, padding=40)
            card_inner.pack(fill=tk.BOTH, expand=True)
            
            # 学科和知识点 - 简洁显示
            header_frame = ttkb.Frame(card_inner)
            header_frame.pack(fill=tk.X, pady=15)
            
            ttkb.Label(
                header_frame, 
                text=f"📚 {mistake['subject']} | 🎯 {', '.join(mistake['knowledge_points'])}",
                font=("Microsoft YaHei", 12, "bold"),
                bootstyle="primary"
            ).pack(anchor=tk.W)
            
            # 题目 - 大号字体
            question_frame = ttkb.LabelFrame(card_inner, text="题目")
            question_frame.pack(fill=tk.X, pady=20)
            
            question_label = ttkb.Label(
                question_frame, 
                text=mistake["question"],
                font=("Microsoft YaHei", 16, "bold"),
                wraplength=850,
                justify=tk.LEFT
            )
            question_label.pack(anchor=tk.W, pady=15, padx=15)
            
            # 错误原因 - 醒目显示
            error_frame = ttkb.LabelFrame(card_inner, text="错误原因")
            error_frame.pack(fill=tk.X, pady=15)
            
            error_reasons = mistake.get("error_reasons", [])
            if error_reasons:
                error_text = "、".join(error_reasons)
            else:
                error_text = "未记录"
            
            error_label = ttkb.Label(
                error_frame, 
                text=error_text,
                font=("Microsoft YaHei", 14),
                bootstyle="danger"
            )
            error_label.pack(anchor=tk.W, pady=10, padx=15)
            
            # 答题区域 - 居中设计
            answer_frame = ttkb.LabelFrame(card_inner, text="答题")
            answer_frame.pack(fill=tk.X, pady=20)
            
            answer_inner = ttkb.Frame(answer_frame, padding=15)
            answer_inner.pack(fill=tk.X)
            
            ttkb.Label(answer_inner, text="你的答案:", font=("Microsoft YaHei", 14)).pack(side=tk.LEFT, padx=10, pady=5)
            self.immersive_answer = ttkb.Entry(answer_inner, width=60, font=("Microsoft YaHei", 14))
            self.immersive_answer.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True, pady=5)
            
            ttkb.Button(
                answer_inner, 
                text="✓ 提交", 
                command=lambda mid=mistake['id']: self.check_immersive_answer(mid),
                bootstyle="success",
                width=10
            ).pack(side=tk.LEFT, padx=10, pady=5)
            
            # AI解析按钮 - 一键展开
            if mistake.get("ai_analysis"):
                ttkb.Button(
                    card_inner, 
                    text="📝 一键展开AI解析", 
                    command=lambda m=mistake: self.show_ai_analysis(m),
                    bootstyle="info-outline",
                    width=20
                ).pack(side=tk.LEFT, padx=10, pady=20)
            
            # 更新状态
            self.immersive_status.config(text=f"{index + 1}/{len(self.immersive_list)}")
            self.immersive_index = index
    
    def navigate_immersive(self, direction, parent):
        """导航沉浸式复习"""
        new_index = self.immersive_index + direction
        if 0 <= new_index < len(self.immersive_list):
            self.show_immersive_card(parent, new_index)
    
    def check_immersive_answer(self, mistake_id):
        """检查沉浸式模式答案"""
        user_answer = self.immersive_answer.get().strip()
        if not user_answer:
            messagebox.showinfo("提示", "请输入答案")
            return
        
        data = load_data()
        correct_answer = ""
        for m in data.get("mistakes", []):
            if str(m["id"]) == mistake_id:
                correct_answer = m["correct_answer"]
                break
        
        is_correct = user_answer == correct_answer
        update_review_status(mistake_id, is_correct)
        
        if is_correct:
            messagebox.showinfo("正确", "✅ 回答正确！")
        else:
            messagebox.showinfo("错误", f"❌ 回答错误，正确答案是: {correct_answer}")
    
    def mark_immersive_mastered(self, parent, window):
        """在沉浸式模式中标记为已掌握"""
        if 0 <= self.immersive_index < len(self.immersive_list):
            mistake = self.immersive_list[self.immersive_index]
            update_review_status(str(mistake["id"]), True)
            messagebox.showinfo("成功", "✅ 已标记为已掌握")
            # 移除已掌握的题目
            self.immersive_list.pop(self.immersive_index)
            if self.immersive_list:
                new_index = min(self.immersive_index, len(self.immersive_list) - 1)
                self.show_immersive_card(parent, new_index)
            else:
                parent.pack_forget()
                ttkb.Label(parent.master, text="🎉 今日复习完成！", font=("Microsoft YaHei", 16, "bold"), bootstyle="success").pack(pady=50)
    
    def mark_immersive_relearn(self, parent):
        """在沉浸式模式中标记为需要重学"""
        if 0 <= self.immersive_index < len(self.immersive_list):
            mistake = self.immersive_list[self.immersive_index]
            update_review_status(str(mistake["id"]), False)
            messagebox.showinfo("成功", "⚠️ 已标记为需要重学")
    
    def show_statistics_page(self):
        """显示统计分析界面"""
        self.clear_content()
        
        # 装饰性横幅 - 增强设计
        banner_frame = ttkb.Frame(self.content_frame, bootstyle="warning")
        banner_frame.pack(fill=tk.X, pady=10)
        
        stats_tips = [
            "� 数据驱动学习，科学提升成绩",
            "🎯 找出薄弱环节，针对性复习",
            "� 追踪学习进度，见证成长历程"
        ]
        
        tip = random.choice(stats_tips)
        
        tip_label = ttkb.Label(
            banner_frame, 
            text=tip, 
            font=("Microsoft YaHei", 12, "bold"),
            bootstyle="inverse"
        )
        tip_label.pack(pady=8)
        
        # 标题 - 添加动画
        title = ttkb.Label(
            self.content_frame, 
            text="📊 统计分析", 
            font=("Microsoft YaHei", 32, "bold"),
            bootstyle="warning"
        )
        title.pack(pady=20)
        
        # 添加标题动画
        self.animate_title(title)
        
        # 更新统计信息
        statistics = update_statistics()
        
        # 统计卡片 - 增强设计
        stats_frame = ttkb.Frame(self.content_frame)
        stats_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        # 总错题数
        total_card = ttkb.Frame(
            stats_frame, 
            bootstyle="primary-card",
            relief="raised",
            borderwidth=3
        )
        total_card.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        
        # 添加悬停效果
        total_card.bind("<Enter>", lambda e, c=total_card: self.on_card_hover(c, True))
        total_card.bind("<Leave>", lambda e, c=total_card: self.on_card_hover(c, False))
        
        total_inner = ttkb.Frame(total_card, padding=25)
        total_inner.pack(fill=tk.BOTH, expand=True)
        
        ttkb.Label(total_inner, text="总错题数", font=("Microsoft YaHei", 18, "bold")).pack(pady=12)
        total_label = ttkb.Label(total_inner, text="0", font=("Microsoft YaHei", 36, "bold"), bootstyle="primary")
        total_label.pack()
        
        # 添加数字动画
        self.animate_stat_value(total_label, 0, statistics["total"])
        
        # 复习完成率
        completion_card = ttkb.Frame(
            stats_frame, 
            bootstyle="success-card",
            relief="raised",
            borderwidth=3
        )
        completion_card.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        
        # 添加悬停效果
        completion_card.bind("<Enter>", lambda e, c=completion_card: self.on_card_hover(c, True))
        completion_card.bind("<Leave>", lambda e, c=completion_card: self.on_card_hover(c, False))
        
        completion_inner = ttkb.Frame(completion_card, padding=25)
        completion_inner.pack(fill=tk.BOTH, expand=True)
        
        ttkb.Label(completion_inner, text="复习完成率", font=("Microsoft YaHei", 18, "bold")).pack(pady=12)
        completion_label = ttkb.Label(completion_inner, text="0%", font=("Microsoft YaHei", 36, "bold"), bootstyle="success")
        completion_label.pack()
        
        # 添加数字动画
        self.animate_stat_value(completion_label, 0, statistics["review_completion"])
        
        # 学科分布 - 增强设计
        subject_frame = ttkb.LabelFrame(self.content_frame, text="学科分布")
        subject_frame.pack(fill=tk.X, pady=15, padx=20, ipady=15)
        
        if statistics["by_subject"]:
            for subject, count in statistics["by_subject"].items():
                bar_frame = ttkb.Frame(subject_frame)
                bar_frame.pack(fill=tk.X, pady=8)
                
                ttkb.Label(bar_frame, text=subject, width=12, font=("Microsoft YaHei", 12, "bold")).pack(side=tk.LEFT, padx=10)
                
                total = statistics["total"]
                progress = ttkb.Progressbar(
                    bar_frame, 
                    bootstyle="info-striped",
                    length=400, 
                    value=0
                )
                progress.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
                
                # 添加进度条动画
                self.animate_progress(progress, 0, (count/total)*100 if total > 0 else 0)
                
                ttkb.Label(bar_frame, text=f"{count}题", width=8, font=("Microsoft YaHei", 12, "bold")).pack(side=tk.LEFT, padx=10)
        else:
            ttkb.Label(subject_frame, text="暂无数据", font=("Microsoft YaHei", 14)).pack(pady=20)
        
        # 错误原因分布 - 增强设计
        error_frame = ttkb.LabelFrame(self.content_frame, text="错误原因分布")
        error_frame.pack(fill=tk.X, pady=15, padx=20, ipady=15)
        
        if statistics["by_error_type"]:
            total_errors = sum(statistics["by_error_type"].values())
            for error_type, count in statistics["by_error_type"].items():
                bar_frame = ttkb.Frame(error_frame)
                bar_frame.pack(fill=tk.X, pady=8)
                
                ttkb.Label(bar_frame, text=error_type, width=18, font=("Microsoft YaHei", 12, "bold")).pack(side=tk.LEFT, padx=10)
                
                progress = ttkb.Progressbar(
                    bar_frame, 
                    bootstyle="danger-striped",
                    length=400, 
                    value=0
                )
                progress.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
                
                # 添加进度条动画
                self.animate_progress(progress, 0, (count/total_errors)*100 if total_errors > 0 else 0)
                
                ttkb.Label(bar_frame, text=f"{count}次", width=8, font=("Microsoft YaHei", 12, "bold")).pack(side=tk.LEFT, padx=10)
        else:
            ttkb.Label(error_frame, text="暂无数据", font=("Microsoft YaHei", 14)).pack(pady=20)
        
        # 调整网格布局
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)
    
    def show_ai_qa_page(self):
        """显示AI答疑界面"""
        self.clear_content()
        
        # 装饰性横幅 - 增强设计
        banner_frame = ttkb.Frame(self.content_frame, bootstyle="danger")
        banner_frame.pack(fill=tk.X, pady=10)
        
        qa_tips = [
            "❓ 有问题就问，AI老师随时在线",
            "💡 详细描述问题，AI回答更准确",
            "📚 知识盲点，一问便知"
        ]
        
        tip = random.choice(qa_tips)
        
        tip_label = ttkb.Label(
            banner_frame, 
            text=tip, 
            font=("Microsoft YaHei", 12, "bold"),
            bootstyle="inverse"
        )
        tip_label.pack(pady=8)
        
        # 标题 - 添加动画
        title = ttkb.Label(
            self.content_frame, 
            text="💬 AI答疑", 
            font=("Microsoft YaHei", 32, "bold"),
            bootstyle="danger"
        )
        title.pack(pady=20)
        
        # 添加标题动画
        self.animate_title(title)
        
        # 问题输入 - 增强设计
        input_frame = ttkb.LabelFrame(self.content_frame, text="输入问题")
        input_frame.pack(fill=tk.X, pady=15, padx=20, ipady=25)
        
        input_inner = ttkb.Frame(input_frame, padding=10)
        input_inner.pack(fill=tk.X)
        
        self.question_entry = ttkb.Entry(input_inner, width=90, font=("Microsoft YaHei", 14))
        self.question_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        ask_btn = ttkb.Button(
            input_inner, 
            text="🚀 提问", 
            command=self.ask_ai,
            bootstyle="primary",
            width=12
        )
        ask_btn.pack(side=tk.LEFT, padx=10)
        
        # 添加按钮悬停效果
        ask_btn.bind("<Enter>", lambda e, b=ask_btn: b.config(bootstyle="primary"))
        ask_btn.bind("<Leave>", lambda e, b=ask_btn: b.config(bootstyle="primary-outline"))
        
        # 回答区域 - 增强设计
        answer_frame = ttkb.LabelFrame(self.content_frame, text="AI回答")
        answer_frame.pack(fill=tk.BOTH, expand=True, pady=15, padx=20, ipady=25)
        
        answer_inner = ttkb.Frame(answer_frame, padding=10)
        answer_inner.pack(fill=tk.BOTH, expand=True)
        
        self.answer_text = tk.Text(answer_inner, wrap=tk.WORD, font=("Microsoft YaHei", 12), spacing1=8, spacing2=5, spacing3=8)
        self.answer_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        scrollbar = ttkb.Scrollbar(answer_inner, command=self.answer_text.yview, bootstyle="primary")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.answer_text.config(yscrollcommand=scrollbar.set)
        
        # 添加默认提示文本 - 先设置为可编辑，插入文本后再禁用
        self.answer_text.config(state=tk.NORMAL)
        self.answer_text.delete(1.0, tk.END)
        self.answer_text.insert(tk.END, "💡 输入问题并点击提问按钮，AI将为你解答...\n\n")
        self.answer_text.insert(tk.END, "📚 示例问题：\n")
        self.answer_text.insert(tk.END, "- 如何解一元二次方程？\n")
        self.answer_text.insert(tk.END, "- 什么是光合作用？\n")
        self.answer_text.insert(tk.END, "- 如何提高英语听力？")
        self.answer_text.config(state=tk.DISABLED)
    
    def ask_ai(self):
        """向AI提问"""
        question = self.question_entry.get().strip()
        if not question:
            messagebox.showinfo("提示", "请输入问题")
            return
        
        # 检查模型可用性
        if not check_model_availability():
            messagebox.showwarning("警告", "ollama服务未启动，无法使用AI答疑功能")
            return
        
        # 显示加载中
        self.answer_text.delete(1.0, tk.END)
        self.answer_text.insert(tk.END, "AI正在思考，请稍候...")
        self.answer_text.config(state=tk.DISABLED)
        
        # 启动线程进行问答
        def qa_thread():
            answer = answer_question(question)
            
            # 更新界面
            self.answer_text.config(state=tk.NORMAL)
            self.answer_text.delete(1.0, tk.END)
            self.answer_text.insert(tk.END, answer)
            self.answer_text.config(state=tk.DISABLED)
        
        threading.Thread(target=qa_thread).start()
    
    def backup_data(self):
        """备份数据"""
        if backup_data():
            messagebox.showinfo("成功", "数据备份成功")
        else:
            messagebox.showerror("错误", "备份失败")

if __name__ == "__main__":
    root = ttkb.Window(themename="darkly")
    app = SmartMistakeBook(root)
    root.mainloop()