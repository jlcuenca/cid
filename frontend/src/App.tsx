import React, { useCallback, useRef, useState, useEffect } from 'react';
import {
  ReactFlow,
  addEdge,
  Background,
  Controls,
  type Connection,
  type Edge,
  type Node,
  useNodesState,
  useEdgesState,
  ReactFlowProvider,
  useReactFlow,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import {
  BookOpen,
  Award,
  Layers,
  Save,
  Play,
  Settings,
  Search,
  ChevronRight,
  X,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Sparkles
} from 'lucide-react';
import { CourseNode, CompetencyNode, SubPathNode } from './components/Nodes';

import { api } from './services/api';

const nodeTypes = {
  course: CourseNode,
  competency: CompetencyNode,
  subPath: SubPathNode,
};

// Mock Simulation Result Type
interface SimulationResult {
  path_id: string;
  student_id: string;
  unlocked_nodes: string[];
  issued_badges: string[];
  logs: string[];
  success: boolean;
}

const Sidebar = () => {
  const onDragStart = (event: React.DragEvent, nodeType: string, label: string) => {
    event.dataTransfer.setData('application/reactflow', nodeType);
    event.dataTransfer.setData('application/label', label);
    event.dataTransfer.effectAllowed = 'move';
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-title">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Layers className="text-indigo-500" /> CID Builder
        </h1>
      </div>

      <div className="mb-8">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={16} />
          <input
            type="text"
            placeholder="Buscar recursos..."
            className="w-full bg-slate-900/50 border border-slate-800 rounded-lg py-2 pl-10 pr-4 text-sm focus:outline-none focus:border-indigo-500 transition-colors"
          />
        </div>
      </div>

      <div className="space-y-6">
        <div>
          <h3 className="text-xs uppercase tracking-widest text-slate-500 font-bold mb-4">Recursos Disponibles</h3>
          <div
            className="node-item"
            onDragStart={(event) => onDragStart(event, 'course', 'Nuevo Curso')}
            draggable
          >
            <BookOpen size={18} />
            <span className="text-sm font-medium">Curso Moodle</span>
          </div>
          <div
            className="node-item"
            onDragStart={(event) => onDragStart(event, 'competency', 'Nueva Competencia')}
            draggable
          >
            <Award size={18} />
            <span className="text-sm font-medium">Competencia</span>
          </div>
          <div
            className="node-item"
            onDragStart={(event) => onDragStart(event, 'subPath', 'Sub-Ruta')}
            draggable
          >
            <Layers size={18} />
            <span className="text-sm font-medium">Sub-Ruta</span>
          </div>
        </div>

        <div>
          <h3 className="text-xs uppercase tracking-widest text-slate-500 font-bold mb-4">Plantillas</h3>
          <div className="p-3 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-between cursor-pointer hover:bg-indigo-500/20 transition-colors">
            <span className="text-xs font-medium text-indigo-300">Ruta de Matemáticas</span>
            <ChevronRight size={14} className="text-indigo-400" />
          </div>
        </div>
      </div>

      <div className="mt-auto pt-6 border-t border-slate-800">
        <button className="btn btn-secondary w-full justify-center">
          <Settings size={16} /> Configuración
        </button>
      </div>
    </aside>
  );
};

const Flow = () => {
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const { screenToFlowPosition } = useReactFlow();

  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const [isSimulating, setIsSimulating] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [simulationResult, setSimulationResult] = useState<SimulationResult | null>(null);

  const [editingRequirementsNodeId, setEditingRequirementsNodeId] = useState<string | null>(null);
  const [currentRule, setCurrentRule] = useState<any>({
    logic_operator: 'AND',
    conditions: [{ field: 'score', operator: '>', value: '80' }]
  });

  const [mappingSource, setMappingSource] = useState<{ nodeId: string, courseId: string, resource: any } | null>(null);
  const [evidenceMappings, setEvidenceMappings] = useState<any[]>([]);

  const onEditRequirements = useCallback((nodeId: string) => {
    const node = nodes.find(n => n.id === nodeId);
    if (node?.data?.requirements) {
      setCurrentRule(node.data.requirements);
    } else {
      setCurrentRule({
        logic_operator: 'AND',
        conditions: [{ field: 'score', operator: '>', value: '80' }]
      });
    }
    setEditingRequirementsNodeId(nodeId);
  }, [nodes]);

  const saveRequirement = (nodeId: string) => {
    setNodes((nds: Node[]) => nds.map((node: Node) => {
      if (node.id === nodeId) {
        return { ...node, data: { ...node.data, requirements: { ...currentRule, id: `rule-${Date.now()}`, name: "Requisito de Avance" } } };
      }
      return node;
    }));
    setEditingRequirementsNodeId(null);
  };

  const onMapEvidence = useCallback((nodeId: string, courseId: string, resource: any) => {
    setMappingSource({ nodeId, courseId, resource });
  }, []);

  const onCompetencyClick = useCallback((nodeId: string) => {
    if (!mappingSource) return;

    const newMapping = {
      id: `ev-${Date.now()}`,
      moodle_activity_id: mappingSource.resource.id,
      moodle_activity_type: mappingSource.resource.type,
      competency_id: nodeId, // Linking to the node ID in the graph
      weight: 1.0
    };

    setEvidenceMappings(prev => [...prev, newMapping]);
    setMappingSource(null);
    alert(`Evidencia "${mappingSource.resource.name}" vinculada con éxito.`);
  }, [mappingSource]);

  const [ob3Result, setOb3Result] = useState<any | null>(null);

  const onExportOB3 = useCallback(async (nodeId: string) => {
    const node = nodes.find(n => n.id === nodeId);
    if (!node) return;

    try {
      const competencyData = {
        id: node.id,
        name: (node.data as any).label,
        description: `Competencia demostrada en el nodo ${node.id}`,
        taxonomy_id: 'cid-framework-v1',
        level: (node.data as any).level?.toLowerCase() || 'intermediate'
      };

      // Filter evidence mappings for this competency
      const nodeMappings = evidenceMappings.filter(m => m.competency_id === nodeId);

      const result = await api.issueBadgeOB3({
        competency: competencyData,
        student_email: 'ghost-student-001@example.edu',
        evidence_mappings: nodeMappings,
        narratives: nodeMappings.map(m => `Validación exitosa de la actividad Moodle ID: ${m.moodle_activity_id}`)
      });

      setOb3Result(result);
    } catch (error) {
      console.error("Export OB3 failed:", error);
      alert("Error al exportar Open Badges 3.0");
    }
  }, [nodes, evidenceMappings]);

  const onAnalyze = useCallback(async (nodeId: string, courseId: string) => {
    console.log(`Analyzing node ${nodeId} (Course: ${courseId})`);
    setNodes((nds: Node[]) => nds.map((node: Node) => {
      if (node.id === nodeId) {
        return { ...node, data: { ...node.data, isAnalyzing: true } };
      }
      return node;
    }));

    try {
      // Use real API
      const response = await api.analyzeSyllabus(courseId);
      setNodes((nds: Node[]) => nds.map((node: Node) => {
        if (node.id === nodeId) {
          return {
            ...node,
            data: {
              ...node.data,
              metadata: response.metadata,
              resources: response.course.resources,
              isAnalyzing: false,
              onMapEvidence,
              onCompetencyClick,
              onExportOB3
            }
          };
        }
        return node;
      }));
    } catch (error) {
      console.error("Analysis failed:", error);
      // Fallback to mock for demo if API fails
      setNodes((nds: Node[]) => nds.map((node: Node) => {
        if (node.id === nodeId) {
          return {
            ...node,
            data: {
              ...node.data,
              metadata: {
                keywords: ['error', 'api', 'offline'],
                difficulty: 'unknown'
              },
              resources: [
                { id: 'mock-1', name: 'Examen de Prueba', type: 'quiz' },
                { id: 'mock-2', name: 'Tarea de Derivadas', type: 'assignment' }
              ],
              isAnalyzing: false,
              onMapEvidence,
              onCompetencyClick,
              onExportOB3
            }
          };
        }
        return node;
      }));
    }
  }, [setNodes, onMapEvidence, onCompetencyClick, onExportOB3]);

  useEffect(() => {
    setNodes([
      {
        id: 'node-1',
        type: 'course',
        position: { x: 250, y: 100 },
        data: { label: 'Matemáticas I', id: 'MATH101', nodeId: 'node-1', onAnalyze, onMapEvidence, onCompetencyClick, onExportOB3 },
      },
      {
        id: 'node-2',
        type: 'competency',
        position: { x: 250, y: 300 },
        data: { label: 'Certificación en Derivadas', level: 'Intermediate', nodeId: 'node-2', onEditRequirements, onCompetencyClick, onExportOB3, isMapping: !!mappingSource },
      },
    ]);
    setEdges([
      { id: 'e1-2', source: 'node-1', target: 'node-2', animated: true },
    ]);
  }, [onAnalyze, onMapEvidence, onEditRequirements, onCompetencyClick, onExportOB3, mappingSource, setNodes, setEdges]);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge({ ...params, animated: true }, eds)),
    [setEdges]
  );

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();

      const type = event.dataTransfer.getData('application/reactflow');
      const label = event.dataTransfer.getData('application/label');

      if (typeof type === 'undefined' || !type) {
        return;
      }

      const position = screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      });

      const nodeId = `node_${Date.now()}`;
      const newNode: Node = {
        id: nodeId,
        type,
        position,
        data: {
          label: `${label}`,
          id: `REF_${Math.floor(Math.random() * 1000)}`,
          nodeId,
          onAnalyze
        },
      };

      setNodes((nds) => nds.concat(newNode));
    },
    [screenToFlowPosition, setNodes, onAnalyze]
  );

  const handleSimulate = async () => {
    setIsSimulating(true);
    try {
      const result = await api.simulatePath({
        path_id: 'path-math-excellence',
        student_id: 'ghost-student-001'
      });
      setSimulationResult(result);
    } catch (error) {
      console.error("Simulation failed:", error);
      // Mock fallback
      setSimulationResult({
        path_id: 'path-math-excellence',
        student_id: 'ghost-student-001',
        unlocked_nodes: ['node-1'],
        issued_badges: [],
        logs: ['Error: Could not connect to simulation service.', 'Falling back to mock logs...'],
        success: false
      });
    } finally {
      setIsSimulating(false);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const pathData = {
        id: 'path-math-excellence',
        name: 'Ruta de Excelencia Matemática',
        description: 'Ruta avanzada para alumnos becados.',
        nodes: nodes.map(n => ({
          id: n.id,
          type: n.type,
          reference_id: (n.data as any).id || (n.data as any).label,
          label: (n.data as any).label,
          position: n.position,
          metadata: (n.data as any).metadata,
          requirements: (n.data as any).requirements
        })),
        edges: edges.map(e => ({ from: e.source, to: e.target })),
        evidence_mappings: evidenceMappings,
        created_by: 'doctor-001'
      };
      await api.savePath(pathData);
      alert("Ruta guardada con éxito!");
    } catch (error) {
      console.error("Save failed:", error);
      alert("Error al guardar la ruta.");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="canvas-container" ref={reactFlowWrapper}>
      <div className="top-bar glass-panel">
        <div className="flex items-center gap-4">
          <h2 className="text-lg font-bold">Ruta: Excelencia Matemática</h2>
          <span className="px-2 py-1 rounded bg-emerald-500/20 text-emerald-400 text-[10px] font-bold uppercase tracking-wider">Borrador</span>
        </div>
        <div className="flex items-center gap-3">
          <button className="btn btn-secondary" onClick={handleSimulate} disabled={isSimulating}>
            {isSimulating ? <Loader2 size={16} className="animate-spin" /> : <Play size={16} />}
            Simular
          </button>
          <button className="btn btn-primary" onClick={handleSave} disabled={isSaving}>
            {isSaving ? <Loader2 size={16} className="animate-spin" /> : <Save size={16} />}
            Guardar Ruta
          </button>
        </div>
      </div>

      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onDrop={onDrop}
        onDragOver={onDragOver}
        nodeTypes={nodeTypes}
        fitView
      >
        <Background color="#334155" gap={20} />
        <Controls />
      </ReactFlow>

      {simulationResult && (
        <div className="modal-overlay">
          <div className="modal-content glass-panel">
            <button
              className="absolute top-4 right-4 text-slate-400 hover:text-white"
              onClick={() => setSimulationResult(null)}
            >
              <X size={20} />
            </button>

            <div className="flex items-center gap-3 mb-6">
              <div className={`p-2 rounded-lg ${simulationResult.success ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'}`}>
                {simulationResult.success ? <CheckCircle2 size={24} /> : <AlertCircle size={24} />}
              </div>
              <div>
                <h3 className="text-xl font-bold">Resultado de Simulación</h3>
                <p className="text-sm text-slate-400">Estudiante: {simulationResult.student_id}</p>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <h4 className="text-xs uppercase tracking-wider text-slate-500 font-bold mb-2">Insignias Otorgadas</h4>
                <div className="flex gap-2 flex-wrap">
                  {simulationResult.issued_badges.map((badge: string) => (
                    <span key={badge} className="badge-pill">
                      <Award size={14} /> {badge}
                    </span>
                  ))}
                  {simulationResult.issued_badges.length === 0 && <span className="text-sm text-slate-500 italic">Ninguna</span>}
                </div>
              </div>

              <div>
                <h4 className="text-xs uppercase tracking-wider text-slate-500 font-bold mb-2">Logs de Ejecución</h4>
                <div className="simulation-log">
                  {simulationResult.logs.map((log: string, i: number) => {
                    let type = 'info';
                    if (log.includes('[OK]') || log.includes('SUCCESS')) type = 'success';
                    if (log.includes('[FAIL]') || log.includes('FAILED')) type = 'failed';
                    if (log.includes('[WARN]')) type = 'warn';
                    if (log.includes('>>')) type = 'highlight';

                    return (
                      <div key={i} className={`log-entry log-${type}`}>
                        {log}
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            <div className="mt-8 flex justify-end">
              <button className="btn btn-primary" onClick={() => setSimulationResult(null)}>
                Cerrar
              </button>
            </div>
          </div>
        </div>
      )}
      {ob3Result && (
        <div className="modal-overlay">
          <div className="modal-content glass-panel max-w-2xl">
            <button
              className="absolute top-4 right-4 text-slate-400 hover:text-white"
              onClick={() => setOb3Result(null)}
            >
              <X size={20} />
            </button>

            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 rounded-lg bg-purple-500/20 text-purple-400">
                <Sparkles size={24} />
              </div>
              <div>
                <h3 className="text-xl font-bold">Open Badges 3.0 (JSON-LD)</h3>
                <p className="text-sm text-slate-400">Insignia generada con metadatos pedagógicos y evidencias.</p>
              </div>
            </div>

            <div className="bg-slate-950 rounded-lg p-4 border border-slate-800 overflow-hidden">
              <pre className="text-[10px] text-indigo-300 font-mono overflow-auto max-h-[400px]">
                {JSON.stringify(ob3Result, null, 2)}
              </pre>
            </div>

            <div className="mt-8 flex justify-end gap-3">
              <button
                className="btn btn-secondary"
                onClick={() => {
                  const blob = new Blob([JSON.stringify(ob3Result, null, 2)], { type: 'application/json' });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = `badge-${ob3Result.id.split('/').pop()}.jsonld`;
                  a.click();
                }}
              >
                Descargar JSON-LD
              </button>
              <button className="btn btn-primary" onClick={() => setOb3Result(null)}>
                Cerrar
              </button>
            </div>
          </div>
        </div>
      )}

      {editingRequirementsNodeId && (
        <div className="modal-overlay">
          <div className="modal-content glass-panel max-w-md">
            <button
              className="absolute top-4 right-4 text-slate-400 hover:text-white"
              onClick={() => setEditingRequirementsNodeId(null)}
            >
              <X size={20} />
            </button>

            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 rounded-lg bg-amber-500/20 text-amber-400">
                <Settings size={24} />
              </div>
              <div>
                <h3 className="text-xl font-bold">Configurar Requisitos</h3>
                <p className="text-sm text-slate-400">Define las condiciones para desbloquear este nodo.</p>
              </div>
            </div>

            <div className="space-y-4">
              <div className="p-4 rounded-lg bg-slate-900/50 border border-slate-800">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-xs font-bold text-slate-500 uppercase">Condición 1</span>
                  <span className="px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-400 text-[10px] font-bold">AND</span>
                </div>

                <div className="space-y-3">
                  <div>
                    <label className="block text-[10px] text-slate-500 uppercase font-bold mb-1">Campo</label>
                    <select
                      className="w-full bg-slate-800 border border-slate-700 rounded p-2 text-sm text-white"
                      value={currentRule.conditions[0].field}
                      onChange={(e) => setCurrentRule({
                        ...currentRule,
                        conditions: [{ ...currentRule.conditions[0], field: e.target.value }]
                      })}
                    >
                      <option value="score">Calificación (Score)</option>
                      <option value="course_completed">Curso Completado</option>
                      <option value="attribute.becado">Atributo: Becado</option>
                    </select>
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-[10px] text-slate-500 uppercase font-bold mb-1">Operador</label>
                      <select
                        className="w-full bg-slate-800 border border-slate-700 rounded p-2 text-sm text-white"
                        value={currentRule.conditions[0].operator}
                        onChange={(e) => setCurrentRule({
                          ...currentRule,
                          conditions: [{ ...currentRule.conditions[0], operator: e.target.value }]
                        })}
                      >
                        <option value=">">Mayor que (&gt;)</option>
                        <option value="==">Igual a (==)</option>
                        <option value="contains">Contiene</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-[10px] text-slate-500 uppercase font-bold mb-1">Valor</label>
                      <input
                        type="text"
                        className="w-full bg-slate-800 border border-slate-700 rounded p-2 text-sm text-white"
                        value={currentRule.conditions[0].value}
                        onChange={(e) => setCurrentRule({
                          ...currentRule,
                          conditions: [{ ...currentRule.conditions[0], value: e.target.value }]
                        })}
                      />
                    </div>
                  </div>
                </div>
              </div>

              <button className="w-full py-2 border border-dashed border-slate-700 rounded text-xs text-slate-500 hover:border-indigo-500 hover:text-indigo-400 transition-colors">
                + Añadir otra condición
              </button>
            </div>

            <div className="mt-8 flex justify-end gap-3">
              <button className="btn btn-secondary" onClick={() => setEditingRequirementsNodeId(null)}>
                Cancelar
              </button>
              <button
                className="btn btn-primary"
                onClick={() => saveRequirement(editingRequirementsNodeId!)}
              >
                Guardar Requisito
              </button>
            </div>
          </div>
        </div>
      )}

      {mappingSource && (
        <div className="fixed bottom-8 left-1/2 -translate-x-1/2 z-50">
          <div className="glass-panel px-6 py-4 border-indigo-500 bg-indigo-500/10 flex items-center gap-6 shadow-2xl animate-bounce">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-full bg-indigo-500 text-white">
                <Award size={20} />
              </div>
              <div>
                <p className="text-sm font-bold">Modo de Mapeo Activo</p>
                <p className="text-xs text-indigo-300">Selecciona una competencia para vincular: <span className="font-mono text-white">{mappingSource.resource.name}</span></p>
              </div>
            </div>
            <button
              className="p-1 hover:bg-white/10 rounded-full transition-colors"
              onClick={() => setMappingSource(null)}
            >
              <X size={20} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default function App() {
  return (
    <div className="app-container">
      <ReactFlowProvider>
        <Sidebar />
        <Flow />
      </ReactFlowProvider>
    </div>
  );
}
