# test_IBCF.py
import pytest
import pandas as pd
from unittest.mock import patch
from card_model import recommend_restaurants_for_user, calculate_cosine_similarity

@pytest.fixture
def setup_data():
    # 假設你有 5 個使用者和 10 家餐廳
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

    # 將資料轉換成 DataFrame
    df = pd.DataFrame(ratings_data)
    pivot_table = df.pivot_table(index='restaurant_id', columns='user_id', values='total_score')

    # 用來填補 NaN 的 Google 評分字典
    google_rating_dict = {k: v if v is not None else 2.5 for k, v in google_rating_data.items()}

    return pivot_table, google_rating_dict

# 使用 patch 模擬 'card_model.Database'
@patch('card_model.Database')  # 這裡應該指向 card_model.Database
def test_collaborative_filtering(mock_db, setup_data):
    pivot_table, google_rating_dict = setup_data

    # 計算餘弦相似度
    cosine_sim_df = calculate_cosine_similarity(pivot_table, google_rating_dict)

    # 假設我們有高分餐廳和尚未評價/考慮過的餐廳
    high_score_restaurants = [101, 102]
    unrated_or_considered_restaurants = [103, 104, 105]

    # 測試推薦邏輯
    recommendations = recommend_restaurants_for_user(cosine_sim_df, high_score_restaurants, unrated_or_considered_restaurants)

    # 檢查推薦結果
    assert len(recommendations) > 0, "應該至少有一個推薦餐廳"
    assert 103 in recommendations, "應推薦 103 號餐廳"
