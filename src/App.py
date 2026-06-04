import sys
import os
import shutil

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from testcase_gen.chains import TestCaseGenPipeline
from db.database import init_db
from db.feature_repo import FeatureRepo
from db.test_case_repo import TestCaseRepo

app = FastAPI(title="TestCase Gen API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

_default_doc_path = os.path.join(os.path.dirname(__file__), "testcase_gen", "A1-需求说明书.docx")
pipeline = TestCaseGenPipeline(text_path=_default_doc_path)


class ExtractRequest(BaseModel):
    doc_path: str | None = None


class SaveTestCasesRequest(BaseModel):
    feature_id: int
    test_cases: list[dict]


@app.post("/api/features/upload")
async def upload_document(file: UploadFile = File(...)):
    """上传文档到服务器"""
    if not file.filename.endswith(('.docx', '.doc')):
        return {"code": 1, "message": "仅支持 .docx 或 .doc 格式的文件"}

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    if os.path.exists(file_path):
        return {"code": 1, "message": "该文档已上传"}

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"code": 0, "data": {"path": file_path, "name": file.filename}}
    except Exception as e:
        return {"code": 1, "message": f"上传失败: {str(e)}"}


@app.get("/api/features/uploaded-docs")
def get_uploaded_docs():
    """获取已上传的文档列表"""
    if not os.path.exists(UPLOAD_DIR):
        return {"code": 0, "data": []}

    docs = []
    for filename in os.listdir(UPLOAD_DIR):
        if filename.endswith(('.docx', '.doc')):
            docs.append({
                "name": filename,
                "path": os.path.join(UPLOAD_DIR, filename),
            })
    return {"code": 0, "data": docs}


@app.get("/api/features")
def get_features():
    """获取所有已提取的功能点"""
    features = FeatureRepo.get_all()
    return {"code": 0, "data": features, "total": len(features)}


@app.post("/api/features/extract")
def extract_features(req: ExtractRequest):
    """从文档提取功能点并存储"""
    try:
        result = pipeline.extract_and_save_features(req.doc_path)
        return {"code": 0, "data": result}
    except Exception as e:
        return {"code": 1, "message": str(e)}


@app.delete("/api/features/{feature_id}")
def delete_feature(feature_id: int):
    """删除指定功能点及其关联的测试用例"""
    TestCaseRepo.delete_by_feature_id(feature_id)
    success = FeatureRepo.delete_by_id(feature_id)
    if success:
        return {"code": 0, "message": "删除成功"}
    return {"code": 1, "message": "功能点不存在"}


@app.post("/api/features/clear")
def clear_features():
    """清空所有功能点和测试用例"""
    from db.database import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM test_cases")
    conn.commit()
    conn.close()
    FeatureRepo.clear_all()
    return {"code": 0, "message": "已清空所有数据"}


@app.get("/api/features/{feature_id}/test-cases")
def get_feature_test_cases(feature_id: int):
    """获取指定功能点下已保存的测试用例"""
    feature = FeatureRepo.get_by_id(feature_id)
    if not feature:
        return {"code": 1, "message": "功能点不存在"}
    cases = TestCaseRepo.get_by_feature_id(feature_id)
    return {"code": 0, "data": {"feature": feature, "test_cases": cases}}


@app.post("/api/test-cases/generate")
def generate_test_cases(req: ExtractRequest):
    """为单个功能点生成测试用例（返回给前端审核，不入库）

    Args:
        req.doc_path: 功能点名称（复用 ExtractRequest 的 doc_path 字段）
    """
    try:
        feature_name = req.doc_path
        if not feature_name:
            return {"code": 1, "message": "请提供功能点名称"}
        result = pipeline.generate_test_cases_for_feature(feature_name)
        return {"code": 0, "data": result}
    except Exception as e:
        return {"code": 1, "message": str(e)}


@app.post("/api/test-cases/generate-all")
def generate_all_test_cases():
    """为所有功能点批量生成测试用例（返回给前端审核，不入库）"""
    try:
        results = pipeline.generate_test_cases_for_all_features()
        total_cases = sum(len(r.get("test_cases", [])) for r in results)
        total_elapsed_time = round(sum(r.get("elapsed_time", 0) for r in results), 1)
        return {
            "code": 0,
            "data": {
                "results": results,
                "total_features": len(results),
                "total_cases": total_cases,
                "total_elapsed_time": total_elapsed_time,
            }
        }
    except Exception as e:
        return {"code": 1, "message": str(e)}


@app.post("/api/test-cases/save")
def save_test_cases(req: SaveTestCasesRequest):
    """保存已通过审核的测试用例到数据库"""
    try:
        feature = FeatureRepo.get_by_id(req.feature_id)
        if not feature:
            return {"code": 1, "message": "功能点不存在"}

        inserted = TestCaseRepo.batch_insert(req.feature_id, req.test_cases)
        return {"code": 0, "data": {"inserted": inserted}}
    except Exception as e:
        return {"code": 1, "message": str(e)}


@app.get("/api/test-cases/stats")
def get_test_case_stats():
    """获取测试用例统计信息"""
    stats = TestCaseRepo.get_stats()
    return {"code": 0, "data": stats}


@app.delete("/api/test-cases/{case_id}")
def delete_test_case(case_id: int):
    """删除指定测试用例"""
    success = TestCaseRepo.delete_by_id(case_id)
    if success:
        return {"code": 0, "message": "删除成功"}
    return {"code": 1, "message": "测试用例不存在"}


@app.delete("/api/test-cases/feature/{feature_id}")
def delete_test_cases_by_feature(feature_id: int):
    """删除指定功能点下的所有测试用例"""
    deleted = TestCaseRepo.delete_by_feature_id(feature_id)
    return {"code": 0, "data": {"deleted": deleted}}


_frontend_dist = os.path.join(os.path.dirname(__file__), "frontend", "dist")
if os.path.exists(_frontend_dist):
    app.mount("/", StaticFiles(directory=_frontend_dist, html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
