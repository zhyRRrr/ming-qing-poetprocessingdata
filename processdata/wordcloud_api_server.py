import os
import pymysql
import numpy as np
import pandas as pd
import base64
import matplotlib
# 在导入pyplot之前，设置后端为非交互式的"Agg"
matplotlib.use('Agg')  # 必须在导入pyplot之前设置
from matplotlib import pyplot as plt
from flask import Flask, request, jsonify
from flask_cors import CORS
from wordcloud import WordCloud, ImageColorGenerator, STOPWORDS
from PIL import Image
import collections
import re
import cv2
import io
import time
import hashlib
import traceback

# 设置matplotlib支持中文显示
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun', 'Arial Unicode MS']
matplotlib.rcParams['axes.unicode_minus'] = False
matplotlib.rcParams['font.family'] = 'sans-serif'

# 创建Flask应用
app = Flask(__name__)
# 添加CORS支持，允许前端跨域请求
CORS(app, resources={r"/*": {"origins": "*"}})

# 连接MySQL数据库
def connect_to_mysql():
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='123456',  # 请替换为您的数据库密码
        database='lunwen',
        charset='utf8mb4'
    )
    return connection

# 获取所有诗人列表
def get_poets():
    connection = connect_to_mysql()
    try:
        with connection.cursor() as cursor:
            # 从poems表中获取所有诗人名称
            sql = "SELECT DISTINCT poetName FROM poems ORDER BY poetName"
            cursor.execute(sql)
            results = cursor.fetchall()
            poets = [result[0] for result in results if result[0]]
            return poets
    finally:
        connection.close()

# 根据诗人获取topicWords数据
def get_topic_words_by_poet(poet_name=None):
    connection = connect_to_mysql()
    try:
        with connection.cursor() as cursor:
            if poet_name and poet_name != "全部诗人":
                # 根据诗人名筛选topicWords
                sql = """
                SELECT t.topicWords 
                FROM topic t
                JOIN poems p ON t.poemId = p.poemId
                WHERE p.poetName = %s
                """
                cursor.execute(sql, (poet_name,))
            else:
                # 获取所有topicWords
                sql = "SELECT topicWords FROM topic"
                cursor.execute(sql)
            
            results = cursor.fetchall()
            return results
    finally:
        connection.close()

# 处理topicWords数据，统计词频
def process_topic_words(topic_words_data):
    all_words = []
    
    print(f"处理 {len(topic_words_data)} 条topicWords数据")
    
    for row in topic_words_data:
        if row[0] is None or len(row[0].strip()) == 0:
            continue
            
        topic_words = row[0]
        # 先尝试使用正则表达式匹配双引号内的内容
        matches = re.findall(r'"([^"]*)"', topic_words)
        
        if matches:
            # 如果找到匹配项，使用它们
            for match in matches:
                # 对于每个匹配项，按照逗号（中文或英文）分割单个词
                words = re.split(r'[,，]', match)
                for word in words:
                    word = word.strip()  # 去除空格
                    if word:  # 确保单词不为空
                        all_words.append(word)
        else:
            # 如果没有匹配项，按照旧的方式处理
            # 尝试按照中文逗号分割
            topics = topic_words.replace('"', '').split('，')
            
            # 对于每个主题，按照英文逗号分割单个词
            for topic in topics:
                words = topic.split(',')
                for word in words:
                    word = word.strip()  # 去除空格
                    if word:  # 确保单词不为空
                        all_words.append(word)
    
    # 统计词频
    word_counts = collections.Counter(all_words)
    
    print(f"总共提取到 {len(all_words)} 个词，有 {len(word_counts)} 个不同的词")
    
    return word_counts

# 加载停用词列表
def load_stopwords():
    stopwords = set(STOPWORDS)
    # 在这里添加基本中文停用词
    chinese_stopwords = {'的', '了', '和', '是', '在', '我', '有', '与', '这', '那', '你', '他', '她', '它'}
    stopwords.update(chinese_stopwords)
    
    # 尝试从stopwords2.txt文件加载停用词
    stopwords_paths = [
        os.path.join('processdata', 'ciyuntu', 'stopwords2.txt'),
        os.path.join('..', 'ciyuntu', 'stopwords2.txt'),
        os.path.join('ciyuntu', 'stopwords2.txt'),
        os.path.abspath(os.path.join('D:', '01', 'lunwen', 'processdata', 'ciyuntu', 'stopwords2.txt'))
    ]
    
    loaded = False
    for path in stopwords_paths:
        try:
            print(f"尝试从 {path} 加载停用词列表")
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    word = line.strip()
                    if word:  # 确保单词不为空
                        stopwords.add(word)
            print(f"成功从 {path} 加载停用词")
            loaded = True
            break
        except FileNotFoundError:
            continue
    
    if not loaded:
        print("警告: 无法加载stopwords2.txt文件，将只使用基本停用词")
    else:
        print(f"总共加载了 {len(stopwords)} 个停用词")
    
    return stopwords

