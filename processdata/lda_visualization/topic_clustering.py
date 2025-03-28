import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from scipy.spatial import ConvexHull
import umap
from matplotlib.patches import Polygon, PathPatch
import matplotlib.path as mpath
from matplotlib.collections import PatchCollection
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import seaborn as sns
from scipy.interpolate import splprep, splev
import mysql.connector
import argparse
from matplotlib.widgets import Button, CheckButtons

# 设置中文字体显示
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'lunwen',
    'charset': 'utf8mb4',
    'connect_timeout': 600,  # 连接超时时间设为10分钟
    'raise_on_warnings': True,  # 显示警告信息
    'use_pure': True  # 使用纯Python实现，避免C扩展可能的问题
}

# 读取topic.csv文件
def read_topic_csv(file_path):
    df = pd.read_csv(file_path)
    return df

# 将每首诗的主题转换为6维向量
def convert_to_vector(topics_str, num_topics=6):
    if pd.isna(topics_str):
        return [0] * num_topics
    
    topics = [int(t) for t in topics_str.split(',')]
    vector = [0] * num_topics
    for topic in topics:
        if 0 <= topic < num_topics:
            vector[topic] = 1
    return vector

# 使用多种降维方法并结合它们的结果
def reduce_dimensions(vectors, n_components=2, perplexity=30, random_state=42, n_neighbors=5, min_dist=0.8, spread=3.0, scale=1.5):
    # PCA降维
    pca = PCA(n_components=n_components)
    pca_result = pca.fit_transform(vectors)
    
    # t-SNE降维
    tsne = TSNE(n_components=n_components, perplexity=perplexity, random_state=random_state)
    tsne_result = tsne.fit_transform(vectors)
    
    # UMAP降维 - 调整参数使点更分散
    reducer = umap.UMAP(
        n_components=n_components,
        n_neighbors=n_neighbors,  # 进一步减小邻居数量，使点更分散
        min_dist=min_dist,    # 显著增大最小距离，使点更分散
        spread=spread,      # 显著增大spread参数使分布更均匀且分散
        random_state=random_state
    )
    umap_result = reducer.fit_transform(vectors)
    
    # 标准化UMAP结果并增大分散程度
    umap_result = (umap_result - umap_result.mean(axis=0)) / umap_result.std(axis=0)
    umap_result *= scale  # 增大缩放因子，使点分布更分散
    
    return {
        'pca': pca_result,
        'tsne': tsne_result,
        'umap': umap_result
    }

# 使用K-means进行聚类
def cluster_points(points, n_clusters=6, random_state=42):
    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state)
    return kmeans.fit_predict(points)

# 创建平滑的边界曲线
def create_smooth_boundary(points, expand_factor=1.2):  # 减小expand_factor使背景色范围更小
    """创建平滑的边界曲线"""
    if len(points) < 4:
        return None
    
    # 计算质心
    centroid = np.mean(points, axis=0)
    
    # 按照与质心的角度排序点
    angles = np.arctan2(points[:, 1] - centroid[1], points[:, 0] - centroid[0])
    sorted_indices = np.argsort(angles)
    sorted_points = points[sorted_indices]
    
    # 添加首尾点以确保闭合
    sorted_points = np.vstack([sorted_points, sorted_points[0]])
    
    try:
        # 使用样条插值创建平滑曲线
        tck, u = splprep([sorted_points[:, 0], sorted_points[:, 1]], s=0, per=True)
        # 生成更多的点使曲线更平滑
        u_new = np.linspace(0, 1, 100)
        smooth_boundary = np.column_stack(splev(u_new, tck))
        
        # 扩大边界
        smooth_boundary = centroid + expand_factor * (smooth_boundary - centroid)
        return smooth_boundary
    except:
        return None

def plot_smooth_clusters(points, labels, ax, alpha=0.12):  # 进一步减小alpha值
    unique_labels = np.unique(labels)
    colors = plt.cm.tab10(np.linspace(0, 1, len(unique_labels)))
    
    for i, label in enumerate(unique_labels):
        mask = labels == label
        cluster_points = points[mask]
        
        # 绘制散点 - 减小点的大小
        ax.scatter(cluster_points[:, 0], cluster_points[:, 1], 
                  color=colors[i], marker='o', label=f'主题聚类 {label}',
                  alpha=0.7, s=30)  # 减小点的大小和不透明度
        
        # 绘制平滑的边界
        if len(cluster_points) >= 4:
            try:
                # 计算凸包
                hull = ConvexHull(cluster_points)
                hull_points = cluster_points[hull.vertices]
                
                # 创建平滑边界
                smooth_boundary = create_smooth_boundary(hull_points)
                if smooth_boundary is not None:
                    # 创建填充多边形
                    poly = Polygon(smooth_boundary, closed=True, alpha=alpha,
                                 facecolor=colors[i], edgecolor=colors[i], linewidth=0.5)  # 减小边界线宽度
                    ax.add_patch(poly)
            except:
                continue

