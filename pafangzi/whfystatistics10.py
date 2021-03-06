# -*- coding: utf-8 -*-
"""
Created on Tue Oct  2 00:00:31 2018

@author: Administrator
"""

import tensorflow as tf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from random import sample
from scipy.spatial.distance import cdist
#PCA主要是用来数据降维，将高维度的特征映射到低维度的特征，加快机器学习的速度。
from sklearn.decomposition import PCA
from sklearn import preprocessing
from scipy.spatial import cKDTree

plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号

def k_means_cluster(points,k,first_centroids=None, predict_method=None):
    max_iters=100
    N, D = points.shape
    K=k      # 被聚为K类
    # 初始聚类中心……
    centroids = tf.Variable(points[sample(range(N), K)] if first_centroids is None else first_centroids)
    # 样本归属聚类中心……
    cluster_assignments = tf.Variable(tf.zeros([N], dtype=tf.int64))
    # 同时计算所有样本与聚类中心的距离……
    rep_points = tf.reshape(tf.tile(points, [1, K]), [N, K, D])
    rep_centroids = tf.reshape(tf.tile(centroids, [N, 1]), [N, K, D])
    sum_squares = tf.reduce_sum(tf.square(rep_points - rep_centroids), reduction_indices=2)

    # 样本对应的聚类中心索引……
    best_centroids = tf.argmin(sum_squares, 1)
    # 新聚类中心对应的样本索引……
    centroids_indies = tf.argmin(sum_squares, 0)

    # 按照`best_centroids`中相同的索引，将points求和……
    total = tf.unsorted_segment_sum(points, best_centroids, K)
    # 按照`best_centroids`中相同的索引，将points计数……
    count = tf.unsorted_segment_sum(tf.ones_like(points), best_centroids, K)
    # 以均值作为新聚类中心的值……
    means = total / count

    did_assignments_change = tf.reduce_any(tf.not_equal(best_centroids, cluster_assignments))

    with tf.control_dependencies([did_assignments_change]):
        do_updates = tf.group(centroids.assign(means), cluster_assignments.assign(best_centroids))
    init = tf.initialize_all_variables()

    sess = tf.Session()
    sess.run(init)

    iters, changed = 0, True
    while changed and iters < max_iters:
        iters += 1
        [changed, _] = sess.run([did_assignments_change, do_updates])

    [centers, cindies, assignments] = sess.run([centroids, centroids_indies, cluster_assignments])
    return iters, centers, assignments


def show():
    d = pd.read_excel("./one_hot.xlsx", sheetname='123')
    d = np.array(d)
    scaler = preprocessing.StandardScaler().fit(d)
    d = scaler.transform(d)
    #以下是将聚类结果可视化出来
    #PCA(n_components=2)表示将4个特征的向量降维到二维，即可以画在平面
    pca_model = PCA(n_components=2)
    #将iris.data转换成标准形式，然后存入reduced_data中
    reduced_data = pca_model.fit_transform(d)
    iters, centers, assignments = k_means_cluster(reduced_data, 8)
    print(centers, assignments)
    
    
    assignments1 = pd.DataFrame(assignments)
    print(assignments1)
    assignments1.to_excel("./one_hot1.xlsx",sheet_name="234",index=False,header=True)
    
    #h表示间距
    h = .2
    #下面求x_min, x_max和y_min, y_max，主要是为了确定坐标轴
    x_min, x_max = reduced_data[:, 0].min() - 1, reduced_data[:, 0].max() + 1
    y_min, y_max = reduced_data[:, 1].min() - 1, reduced_data[:, 1].max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))
    
    xx_pt = list(xx.ravel())
    yy_pt = list(yy.ravel())
    xy_pts = np.array([[x,y] for x,y in zip(xx_pt, yy_pt)])
    mytree = cKDTree(centers)
    dist, indexes = mytree.query(xy_pts)
    indexes =indexes.reshape(xx.shape)
    
    #下面使用matplotlib将图给画出来
    plt.clf()
    plt.imshow(indexes, interpolation='nearest', extent=(xx.min(), xx.max(), yy.min(), yy.max()), cmap=plt.cm.Paired, aspect='auto', origin='lower')
    symbols = ['o', '^', 'D', 's', '.', ',', '<',  '*']
    #sym=[sysmbols[i] for i in assignments]
    for i in range(8):
        x=[]
        y=[]
        for j in range(assignments.shape[0]):
            if assignments[j]==i:
                x.append(reduced_data[j][0])
                y.append(reduced_data[i][1])
        plt.plot(x, y, symbols[i], markersize=10)
        
    """
    temp_group = reduced_data[(i*50) : (50)*(i+1)]
    plt.plot(temp_group[:, 0], temp_group[:, 1], symbols[i], markersize=10)
    """

    plt.scatter(centers[:, 0], centers[:, 1], marker='x',color='black', s=169, linewidths=3, zorder=10)
    plt.title('K-means clustering')
    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)
    plt.savefig('./whfypca.png')
    plt.show()

    
if __name__ == "__main__":
    show()