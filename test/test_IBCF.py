import pandas as pd
import sys
import os

# 將 model 資料夾路徑添加到 sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'model')))
from utils import recommend_restaurants_for_user, calculate_cosine_similarity

def test_calculate_cosine_similarity():
    ratings_data = [
        {'user_id': 1, 'restaurant_id': 101, 'total_score': 5},
        {'user_id': 1, 'restaurant_id': 102, 'total_score': 4},
        {'user_id': 2, 'restaurant_id': 103, 'total_score': 5},
        {'user_id': 2, 'restaurant_id': 104, 'total_score': 3},
        {'user_id': 3, 'restaurant_id': 105, 'total_score': 2.5},
        {'user_id': 3, 'restaurant_id': 106, 'total_score': 5},
    ]

    google_rating_data = {
        101: 4.2,
        102: 3.9,
        103: None,
        104: 4.5,
        105: None,
        106: 4.1,
    }

    # 預期的相似度矩陣
    expected_cosine_sim = pd.DataFrame(
        [
            [1.000000, 0.997391, 0.925445, 0.988563, 0.996455, 0.987817],
            [0.997391, 1.000000, 0.940744, 0.985704, 0.999928, 0.994737],
            [0.925445, 0.940744, 1.000000, 0.870388, 0.942809, 0.922460],
            [0.988563, 0.985704, 0.870388, 1.000000, 0.984732, 0.988540],
            [0.996455, 0.999928, 0.942809, 0.984732, 1.000000, 0.995383],
            [0.987817, 0.994737, 0.922460, 0.988540, 0.995383, 1.000000]
        ],
        index=[101, 102, 103, 104, 105, 106],
        columns=[101, 102, 103, 104, 105, 106]
    )
    expected_cosine_sim.index.name = 'restaurant_id'
    expected_cosine_sim.columns.name = 'restaurant_id'

    # 將資料轉換成 DataFrame
    df = pd.DataFrame(ratings_data)
    pivot_table = df.pivot_table(index='restaurant_id', columns='user_id', values='total_score')

    # 用來填補 NaN 的 Google 評分字典
    google_rating_dict = {k: v if v is not None else 2.5 for k, v in google_rating_data.items()}

    # 計算餘弦相似度
    cosine_sim_df = calculate_cosine_similarity(pivot_table, google_rating_dict)

    # 比對相似度矩陣與預期結果是否一致
    pd.testing.assert_frame_equal(cosine_sim_df, expected_cosine_sim, atol=1e-5)

def test_recommend_restaurants_for_user():

    cosine_sim_df = pd.DataFrame(
        [
            [1.000000, 0.997391, 0.925445, 0.988563, 0.996455, 0.987817],
            [0.997391, 1.000000, 0.940744, 0.985704, 0.999928, 0.994737],
            [0.925445, 0.940744, 1.000000, 0.870388, 0.942809, 0.922460],
            [0.988563, 0.985704, 0.870388, 1.000000, 0.984732, 0.988540],
            [0.996455, 0.999928, 0.942809, 0.984732, 1.000000, 0.995383],
            [0.987817, 0.994737, 0.922460, 0.988540, 0.995383, 1.000000]
        ],
        index=[101, 102, 103, 104, 105, 106],
        columns=[101, 102, 103, 104, 105, 106]
    )
    high_score_restaurants = [101, 102]
    unrated_or_considered_restaurants = [103, 104, 105]

    # 測試推薦結果
    recommendations = recommend_restaurants_for_user(cosine_sim_df, high_score_restaurants, unrated_or_considered_restaurants)

    # 確保推薦結果包含 105
    assert 105 in recommendations, "推薦結果應包含餐廳 105"