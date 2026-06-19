import requests
import json
import time

# ollama本地接口配置
OLLAMA_API_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "deepseek-r1:7b"

# 备用模型列表（如果deepseek-r1:7b不可用）
FALLBACK_MODELS = ["qwen2.5:7b", "llama3:8b", "mistral:7b", "deepseek-coder:6.7b"]

# 超时设置
TIMEOUT = 120  # 增加超时时间以支持7B模型

def call_ollama(prompt, model=DEFAULT_MODEL, temperature=0.7, max_tokens=1000):
    """调用本地ollama大模型"""
    # 尝试默认模型
    result = _do_ollama_request(prompt, model, temperature, max_tokens)
    
    # 如果失败，尝试备用模型
    if "错误" in result:
        for fallback_model in FALLBACK_MODELS:
            print(f"尝试备用模型: {fallback_model}")
            result = _do_ollama_request(prompt, fallback_model, temperature, max_tokens)
            if "错误" not in result:
                global DEFAULT_MODEL
                DEFAULT_MODEL = fallback_model
                print(f"使用备用模型: {fallback_model}")
                break
    
    return result

def _do_ollama_request(prompt, model, temperature, max_tokens):
    """执行实际的Ollama API请求"""
    try:
        payload = {
            "model": model,
            "prompt": prompt,
            "temperature": temperature,
            "num_predict": max_tokens,
            "stream": False  # 使用非流式响应
        }
        
        response = requests.post(
            OLLAMA_API_URL,
            json=payload,
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("response", "")
        elif response.status_code == 404:
            return f"错误：模型 '{model}' 未找到，请运行 'ollama pull {model}'"
        else:
            return f"API调用失败: {response.status_code}"
    except requests.exceptions.ConnectionError:
        return "错误：无法连接到ollama服务，请确保ollama已启动并运行"
    except requests.exceptions.Timeout:
        return "错误：模型调用超时，请尝试减少max_tokens或使用更小的模型"
    except Exception as e:
        return f"错误：{str(e)}"

def analyze_mistake(question, correct_answer, wrong_answer):
    """使用大模型分析错题"""
    prompt = f"""你是一位专业的中学教师，擅长分析学生的错题。请按照以下要求分析这道错题：

题目：{question}
正确答案：{correct_answer}
学生错误答案：{wrong_answer}

请从以下几个方面进行分析：
1. 错误类型（概念混淆/计算失误/审题不清/逻辑漏洞/方法错误/步骤遗漏）
2. 错因剖析（详细解释学生为什么会犯这个错误）
3. 正确解法（给出完整的解题步骤）
4. 考点讲解（解释本题考查的知识点）
5. 避坑技巧（如何避免类似错误）
6. 思路总结（总结解题思路和方法）

请用通俗易懂的语言，适合中学生理解的方式回答，不要使用过于专业的术语。"""
    
    return call_ollama(prompt)

def generate_similar_questions(question, subject, knowledge_points):
    """生成同类变式题"""
    prompt = f"""你是一位专业的中学教师，请根据以下题目生成1-2道同类变式题：

原题：{question}
学科：{subject}
知识点：{', '.join(knowledge_points)}

要求：
1. 保持相同的知识点和题型
2. 改变题目中的具体数字或情境
3. 确保题目有一定的难度梯度
4. 每道题提供正确答案
5. 用中文表述，适合中学生使用"""
    
    return call_ollama(prompt, max_tokens=1500)

def answer_question(question, context=""):
    """回答学生的问题"""
    prompt = f"""你是一位专业的中学教师，擅长解答学生的问题。请回答以下问题：

问题：{question}

{"上下文：" + context if context else ""}

请用通俗易懂的语言，适合中学生理解的方式回答，不要使用过于专业的术语，确保答案准确、清晰、详细。"""
    
    return call_ollama(prompt)

def check_model_availability():
    """检查模型是否可用"""
    try:
        # 先尝试默认模型
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": DEFAULT_MODEL,
                "prompt": "hi",
                "num_predict": 10,
                "stream": False
            },
            timeout=10
        )
        
        if response.status_code == 200:
            return True
        
        # 尝试备用模型
        for model in FALLBACK_MODELS:
            try:
                response = requests.post(
                    OLLAMA_API_URL,
                    json={
                        "model": model,
                        "prompt": "hi",
                        "num_predict": 10,
                        "stream": False
                    },
                    timeout=10
                )
                if response.status_code == 200:
                    global DEFAULT_MODEL
                    DEFAULT_MODEL = model
                    return True
            except:
                continue
        
        return False
    except Exception as e:
        print(f"模型检查错误: {e}")
        return False

def get_available_models():
    """获取可用的模型列表"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return [m["name"] for m in data.get("models", [])]
        return []
    except:
        return []

def get_current_model():
    """获取当前使用的模型"""
    return DEFAULT_MODEL