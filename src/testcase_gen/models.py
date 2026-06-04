from typing import List

from pydantic import BaseModel, Field


class TestCase(BaseModel):
    """单个测试用例的结构定义"""
    module_name: str = Field(description="模块名称")
    function: str = Field(description="功能项")
    case_description: str = Field(description="用例说明")
    precondition: str = Field(description="前置条件")
    input_data: str = Field(description="输入")
    steps: str = Field(description="执行步骤")
    expected_result: str = Field(description="预期结果")
    priority: str = Field(description="重要程度")
    test_result: str = Field(description="执行用例测试结果")


class TestCaseList(BaseModel):
    """测试用例列表"""
    test_cases: List[TestCase] = Field(description="生成的测试用例列表")


class FeaturePoint(BaseModel):
    """单个功能点"""
    category: str = Field(description="功能点分类，如：通用功能、用户管理、订单管理等")
    feature: str = Field(description="具体功能点，如：登录、修改密码、下单等")


class FeaturePointList(BaseModel):
    """功能点列表"""
    feature_points: List[FeaturePoint] = Field(description="从目录中提取的功能点列表")
