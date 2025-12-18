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
    background: '#dc2626', // 红色：被告人
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
    background: '#059669', // 绿色：中间人 (User Requested Green)
    color: 'white',
    border: '2px solid #047857',
    padding: '10px',
    borderRadius: '8px',
    width: 180,
    textAlign: 'center',
    fontWeight: 'bold',
  },
  briber: {
    background: '#3b82f6', // 蓝色：行贿人/未遂
    color: 'white',
    border: '1px solid #1d4ed8',
    padding: '8px',
    borderRadius: '6px',
    width: 160,
    fontSize: '12px',
    textAlign: 'center',
  },
  // 资金节点样式
  moneyHeldByWang: {
    background: '#ef4444', // 红底：被告人控制
    color: 'white',
    border: '2px dashed white',
    padding: '8px',
    borderRadius: '4px',
    fontSize: '12px',
    width: 180,
    textAlign: 'left',
    boxShadow: '0 2px 4px rgba(239, 68, 68, 0.4)',
  },
  moneyHeldByIntermediary: {
    background: '#10b981', // 绿底：中间人控制
    color: 'white',
    border: '1px solid #059669',
    padding: '8px',
    borderRadius: '4px',
    fontSize: '12px',
    width: 180,
    textAlign: 'left',
  },
  moneyHeldByBriber: {
    background: '#93c5fd', // 浅蓝底：行贿人保管/未遂
    color: '#1e3a8a', 
    border: '1px dashed #3b82f6',
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

// --- 数据统计 (单位：万元) ---
// 总额: 7539.09
// 1. 红色 (王雄昌): F9(250) + F6(150) = 400 (占比 5.3%)
// 2. 蓝色 (未遂/行贿人): F7(600) + F8(400) + F3未(1000) + F6未(525) + F5未(200) + F4未(12) = 2737 (占比 36.3%)
// 3. 绿色 (中间人): F1(1700) + F2(920) + F3实(400) + F4实(982) + F5实(400) = 4402 (占比 58.4%)

// --- 节点定义 ---
const initialNodes = [
  // 1. 中心被告人
  {
    id: 'wang',
    type: 'custom',
    data: { label: '被告人：王雄昌', subLabel: '实际经手极少，多为“知情”' },
    position: { x: 600, y: 350 },
    style: nodeStyles.defendant,
  },

  // --- 左上角：实际经手 (红色) ---
  {
    id: 'note-direct',
    type: 'default',
    data: { label: '一、实际占有 (红色区域)' },
    position: { x: 100, y: 50 },
    style: { ...nodeStyles.annotation, borderLeft: '5px solid #ef4444', color: '#ef4444' },
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
    data: { label: '⚠️ 实际入袋', amount: '250万元 (炒股获利)', subLabel: '王雄昌亲自控制' },
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
    data: { label: '⚠️ 实际入袋', amount: '150万元', subLabel: '王雄昌亲自收受' },
    position: { x: 250, y: 220 },
    style: nodeStyles.moneyHeldByWang,
  },
  {
    id: 'money6-fake',
    type: 'custom',
    data: { label: '❌ 未遂/未付', amount: '525万元', subLabel: '尚未实际取得' },
    position: { x: 250, y: 300 },
    style: nodeStyles.moneyHeldByBriber,
  },

  // --- 右侧：承诺型/行贿人保管 (蓝色) ---
  {
    id: 'note-promise',
    type: 'default',
    data: { label: '二、空头支票/未遂 (蓝色区域)' },
    position: { x: 900, y: 50 },
    style: { ...nodeStyles.annotation, borderLeft: '5px solid #3b82f6', color: '#3b82f6' },
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
    style: nodeStyles.moneyHeldByBriber,
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
    style: nodeStyles.moneyHeldByBriber,
  },

  // --- 底部：中间人控制 (绿色) ---
  {
    id: 'note-group',
    type: 'default',
    data: { label: '三、中间人截留 (绿色区域)' },
    position: { x: 500, y: 500 },
    style: { ...nodeStyles.annotation, borderLeft: '5px solid #10b981', color: '#059669' },
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
    style: nodeStyles.moneyHeldByIntermediary,
  },
  {
    id: 'money1-rem',
    type: 'custom',
    data: { label: '💸 团伙截留 (事实一)', amount: '1360万+ (占80%)', subLabel: '苏/黎实际占有' },
    position: { x: 50, y: 780 },
    style: nodeStyles.moneyHeldByIntermediary,
  },
  {
    id: 'money2',
    type: 'custom',
    data: { label: '🔒 廖炼炼保管 (事实二)', amount: '180万元 (占20%)', subLabel: '王雄昌从未经手' },
    position: { x: 250, y: 700 },
    style: nodeStyles.moneyHeldByIntermediary,
  },
    {
    id: 'money2-rem',
    type: 'custom',
    data: { label: '💸 团伙截留 (事实二)', amount: '1000万+ (占80%)', subLabel: '苏/黎实际占有' },
    position: { x: 250, y: 780 },
    style: nodeStyles.moneyHeldByIntermediary,
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
    style: nodeStyles.moneyHeldByIntermediary,
  },
  {
    id: 'money3-fake',
    type: 'custom',
    data: { label: '❌ 未遂 (画饼)', amount: '1000万元', subLabel: '许于辰无支付能力' },
    position: { x: 500, y: 780 },
    style: nodeStyles.moneyHeldByBriber,
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
    style: nodeStyles.moneyHeldByIntermediary,
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
    style: nodeStyles.moneyHeldByIntermediary,
  },
   {
    id: 'money5-fake',
    type: 'custom',
    data: { label: '❌ 未遂', amount: '200万元', subLabel: '未实际取得' },
    position: { x: 900, y: 780 },
    style: nodeStyles.moneyHeldByBriber,
  },
];

const initialEdges = [
  { id: 'e-w-m9', source: 'fact9', target: 'money9', animated: true },
  { id: 'e-m9-w', source: 'money9', target: 'wang', style: { stroke: '#ef4444', strokeWidth: 3 }, label: '实际流入' },
  { id: 'e-w-m6', source: 'fact6', target: 'money6-real', animated: true },
  { id: 'e-m6-w', source: 'money6-real', target: 'wang', style: { stroke: '#ef4444', strokeWidth: 3 }, label: '实际流入' },
  { id: 'e-fact6-fake', source: 'fact6', target: 'money6-fake', type: 'step' },
  { id: 'e-f7-m7', source: 'fact7', target: 'money7', animated: true },
  { id: 'e-m7-w', source: 'money7', target: 'wang', style: { stroke: '#94a3b8', strokeDasharray: '5 5' }, label: '未物理转移', markerEnd: { type: MarkerType.ArrowClosed } },
  { id: 'e-f8-m8', source: 'fact8', target: 'money8', animated: true },
  { id: 'e-m8-w', source: 'money8', target: 'wang', style: { stroke: '#94a3b8', strokeDasharray: '5 5' }, label: '未物理转移', markerEnd: { type: MarkerType.ArrowClosed } },
  { id: 'e-g1-m1', source: 'group1', target: 'money1', label: '保管' },
  { id: 'e-g1-m1rem', source: 'group1', target: 'money1-rem', label: '截留' },
  { id: 'e-g1-m2', source: 'group1', target: 'money2', label: '保管' },
  { id: 'e-g1-m2rem', source: 'group1', target: 'money2-rem', label: '截留' },
  { id: 'e-w-g1', source: 'wang', target: 'group1', style: { stroke: '#10b981', strokeDasharray: '5 5' }, label: '通过中间人' },
  { id: 'e-xie-m3', source: 'intermediary-xie', target: 'money3-xie', label: '占有' },
  { id: 'e-w-xie', source: 'wang', target: 'intermediary-xie', style: { stroke: '#10b981', strokeDasharray: '5 5' }, label: '知情' },
  { id: 'e-wu-m4', source: 'intermediary-wu', target: 'money4', label: '占有' },
  { id: 'e-w-wu', source: 'wang', target: 'intermediary-wu', style: { stroke: '#10b981', strokeDasharray: '5 5' }, label: '知情' },
  { id: 'e-he-m5', source: 'intermediary-he', target: 'money5', label: '占有' },
  { id: 'e-w-he', source: 'wang', target: 'intermediary-he', style: { stroke: '#10b981', strokeDasharray: '5 5' }, label: '知情' },
];

const AnalysisPanel = () => {
  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif', borderTop: '2px solid #eee', backgroundColor: '#f8fafc' }}>
      <h3 style={{ marginTop: 0, color: '#334155', borderBottom: '2px solid #cbd5e1', paddingBottom: '10px' }}>
        📊 资金实际流向与控制权分析 (总指控金额：7539万元)
      </h3>
      
      <div style={{ display: 'flex', flexDirection: 'row', gap: '30px', flexWrap: 'wrap' }}>
        {/* 饼图区域 */}
        <div style={{ flex: '0 0 250px', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <div style={{ 
            width: '200px', 
            height: '200px', 
            borderRadius: '50%', 
            background: 'conic-gradient(#dc2626 0% 5.3%, #10b981 5.3% 63.7%, #3b82f6 63.7% 100%)',
            marginBottom: '15px',
            boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
          }}></div>
          <div style={{ width: '100%', fontSize: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '5px' }}>
              <span style={{ width: '12px', height: '12px', background: '#dc2626', marginRight: '8px', borderRadius: '2px' }}></span>
              <span>被告人实际占有: <b>5.3%</b> (400万)</span>
            </div>
             <div style={{ display: 'flex', alignItems: 'center', marginBottom: '5px' }}>
              <span style={{ width: '12px', height: '12px', background: '#10b981', marginRight: '8px', borderRadius: '2px' }}></span>
              <span>中间人截留: <b>58.4%</b> (4402万)</span>
            </div>
             <div style={{ display: 'flex', alignItems: 'center', marginBottom: '5px' }}>
              <span style={{ width: '12px', height: '12px', background: '#3b82f6', marginRight: '8px', borderRadius: '2px' }}></span>
              <span>空头支票/未遂: <b>36.3%</b> (2737万)</span>
            </div>
          </div>
        </div>

        {/* 文字分析区域 */}
        <div style={{ flex: '1', minWidth: '300px' }}>
          <div style={{ marginBottom: '15px' }}>
            <h4 style={{ color: '#b91c1c', margin: '0 0 5px 0', display: 'flex', alignItems: 'center' }}>
              🔴 “实际受贿”（入袋）
            </h4>
            <p style={{ fontSize: '13px', lineHeight: '1.6', color: '#334155', margin: 0 }}>
              请注意图表左上角的红色实线区域。只有事实九（林汉枫250万）和事实六（王慧150万）这两笔，共计<b>400万元</b>，确凿无疑地进入了王雄昌个人的控制范围（如炒股、现金收受）。<br/>
              相比之下，起诉书指控的总额是7539万。这意味着，<b>超过94%的指控金额，王雄昌并未发生物理上的接触或占有。</b>
            </p>
          </div>

          <div style={{ marginBottom: '15px' }}>
            <h4 style={{ color: '#047857', margin: '0 0 5px 0', display: 'flex', alignItems: 'center' }}>
              🟢 “中间人截留”（底部绿色区域）
            </h4>
            <p style={{ fontSize: '13px', lineHeight: '1.6', color: '#334155', margin: 0 }}>
              在涉及廖炼炼、苏林、吴卫明、何斌的几起共同受贿中，资金几乎全部停留在中间人手中。
              特别是事实一和事实二，中间人截留了80%以上的利益，而王雄昌所谓的“份子钱”也是由廖炼炼“代为保管”。这种<b>“钱在别人手，罪在我头上”</b>的结构，退一万步讲，至少也应认定<b>从犯</b>。
            </p>
          </div>

          <div>
            <h4 style={{ color: '#1d4ed8', margin: '0 0 5px 0', display: 'flex', alignItems: 'center' }}>
              🔵 “空头支票”（右侧蓝色区域）
            </h4>
            <p style={{ fontSize: '13px', lineHeight: '1.6', color: '#334155', margin: 0 }}>
              事实七（王晓毅）和事实八（蒋兆国）共计1000万元，标记为“行贿人保管”。这在图上显示为资金流动的死循环——钱根本没有离开行贿人的口袋。这部分金额应认定<b>无罪</b>、退一万步讲也是定<b>“不能犯未遂”</b>（行贿人根本没有支付能力和支付意愿）。
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default function App() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  return (
    <div style={{ width: '100%', border: '1px solid #ccc', display: 'flex', flexDirection: 'column', background: '#fff' }}>
      <div style={{ height: '800px', width: '100%' }}>
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
      <AnalysisPanel />
    </div>
  );
}