# 检查并确保字体文件存在
def ensure_font_exists():
    # 常见的中文字体路径
    font_paths = [
        'C:\\Windows\\Fonts\\simhei.ttf',  # Windows黑体
        'C:\\Windows\\Fonts\\simkai.ttf',  # Windows楷体
        'C:\\Windows\\Fonts\\simsun.ttc',  # Windows宋体
        'C:\\Windows\\Fonts\\msyh.ttc',    # Windows微软雅黑
        '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',  # Linux文泉驿微米黑
        '/System/Library/Fonts/PingFang.ttc'  # macOS苹方
    ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            print(f"使用字体: {font_path}")
            return font_path
    
    # 如果找不到任何字体，给出警告并使用默认路径
    print("警告: 找不到任何中文字体文件，将使用默认字体路径，可能导致中文显示为方块")
    return 'C:\\Windows\\Fonts\\simhei.ttf'

# 生成词云图
def generate_wordcloud(word_counts, max_words=2000):
    if not word_counts:
        return None, None
        
    # 加载mask图片
    mask_paths = [
        os.path.join('..', 'ciyuntu', 'ciyun1.png'),
        os.path.join('ciyuntu', 'ciyun1.png'),
        os.path.join('processdata', 'ciyuntu', 'ciyun1.png'),
        os.path.join('..', '..', 'processdata', 'ciyuntu', 'ciyun1.png'),
        os.path.abspath(os.path.join('D:', '01', 'lunwen', 'processdata', 'ciyuntu', 'ciyun1.png'))
    ]
    
    mask_img = None
    for mask_path in mask_paths:
        try:
            print(f"尝试加载蒙版图片: {mask_path}")
            mask_img = Image.open(mask_path).convert('RGBA')
            print(f"成功加载蒙版图片: {mask_path}")
            break
        except FileNotFoundError:
            continue
    
    if mask_img is None:
        print("错误：无法找到蒙版图片。请确保文件存在并提供正确的路径。")
        return None, None
    
    print(f"原始蒙版图片尺寸(PIL格式): {mask_img.size}")
    mask_data = np.array(mask_img)
    
    # 创建一个只在轮廓内部有值的mask
    mask = np.zeros(mask_data.shape[:2], np.uint8)
    mask[mask_data[:, :, 3] <= 50] = 255  # 不透明区域（轮廓内部）
    mask[mask_data[:, :, 3] > 50] = 0     # 透明区域（轮廓外部）
    
    # 清理mask噪点
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    
    # 创建缩小的内部mask，避免文字太靠近边缘
    erosion_kernel = np.ones((5, 5), np.uint8)
    inner_mask = cv2.erode(mask, erosion_kernel, iterations=1)
    
    print(f"蒙版numpy数组尺寸: {mask.shape}")
    print(f"蒙版中非零像素数量: {np.count_nonzero(mask)}")
    print(f"内部蒙版中非零像素数量: {np.count_nonzero(inner_mask)}")
    
    # 设置词云参数
    font_path = ensure_font_exists()
    
    # 加载停用词
    stopwords = load_stopwords()
    
    # 创建图像颜色生成器
    image_colors = ImageColorGenerator(mask_data)
    
    try:
        wordcloud = WordCloud(
            background_color=None,  # 将背景设置为透明
            mode="RGBA",            # 使用RGBA模式支持透明度
            mask=inner_mask,
            max_words=max_words,
            max_font_size=45,       # 降低最大字体大小（原为60）
            min_font_size=8,        # 添加最小字体大小
            stopwords=stopwords,    # 添加停用词
            prefer_horizontal=0.9,
            relative_scaling=0.5,   # 降低词频对字体大小的影响（原为0.8）
            font_path=font_path,    # 使用已确认存在的字体
            width=mask.shape[1],
            height=mask.shape[0],
            random_state=42,
            # 添加额外参数以支持中文
            collocations=False,     # 避免词组重复
            regexp=r"[\w\u4e00-\u9fa5]+"  # 增加对中文字符的支持
        ).generate_from_frequencies(word_counts)
        
        if wordcloud is None or len(wordcloud.words_) == 0:
            print("警告：词云生成失败或为空！")
            return None, None

        print(f"词云中的词语数量: {len(wordcloud.words_)}")
        
        # 使用图像颜色为词云着色
        colored_wordcloud = wordcloud.recolor(color_func=image_colors)
        
        return wordcloud, colored_wordcloud
        
    except Exception as e:
        print(f"生成词云图像时出错: {str(e)}")
        traceback.print_exc()
        return None, None

# 保存词云图到内存字节流并返回base64编码
def save_wordcloud_to_base64(wordcloud):
    if wordcloud is None:
        return None
        
    try:
        # 创建一个具有透明背景的新图形
        fig = plt.figure(figsize=(10, 8), dpi=100)
        ax = plt.subplot(111)
        
        # 设置透明背景
        fig.patch.set_alpha(0)
        ax.patch.set_alpha(0)
        
        # 禁用所有轴线、标签等
        ax.axis('off')
        plt.xticks([])
        plt.yticks([])
        plt.grid(False)
        
        # 显示词云图并禁用任何边框
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.tight_layout(pad=0)
        
        # 保存到内存中的字节流，确保透明度被保留
        img_bytes = io.BytesIO()
        plt.savefig(img_bytes, format='PNG', 
                    bbox_inches='tight', 
                    pad_inches=0, 
                    transparent=True,  # 启用透明背景
                    facecolor='none',  # 无面板颜色
                    edgecolor='none')  # 无边缘颜色
        
        # 重要：确保关闭图形释放资源
        plt.close(fig)
        
        # 将字节流转换为base64编码
        img_bytes.seek(0)
        base64_data = base64.b64encode(img_bytes.read()).decode('utf-8')
        
        # 释放BytesIO资源
        img_bytes.close()
        
        return base64_data
    except Exception as e:
        print(f"保存词云图到base64时出错: {str(e)}")
        traceback.print_exc()
        # 确保出错时也关闭图形
        plt.close('all')
        return None

# API端点：获取所有诗人名称
@app.route('/poets', methods=['GET'])
def api_get_poets():
    try:
        poets = get_poets()
        return jsonify({
            'success': True,
            'poets': poets
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# API端点：生成词云图
@app.route('/generate_wordcloud', methods=['POST'])
def api_generate_wordcloud():
    try:
        print("收到词云图生成请求")
        data = request.json
        poet_name = data.get('poet_name', '全部诗人')
        print(f"请求生成词云图的诗人: {poet_name}")
        
        # 获取主题词数据
        topic_words_data = get_topic_words_by_poet(poet_name)
        
        if not topic_words_data:
            print(f"未找到诗人 {poet_name} 的数据")
            return jsonify({
                'success': False,
                'error': f'未找到 {poet_name} 的数据'
            }), 404
            
        print(f"获取到 {len(topic_words_data)} 条主题词数据")
            
        # 处理数据，统计词频
        word_counts = process_topic_words(topic_words_data)
        
        if not word_counts:
            print(f"无法从诗人 {poet_name} 提取任何有效词语")
            return jsonify({
                'success': False,
                'error': f'无法从 {poet_name} 提取任何有效词语'
            }), 404
        
        print(f"成功提取 {len(word_counts)} 个不同词语")
        
        # 生成词云图
        _, colored_wordcloud = generate_wordcloud(word_counts)
        
        if colored_wordcloud is None:
            print("词云生成失败")
            return jsonify({
                'success': False,
                'error': '词云生成失败'
            }), 500
            
        print("词云生成成功，正在转换为base64")
            
        # 将词云图转换为base64编码
        base64_image = save_wordcloud_to_base64(colored_wordcloud)
        
        if base64_image is None:
            print("词云图保存为base64失败")
            return jsonify({
                'success': False,
                'error': '词云图保存失败'
            }), 500
            
        print(f"成功生成诗人 {poet_name} 的词云图，base64长度: {len(base64_image)}")
            
        return jsonify({
            'success': True,
            'poet': poet_name,
            'image': base64_image
        })
        
    except Exception as e:
        error_msg = f"生成词云图时出错: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500

# 在WebSocket服务器中添加处理诗人列表请求的功能
# 这部分需要添加到python_socket.py的handle_connection函数中
"""
elif data['action'] == 'fetch_poets':
    # 获取诗人列表
    try:
        from wordcloud_api_server import get_poets
        poets = get_poets()
        await websocket.send(json.dumps({
            'type': 'poet_list',
            'success': True,
            'poets': poets
        }))
    except Exception as e:
        await websocket.send(json.dumps({
            'type': 'poet_list',
            'success': False,
            'error': str(e)
        }))
"""

# 启动Flask应用
if __name__ == '__main__':
    print("启动词云图API服务器...")
    app.run(host='0.0.0.0', port=5000, debug=True) 