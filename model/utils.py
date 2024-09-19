import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


def calculate_cosine_similarity(pivot_table, google_rating_dict):
    # 使用 Google Rating 填充 NaN 值
    pivot_table_filled = pivot_table.apply(lambda row: row.fillna(google_rating_dict.get(row.name)), axis=1)

    # 計算餐廳之間的餘弦相似度
    cosine_sim_matrix = cosine_similarity(pivot_table_filled)

    # 將相似度矩陣轉換成 DataFrame
    cosine_sim_df = pd.DataFrame(cosine_sim_matrix, index=pivot_table.index, columns=pivot_table.index)

    return cosine_sim_df

def recommend_restaurants_for_user(cosine_sim_df, high_score_restaurants, unrated_or_considered_restaurants, top_n=3):
    recommended_restaurants = set()
    
    for restaurant_id in high_score_restaurants:
        
        # 找到與此餐廳相似的餐廳
        similar_restaurants = cosine_sim_df[restaurant_id].sort_values(ascending=False).index.tolist()
        
        # 過濾出尚未評價的餐廳
        similar_unrated_or_considered_restaurants = [r for r in similar_restaurants if r in unrated_or_considered_restaurants]
        
        # 添加到推薦列表
        recommended_restaurants.update(similar_unrated_or_considered_restaurants[:top_n])
    
    return list(recommended_restaurants)