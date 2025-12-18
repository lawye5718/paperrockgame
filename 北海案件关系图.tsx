import React, { useCallback } from 'react';
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

// --- 样式定义 ---
const nodeStyles = {
  defendant: {
    background: '#dc2626', // 红色
    color: 'white',
    border: '3px solid #991b1b',
    padding: '15px',
    borderRadius: '12px',
    fontWeight: '900',
    width: 220,
    textAlign: 'center',
    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
  },
  intermediary: {
    background: '#f59e0b', // 橙色
    color: 'white',
    border: '2px solid #d97706',
    padding: '10px',
    borderRadius: '8px',
    width: 180,
    textAlign: 'center',
    fontWeight: 'bold',
  },
  briber: {
    background: '#3b82f6', // 蓝色
    color: 'white',
    border: '1px solid #1d4ed8',
    padding: '8px',
    borderRadius: '6px',
    width: 160,
    fontSize: '12px',
    textAlign: 'center',
  },
  // 资金节点样式：根据谁实际占有来区分颜色
  moneyHeldByWang: {
    background: '#ef4444', // 红底
    color: 'white',
    border: '2px dashed white',
    padding: '8px',
    borderRadius: '4px',
    fontSize: '12px',
    width: 180,
    textAlign: 'left',
  },
  moneyHeldByOther: {
    background: '#64748b', // 灰底
    color: 'white',
    border: '1px solid #475569',
    padding: '8px',
    borderRadius: '4px',
    fontSize: '12px',
    width: 180,
    textAlign: 'left',
  },
  moneyUnpaid: {
    background: '#e2e8f0', // 浅灰底
    color: '#94a3b8', // 浅灰字
    border: '1px dashed #94a3b8',
    padding: '8px',
    borderRadius: '4px',
    fontSize: '12px',
    width: 180,
    textAlign: 'left',
    fontStyle: 'italic',
  },
  annotation: {
      fontSize: '14px',
      fontWeight: 'bold',
      background: '#fff',
      padding: '5px',
      border: '1px solid #ccc',
      borderRadius: '4px',
      color: '#333',
  }
};

const CustomNode = ({ data, style }) => (
  <div style={style}>
    <Handle type="target" position={Position.Top} />
    <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>{data.label}</div>
    {data.subLabel && <div style={{ fontSize: '11px', opacity: 0.9 }}>{data.subLabel}</div>}
    {data.amount && <div style={{ marginTop: '4px', borderTop: '1px solid rgba(255,255,255,0.3)', paddingTop: '2px' }}>💰 {data.amount}</div>}
    <Handle type="source" position={Position.Bottom} />
  </div>
);

const nodeTypes = {
  custom: CustomNode,
};

