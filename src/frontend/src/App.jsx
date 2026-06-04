import React, { useState } from 'react'
import { Layout, Menu, Typography } from 'antd'
import {
  FileTextOutlined,
  ExperimentOutlined,
  DatabaseOutlined,
} from '@ant-design/icons'
import FeaturePanel from './components/FeaturePanel'
import GeneratePanel from './components/GeneratePanel'
import SavedPanel from './components/SavedPanel'

const { Header, Sider, Content } = Layout
const { Title } = Typography

function App() {
  const [activeTab, setActiveTab] = useState('features')

  const menuItems = [
    {
      key: 'features',
      icon: <FileTextOutlined />,
      label: '功能点管理',
    },
    {
      key: 'generate',
      icon: <ExperimentOutlined />,
      label: '测试用例生成',
    },
    {
      key: 'saved',
      icon: <DatabaseOutlined />,
      label: '已保存用例',
    },
  ]

  const renderContent = () => {
    switch (activeTab) {
      case 'features':
        return <FeaturePanel />
      case 'generate':
        return <GeneratePanel />
      case 'saved':
        return <SavedPanel />
      default:
        return <FeaturePanel />
    }
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider theme="light" width={220} style={{ borderRight: '1px solid #f0f0f0' }}>
        <div style={{ padding: '20px 16px', borderBottom: '1px solid #f0f0f0' }}>
          <Title level={4} style={{ margin: 0 }}>
            TestCase Gen
          </Title>
        </div>
        <Menu
          mode="inline"
          selectedKeys={[activeTab]}
          items={menuItems}
          onClick={({ key }) => setActiveTab(key)}
          style={{ borderRight: 'none' }}
        />
      </Sider>
      <Layout>
        <Header style={{ background: '#fff', padding: '0 24px', borderBottom: '1px solid #f0f0f0' }}>
          <Title level={4} style={{ margin: '12px 0 0' }}>
            {menuItems.find((item) => item.key === activeTab)?.label}
          </Title>
        </Header>
        <Content style={{ margin: '24px 16px', padding: 24, background: '#fff' }}>
          {renderContent()}
        </Content>
      </Layout>
    </Layout>
  )
}

export default App
