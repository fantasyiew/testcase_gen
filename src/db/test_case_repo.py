from .database import get_connection


class TestCaseRepo:
    """测试用例数据访问层"""

    @staticmethod
    def get_by_feature_id(feature_id: int) -> list[dict]:
        """获取指定功能点下已保存的测试用例"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM test_cases WHERE feature_point_id = ? ORDER BY id",
            (feature_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def get_all() -> list[dict]:
        """获取所有已保存的测试用例"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT tc.*, fp.full_name as feature_name
            FROM test_cases tc
            LEFT JOIN feature_points fp ON tc.feature_point_id = fp.id
            ORDER BY tc.id
        """)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def get_stats() -> dict:
        """获取测试用例统计信息"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as total FROM test_cases")
        total = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT fp.full_name as feature_name, COUNT(tc.id) as case_count
            FROM feature_points fp
            LEFT JOIN test_cases tc ON fp.id = tc.feature_point_id
            GROUP BY fp.id
            HAVING case_count > 0
        """)
        by_feature = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return {"total": total, "by_feature": by_feature}

    @staticmethod
    def batch_insert(feature_id: int, test_cases: list[dict]) -> int:
        """批量保存测试用例（已通过审核）

        Args:
            feature_id: 关联的功能点ID
            test_cases: 测试用例列表

        Returns:
            插入的数量
        """
        conn = get_connection()
        cursor = conn.cursor()
        inserted = 0

        for case in test_cases:
            cursor.execute(
                """INSERT INTO test_cases
                   (feature_point_id, module_name, function, case_description, precondition,
                    input_data, steps, expected_result, priority, test_result, review_status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    feature_id,
                    case.get("module_name", ""),
                    case.get("function", ""),
                    case.get("case_description", ""),
                    case.get("precondition", ""),
                    case.get("input_data", ""),
                    case.get("steps", ""),
                    case.get("expected_result", ""),
                    case.get("priority", "中"),
                    case.get("test_result", "未执行"),
                    "已通过"
                )
            )
            inserted += 1

        conn.commit()
        conn.close()
        return inserted

    @staticmethod
    def delete_by_id(case_id: int) -> bool:
        """删除指定测试用例"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM test_cases WHERE id = ?", (case_id,))
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        return deleted

    @staticmethod
    def delete_by_feature_id(feature_id: int) -> int:
        """删除指定功能点下的所有测试用例"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM test_cases WHERE feature_point_id = ?", (feature_id,))
        count = cursor.rowcount
        conn.commit()
        conn.close()
        return count
