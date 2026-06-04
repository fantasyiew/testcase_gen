import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "testcase_gen.db")


def get_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    """初始化数据库表"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feature_points (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            feature TEXT NOT NULL,
            full_name TEXT NOT NULL,
            doc_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(full_name, doc_path)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS test_cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            feature_point_id INTEGER,
            module_name TEXT,
            function TEXT,
            case_description TEXT,
            precondition TEXT,
            input_data TEXT,
            steps TEXT,
            expected_result TEXT,
            priority TEXT,
            test_result TEXT DEFAULT '未执行',
            review_status TEXT DEFAULT '已通过',
            review_comment TEXT,
            reviewed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (feature_point_id) REFERENCES feature_points(id)
        )
    """)

    conn.commit()
    conn.close()


def get_db():
    """获取数据库连接的上下文管理器"""
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()