def save_results_to_db(coords, labels, topics, vectors):
    """保存处理结果到数据库"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 创建新表来存储降维和聚类结果
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS topic_visualization (
                id INT AUTO_INCREMENT PRIMARY KEY,
                original_topic VARCHAR(255),
                vector_dim1 FLOAT,
                vector_dim2 FLOAT,
                vector_dim3 FLOAT,
                vector_dim4 FLOAT,
                vector_dim5 FLOAT,
                vector_dim6 FLOAT,
                umap_x FLOAT,
                umap_y FLOAT,
                cluster_label INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 准备插入数据
        insert_query = """
            INSERT INTO topic_visualization 
            (original_topic, vector_dim1, vector_dim2, vector_dim3, vector_dim4, vector_dim5, vector_dim6, 
             umap_x, umap_y, cluster_label)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # 构建数据
        data_to_insert = []
        for i in range(len(topics)):
            topic_str = str(topics[i]) if not pd.isna(topics[i]) else ""
            data_to_insert.append((
                topic_str,
                float(vectors[i][0]),
                float(vectors[i][1]),
                float(vectors[i][2]),
                float(vectors[i][3]),
                float(vectors[i][4]),
                float(vectors[i][5]),
                float(coords[i][0]),
                float(coords[i][1]),
                int(labels[i])
            ))
        
        # 分批插入数据，每批1000条
        batch_size = 1000
        total_batches = (len(data_to_insert) + batch_size - 1) // batch_size
        
        for i in range(0, len(data_to_insert), batch_size):
            batch = data_to_insert[i:i + batch_size]
            try:
                cursor.executemany(insert_query, batch)
                conn.commit()
                print(f"已插入第 {i//batch_size + 1}/{total_batches} 批数据，共 {len(batch)} 条")
            except Exception as e:
                print(f"插入第 {i//batch_size + 1} 批数据时出错: {str(e)}")
                conn.rollback()
                raise e
        
        print(f"成功将{len(data_to_insert)}条处理结果保存到数据库。")
        
    except Exception as e:
        print(f"数据库操作出错: {str(e)}")
        raise e
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def create_interactive_plot(coords, labels, topic_strings, vectors, output_file='topic_clusters_interactive.png'):
    """创建交互式散点图"""
    fig = plt.figure(figsize=(16, 14))
    ax = plt.gca()
    
    # 设置背景样式
    ax.set_facecolor('#ffffff')
    plt.gcf().patch.set_facecolor('#ffffff')
    
    # 设置网格样式
    ax.grid(True, linestyle='--', alpha=0.2)
    
    # 选择颜色方案
    colors = plt.cm.Set1(np.linspace(0, 1, len(np.unique(labels))))
    
    # 获取唯一的标签
    unique_labels = np.unique(labels)
    
    # 计算每个聚类的大小并按大小排序
    cluster_sizes = [np.sum(labels == label) for label in unique_labels]
    size_order = np.argsort(cluster_sizes)[::-1]
    
    # 创建图例句柄和标签
    legend_handles = []
    legend_labels = []
    
    # 为每个主题准备不同的颜色
    topic_colors = {}
    topic_nums = range(6)  # 6个主题
    topic_color_map = plt.cm.tab10(np.linspace(0, 1, 6))
    for i, topic_num in enumerate(topic_nums):
        topic_colors[topic_num] = topic_color_map[i]
    
    # 添加主题色图例
    for topic_num, color in topic_colors.items():
        legend_handles.append(plt.Line2D([0], [0], marker='o', color='w', 
                                        markerfacecolor=color, markersize=10))
        legend_labels.append(f'主题: {topic_num}')
    
    # 创建散点图
    scatter_plots = []
    for idx in size_order:
        label = unique_labels[idx]
        mask = labels == label
        cluster_points = coords[mask]
        cluster_topics = [topic_strings[i] for i in range(len(labels)) if labels[i] == label]
        
        # 为每个点添加随机偏移以减少重叠
        jittered_points = cluster_points + np.random.normal(0, 0.02, cluster_points.shape)
        
        # 绘制散点
        scatter = ax.scatter(
            jittered_points[:, 0],
            jittered_points[:, 1],
            color=colors[idx],
            marker='o',
            alpha=0.8,
            s=35,
            edgecolor='white',
            linewidth=0.5,
            zorder=3
        )
        scatter_plots.append(scatter)
        
        # 添加到图例
        legend_handles.append(scatter)
        legend_labels.append(f'聚类 {label} ({len(cluster_points)}首)')
    
    # 创建复选框
    checkbox_ax = plt.axes([0.02, 0.02, 0.2, 0.2])
    checkbox_labels = [f'聚类 {label}' for label in unique_labels]
    checkbox = CheckButtons(checkbox_ax, checkbox_labels, [True] * len(unique_labels))
    
    # 创建数据查看文本框
    text_ax = plt.axes([0.8, 0.02, 0.18, 0.2])
    text_ax.set_facecolor('white')
    text_ax.set_xticks([])
    text_ax.set_yticks([])
    text_box = text_ax.text(0.5, 0.5, '', ha='center', va='center', wrap=True)
    
    # 存储原始数据
    scatter_data = {
        'coords': coords,
        'labels': labels,
        'topics': topic_strings,
        'vectors': vectors
    }
    
    def update_visibility(label):
        """更新散点图的可见性"""
        idx = int(label.split()[-1])
        scatter_plots[idx].set_visible(checkbox.get_status()[idx])
        
        # 更新高亮效果
        for i, scatter in enumerate(scatter_plots):
            is_visible = checkbox.get_status()[i]
            if is_visible:
                scatter.set_alpha(0.8)  # 高亮显示
                scatter.set_zorder(3)  # 放到上层
            else:
                scatter.set_alpha(0.2)  # 变透明
                scatter.set_zorder(1)  # 放到底层
        
        plt.draw()
    
    def on_click(event):
        """处理点击事件"""
        if event.inaxes == ax:
            # 计算点击位置到所有点的距离
            distances = np.sqrt(np.sum((coords - np.array([event.xdata, event.ydata]))**2, axis=1))
            closest_idx = np.argmin(distances)
            
            # 更新文本框内容
            topic = topic_strings[closest_idx]
            vector = vectors[closest_idx]
            text = f'主题: {topic}\n'
            text += f'向量: [{", ".join([f"{v:.1f}" for v in vector])}]\n'
            text += f'聚类: {labels[closest_idx]}'
            text_box.set_text(text)
            plt.draw()
    
    # 绑定事件
    checkbox.on_clicked(update_visibility)
    fig.canvas.mpl_connect('button_press_event', on_click)
    
    plt.title('诗词主题聚类分布图', fontsize=20, pad=20)
    plt.xlabel('UMAP特征1', fontsize=16)
    plt.ylabel('UMAP特征2', fontsize=16)
    
    # 添加图例
    plt.legend(legend_handles, legend_labels, bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=14)
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图片
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"已保存交互式聚类图到: {output_file}")
    
    # 显示图形
    plt.show()

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='诗词主题聚类可视化工具')
    
    # UMAP参数
    parser.add_argument('--n_neighbors', type=int, default=5, help='UMAP的邻居数量，较小的值使聚类更分散')
    parser.add_argument('--min_dist', type=float, default=0.8, help='UMAP的最小距离，较大的值使点之间距离更大')
    parser.add_argument('--spread', type=float, default=3.0, help='UMAP的spread参数，较大的值使分布更分散')
    parser.add_argument('--scale', type=float, default=1.5, help='坐标缩放因子，较大的值使整体分布更大')
    
    # 聚类参数
    parser.add_argument('--n_clusters', type=int, default=6, help='聚类数量')
    
    # 输入文件
    parser.add_argument('--input', type=str, default='topic.csv', help='输入CSV文件路径')
    
    # 输出文件
    parser.add_argument('--output', type=str, default='topic_clusters_interactive.png', help='输出文件路径')
    
    return parser.parse_args()

