import React, { useState, useEffect } from 'react'
import { Table, Card, Statistic, Row, Col, Tag, Button, message, Popconfirm, Modal, Checkbox, Space, Spin, Alert, Tooltip } from 'antd'
import { ReloadOutlined, DeleteOutlined, ExperimentOutlined, SaveOutlined, DownloadOutlined, ClockCircleOutlined } from '@ant-design/icons'
import { featureApi, testCaseApi } from '../api'
import * as XLSX from 'xlsx-js-style'

function SavedPanel() {
  const [features, setFeatures] = useState([])
  const [savedCases, setSavedCases] = useState({})
  const [loading, setLoading] = useState(false)
  const [exportModalOpen, setExportModalOpen] = useState(false)

  const fetchData = async () => {
    setLoading(true)
    try {
      const [featuresRes, statsRes] = await Promise.all([
        featureApi.getAll(),
        testCaseApi.getStats(),
      ])

      if (featuresRes.data.code === 0) {
        setFeatures(featuresRes.data.data)
      }

      if (statsRes.data.code === 0) {
        const casesByFeature = {}
        for (const item of statsRes.data.data.by_feature || []) {
          casesByFeature[item.feature_name] = item.case_count
        }
        setSavedCases(casesByFeature)
      }
    } catch (err) {
      message.error('获取数据失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const handleDeleteCase = async (caseId) => {
    try {
      const res = await testCaseApi.delete(caseId)
      if (res.data.code === 0) {
        message.success('删除成功')
        fetchData()
      }
    } catch (err) {
      message.error('删除失败')
    }
  }

  const columns = [
    {
      title: '功能点',
      dataIndex: 'full_name',
      render: (text) => <Tag color="blue">{text}</Tag>,
    },
    {
      title: '已保存用例',
      dataIndex: 'id',
      render: (_, record) => {
        const count = savedCases[record.full_name] || 0
        return <Tag color="green">{count} 条</Tag>
      },
    },
    {
      title: '分类',
      dataIndex: 'category',
    },
    {
      title: '具体功能',
      dataIndex: 'feature',
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      render: (_, record) => (
        <Space>
          <GenerateCaseButton featureId={record.id} featureName={record.full_name} onSaved={fetchData} />
          <ExpandableCaseTable featureId={record.id} featureName={record.full_name} caseCount={savedCases[record.full_name] || 0} onDelete={handleDeleteCase} onRefresh={fetchData} />
        </Space>
      ),
    },
  ]

  const totalCases = Object.values(savedCases).reduce((sum, count) => sum + count, 0)

  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={8}>
          <Card>
            <Statistic title="功能点总数" value={features.length} suffix="个" loading={loading} />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic title="已保存用例" value={totalCases} suffix="条" loading={loading} />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic title="已覆盖功能点" value={Object.keys(savedCases).filter((k) => savedCases[k] > 0).length} suffix="个" loading={loading} />
          </Card>
        </Col>
      </Row>

      <Space style={{ marginBottom: 16 }}>
        <Button icon={<ReloadOutlined />} onClick={fetchData}>
          刷新
        </Button>
        <Button type="primary" icon={<DownloadOutlined />} onClick={() => setExportModalOpen(true)}>
          导出Excel
        </Button>
      </Space>

      <Table
        columns={columns}
        dataSource={features}
        loading={loading}
        rowKey="id"
        pagination={{ pageSize: 20 }}
      />

      <ExportModal features={features} open={exportModalOpen} onCancel={() => setExportModalOpen(false)} />
    </div>
  )
}

function ExportModal({ features, open, onCancel }) {
  const [selectedIds, setSelectedIds] = useState([])
  const [exporting, setExporting] = useState(false)

  const handleSelectAll = (checked) => {
    if (checked) {
      setSelectedIds(features.map((f) => f.id))
    } else {
      setSelectedIds([])
    }
  }

  const handleSelect = (id, checked) => {
    if (checked) {
      setSelectedIds((prev) => [...prev, id])
    } else {
      setSelectedIds((prev) => prev.filter((i) => i !== id))
    }
  }

  const handleExport = async () => {
    if (selectedIds.length === 0) {
      message.warning('请至少选择一个功能点')
      return
    }

    setExporting(true)
    try {
      const wb = XLSX.utils.book_new()
      const headerRow = ['模块名称', '功能项', '用例说明', '前置条件', '输入', '执行步骤', '预期结果', '重要程度', '执行用例测试结果']
      const wsData = [headerRow]
      const merges = []

      let rowIdx = 1
      for (const featureId of selectedIds) {
        const res = await featureApi.getTestCases(featureId)
        if (res.data.code === 0) {
          const feature = res.data.data.feature
          const cases = res.data.data.test_cases

          wsData.push([feature.full_name])
          merges.push({ s: { r: rowIdx, c: 0 }, e: { r: rowIdx, c: 8 } })
          rowIdx += 1

          for (const tc of cases) {
            wsData.push([
              tc.module_name,
              tc.function,
              tc.case_description,
              tc.precondition,
              tc.input_data,
              tc.steps,
              tc.expected_result,
              tc.priority,
              tc.test_result,
            ])
            rowIdx += 1
          }
        }
      }

      const ws = XLSX.utils.aoa_to_sheet(wsData)

      ws['!cols'] = [
        { wch: 15 }, { wch: 15 }, { wch: 25 }, { wch: 25 },
        { wch: 20 }, { wch: 30 }, { wch: 30 }, { wch: 10 }, { wch: 15 },
      ]
      ws['!merges'] = merges

      const grayFill = { patternType: 'solid', fgColor: { rgb: 'D9D9D9' } }
      const headerStyle = { fill: grayFill, font: { bold: true }, alignment: { horizontal: 'center', vertical: 'center' } }
      const featureStyle = { fill: grayFill, font: { bold: true }, alignment: { horizontal: 'center', vertical: 'center' } }

      for (let c = 0; c < 9; c++) {
        const cellRef = XLSX.utils.encode_cell({ r: 0, c })
        if (ws[cellRef]) {
          ws[cellRef].s = headerStyle
        }
      }

      let currentRow = 1
      for (const featureId of selectedIds) {
        const res = await featureApi.getTestCases(featureId)
        if (res.data.code === 0) {
          const cases = res.data.data.test_cases
          for (let c = 0; c < 9; c++) {
            const cellRef = XLSX.utils.encode_cell({ r: currentRow, c })
            if (ws[cellRef]) {
              ws[cellRef].s = featureStyle
            }
          }
          currentRow += 1 + cases.length
        }
      }

      XLSX.utils.book_append_sheet(wb, ws, '测试用例')

      const wbout = XLSX.write(wb, { bookType: 'xlsx', type: 'array' })
      const blob = new Blob([wbout], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = '测试用例.xlsx'
      a.click()
      URL.revokeObjectURL(url)

      message.success('导出成功')
      onCancel()
    } catch (err) {
      console.error('Export error:', err)
      message.error('导出失败')
    } finally {
      setExporting(false)
    }
  }

  return (
    <Modal
      title="导出测试用例"
      open={open}
      onCancel={onCancel}
      confirmLoading={exporting}
      onOk={handleExport}
      width={600}
    >
      <div style={{ marginBottom: 12 }}>
        <Checkbox
          onChange={(e) => handleSelectAll(e.target.checked)}
          checked={selectedIds.length === features.length && features.length > 0}
        >
          全选
        </Checkbox>
      </div>
      <div style={{ maxHeight: 400, overflow: 'auto' }}>
        {features.map((f) => (
          <div key={f.id} style={{ padding: '4px 0' }}>
            <Checkbox
              checked={selectedIds.includes(f.id)}
              onChange={(e) => handleSelect(f.id, e.target.checked)}
            >
              {f.full_name}
            </Checkbox>
          </div>
        ))}
      </div>
    </Modal>
  )
}

/** 格式化耗时显示 */
function formatElapsed(seconds) {
  if (seconds == null || seconds === 0) return '-'
  if (seconds >= 60) {
    const m = Math.floor(seconds / 60)
    const s = Math.round(seconds % 60)
    return s > 0 ? `${m}分${s}秒` : `${m}分钟`
  }
  return `${seconds}秒`
}

function GenerateCaseButton({ featureId, featureName, onSaved }) {
  const [modalOpen, setModalOpen] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [testCases, setTestCases] = useState([])
  const [selectedIndices, setSelectedIndices] = useState([])
  const [elapsedTime, setElapsedTime] = useState(null)

  const handleGenerate = async () => {
    setModalOpen(true)
    setGenerating(true)
    setTestCases([])
    setSelectedIndices([])
    setElapsedTime(null)

    try {
      const res = await testCaseApi.generate(featureName)
      if (res.data.code === 0) {
        setTestCases(res.data.data.test_cases || [])
        setElapsedTime(res.data.data.elapsed_time)
        const timeStr = formatElapsed(res.data.data.elapsed_time)
        message.success(`已生成 ${res.data.data.test_cases?.length || 0} 个测试用例，耗时 ${timeStr}`)
      } else {
        message.error(res.data.message || '生成失败')
      }
    } catch (err) {
      message.error('生成测试用例失败')
    } finally {
      setGenerating(false)
    }
  }

  const handleSelectAll = (checked) => {
    if (checked) {
      setSelectedIndices(Array.from({ length: testCases.length }, (_, i) => i))
    } else {
      setSelectedIndices([])
    }
  }

  const handleSelect = (index, checked) => {
    if (checked) {
      setSelectedIndices((prev) => [...prev, index])
    } else {
      setSelectedIndices((prev) => prev.filter((i) => i !== index))
    }
  }

  const handleSave = async () => {
    if (selectedIndices.length === 0) {
      message.warning('请先勾选要通过的测试用例')
      return
    }

    const casesToSave = selectedIndices.map((i) => testCases[i])

    try {
      const res = await testCaseApi.save(featureId, casesToSave)
      if (res.data.code === 0) {
        message.success(`已保存 ${res.data.data.inserted} 个测试用例`)
        setModalOpen(false)
        onSaved()
      } else {
        message.error(res.data.message || '保存失败')
      }
    } catch (err) {
      message.error('保存失败')
    }
  }

  const renderEllipsis = (text) => (
    <Tooltip title={text} placement="topLeft">
      <div style={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
        {text}
      </div>
    </Tooltip>
  )

  const caseColumns = [
    {
      title: (
        <Checkbox
          onChange={(e) => handleSelectAll(e.target.checked)}
          checked={selectedIndices.length === testCases.length && testCases.length > 0}
        />
      ),
      width: 50,
      render: (_, record, index) => (
        <Checkbox
          checked={selectedIndices.includes(index)}
          onChange={(e) => handleSelect(index, e.target.checked)}
        />
      ),
    },
    { title: '模块', dataIndex: 'module_name', width: 100 },
    { title: '功能项', dataIndex: 'function', width: 100 },
    { title: '用例说明', dataIndex: 'case_description', width: 150 },
    { title: '前置条件', dataIndex: 'precondition', width: 150, ellipsis: true, render: renderEllipsis },
    { title: '输入', dataIndex: 'input_data', width: 150, ellipsis: true, render: renderEllipsis },
    { title: '执行步骤', dataIndex: 'steps', width: 200, ellipsis: true, render: renderEllipsis },
    { title: '预期结果', dataIndex: 'expected_result', width: 200, ellipsis: true, render: renderEllipsis },
    {
      title: '优先级',
      dataIndex: 'priority',
      width: 70,
      render: (text) => {
        const color = text === '高' ? 'red' : text === '中' ? 'orange' : 'green'
        return <Tag color={color}>{text}</Tag>
      },
    },
  ]

  return (
    <>
      <Button type="primary" size="small" icon={<ExperimentOutlined />} onClick={handleGenerate}>
        生成用例
      </Button>

      <Modal
        title={`生成测试用例 - ${featureName}`}
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        width={1200}
        footer={
          <Space>
            <span>已选择 {selectedIndices.length}/{testCases.length} 条</span>
            <Button onClick={() => setModalOpen(false)}>取消</Button>
            <Button
              type="primary"
              icon={<SaveOutlined />}
              disabled={selectedIndices.length === 0}
              onClick={handleSave}
            >
              保存已选
            </Button>
          </Space>
        }
      >
        {generating ? (
          <div style={{ textAlign: 'center', padding: 40 }}>
            <Spin size="large" tip="正在调用大模型生成测试用例，请稍候..." />
          </div>
        ) : testCases.length === 0 ? (
          <Alert message="未生成测试用例" description="请等待生成完成" type="info" showIcon />
        ) : (
          <>
            {elapsedTime > 0 && (
              <div style={{ marginBottom: 12 }}>
                <Tag icon={<ClockCircleOutlined />} color="processing">
                  耗时 {formatElapsed(elapsedTime)}
                </Tag>
              </div>
            )}
            <Table
              columns={caseColumns}
              dataSource={testCases.map((c, i) => ({ ...c, key: i }))}
              size="small"
              pagination={{ pageSize: 10 }}
              rowKey="key"
              scroll={{ x: 1170 }}
            />
          </>
        )}
      </Modal>
    </>
  )
}

function ExpandableCaseTable({ featureId, featureName, caseCount, onDelete, onRefresh }) {
  const [modalOpen, setModalOpen] = useState(false)
  const [cases, setCases] = useState([])
  const [loading, setLoading] = useState(false)

  const handleOpen = async () => {
    setModalOpen(true)
    setLoading(true)
    await fetchTestCases()
    setLoading(false)
  }

  const fetchTestCases = async () => {
    try {
      const res = await featureApi.getTestCases(featureId)
      if (res.data.code === 0) {
        setCases(res.data.data.test_cases)
      }
    } catch (err) {
      message.error('获取测试用例失败')
    }
  }

  const handleDelete = async (caseId) => {
    try {
      const res = await testCaseApi.delete(caseId)
      if (res.data.code === 0) {
        message.success('删除成功')
        await fetchTestCases()
        if (onRefresh) onRefresh()
      } else {
        message.error(res.data.message || '删除失败')
      }
    } catch (err) {
      message.error('删除失败')
    }
  }

  const handleClearAll = async () => {
    try {
      const res = await testCaseApi.deleteByFeature(featureId)
      if (res.data.code === 0) {
        message.success(`已清空 ${res.data.data.deleted} 条用例`)
        await fetchTestCases()
        if (onRefresh) onRefresh()
      } else {
        message.error(res.data.message || '清空失败')
      }
    } catch (err) {
      message.error('清空失败')
    }
  }

  const renderEllipsis = (text) => (
    <Tooltip title={text} placement="topLeft">
      <div style={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
        {text}
      </div>
    </Tooltip>
  )

  const caseColumns = [
    { title: '模块', dataIndex: 'module_name', width: 100 },
    { title: '功能项', dataIndex: 'function', width: 100 },
    { title: '用例说明', dataIndex: 'case_description', width: 180 },
    { title: '前置条件', dataIndex: 'precondition', width: 180, ellipsis: true, render: renderEllipsis },
    { title: '输入', dataIndex: 'input_data', width: 160, ellipsis: true, render: renderEllipsis },
    { title: '执行步骤', dataIndex: 'steps', width: 220, ellipsis: true, render: renderEllipsis },
    { title: '预期结果', dataIndex: 'expected_result', width: 220, ellipsis: true, render: renderEllipsis },
    {
      title: '优先级',
      dataIndex: 'priority',
      width: 70,
      render: (text) => {
        const color = text === '高' ? 'red' : text === '中' ? 'orange' : 'green'
        return <Tag color={color}>{text}</Tag>
      },
    },
    {
      title: '测试结果',
      dataIndex: 'test_result',
      width: 80,
      render: (text) => <Tag color={text === '未执行' ? 'default' : 'success'}>{text}</Tag>,
    },
    {
      title: '操作',
      key: 'action',
      width: 70,
      render: (_, record) => (
        <Popconfirm title="确定删除?" onConfirm={() => handleDelete(record.id)}>
          <Button type="link" danger icon={<DeleteOutlined />} size="small" />
        </Popconfirm>
      ),
    },
  ]

  const totalWidth = 100 + 100 + 180 + 180 + 160 + 220 + 220 + 70 + 80 + 70

  return (
    <>
      <Button size="small" onClick={handleOpen}>
        查看用例
      </Button>

      <Modal
        title={`测试用例 — ${featureName}`}
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        width="90%"
        style={{ top: 20 }}
        footer={
          <Space>
            {cases.length > 0 && (
              <Popconfirm title={`确定清空该功能点下的 ${cases.length} 条用例?`} onConfirm={handleClearAll}>
                <Button danger>清空用例</Button>
              </Popconfirm>
            )}
            <Button onClick={() => setModalOpen(false)}>关闭</Button>
          </Space>
        }
      >
        <Table
          columns={caseColumns}
          dataSource={cases}
          size="small"
          loading={loading}
          pagination={{ pageSize: 10, showTotal: (t) => `共 ${t} 条` }}
          rowKey="id"
          scroll={{ x: totalWidth }}
        />
      </Modal>
    </>
  )
}

export default SavedPanel
