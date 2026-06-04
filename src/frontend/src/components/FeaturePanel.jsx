import React, { useState, useEffect } from 'react'
import { Table, Button, Modal, message, Popconfirm, Tag, Space, Upload, Select, Typography } from 'antd'
import { PlusOutlined, DeleteOutlined, ReloadOutlined, UploadOutlined } from '@ant-design/icons'
import { featureApi } from '../api'

const { Text } = Typography

function FeaturePanel() {
  const [features, setFeatures] = useState([])
  const [loading, setLoading] = useState(false)
  const [extractModalOpen, setExtractModalOpen] = useState(false)
  const [uploadedFiles, setUploadedFiles] = useState([])
  const [selectedDoc, setSelectedDoc] = useState(null)

  const fetchFeatures = async () => {
    setLoading(true)
    try {
      const res = await featureApi.getAll()
      if (res.data.code === 0) {
        setFeatures(res.data.data)
      }
    } catch (err) {
      message.error('获取功能点失败')
    } finally {
      setLoading(false)
    }
  }

  const fetchUploadedDocs = async () => {
    try {
      const res = await featureApi.getUploadedDocs()
      if (res.data.code === 0) {
        setUploadedFiles(res.data.data)
      }
    } catch (err) {
      console.error('获取已上传文档失败:', err)
    }
  }

  useEffect(() => {
    fetchFeatures()
    fetchUploadedDocs()
  }, [])

  const handleUpload = async (file) => {
    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await featureApi.uploadDoc(formData)
      if (res.data.code === 0) {
        message.success(`文档 "${file.name}" 上传成功`)
        fetchUploadedDocs()
      } else {
        message.error(res.data.message || '上传失败')
      }
    } catch (err) {
      console.error('Upload error:', err)
      message.error(`上传失败: ${err.message || '未知错误'}`)
    }
    return false
  }

  const handleExtract = async () => {
    if (!selectedDoc) {
      message.warning('请先选择或上传文档')
      return
    }

    setLoading(true)
    try {
      const res = await featureApi.extract(selectedDoc)
      if (res.data.code === 0) {
        const { inserted, skipped, cached } = res.data.data.stats
        if (cached) {
          message.info(`已从缓存加载 ${skipped} 个功能点`)
        } else {
          message.success(`成功提取 ${inserted} 个功能点，跳过 ${skipped} 个`)
        }
        setExtractModalOpen(false)
        fetchFeatures()
      } else {
        message.error(res.data.message || '提取失败')
      }
    } catch (err) {
      message.error('提取功能点失败')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id) => {
    try {
      const res = await featureApi.delete(id)
      if (res.data.code === 0) {
        message.success('删除成功')
        fetchFeatures()
      }
    } catch (err) {
      message.error('删除失败')
    }
  }

  const handleClear = async () => {
    try {
      const res = await featureApi.clear()
      if (res.data.code === 0) {
        message.success(res.data.message)
        fetchFeatures()
      }
    } catch (err) {
      message.error('清空失败')
    }
  }

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      width: 60,
    },
    {
      title: '功能点',
      dataIndex: 'full_name',
      render: (text) => <Tag color="blue">{text}</Tag>,
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
      title: '来源文档',
      dataIndex: 'doc_path',
      ellipsis: true,
    },
    {
      title: '提取时间',
      dataIndex: 'created_at',
      width: 180,
    },
    {
      title: '操作',
      key: 'action',
      width: 100,
      render: (_, record) => (
        <Popconfirm title="确定删除?" onConfirm={() => handleDelete(record.id)}>
          <Button type="link" danger icon={<DeleteOutlined />} size="small">
            删除
          </Button>
        </Popconfirm>
      ),
    },
  ]

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => {
          fetchUploadedDocs()
          setExtractModalOpen(true)
        }}>
          从文档提取
        </Button>
        <Button icon={<ReloadOutlined />} onClick={fetchFeatures}>
          刷新
        </Button>
        <Popconfirm title="确定清空所有功能点?" onConfirm={handleClear}>
          <Button danger>清空全部</Button>
        </Popconfirm>
      </Space>

      <Table
        columns={columns}
        dataSource={features}
        loading={loading}
        rowKey="id"
        pagination={{ pageSize: 20 }}
      />

      <Modal
        title="从文档提取功能点"
        open={extractModalOpen}
        onOk={handleExtract}
        onCancel={() => setExtractModalOpen(false)}
        confirmLoading={loading}
        width={600}
      >
        <div style={{ marginBottom: 16 }}>
          <Text strong>上传新文档：</Text>
          <Upload
            beforeUpload={handleUpload}
            accept=".docx,.doc"
            maxCount={1}
            showUploadList={false}
          >
            <Button icon={<UploadOutlined />}>选择 .docx 文件</Button>
          </Upload>
        </div>

        <div>
          <Text strong>选择已上传的文档：</Text>
          <Select
            style={{ width: '100%', marginTop: 8 }}
            placeholder="选择文档"
            value={selectedDoc}
            onChange={setSelectedDoc}
            options={uploadedFiles.map((f) => ({ label: f.name, value: f.path }))}
          />
          {uploadedFiles.length === 0 && (
            <Text type="secondary" style={{ display: 'block', marginTop: 8 }}>
              暂无已上传的文档，请先上传
            </Text>
          )}
        </div>
      </Modal>
    </div>
  )
}

export default FeaturePanel
