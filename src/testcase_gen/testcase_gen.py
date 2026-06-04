import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from chains import TestCaseGenPipeline
from db.database import init_db
from db.feature_repo import FeatureRepo


if __name__ == "__main__":
    init_db()
    pipeline = TestCaseGenPipeline()

    # print("\n=== 从 Word 文档提取功能点并存储 ===")
    # result = pipeline.extract_and_save_features()
    #
    # print(f"提取到 {len(result['features'])} 个功能点")
    # print(f"存储结果: 新增 {result['stats']['inserted']} 条, 跳过 {result['stats']['skipped']} 条")
    #
    # print("\n=== 数据库中所有功能点 ===")
    # features = FeatureRepo.get_all()
    # for f in features:
    #     print(f"  [{f['id']}] {f['full_name']} (来源: {f['doc_path']})")
    #
    # print(f"\n总计: {FeatureRepo.count()} 条")

    # print("\n=== 生成测试用例 ===")
    test_point_query = "通用功能-个人中心的相关说明是什么？"
    test_point = pipeline.invoke_rag(test_point_query)
    #
    print("-------------------------测试功能点-------------------------")
    print(test_point)
    #
    # test_case = pipeline.invoke_test_gen(context=test_point, input_desc="登录，修改密码功能")
    #
    # print("-------------------------测试用例-------------------------")
    # print(f"生成了 {len(test_case.test_cases)} 个测试用例")
    # for i, case in enumerate(test_case.test_cases, 1):
    #     print(f"\n--- 测试用例 {i} ---")
    #     print(f"模块名称：{case.module_name}")
    #     print(f"功能项：{case.function}")
    #     print(f"用例说明：{case.case_description}")
    #     print(f"前置条件：{case.precondition}")
    #     print(f"输入：{case.input_data}")
    #     print(f"执行步骤：{case.steps}")
    #     print(f"预期结果：{case.expected_result}")
    #     print(f"重要程度：{case.priority}")
    #     print(f"测试结果：{case.test_result}")
