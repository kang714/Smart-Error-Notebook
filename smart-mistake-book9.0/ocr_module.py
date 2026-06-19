import pytesseract
from PIL import Image
import re

def ocr_image(image_path):
    """识别图片中的文字"""
    try:
        # 打开图片
        img = Image.open(image_path)
        
        # 使用pytesseract识别文字
        text = pytesseract.image_to_string(img, lang='chi_sim+eng')
        
        # 清理识别结果
        text = clean_ocr_text(text)
        
        # 拆分题目和选项
        result = split_question_options(text)
        
        return result
    except Exception as e:
        print(f"OCR识别失败: {e}")
        return {
            "question": "",
            "options": [],
            "raw_text": ""
        }

def clean_ocr_text(text):
    """清理OCR识别结果"""
    # 移除多余的空行
    lines = text.strip().split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        if line:
            # 移除乱码字符
            line = re.sub(r'[\x00-\x1f\x7f-\xff]', '', line)
            if line:
                cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

def split_question_options(text):
    """拆分题目和选项"""
    lines = text.split('\n')
    question_lines = []
    options = []
    
    # 识别选项的正则表达式
    option_pattern = re.compile(r'^[A-Da-d][.．、)]')
    
    in_question = True
    
    for line in lines:
        if option_pattern.match(line):
            # 找到选项开始
            in_question = False
            # 提取选项内容
            option_text = re.sub(r'^[A-Da-d][.．、)]\s*', '', line)
            options.append(option_text)
        elif in_question:
            # 题目部分
            question_lines.append(line)
        else:
            # 选项的延续（如果选项内容跨行）
            if options:
                options[-1] += ' ' + line
    
    question = ' '.join(question_lines)
    
    return {
        "question": question,
        "options": options,
        "raw_text": text
    }

def extract_answer(text):
    """尝试从文本中提取答案"""
    # 查找答案模式
    answer_patterns = [
        r'答案[:：]\s*([A-Da-d])',
        r'正确答案[:：]\s*([A-Da-d])',
        r'答案是[:：]\s*([A-Da-d])'
    ]
    
    for pattern in answer_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).upper()
    
    return ""
