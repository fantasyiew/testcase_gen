from .database import get_connection


class FeatureRepo:
    """功能点数据访问层"""

    @staticmethod
    def get_all() -> list[dict]:
        """获取所有功能点"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, category, feature, full_name, doc_path, created_at FROM feature_points ORDER BY id")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def get_by_id(feature_id: int) -> dict | None:
        """根据ID获取功能点"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, category, feature, full_name, doc_path, created_at FROM feature_points WHERE id = ?", (feature_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def insert(category: str, feature: str, full_name: str, doc_path: str = None) -> int | None:
        """插入单个功能点，若已存在则跳过"""
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO feature_points (category, feature, full_name, doc_path) VALUES (?, ?, ?, ?)",
                (category, feature, full_name, doc_path)
            )
            conn.commit()
            feature_id = cursor.lastrowid
            conn.close()
            return feature_id
        except Exception:
            conn.close()
            return None

    @staticmethod
    def batch_insert(features: list[dict], doc_path: str = None) -> dict:
        """批量插入功能点

        Args:
            features: [{"category": "xx", "feature": "xx"}, ...]
            doc_path: 来源文档路径

        Returns:
            {"inserted": int, "skipped": int}
        """
        conn = get_connection()
        cursor = conn.cursor()
        inserted = 0
        skipped = 0

        for fp in features:
            full_name = f"{fp['category']}-{fp['feature']}"
            try:
                cursor.execute(
                    "INSERT INTO feature_points (category, feature, full_name, doc_path) VALUES (?, ?, ?, ?)",
                    (fp["category"], fp["feature"], full_name, doc_path)
                )
                inserted += 1
            except Exception:
                skipped += 1

        conn.commit()
        conn.close()
        return {"inserted": inserted, "skipped": skipped}

    @staticmethod
    def delete_by_id(feature_id: int) -> bool:
        """删除指定功能点"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM feature_points WHERE id = ?", (feature_id,))
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        return deleted

    @staticmethod
    def clear_all() -> int:
        """清空所有功能点"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM feature_points")
        count = cursor.rowcount
        conn.commit()
        conn.close()
        return count

    @staticmethod
    def count() -> int:
        """获取功能点总数"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM feature_points")
        count = cursor.fetchone()["cnt"]
        conn.close()
        return count

    @staticmethod
    def exists_by_doc(doc_path: str) -> bool:
        """检查指定文档是否已提取过功能点"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM feature_points WHERE doc_path = ?", (doc_path,))
        count = cursor.fetchone()["cnt"]
        conn.close()
        return count > 0

    @staticmethod
    def get_by_doc(doc_path: str) -> list[dict]:
        """获取指定文档的所有功能点"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, category, feature, full_name, doc_path, created_at FROM feature_points WHERE doc_path = ? ORDER BY id", (doc_path,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
