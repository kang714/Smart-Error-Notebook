import json
import os
import datetime
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 数据存储文件路径
DATA_FILE = "data.json"

# 艾宾浩斯遗忘曲线时间间隔（天）
EBBINGHAUS_INTERVALS = [1, 2, 4, 7, 15, 30]

def load_data():
    """加载错题数据"""
    if not os.path.exists(DATA_FILE):
        # 初始化数据结构
        initial_data = {
            "mistakes": [],
            "next_review": {},
            "statistics": {
                "total": 0,
                "by_subject": {},
                "by_error_type": {},
                "review_completion": 0
            }
        }
        save_data(initial_data)
        return initial_data
    
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载数据失败: {e}")
        return {
            "mistakes": [],
            "next_review": {},
            "statistics": {
                "total": 0,
                "by_subject": {},
                "by_error_type": {},
                "review_completion": 0
            }
        }

def save_data(data):
    """保存错题数据"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存数据失败: {e}")
        return False

def calculate_next_review_time(current_time, review_count):
    """根据艾宾浩斯遗忘曲线计算下次复习时间"""
    if review_count >= len(EBBINGHAUS_INTERVALS):
        # 超过最大间隔后，使用最大间隔
        days = EBBINGHAUS_INTERVALS[-1]
    else:
        days = EBBINGHAUS_INTERVALS[review_count]
    
    next_time = current_time + datetime.timedelta(days=days)
    return next_time.strftime("%Y-%m-%d %H:%M:%S")

def get_today_review_list():
    """获取今日待复习的错题"""
    data = load_data()
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    review_list = []
    
    for mistake_id, next_review in data.get("next_review", {}).items():
        if next_review.startswith(today):
            # 查找对应的错题
            for mistake in data.get("mistakes", []):
                if str(mistake.get("id")) == mistake_id:
                    review_list.append(mistake)
                    break
    
    return review_list

def update_review_status(mistake_id, is_correct):
    """更新复习状态"""
    data = load_data()
    
    # 查找错题
    for mistake in data.get("mistakes", []):
        if str(mistake.get("id")) == mistake_id:
            if is_correct:
                # 答对了，增加复习次数
                mistake["review_count"] = mistake.get("review_count", 0) + 1
                mistake["last_review"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # 计算下次复习时间
                next_review = calculate_next_review_time(
                    datetime.datetime.now(),
                    mistake["review_count"]
                )
                data["next_review"][mistake_id] = next_review
            else:
                # 答错了，重置复习次数
                mistake["review_count"] = 0
                mistake["last_review"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # 重新开始复习周期
                next_review = calculate_next_review_time(
                    datetime.datetime.now(),
                    0
                )
                data["next_review"][mistake_id] = next_review
            break
    
    save_data(data)

def find_similar_mistakes(current_mistake, top_n=3):
    """使用TF-IDF查找相似的错题"""
    data = load_data()
    mistakes = data.get("mistakes", [])
    
    if len(mistakes) <= 1:
        return []
    
    # 准备文本数据
    texts = []
    mistake_ids = []
    
    for mistake in mistakes:
        if str(mistake.get("id")) == str(current_mistake.get("id")):
            continue
        
        # 合并题干、知识点等信息作为文本
        text = " ".join([
            mistake.get("question", ""),
            mistake.get("subject", ""),
            " ".join(mistake.get("knowledge_points", [])),
            " ".join(mistake.get("error_reasons", []))
        ])
        texts.append(text)
        mistake_ids.append(mistake.get("id"))
    
    if not texts:
        return []
    
    # 创建当前错题的文本
    current_text = " ".join([
        current_mistake.get("question", ""),
        current_mistake.get("subject", ""),
        " ".join(current_mistake.get("knowledge_points", [])),
        " ".join(current_mistake.get("error_reasons", []))
    ])
    
    # 使用TF-IDF向量化
    vectorizer = TfidfVectorizer(stop_words=None, max_features=1000)
    tfidf_matrix = vectorizer.fit_transform(texts + [current_text])
    
    # 计算相似度
    similarity_scores = cosine_similarity(
        tfidf_matrix[-1:],
        tfidf_matrix[:-1]
    )[0]
    
    # 排序并获取top_n
    similar_indices = similarity_scores.argsort()[-top_n:][::-1]
    similar_mistakes = []
    
    for idx in similar_indices:
        if similarity_scores[idx] > 0.1:  # 相似度阈值
            for mistake in mistakes:
                if mistake.get("id") == mistake_ids[idx]:
                    similar_mistakes.append(mistake)
                    break
    
    return similar_mistakes

def generate_mistake_id():
    """生成唯一的错题ID"""
    data = load_data()
    existing_ids = [str(mistake.get("id")) for mistake in data.get("mistakes", [])]
    
    while True:
        new_id = str(random.randint(100000, 999999))
        if new_id not in existing_ids:
            return new_id

def update_statistics():
    """更新统计信息"""
    data = load_data()
    mistakes = data.get("mistakes", [])
    
    statistics = {
        "total": len(mistakes),
        "by_subject": {},
        "by_error_type": {},
        "review_completion": 0
    }
    
    # 按学科统计
    for mistake in mistakes:
        subject = mistake.get("subject", "其他")
        if subject not in statistics["by_subject"]:
            statistics["by_subject"][subject] = 0
        statistics["by_subject"][subject] += 1
        
        # 按错误类型统计
        for error_reason in mistake.get("error_reasons", []):
            if error_reason not in statistics["by_error_type"]:
                statistics["by_error_type"][error_reason] = 0
            statistics["by_error_type"][error_reason] += 1
    
    # 计算复习完成率
    if mistakes:
        reviewed_count = sum(1 for mistake in mistakes if mistake.get("review_count", 0) > 0)
        statistics["review_completion"] = int((reviewed_count / len(mistakes)) * 100)
    
    data["statistics"] = statistics
    save_data(data)
    return statistics

def backup_data():
    """备份数据"""
    try:
        if os.path.exists(DATA_FILE):
            backup_file = f"data_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            import shutil
            shutil.copy2(DATA_FILE, backup_file)
            return True
        return False
    except Exception as e:
        print(f"备份失败: {e}")
        return False