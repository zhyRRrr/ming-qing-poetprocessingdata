1. 新表emotion_visualization，包含以下字段：

* id: 自增主键
* original_emotion: 原始情感文本
* vector_dim1到vector_dim5: 5维情感向量
* umap_x和umap_y: UMAP降维后的二维坐标
* cluster_label: 聚类标签
* created_at: 创建时间戳