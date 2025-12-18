import React from 'react';
import ReactDOM from 'react-dom/client';
import ReactFlow, {
  ReactFlowProvider,
  useNodesState,
  useEdgesState,
  addEdge,
  MiniMap,
  Controls,
  Background,
  Handle,
  Position,
  MarkerType,
} from 'reactflow';
import 'reactflow/dist/style.css';

// 自定义节点样式
const nodeStyles = {
  defendant: {
    background: '#ef4444',
    color: 'white',
    border: '2px solid #b91c1c',
    padding: '10px',
    borderRadius: '8px',
    fontWeight: 'bold',
    width: 180,
    textAlign: 'center',
  },
  intermediary: {
    background: '#f59e0b',
    color: 'white',
    border: '1px solid #d97706',
    padding: '8px',
    borderRadius: '6px',
    width: 160,
    fontSize: '12px',
  },
  giver: {
    background: '#3b82f6',
    color: 'white',
    border: '1px solid #1d4ed8',
    padding: '8px',
    borderRadius: '6px',
    width: 150,
    fontSize: '12px',
  },
  money: {
    background: '#10b981',
    color: 'white',
    border: '1px solid #059669',
    padding: '5px',
    borderRadius: '4px',
    fontSize: '11px',
    width: 140,
  },
};

// 自定义节点组件
const CustomNode = ({ data, style }) => (
  <div style={style}>
    <Handle type="target" position={Position.Top} />
    <div>{data.label}</div>
    {data.subLabel && <div style={{ fontSize: '10px', opacity: 0.8 }}>{data.subLabel}</div>}
    <Handle type="source" position={Position.Bottom} />
  </div>
);

const nodeTypes = {
  custom: CustomNode,
};

const initialNodes = [
  // 中心人物
  {
    id: '1',
    type: 'custom',
    data: { label: '被告人：王雄昌', subLabel: '原钦州市长' },
    position: { x: 600, y: 50 },
    style: nodeStyles.defendant,
  },

  // 左侧分支：特殊的"共同受贿"（低分成比例）
  {
    id: 'group1',
    type: 'custom',
    data: { label: '中间人团伙 A', subLabel: '廖炼炼、苏林、黎小宋' },
    position: { x: 200, y: 200 },
    style: nodeStyles.intermediary,
  },
  {
    id: 'fact1',
    type: 'custom',
    data: { label: '事实一：中建交通三公司', subLabel: '总额1700万' },
    position: { x: 100, y: 350 },
    style: nodeStyles.giver,
  },
  {
    id: 'fact2',
    type: 'custom',
    data: { label: '事实二：麻华兴', subLabel: '总额920万(实收1260万)' },
    position: { x: 300, y: 350 },
    style: nodeStyles.giver,
  },
  {
    id: 'share1',
    type: 'custom',
    data: { label: '王分得20%', subLabel: '340万 (廖炼炼保管)' },
    position: { x: 100, y: 450 },
    style: nodeStyles.money,
  },
  {
    id: 'share2',
    type: 'custom',
    data: { label: '王分得20%', subLabel: '180万 (廖炼炼保管)' },
    position: { x: 300, y: 450 },
    style: nodeStyles.money,
  },

  // 中间分支：泰嘉项目烂尾案
  {
    id: 'group2',
    type: 'custom',
    data: { label: '中间人 B', subLabel: '谢斌' },
    position: { x: 600, y: 200 },
    style: nodeStyles.intermediary,
  },
  {
    id: 'fact3',
    type: 'custom',
    data: { label: '事实三：许于辰(泰嘉)', subLabel: '承诺1400万' },
    position: { x: 600, y: 350 },
    style: nodeStyles.giver,
  },
  {
    id: 'share3',
    type: 'custom',
    data: { label: '主要由谢斌收受', subLabel: '1000万未遂' },
    position: { x: 600, y: 450 },
    style: nodeStyles.money,
  },

  // 右侧分支：行贿人保管/未遂/知情
  {
    id: 'fact7',
    type: 'custom',
    data: { label: '事实七：王晓毅', subLabel: '承诺600万' },
    position: { x: 900, y: 200 },
    style: nodeStyles.giver,
  },
  {
    id: 'share7',
    type: 'custom',
    data: { label: '行贿人保管', subLabel: '资金未实际转移' },
    position: { x: 900, y: 300 },
    style: nodeStyles.money,
  },
  {
    id: 'fact8',
    type: 'custom',
    data: { label: '事实八：蒋兆国', subLabel: '承诺400万' },
    position: { x: 1100, y: 200 },
    style: nodeStyles.giver,
  },
  {
    id: 'share8',
    type: 'custom',
    data: { label: '行贿人保管', subLabel: '资金未实际转移' },
    position: { x: 1100, y: 300 },
    style: nodeStyles.money,
  },
  
  // 其他共同受贿
  {
    id: 'group3',
    type: 'custom',
    data: { label: '中间人 C', subLabel: '吴卫明' },
    position: { x: 450, y: 550 },
    style: nodeStyles.intermediary,
  },
   {
    id: 'fact4',
    type: 'custom',
    data: { label: '事实四：陈志涛', subLabel: '994万' },
    position: { x: 450, y: 650 },
    style: nodeStyles.giver,
  },
  
  {
    id: 'group4',
    type: 'custom',
    data: { label: '中间人 D', subLabel: '何斌(下属)' },
    position: { x: 750, y: 550 },
    style: nodeStyles.intermediary,
  },
   {
    id: 'fact5',
    type: 'custom',
    data: { label: '事实五：李瑜', subLabel: '600万' },
    position: { x: 750, y: 650 },
    style: nodeStyles.giver,
  },
];