// --- 数据定义 ---
const initialNodes = [
  // 1. 中心被告人
  {
    id: 'wang',
    type: 'custom',
    data: { label: '被告人：王雄昌', subLabel: '实际经手极少，多为“知情”' },
    position: { x: 600, y: 350 }, // 放在中心
    style: nodeStyles.defendant,
  },

  // --- 左上角：少数实际经手 (Direct Control) ---
  {
    id: 'note-direct',
    type: 'default',
    data: { label: '第一类：王雄昌实际经手/占有 (仅2笔)' },
    position: { x: 100, y: 50 },
    style: { ...nodeStyles.annotation, borderLeft: '5px solid #ef4444' },
  },
  {
    id: 'fact9',
    type: 'custom',
    data: { label: '事实九：林汉枫', subLabel: '直接送现金/转账' },
    position: { x: 50, y: 120 },
    style: nodeStyles.briber,
  },
  {
    id: 'money9',
    type: 'custom',
    data: { label: '⚠️ 实际入账', amount: '250万元 (炒股获利)', subLabel: '王雄昌亲自控制' },
    position: { x: 50, y: 220 },
    style: nodeStyles.moneyHeldByWang,
  },
  {
    id: 'fact6',
    type: 'custom',
    data: { label: '事实六：王慧', subLabel: '早期宁波任职期间' },
    position: { x: 250, y: 120 },
    style: nodeStyles.briber,
  },
  {
    id: 'money6-real',
    type: 'custom',
    data: { label: '⚠️ 实际入账', amount: '150万元', subLabel: '王雄昌亲自收受' },
    position: { x: 250, y: 220 },
    style: nodeStyles.moneyHeldByWang,
  },
  {
    id: 'money6-fake',
    type: 'custom',
    data: { label: '❌ 未遂/未付', amount: '525万元', subLabel: '尚未实际取得' },
    position: { x: 250, y: 300 },
    style: nodeStyles.moneyUnpaid,
  },

  // --- 右侧：承诺型/行贿人保管 (Briber Custody) ---
  {
    id: 'note-promise',
    type: 'default',
    data: { label: '第二类：行贿人“代管” (实质未遂)' },
    position: { x: 900, y: 50 },
    style: { ...nodeStyles.annotation, borderLeft: '5px solid #3b82f6' },
  },
  {
    id: 'fact7',
    type: 'custom',
    data: { label: '事实七：王晓毅', subLabel: '口头承诺' },
    position: { x: 900, y: 120 },
    style: nodeStyles.briber,
  },
  {
    id: 'money7',
    type: 'custom',
    data: { label: '🔒 行贿人保管', amount: '600万元', subLabel: '钱仍在行贿人处' },
    position: { x: 900, y: 220 },
    style: nodeStyles.moneyHeldByOther,
  },
  {
    id: 'fact8',
    type: 'custom',
    data: { label: '事实八：蒋兆国', subLabel: '口头承诺' },
    position: { x: 1100, y: 120 },
    style: nodeStyles.briber,
  },
  {
    id: 'money8',
    type: 'custom',
    data: { label: '🔒 行贿人保管', amount: '400万元', subLabel: '钱仍在行贿人处' },
    position: { x: 1100, y: 220 },
    style: nodeStyles.moneyHeldByOther,
  },

  // --- 底部：中间人控制/特定关系人 (Intermediary Control) ---
  {
    id: 'note-group',
    type: 'default',
    data: { label: '第三类：中间人团伙截留/保管 (王未经手)' },
    position: { x: 500, y: 500 },
    style: { ...nodeStyles.annotation, borderLeft: '5px solid #f59e0b' },
  },
  
  // 事实一 & 二 (廖炼炼团伙)
  {
    id: 'group1',
    type: 'custom',
    data: { label: '中间人团伙', subLabel: '廖炼炼、苏林、黎小宋' },
    position: { x: 100, y: 600 },
    style: nodeStyles.intermediary,
  },
  {
    id: 'money1',
    type: 'custom',
    data: { label: '🔒 廖炼炼保管 (事实一)', amount: '340万元 (占20%)', subLabel: '王雄昌从未经手' },
    position: { x: 50, y: 700 },
    style: nodeStyles.moneyHeldByOther,
  },
  {
    id: 'money1-rem',
    type: 'custom',
    data: { label: '💸 团伙截留 (事实一)', amount: '1360万+ (占80%)', subLabel: '苏/黎实际占有' },
    position: { x: 50, y: 780 },
    style: nodeStyles.moneyHeldByOther,
  },
  {
    id: 'money2',
    type: 'custom',
    data: { label: '🔒 廖炼炼保管 (事实二)', amount: '180万元 (占20%)', subLabel: '王雄昌从未经手' },
    position: { x: 250, y: 700 },
    style: nodeStyles.moneyHeldByOther,
  },
    {
    id: 'money2-rem',
    type: 'custom',
    data: { label: '💸 团伙截留 (事实二)', amount: '1000万+ (占80%)', subLabel: '苏/黎实际占有' },
    position: { x: 250, y: 780 },
    style: nodeStyles.moneyHeldByOther,
  },

  // 事实三 (谢斌/泰嘉)
  {
    id: 'intermediary-xie',
    type: 'custom',
    data: { label: '中间人：谢斌', subLabel: '泰嘉项目引进人' },
    position: { x: 500, y: 600 },
    style: nodeStyles.intermediary,
  },
  {
    id: 'money3-xie',
    type: 'custom',
    data: { label: '💸 谢斌占有', amount: '400万元', subLabel: '王雄昌仅“知情”' },
    position: { x: 500, y: 700 },
    style: nodeStyles.moneyHeldByOther,
  },
  {
    id: 'money3-fake',
    type: 'custom',
    data: { label: '❌ 未遂 (画饼)', amount: '1000万元', subLabel: '许于辰无支付能力' },
    position: { x: 500, y: 780 },
    style: nodeStyles.moneyUnpaid,
  },

  // 事实四 (吴卫明)
  {
    id: 'intermediary-wu',
    type: 'custom',
    data: { label: '中间人：吴卫明', subLabel: '私营企业主' },
    position: { x: 700, y: 600 },
    style: nodeStyles.intermediary,
  },
  {
    id: 'money4',
    type: 'custom',
    data: { label: '💸 吴卫明占有', amount: '约982万元', subLabel: '王雄昌仅“知情/同意”' },
    position: { x: 700, y: 700 },
    style: nodeStyles.moneyHeldByOther,
  },

  // 事实五 (何斌)
  {
    id: 'intermediary-he',
    type: 'custom',
    data: { label: '中间人：何斌', subLabel: '原国企老总' },
    position: { x: 900, y: 600 },
    style: nodeStyles.intermediary,
  },
  {
    id: 'money5',
    type: 'custom',
    data: { label: '💸 何斌占有', amount: '400万元', subLabel: '王雄昌仅“知情”' },
    position: { x: 900, y: 700 },
    style: nodeStyles.moneyHeldByOther,
  },
   {
    id: 'money5-fake',
    type: 'custom',
    data: { label: '❌ 未遂', amount: '200万元', subLabel: '未实际取得' },
    position: { x: 900, y: 780 },
    style: nodeStyles.moneyUnpaid,
  },
];