def main():
    # 解析命令行参数
    args = parse_args()
    
    # 读取topic.csv文件
    print(f"正在读取主题数据: {args.input}")
    
    try:
        topic_df = read_topic_csv(args.input)
    except FileNotFoundError:
        # 尝试不同的路径
        try_paths = ['processdata/topic.csv', '../topic.csv', './topic.csv', 'lda_visualization/topic.csv']
        found = False
        
        for path in try_paths:
            try:
                print(f"尝试读取: {path}")
                topic_df = read_topic_csv(path)
                print(f"成功从 {path} 读取数据")
                found = True
                break
            except FileNotFoundError:
                continue
        
        if not found:
            print("错误: 无法找到topic.csv文件。请确保文件存在并提供正确路径。")
            print("可以使用 --input 参数指定文件路径，例如: --input=./topic.csv")
            return
    
    # 将主题转换为向量
    print("正在转换主题数据为向量...")
    vectors = []
    for topics_str in topic_df['topics']:
        vector = convert_to_vector(topics_str)
        vectors.append(vector)
    
    vectors = np.array(vectors)
    
    # 降维
    print("正在进行降维...")
    dim_reduction_results = reduce_dimensions(
        vectors,
        n_neighbors=args.n_neighbors,
        min_dist=args.min_dist,
        spread=args.spread,
        scale=args.scale
    )
    
    # 使用UMAP结果进行聚类和可视化
    umap_result = dim_reduction_results['umap']
    
    # 聚类
    print(f"正在进行聚类 (n_clusters={args.n_clusters})...")
    cluster_labels = cluster_points(umap_result, n_clusters=args.n_clusters)
    
    # 保存结果到数据库
    print("正在将结果保存到数据库...")
    save_results_to_db(umap_result, cluster_labels, topic_df['topics'], vectors)
    
    # 创建交互式可视化
    print("正在生成交互式可视化...")
    create_interactive_plot(
        umap_result, 
        cluster_labels, 
        topic_df['topics'], 
        vectors,
        output_file=args.output
    )
    
    print(f"处理完成！共处理了{len(vectors)}首诗的主题分布，识别出{args.n_clusters}个聚类。")
    print(f"生成的图像文件：{args.output}")

if __name__ == "__main__":
    main() 