const initialEdges = [
  { id: 'e1-g1', source: '1', target: 'group1', label: '提供权力支持', animated: true },
  { id: 'eg1-f1', source: 'group1', target: 'fact1', label: '索取/收受' },
  { id: 'eg1-f2', source: 'group1', target: 'fact2', label: '索取/收受' },
  { id: 'ef1-s1', source: 'fact1', target: 'share1' },
  { id: 'ef2-s2', source: 'fact2', target: 'share2' },
  
  { id: 'e1-g2', source: '1', target: 'group2', label: '引进项目/权力支持', animated: true },
  { id: 'eg2-f3', source: 'group2', target: 'fact3' },
  { id: 'ef3-s3', source: 'fact3', target: 'share3' },
  
  { id: 'e1-f7', source: '1', target: 'fact7', label: '口头答应' },
  { id: 'ef7-s7', source: 'fact7', target: 'share7', label: '无物理转移', markerEnd: { type: MarkerType.ArrowClosed } },
  
  { id: 'e1-f8', source: '1', target: 'fact8', label: '口头答应' },
  { id: 'ef8-s8', source: 'fact8', target: 'share8', label: '无物理转移', markerEnd: { type: MarkerType.ArrowClosed } },
  
  { id: 'e1-g3', source: '1', target: 'group3' },
  { id: 'eg3-f4', source: 'group3', target: 'fact4' },
  
  { id: 'e1-g4', source: '1', target: 'group4' },
  { id: 'eg4-f5', source: 'group4', target: 'fact5' },
];

function FlowChart() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  return (
    <div style={{ width: '100%', height: '100%' }}>
      <ReactFlowProvider>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          nodeTypes={nodeTypes}
          fitView
          attributionPosition="bottom-right"
        >
          <Background color="#888" gap={16} />
          <Controls />
          <MiniMap />
        </ReactFlow>
      </ReactFlowProvider>
    </div>
  );
}

export default function App() {
  return (
    <div style={{ height: '100vh', width: '100%' }}>
      <FlowChart />
    </div>
  );
}