const initialEdges = [
  // 连接被告人与钱款（只有实际经手的才实线连接，其他的用虚线表示名义关联）
  
  // 1. 实际经手 (实线红色)
  { id: 'e-w-m9', source: 'fact9', target: 'money9', animated: true },
  { id: 'e-m9-w', source: 'money9', target: 'wang', style: { stroke: '#ef4444', strokeWidth: 3 }, label: '实际流入' },
  
  { id: 'e-w-m6', source: 'fact6', target: 'money6-real', animated: true },
  { id: 'e-m6-w', source: 'money6-real', target: 'wang', style: { stroke: '#ef4444', strokeWidth: 3 }, label: '实际流入' },
  { id: 'e-fact6-fake', source: 'fact6', target: 'money6-fake', type: 'step' },

  // 2. 行贿人保管 (虚线阻断)
  { id: 'e-f7-m7', source: 'fact7', target: 'money7', animated: true },
  { id: 'e-m7-w', source: 'money7', target: 'wang', style: { stroke: '#94a3b8', strokeDasharray: '5 5' }, label: '未物理转移', markerEnd: { type: MarkerType.ArrowClosed } },
  
  { id: 'e-f8-m8', source: 'fact8', target: 'money8', animated: true },
  { id: 'e-m8-w', source: 'money8', target: 'wang', style: { stroke: '#94a3b8', strokeDasharray: '5 5' }, label: '未物理转移', markerEnd: { type: MarkerType.ArrowClosed } },

  // 3. 中间人持有 (连接到中间人，王雄昌只是虚线关联)
  { id: 'e-g1-m1', source: 'group1', target: 'money1', label: '保管' },
  { id: 'e-g1-m1rem', source: 'group1', target: 'money1-rem', label: '截留' },
  { id: 'e-g1-m2', source: 'group1', target: 'money2', label: '保管' },
  { id: 'e-g1-m2rem', source: 'group1', target: 'money2-rem', label: '截留' },
  
  // 王雄昌与中间人的关系
  { id: 'e-w-g1', source: 'wang', target: 'group1', style: { stroke: '#f59e0b', strokeDasharray: '5 5' }, label: '通过中间人受贿' },
  
  { id: 'e-xie-m3', source: 'intermediary-xie', target: 'money3-xie', label: '占有' },
  { id: 'e-w-xie', source: 'wang', target: 'intermediary-xie', style: { stroke: '#f59e0b', strokeDasharray: '5 5' }, label: '知情' },
  
  { id: 'e-wu-m4', source: 'intermediary-wu', target: 'money4', label: '占有' },
  { id: 'e-w-wu', source: 'wang', target: 'intermediary-wu', style: { stroke: '#f59e0b', strokeDasharray: '5 5' }, label: '知情' },
  
  { id: 'e-he-m5', source: 'intermediary-he', target: 'money5', label: '占有' },
  { id: 'e-w-he', source: 'wang', target: 'intermediary-he', style: { stroke: '#f59e0b', strokeDasharray: '5 5' }, label: '知情' },

];

export default function App() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  return (
    <div style={{ height: '800px', width: '100%', border: '1px solid #ccc' }}>
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
          <Background color="#f1f5f9" gap={16} />
          <Controls />
          <MiniMap />
        </ReactFlow>
      </ReactFlowProvider>
    </div>
  );
}