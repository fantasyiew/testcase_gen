import React, { useState, useEffect } from 'react'
import { Button, Table, message, Space, Card, Collapse, Checkbox, Tag, Spin, Alert, Row, Col, Statistic } from 'antd'
import { ExperimentOutlined, SaveOutlined, ReloadOutlined } from '@ant-design/icons'
import { featureApi, testCaseApi } from '../api'

function GeneratePanel() {
  const [features, setFeatures] = useState([])
  const [generating, setGenerating] = useState(false)
  const [generationResults, setGenerationResults] = useState([])
  const [selectedCases, setSelectedCases] = useState({})

  const fetchFeatures = async () => {
    try {
      const res = await featureApi.getAll()
      if (res.data.code === 0) {
        setFeatures(res.data.data)
      }
    } catch (err) {
      message.error('获取功能点失败')
    }
  }

  useEffect(() => {
    fetchFeatures()
  }, [])

  const handleGenerateAll = async () => {
    if (features.length === 0) {
      message.warning('请先提取功能点')
      return
    }

    setGenerating(true)
    setGenerationResults([])
    setSelectedCases({})

    try {
      const res = await testCaseApi.generateAll()
      if (res.data.code === 0) {
        const results = res.data.data.results
        setGenerationResults(results)

        const initialSelected = {}
        results.forEach((r) => {
          initialSelected[r.feature_name] = []
        })
        setSelectedCases(initialSelected)

        message.success(`已生成 ${res.data.data.total_cases} 个测试用例，请审核后保存`)
      } else {
        message.error(res.data.message || '生成失败')
      }
    } catch (err) {
      message.error('生成测试用例失败')
    } finally {
      setGenerating(false)
    }
  }

  const handleCaseSelect = (featureName, caseIndex, checked) => {
    setSelectedCases((prev) => {
      const current = prev[featureName] || []
      if (checked) {
        return { ...prev, [featureName]: [...current, caseIndex] }
      } else {
        return { ...prev, [featureName]: current.filter((i) => i !== caseIndex) }
      }
    })
  }

  const handleSelectAll = (featureName, totalCases, checked) => {
    if (checked) {
      setSelectedCases((prev) => ({
        ...prev,
        [featureName]: Array.from({ length: totalCases }, (_, i) => i),
      }))
    } else {
      setSelectedCases((prev) => ({ ...prev, [featureName]: [] }))
    }
  }

  const handleSave = async (featureName) => {
    const feature = features.find((f) => f.full_name === featureName)
    if (!feature) return

    const result = generationResults.find((r) => r.feature_name === featureName)
    if (!result) return

    const selectedIndices = selectedCases[featureName] || []
    const casesToSave = selectedIndices.map((i) => result.test_cases[i])

    if (casesToSave.length === 0) {
      message.warning('请先勾选要通过的测试用例')
      return
    }

    try {
      const res = await testCaseApi.save(feature.id, casesToSave)
      if (res.data.code === 0) {
        message.success(`已保存 ${res.data.data.inserted} 个测试用例`)
        setSelectedCases((prev) => ({ ...prev, [featureName]: [] }))
      } else {
        message.error(res.data.message || '保存失败')
      }
    } catch (err) {
      message.error('保存失败')
    }
  }

  const getCaseColumns = (featureName) => [
    {
      title: (
        <Checkbox
          onChange={(e) => {
            const result = generationResults.find((r) => r.feature_name === featureName)
            if (result) handleSelectAll(featureName, result.test_cases.length, e.target.checked)
          }}
          checked={(selectedCases[featureName] || []).length === (generationResults.find((r) => r.feature_name === featureName)?.test_cases.length || 0)}
        />
      ),
      width: 50,
    },
    { title: '模块名称', dataIndex: 'module_name', width: 120 },
    { title: '功能项', dataIndex: 'function', width: 100 },
    { title: '用例说明', dataIndex: 'case_description', width: 180 },
    { title: '前置条件', dataIndex: 'precondition', ellipsis: true },
    { title: '输入', dataIndex: 'input_data', ellipsis: true },
    { title: '执行步骤', dataIndex: 'steps', ellipsis: true },
    { title: '预期结果', dataIndex: 'expected_result', ellipsis: true },
    {
      title: '优先级',
      dataIndex: 'priority',
      width: 80,
      render: (text) => {
        const color = text === '高' ? 'red' : text === '中' ? 'orange' : 'green'
        return <Tag color={color}>{text}</Tag>
      },
    },
  ]

  const totalGenerated = generationResults.reduce((sum, r) => sum + (r.test_cases?.length || 0), 0)
  const totalSelected = Object.values(selectedCases).reduce((sum, arr) => sum + arr.length, 0)

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Button type="primary" icon={<ExperimentOutlined />} onClick={handleGenerateAll} loading={generating}>
          生成全部测试用例
        </Button>
        <Button icon={<ReloadOutlined />} onClick={fetchFeatures}>
          刷新功能点
        </Button>
        {totalSelected > 0 && (
          <Tag color="processing">已选择 {totalSelected} 个用例待保存</Tag>
        )}
      </Space>

      {generating && (
        <div style={{ textAlign: 'center', padding: 40 }}>
          <Spin size="large" tip="正在调用大模型生成测试用例，请稍候..." />
        </div>
      )}

      {!generating && generationResults.length === 0 && (
        <Alert
          message="提示"
          description="点击「生成全部测试用例」按钮开始批量生成。生成结果需人工审核后保存。"
          type="info"
          showIcon
        />
      )}

      {!generating && generationResults.length > 0 && (
        <>
          <Row gutter={16} style={{ marginBottom: 16 }}>
            <Col span={8}>
              <Card>
                <Statistic title="功能点数量" value={generationResults.length} suffix="个" />
              </Card>
            </Col>
            <Col span={8}>
              <Card>
                <Statistic title="生成用例总数" value={totalGenerated} suffix="条" />
              </Card>
            </Col>
            <Col span={8}>
              <Card>
                <Statistic title="已选择保存" value={totalSelected} suffix="条" />
              </Card>
            </Col>
          </Row>

          <Collapse defaultActiveKey={[]}>
            {generationResults.map((result) => {
              const selectedCount = (selectedCases[result.feature_name] || []).length
              const hasError = result.error

              return (
                <Collapse.Panel
                  key={result.feature_name}
                  header={
                    <Space>
                      <Tag color="blue">{result.feature_name}</Tag>
                      <Tag>{result.test_cases?.length || 0} 条用例</Tag>
                      {selectedCount > 0 && <Tag color="green">已选 {selectedCount}</Tag>}
                      {hasError && <Tag color="red">生成失败</Tag>}
                    </Space>
                  }
                >
                  {hasError ? (
                    <Alert message="生成失败" description={result.error} type="error" />
                  ) : (
                    <>
                      <div style={{ marginBottom: 12 }}>
                        <Space>
                          <span>已选择 {selectedCount}/{result.test_cases?.length || 0} 条</span>
                          <Button
                            size="small"
                            type="primary"
                            icon={<SaveOutlined />}
                            disabled={selectedCount === 0}
                            onClick={() => handleSave(result.feature_name)}
                          >
                            保存已选
                          </Button>
                        </Space>
                      </div>
                      <Table
                        columns={getCaseColumns(result.feature_name)}
                        dataSource={result.test_cases?.map((c, i) => ({ ...c, key: i }))}
                        size="small"
                        pagination={false}
                        rowKey="key"
                      />
                    </>
                  )}
                </Collapse.Panel>
              )
            })}
          </Collapse>
        </>
      )}
    </div>
  )
}

export default GeneratePanel
