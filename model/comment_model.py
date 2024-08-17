from dbconfig import Database
from pydantic import BaseModel
from typing import Optional
import re

class Comment(BaseModel):
    user_id: int
    restaurant_id: int
    place_id: str
    image: Optional[str] = None
    rating: int
    context: str
    checkin: Optional[bool] = False

class RestaurantComment(BaseModel):
    id: int
    username: str
    avg_rating: float | None
    rating: int
    context: str
    url: Optional[str] = None

class UserComment(BaseModel):
    id:int
    restaurant_name:str
    created_at: str
    rating: int
    context: str
    url: Optional[str] = None



class CommentModel:
    def record_comment(comment:Comment): 
        if comment.image is not None:
            image_table_sql="INSERT INTO images (place_id, url, upload_by_user) VALUES (%s, %s, %s)"
            image_table_val = (comment.place_id, comment.image, True)
            image_id = Database.create_and_return_id(sql=image_table_sql, val=image_table_val)

            comment_table_sql = """
            INSERT INTO comments (user_id, restaurant_id, image_id, rating, context, checkin) 
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            comment_table_val = (comment.user_id, comment.restaurant_id, image_id, comment.rating, comment.context, comment.checkin)
            result = Database.create(comment_table_sql, comment_table_val)
            if result>0:
                print("評論新增成功")
                return True
            else:
                print("有錯")
                return False

        else:
            comment_table_sql = """
            INSERT INTO comments (user_id, restaurant_id, rating, context, checkin) 
            VALUES (%s, %s, %s, %s, %s)
            """
            comment_table_val = (comment.user_id, comment.restaurant_id, comment.rating, comment.context, comment.checkin)
            result = Database.create(comment_table_sql, comment_table_val)
            if result>0:
                print("沒圖片評論新增成功")
                return True
            else:
                print("有錯")
                return False
            
    def get_restaurant_comment(restaurant_id):
        sql = f"""
        SELECT c.id, c.rating, c.context, u.username, u.avg_rating, i.url 
        FROM (SELECT * FROM comments WHERE restaurant_id = {restaurant_id}) AS c 
        JOIN users AS u ON c.user_id = u.id 
        LEFT JOIN images AS i ON c.image_id = i.id
        ORDER BY id DESC;
        """
        results = Database.read_all(sql)
        comment_group = []
        for result in results:
            comment_group.append(RestaurantComment(**result))
        return comment_group

    def get_user_comment(user_id):
        sql = f"""
        SELECT c.id, r.name AS restaurant_name, c.rating, c.context, c.created_at, i.url 
        FROM (SELECT * FROM comments WHERE user_id = {user_id}) AS c 
        JOIN restaurants AS r ON c.restaurant_id = r.id 
        LEFT JOIN images AS i ON c.image_id = i.id
        ORDER BY c.created_at DESC;
        """
        results = Database.read_all(sql)
        comment_group = []
        datetime_pattern = r'(\d{4}-\d{2}-\d{2})'

        for result in results:
            result["created_at"] = re.search(datetime_pattern, str(result["created_at"])).group(1)
            comment_group.append(UserComment(**result))

        return comment_group
    
    def delete(comment_id, user_id):
        ## 查詢留言，取得圖片url，驗證身分
        sql = """
        SELECT c.comment_id, c.image_id, i.url 
        FROM (SELECT id AS comment_id, image_id FROM comments WHERE id = %s AND user_id = %s) AS c 
        LEFT JOIN images AS i ON c.image_id = i.id;
        """
        val = (comment_id, user_id)
        result = Database.read_one(sql, val)

        if (result is None):
            return "error"

        # 刪除留言
        sql = "DELETE FROM comments WHERE id = %s"
        val = (comment_id,)
        Database.delete(sql, val)
        

        # 刪除圖片
        if result["image_id"] is not None:
            sql = "DELETE FROM images WHERE id = %s"
            val = (result["image_id"],)
            Database.delete(sql, val)
            return result["url"]
        else:
            return "no image"