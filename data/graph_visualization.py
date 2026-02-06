"""
그래프 시각화 도구
pkl 파일에서 그래프를 로드하여 다양한 방식으로 시각화
"""

import pickle
import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd

class GraphVisualizer:
    def __init__(self, graph_path="./recommendation_graph.pkl"):
        self.graph_path = graph_path
        self.graph = None
        self.node_types = None
        self.node_id_mapping = None
        
    def load_graph(self):
        """pkl 파일에서 그래프 로드"""
        try:
            with open(self.graph_path, 'rb') as f:
                graph_data = pickle.load(f)
            
            self.graph = graph_data['graph']
            self.node_types = graph_data['node_types']
            self.node_id_mapping = graph_data['node_id_mapping']
            
            print(f"그래프 로드 완료: {self.graph_path}")
            print(f"노드: {self.graph.number_of_nodes()}개, 엣지: {self.graph.number_of_edges()}개")
            
        except FileNotFoundError:
            print(f"그래프 파일을 찾을 수 없습니다: {self.graph_path}")
            print("먼저 graph_gen.py를 실행하여 그래프를 생성하세요.")
            
    def plot_basic_graph(self, figsize=(15, 10), save_path=None):
        """기본 NetworkX 시각화"""
        if self.graph is None:
            self.load_graph()
            
        plt.figure(figsize=figsize)
        
        # 노드 타입별 색상 설정
        color_map = {
            'trait': '#FF6B6B',      # 빨강
            'concept': '#4ECDC4',    # 청록
            'item': '#45B7D1',       # 파랑
            'user': '#96CEB4'        # 초록
        }
        
        # 노드 색상 리스트 생성
        node_colors = []
        for node_id in self.graph.nodes():
            node_type = self.graph.nodes[node_id].get('type', 'unknown')
            node_colors.append(color_map.get(node_type, '#CCCCCC'))
        
        # 레이아웃 계산
        pos = nx.spring_layout(self.graph, k=1, iterations=50)
        
        # 그래프 그리기
        nx.draw(self.graph, pos, 
                node_color=node_colors,
                node_size=50,
                with_labels=False,
                edge_color='lightgray',
                alpha=0.7)
        
        # 범례 추가
        for node_type, color in color_map.items():
            if node_type in [nodes for nodes in self.node_types.keys() if self.node_types[nodes]]:
                plt.scatter([], [], c=color, label=f'{node_type.title()} ({len(self.node_types[node_type])})')
        
        plt.legend()
        plt.title("Knowledge Graph Visualization")
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"그래프 이미지 저장: {save_path}")
        
        plt.show()
    
    def export_to_gexf(self, output_path="knowledge_graph.gexf"):
        """Gephi용 GEXF 파일 생성"""
        if self.graph is None:
            self.load_graph()
        
        nx.write_gexf(self.graph, output_path)
        print(f"GEXF 파일 생성 완료: {output_path}")
        print("Gephi에서 열어서 고급 시각화를 확인하세요!")
    
    def plot_full_knowledge_graph(self, save_path=None):
        """전체 지식 그래프 시각화 (Item-Concept, Trait-Concept 관계 모두 포함)"""
        if self.graph is None:
            self.load_graph()
        
        # 전체 그래프 사용 (User 노드 제외)
        nodes_to_include = []
        for node_type in ['item', 'trait', 'concept']:
            if node_type in self.node_types:
                nodes_to_include.extend(self.node_types[node_type])
        
        subgraph = self.graph.subgraph(nodes_to_include)
        
        # 레이아웃 계산 (노드가 많으므로 성능 고려)
        print("레이아웃 계산 중... (시간이 걸릴 수 있습니다)")
        pos = nx.spring_layout(subgraph, k=2, iterations=50)
        
        # 엣지 그리기
        edge_x, edge_y = [], []
        edge_colors = []
        
        for edge in subgraph.edges(data=True):
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            
            # 엣지 타입별 색상
            relation = edge[2].get('relation', 'unknown')
            if relation == 'trait_concept':
                edge_colors.extend(['rgba(255,107,107,0.6)', 'rgba(255,107,107,0.6)', None])
            elif relation == 'item_concept':
                edge_colors.extend(['rgba(69,183,209,0.3)', 'rgba(69,183,209,0.3)', None])
            else:
                edge_colors.extend(['rgba(125,125,125,0.3)', 'rgba(125,125,125,0.3)', None])
        
        edge_trace = go.Scatter(x=edge_x, y=edge_y,
                               line=dict(width=1, color='rgba(125,125,125,0.3)'),
                               hoverinfo='none', mode='lines')
        
        # 노드별 정보
        color_map = {
            'trait': '#FF6B9D',      # 핑크-레드 (더 부드러운 색)
            'concept': '#4ECDC4',    # 청록 (유지)
            'item': '#45B7D1'        # 파랑 (유지)
        }
        
        node_traces = []
        for node_type in ['trait', 'concept', 'item']:
            if node_type not in self.node_types or not self.node_types[node_type]:
                continue
                
            x_coords, y_coords, texts, names = [], [], [], []
            
            for node_id in self.node_types[node_type]:
                if node_id in pos:
                    x, y = pos[node_id]
                    x_coords.append(x)
                    y_coords.append(y)
                    
                    node_data = subgraph.nodes[node_id]
                    node_name = node_data.get('name', str(node_id))
                    degree = subgraph.degree(node_id)
                    
                    texts.append(f"{node_name}<br>연결: {degree}개<br>타입: {node_type}")
                    names.append(node_name if node_type != 'item' else '')  # Item은 너무 많아서 라벨 제외
            
            if x_coords:
                # 노드 크기 (타입별로 다르게)
                node_size = 15 if node_type == 'item' else 25
                show_text = node_type != 'item'  # Item은 텍스트 숨김
                
                node_trace = go.Scatter(
                    x=x_coords, y=y_coords,
                    mode='markers' + ('+text' if show_text else ''),
                    text=names if show_text else [],
                    textposition="middle center",
                    hovertext=texts,
                    hoverinfo='text',
                    marker=dict(
                        size=node_size, 
                        color=color_map[node_type],
                        line=dict(width=1, color='white')
                    ),
                    name=f'{node_type.title()} ({len(x_coords)})',
                    textfont=dict(size=8, color='white') if show_text else None
                )
                node_traces.append(node_trace)
        
        # 레이아웃 설정
        layout = go.Layout(
            title=dict(text='Knowledge Graph: Item-Concept & Trait-Concept Relations', font=dict(size=20)),
            showlegend=True,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            annotations=[dict(
                text="Trait(빨강) ↔ Concept(청록) ↔ Item(파랑) 관계를 보여줍니다",
                showarrow=False, xref="paper", yref="paper",
                x=0.005, y=-0.002, xanchor='left', yanchor='bottom',
                font=dict(color="gray", size=12)
            )],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='black', paper_bgcolor='black'
        )
        
        fig = go.Figure(data=[edge_trace] + node_traces, layout=layout)
        
        if save_path:
            fig.write_html(save_path)
            print(f"전체 지식 그래프 저장: {save_path}")
        
        fig.show()
        return fig

    def plot_3d_knowledge_graph(self, save_path=None):
        """3D 인터랙티브 지식 그래프 시각화"""
        if self.graph is None:
            self.load_graph()
        
        # 전체 그래프 사용 (User 노드 제외)
        nodes_to_include = []
        for node_type in ['item', 'trait', 'concept']:
            if node_type in self.node_types:
                nodes_to_include.extend(self.node_types[node_type])
        
        subgraph = self.graph.subgraph(nodes_to_include)
        
        # 3D 레이아웃 계산
        print("3D 레이아웃 계산 중...")
        pos_2d = nx.spring_layout(subgraph, k=2, iterations=50)
        
        # 3D 좌표 생성 (진짜 구형 배치)
        pos_3d = {}
        
        # Trait 노드만 균등 배치를 위해 먼저 수집
        trait_nodes = []
        for node_id in pos_2d:
            node_type = subgraph.nodes[node_id].get('type', 'unknown')
            if node_type == 'trait':
                trait_nodes.append(node_id)
        
        # Trait 노드 인덱스
        trait_idx = 0
        
        for node_id in pos_2d:
            node_type = subgraph.nodes[node_id].get('type', 'unknown')
            
            if node_type == 'concept':
                # Concept는 중심 작은 구에 배치 (원래대로)
                radius = np.random.uniform(0.5, 1.0)
                theta = np.random.uniform(0, 2 * np.pi)
                phi = np.random.uniform(0, np.pi)
                x = radius * np.sin(phi) * np.cos(theta)
                y = radius * np.sin(phi) * np.sin(theta)
                z = radius * np.cos(phi)
                
            elif node_type == 'trait':
                # Trait는 바깥쪽 구 표면에 균등하게 배치
                n_traits = len(trait_nodes)
                radius = 4.0 + (trait_idx / n_traits) * 1.0  # 4.0 ~ 5.0
                # 균등 분포를 위한 인덱스 기반 각도
                theta = 2 * np.pi * trait_idx * 0.618033988749895  # 황금각 사용
                phi = np.arccos(1 - 2 * (trait_idx + 0.5) / n_traits)
                x = radius * np.sin(phi) * np.cos(theta)
                y = radius * np.sin(phi) * np.sin(theta)
                z = radius * np.cos(phi)
                trait_idx += 1
                
            else:  # item
                # Item은 중간 구 껍질에 배치 (원래대로)
                radius = np.random.uniform(2.0, 3.5)
                theta = np.random.uniform(0, 2 * np.pi)
                phi = np.random.uniform(0, np.pi)
                x = radius * np.sin(phi) * np.cos(theta)
                y = radius * np.sin(phi) * np.sin(theta)
                z = radius * np.cos(phi)
            
            pos_3d[node_id] = (x, y, z)
        
        # 3D 엣지 그리기 (관계별로 분리하여 레전드 필터링 가능)
        edge_trace = []
        
        # Trait-Concept 엣지
        trait_concept_edges = [(e[0], e[1]) for e in subgraph.edges(data=True) 
                              if e[2].get('relation') == 'trait_concept']
        if trait_concept_edges:
            tc_x, tc_y, tc_z = [], [], []
            tc_weights = []
            for edge in trait_concept_edges:
                x0, y0, z0 = pos_3d[edge[0]]
                x1, y1, z1 = pos_3d[edge[1]]
                tc_x.extend([x0, x1, None])
                tc_y.extend([y0, y1, None])
                tc_z.extend([z0, z1, None])
                
                # 가중치 정보 수집
                edge_data = subgraph.get_edge_data(edge[0], edge[1])
                weight = edge_data.get('weight', 1.0)
                tc_weights.extend([weight, weight, None])
            
            edge_trace.append(go.Scatter3d(
                x=tc_x, y=tc_y, z=tc_z,
                mode='lines',
                line=dict(color='rgba(255,107,157,0.8)', width=2),
                hoverinfo='text',
                hovertext=[f"가중치: {w:.2f}" if w is not None else "" for w in tc_weights],
                name='Trait-Concept',
                legendgroup='trait_concept',
                showlegend=True
            ))
        
        # Item-Concept 엣지
        item_concept_edges = [(e[0], e[1]) for e in subgraph.edges(data=True) 
                             if e[2].get('relation') == 'item_concept']
        if item_concept_edges:
            ic_x, ic_y, ic_z = [], [], []
            ic_weights = []
            for edge in item_concept_edges:
                x0, y0, z0 = pos_3d[edge[0]]
                x1, y1, z1 = pos_3d[edge[1]]
                ic_x.extend([x0, x1, None])
                ic_y.extend([y0, y1, None])
                ic_z.extend([z0, z1, None])
                
                # 가중치 정보 수집
                edge_data = subgraph.get_edge_data(edge[0], edge[1])
                weight = edge_data.get('weight', 1.0)
                ic_weights.extend([weight, weight, None])
            
            edge_trace.append(go.Scatter3d(
                x=ic_x, y=ic_y, z=ic_z,
                mode='lines',
                line=dict(color='rgba(69,183,209,0.15)', width=0.3),
                hoverinfo='text',
                hovertext=[f"가중치: {w:.3f}" if w is not None else "" for w in ic_weights],
                name='Item-Concept',
                legendgroup='item_concept',
                showlegend=True
            ))
        
        # Item-Trait 엣지
        item_trait_edges = [(e[0], e[1]) for e in subgraph.edges(data=True) 
                           if e[2].get('relation') == 'item_trait']
        if item_trait_edges:
            it_x, it_y, it_z = [], [], []
            it_weights = []
            for edge in item_trait_edges:
                x0, y0, z0 = pos_3d[edge[0]]
                x1, y1, z1 = pos_3d[edge[1]]
                it_x.extend([x0, x1, None])
                it_y.extend([y0, y1, None])
                it_z.extend([z0, z1, None])
                
                # 가중치 정보 수집
                edge_data = subgraph.get_edge_data(edge[0], edge[1])
                weight = edge_data.get('weight', 1.0)
                it_weights.extend([weight, weight, None])
            
            edge_trace.append(go.Scatter3d(
                x=it_x, y=it_y, z=it_z,
                mode='lines',
                line=dict(color='rgba(80,80,80,0.2)', width=0.3),
                hoverinfo='text',
                hovertext=[f"가중치: {w:.3f}" if w is not None else "" for w in it_weights],
                name='Item-Trait',
                legendgroup='item_trait',
                showlegend=True
            ))
        
        # 3D 노드 그리기
        color_map = {
            'trait': '#FF6B6B',      # 빨강
            'concept': '#32CD32',    # 초록 (LimeGreen)
            'item': '#45B7D1'        # 파랑
        }
        
        node_traces = []
        for node_type in ['trait', 'concept', 'item']:
            if node_type not in self.node_types or not self.node_types[node_type]:
                continue
                
            x_coords, y_coords, z_coords, texts, names = [], [], [], [], []
            
            for node_id in self.node_types[node_type]:
                if node_id in pos_3d:
                    x, y, z = pos_3d[node_id]
                    x_coords.append(x)
                    y_coords.append(y)
                    z_coords.append(z)
                    
                    node_data = subgraph.nodes[node_id]
                    node_name = node_data.get('name', str(node_id))
                    degree = subgraph.degree(node_id)
                    
                    texts.append(f"{node_name}<br>연결: {degree}개<br>타입: {node_type}")
                    names.append(node_name if node_type != 'item' else '')
            
            if x_coords:
                # 노드 크기 (더 작고 깔끔하게)
                if node_type == 'concept':
                    base_size = 8  # Concept는 중간 크기
                elif node_type == 'trait':
                    base_size = 10  # Trait는 약간 크게 (중요하니까)
                else:  # item
                    base_size = 3   # Item은 아주 작게 (너무 많아서)
                
                sizes = [base_size for _ in self.node_types[node_type] if node_id in pos_3d]
                
                node_trace = go.Scatter3d(
                    x=x_coords, y=y_coords, z=z_coords,
                    mode='markers+text',
                    text=names,
                    textposition="middle center",
                    hovertext=texts,
                    hoverinfo='text',
                    marker=dict(
                        size=sizes,
                        color=color_map[node_type],
                        line=dict(width=1, color='rgba(255,255,255,0.8)'),  # 더 부드러운 테두리
                        opacity=0.95  # 약간의 투명도
                    ),
                    name=f'{node_type.title()} ({len(x_coords)})',
                    legendgroup=node_type,
                    textfont=dict(size=10, color='white') if node_type != 'item' else None
                )
                node_traces.append(node_trace)
        
        # 3D 레이아웃 설정 (깔끔하고 중앙 배치)
        layout = go.Layout(
            showlegend=True,
            hovermode='closest',
            margin=dict(b=0,l=0,r=0,t=0),  # 모든 여백 제거
            scene=dict(
                # 축과 격자 완전히 숨김
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, 
                          title='', showline=False, showbackground=False, visible=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, 
                          title='', showline=False, showbackground=False, visible=False),
                zaxis=dict(showgrid=False, zeroline=False, showticklabels=False, 
                          title='', showline=False, showbackground=False, visible=False),
                bgcolor='rgba(0,0,0,1)',
                camera=dict(
                    eye=dict(x=1.8, y=1.8, z=1.8),  # 더 나은 시점
                    center=dict(x=0, y=0, z=0)  # 중앙 고정
                ),
                aspectmode='cube'  # 정육면체 비율로 고정
            ),
            paper_bgcolor='black',
            plot_bgcolor='black',
            font=dict(color='white', size=11),
            legend=dict(
                x=0.02, y=0.98,  # 왼쪽 위 모서리
                bgcolor='rgba(0,0,0,0.7)',
                bordercolor='rgba(255,255,255,0.3)',
                borderwidth=1
            )
        )
        
        fig = go.Figure(data=edge_trace + node_traces, layout=layout)
        
        if save_path:
            # HTML에 자동 회전 기능과 버튼 추가
            html_str = fig.to_html(include_plotlyjs='cdn', div_id='plotly-3d-graph')
            
            # 자동 회전 스크립트 추가
            auto_rotate_script = """
<div id="auto-rotate-control" style="position: fixed; top: 20px; right: 20px; z-index: 10000; pointer-events: auto;">
    <button id="rotate-btn" style="
        background-color: rgba(255, 107, 107, 0.9);
        color: white;
        border: 2px solid rgba(255, 107, 107, 0.8);
        border-radius: 8px;
        padding: 12px 24px;
        font-size: 14px;
        cursor: pointer;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    ">자동 회전 OFF</button>
</div>

<script>
(function() {
    let isRotating = true;  // 기본적으로 회전 시작
    let animationId = null;
    let angle = 0;
    const rotationSpeed = 0.03;  // 회전 속도 3배 증가
    
    function waitForPlotly() {
        const gd = document.getElementById('plotly-3d-graph') || 
                   document.querySelector('[data-plotly]') || 
                   document.querySelector('.plotly') ||
                   document.querySelector('div[id*="plotly"]');
        
        if (typeof Plotly !== 'undefined' && gd) {
            // Plotly가 완전히 로드될 때까지 추가 대기
            setTimeout(function() {
                if (gd.data && gd.data.length > 0) {
                    initAutoRotate(gd);
                    // 자동으로 회전 시작
                    startRotation(gd);
                } else {
                    setTimeout(waitForPlotly, 200);
                }
            }, 500);
        } else {
            setTimeout(waitForPlotly, 100);
        }
    }
    
    function initAutoRotate(gd) {
        const btn = document.getElementById('rotate-btn');
        if (!btn) {
            console.error('버튼을 찾을 수 없습니다');
            return;
        }
        
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            isRotating = !isRotating;
            btn.textContent = isRotating ? '자동 회전 OFF' : '자동 회전 ON';
            btn.style.backgroundColor = isRotating ? 'rgba(255, 107, 107, 0.9)' : 'rgba(0, 0, 0, 0.8)';
            btn.style.borderColor = isRotating ? 'rgba(255, 107, 107, 0.8)' : 'rgba(255, 255, 255, 0.5)';
            
            if (isRotating) {
                startRotation(gd);
            } else {
                stopRotation();
            }
        });
        
        // 사용자가 그래프를 직접 조작할 때 회전 중지
        gd.on('plotly_relayout', function() {
            if (isRotating) {
                stopRotation();
                isRotating = false;
                btn.textContent = '자동 회전 ON';
                btn.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
                btn.style.borderColor = 'rgba(255, 255, 255, 0.5)';
            }
        });
    }
    
    function startRotation(gd) {
        function rotate() {
            if (!isRotating) return;
            
            angle += rotationSpeed;
            
            const radius = 6;
            const eyeX = radius * Math.sin(angle);
            const eyeZ = radius * Math.cos(angle);
            const eyeY = 2;
            
            Plotly.relayout(gd, {
                'scene.camera.eye.x': eyeX,
                'scene.camera.eye.y': eyeY,
                'scene.camera.eye.z': eyeZ,
                'scene.camera.center.x': 0,
                'scene.camera.center.y': 0,
                'scene.camera.center.z': 0,
                'scene.camera.up.x': 0,
                'scene.camera.up.y': 1,
                'scene.camera.up.z': 0
            });
            
            animationId = requestAnimationFrame(rotate);
        }
        rotate();
    }
    
    function stopRotation() {
        if (animationId) {
            cancelAnimationFrame(animationId);
            animationId = null;
        }
    }
    
    // DOM이 로드된 후 실행
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', waitForPlotly);
    } else {
        waitForPlotly();
    }
})();
</script>
"""
            
            # </body> 태그 앞에 스크립트 삽입
            if '</body>' in html_str:
                html_str = html_str.replace('</body>', auto_rotate_script + '</body>')
            else:
                # </body> 태그가 없으면 끝에 추가
                html_str += auto_rotate_script
            
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(html_str)
            
            print(f"3D 지식 그래프 저장: {save_path}")
            print("자동 회전 기능이 포함되었습니다. 오른쪽 상단 버튼으로 제어하세요.")
        
        fig.show()
        return fig

    def plot_subgraph(self, node_types=['trait', 'concept'], save_path=None):
        """특정 노드 타입만 포함한 서브그래프 시각화"""
        if self.graph is None:
            self.load_graph()
        
        # 서브그래프 생성
        subgraph_nodes = []
        for node_type in node_types:
            if node_type in self.node_types:
                subgraph_nodes.extend(self.node_types[node_type])
        
        subgraph = self.graph.subgraph(subgraph_nodes)
        
        # 레이아웃 계산 (더 나은 간격)
        pos = nx.spring_layout(subgraph, k=3, iterations=100)
        
        # Plotly 시각화
        edge_x, edge_y = [], []
        for edge in subgraph.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        edge_trace = go.Scatter(x=edge_x, y=edge_y,
                               line=dict(width=2, color='rgba(125,125,125,0.5)'),
                               hoverinfo='none', mode='lines')
        
        # 노드별 정보
        color_map = {'trait': '#FF6B6B', 'concept': '#4ECDC4', 'item': '#45B7D1', 'user': '#96CEB4'}
        node_trace_data = {nt: {'x': [], 'y': [], 'text': [], 'names': []} for nt in node_types}
        
        for node_id in subgraph.nodes():
            node_data = subgraph.nodes[node_id]
            node_type = node_data.get('type', 'unknown')
            
            if node_type in node_trace_data:
                x, y = pos[node_id]
                node_trace_data[node_type]['x'].append(x)
                node_trace_data[node_type]['y'].append(y)
                node_name = node_data.get('name', str(node_id))
                node_trace_data[node_type]['text'].append(f"{node_name}<br>Connections: {subgraph.degree(node_id)}")
                node_trace_data[node_type]['names'].append(node_name)
        
        traces = [edge_trace]
        for node_type, data in node_trace_data.items():
            if data['x']:
                node_trace = go.Scatter(
                    x=data['x'], y=data['y'],
                    mode='markers+text',
                    text=data['names'],
                    textposition="middle center",
                    hovertext=data['text'],
                    hoverinfo='text',
                    marker=dict(size=20, color=color_map[node_type], line=dict(width=2, color='white')),
                    name=f'{node_type.title()} ({len(data["x"])})',
                    textfont=dict(size=10, color='white')
                )
                traces.append(node_trace)
        
        layout = go.Layout(
            title=dict(text=f'{" & ".join([nt.title() for nt in node_types])} Network', font=dict(size=20)),
            showlegend=True,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            annotations=[dict(
                text="클릭하고 드래그하여 확대/이동 가능",
                showarrow=False, xref="paper", yref="paper",
                x=0.005, y=-0.002, xanchor='left', yanchor='bottom',
                font=dict(color="gray", size=12)
            )],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='black', paper_bgcolor='black'
        )
        
        fig = go.Figure(data=traces, layout=layout)
        
        if save_path:
            fig.write_html(save_path)
            print(f"서브그래프 저장: {save_path}")
        
        fig.show()
        return fig

    def plot_interactive_graph(self, save_path=None):
        """Plotly를 이용한 인터랙티브 시각화 (전체 그래프 - 성능 주의)"""
        if self.graph is None:
            self.load_graph()
        
        print("⚠️  전체 그래프는 노드가 많아 느릴 수 있습니다. 서브그래프를 권장합니다.")
        
        # 레이아웃 계산 (성능 고려)
        pos = nx.spring_layout(self.graph, k=0.5, iterations=30)
        
        # 엣지 좌표 계산
        edge_x = []
        edge_y = []
        for edge in self.graph.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        # 엣지 그리기
        edge_trace = go.Scatter(x=edge_x, y=edge_y,
                               line=dict(width=0.5, color='lightgray'),
                               hoverinfo='none',
                               mode='lines')
        
        # 노드별 정보 수집
        node_trace_data = {}
        color_map = {
            'trait': '#FF6B6B',
            'concept': '#4ECDC4', 
            'item': '#45B7D1',
            'user': '#96CEB4'
        }
        
        for node_type in color_map.keys():
            node_trace_data[node_type] = {
                'x': [], 'y': [], 'text': [], 'ids': []
            }
        
        for node_id in self.graph.nodes():
            node_data = self.graph.nodes[node_id]
            node_type = node_data.get('type', 'unknown')
            
            if node_type in node_trace_data:
                x, y = pos[node_id]
                node_trace_data[node_type]['x'].append(x)
                node_trace_data[node_type]['y'].append(y)
                node_trace_data[node_type]['text'].append(
                    f"{node_data.get('name', node_id)}<br>ID: {node_id}<br>Type: {node_type}"
                )
                node_trace_data[node_type]['ids'].append(node_id)
        
        # 노드 트레이스 생성
        traces = [edge_trace]
        for node_type, data in node_trace_data.items():
            if data['x']:  # 해당 타입의 노드가 있는 경우만
                node_trace = go.Scatter(
                    x=data['x'], y=data['y'],
                    mode='markers',
                    hoverinfo='text',
                    text=data['text'],
                    marker=dict(size=8, color=color_map[node_type]),
                    name=f'{node_type.title()} ({len(data["x"])})'
                )
                traces.append(node_trace)
        
        # 레이아웃 설정
        layout = go.Layout(
            title=dict(text='Interactive Knowledge Graph', font=dict(size=16)),
            showlegend=True,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            annotations=[ dict(
                text="그래프 노드를 클릭하거나 호버하여 정보를 확인하세요",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.005, y=-0.002,
                xanchor='left', yanchor='bottom',
                font=dict(color="gray", size=12)
            )],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
        
        fig = go.Figure(data=traces, layout=layout)
        
        if save_path:
            fig.write_html(save_path)
            print(f"인터랙티브 그래프 저장: {save_path}")
        
        fig.show()
    
    def plot_statistics(self):
        """그래프 통계 시각화"""
        if self.graph is None:
            self.load_graph()
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # 1. 노드 타입별 개수
        node_counts = {k: len(v) for k, v in self.node_types.items() if v}
        axes[0,0].bar(node_counts.keys(), node_counts.values(), 
                     color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])
        axes[0,0].set_title('Node Count by Type')
        axes[0,0].set_ylabel('Count')
        
        # 2. 차수 분포
        degrees = [self.graph.degree(n) for n in self.graph.nodes()]
        axes[0,1].hist(degrees, bins=20, alpha=0.7, color='skyblue')
        axes[0,1].set_title('Degree Distribution')
        axes[0,1].set_xlabel('Degree')
        axes[0,1].set_ylabel('Frequency')
        
        # 3. 엣지 타입별 개수
        edge_types = {}
        for _, _, data in self.graph.edges(data=True):
            relation = data.get('relation', 'unknown')
            edge_types[relation] = edge_types.get(relation, 0) + 1
        
        axes[1,0].bar(edge_types.keys(), edge_types.values(), color='lightcoral')
        axes[1,0].set_title('Edge Count by Relation Type')
        axes[1,0].set_ylabel('Count')
        axes[1,0].tick_params(axis='x', rotation=45)
        
        # 4. 가중치 분포
        weights = [data.get('weight', 1.0) for _, _, data in self.graph.edges(data=True)]
        axes[1,1].hist(weights, bins=20, alpha=0.7, color='lightgreen')
        axes[1,1].set_title('Edge Weight Distribution')
        axes[1,1].set_xlabel('Weight')
        axes[1,1].set_ylabel('Frequency')
        
        plt.tight_layout()
        plt.show()
    
    def print_graph_info(self):
        """그래프 정보 출력"""
        if self.graph is None:
            self.load_graph()
        
        print("\n=== 그래프 정보 ===")
        print(f"전체 노드: {self.graph.number_of_nodes()}개")
        print(f"전체 엣지: {self.graph.number_of_edges()}개")
        
        print(f"\n노드 타입별:")
        for node_type, nodes in self.node_types.items():
            print(f"  {node_type}: {len(nodes)}개")
        
        # 엣지 타입별 통계
        edge_types = {}
        for _, _, data in self.graph.edges(data=True):
            relation = data.get('relation', 'unknown')
            edge_types[relation] = edge_types.get(relation, 0) + 1
        
        print(f"\n엣지 타입별:")
        for relation, count in edge_types.items():
            print(f"  {relation}: {count}개")

def main():
    """시각화 실행 예제"""
    visualizer = GraphVisualizer()
    
    # 그래프 정보 출력
    visualizer.print_graph_info()
    
    # GEXF 파일 생성 (Gephi용)
    print("\n=== Gephi용 GEXF 파일 생성 ===")
    visualizer.export_to_gexf("knowledge_graph.gexf")
    
    # 3D 인터랙티브 그래프 시각화
    print("\n=== 3D 인터랙티브 지식 그래프 ===")
    visualizer.plot_3d_knowledge_graph("knowledge_graph_3d.html")
    
    # 통계 시각화
    print("\n=== 그래프 통계 ===")
    visualizer.plot_statistics()

if __name__ == "__main__":
    main()