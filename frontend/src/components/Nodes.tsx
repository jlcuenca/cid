import React, { memo } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';
import { BookOpen, Award, Layers, Sparkles, Loader2 } from 'lucide-react';

export const CourseNode = memo(({ data }: NodeProps) => {
    const label = (data.label as React.ReactNode) || 'Sin nombre';
    const metadata = data.metadata as any;

    const onAnalyze = (e: React.MouseEvent) => {
        e.stopPropagation();
        if (data.onAnalyze) {
            // Pass internal nodeId (from props) and courseId (from data)
            (data.onAnalyze as (nodeId: string, courseId: string) => void)((data as any).nodeId, data.id as string);
        }
    };

    return (
        <div className="custom-node node-course group">
            <Handle type="target" position={Position.Top} />
            <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                    <BookOpen size={16} className="text-indigo-400" />
                    <span className="node-type">Curso</span>
                </div>
                <button
                    onClick={onAnalyze}
                    disabled={data.isAnalyzing as boolean}
                    className="p-1 rounded-full bg-indigo-500/10 text-indigo-400 opacity-0 group-hover:opacity-100 transition-opacity hover:bg-indigo-500/20 disabled:opacity-50"
                    title="Analizar con AI"
                >
                    {data.isAnalyzing ? <Loader2 size={12} className="animate-spin" /> : <Sparkles size={12} />}
                </button>
            </div>
            <div className="node-label">{label}</div>
            <div className="text-[10px] text-slate-500 font-mono mt-1">{data.id as string}</div>

            {metadata && (
                <div className="mt-2 pt-2 border-t border-slate-700/50">
                    <div className="flex gap-1 flex-wrap">
                        {(metadata.keywords || []).slice(0, 3).map((kw: string) => (
                            <span key={kw} className="text-[10px] px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                                {kw}
                            </span>
                        ))}
                    </div>
                </div>
            )}

            {data.resources && (data.resources as any[]).length > 0 && (
                <div className="mt-3 pt-2 border-t border-slate-700/50">
                    <h4 className="text-[10px] uppercase tracking-wider text-slate-500 font-bold mb-2 flex items-center gap-1">
                        <Layers size={10} /> Contenido Moodle
                    </h4>
                    <div className="space-y-1">
                        {(data.resources as any[]).map((res: any) => (
                            <div key={res.id} className="flex items-center justify-between p-1.5 rounded bg-slate-900/50 border border-slate-800 group/res">
                                <div className="flex items-center gap-2 overflow-hidden">
                                    <div className="w-1.5 h-1.5 rounded-full bg-indigo-500" />
                                    <span className="text-[10px] text-slate-300 truncate">{res.name}</span>
                                </div>
                                <button
                                    className="p-1 rounded bg-indigo-500/10 text-indigo-400 opacity-0 group-hover/res:opacity-100 transition-opacity hover:bg-indigo-500/20"
                                    title="Mapear como evidencia"
                                    onClick={() => (data as any).onMapEvidence?.((data as any).nodeId, data.id as string, res)}
                                >
                                    <Award size={10} />
                                </button>
                            </div>
                        ))}
                    </div>
                </div>
            )}
            <Handle type="source" position={Position.Bottom} />
        </div>
    );
});

export const CompetencyNode = memo(({ data }: NodeProps) => {
    const label = (data.label as React.ReactNode) || 'Sin nombre';
    const isMapping = data.isMapping as boolean;

    const onClick = () => {
        if (isMapping && (data as any).onCompetencyClick) {
            (data as any).onCompetencyClick(data.nodeId);
        }
    };

    return (
        <div
            className={`custom-node node-competency ${isMapping ? 'ring-4 ring-indigo-500 ring-offset-4 ring-offset-slate-900 cursor-pointer animate-pulse' : ''}`}
            onClick={onClick}
        >
            <Handle type="target" position={Position.Top} />
            <div className="flex items-center gap-2 mb-2">
                <Award size={16} className="text-purple-400" />
                <span className="node-type">Competencia</span>
            </div>
            <div className="node-label">{label}</div>
            <div className="text-[10px] text-slate-400 mt-1">{data.level as string}</div>

            {data.requirements && (
                <div className="mt-2 pt-2 border-t border-slate-700/50">
                    <div className="flex items-center justify-between">
                        <span className="text-[10px] text-amber-400 font-bold flex items-center gap-1">
                            <Settings size={10} /> Requisitos
                        </span>
                        <button
                            className="text-[10px] text-indigo-400 hover:underline"
                            onClick={(e) => {
                                e.stopPropagation();
                                (data as any).onEditRequirements?.(data.nodeId);
                            }}
                        >
                            Editar
                        </button>
                    </div>
                    <div className="mt-1 text-[9px] text-slate-500 italic truncate">
                        {JSON.stringify(data.requirements)}
                    </div>
                </div>
            )}

            <button
                className="mt-3 w-full py-1.5 bg-purple-500/10 border border-purple-500/30 rounded text-[10px] text-purple-300 hover:bg-purple-500/20 transition-colors flex items-center justify-center gap-1.5"
                onClick={(e) => {
                    e.stopPropagation();
                    (data as any).onExportOB3?.(data.nodeId);
                }}
            >
                <Sparkles size={10} /> Exportar Open Badges 3.0
            </button>

            {!data.requirements && (
                <button
                    className="mt-2 w-full py-1 border border-dashed border-slate-700 rounded text-[9px] text-slate-500 hover:border-indigo-500 hover:text-indigo-400 transition-colors"
                    onClick={(e) => {
                        e.stopPropagation();
                        (data as any).onEditRequirements?.(data.nodeId);
                    }}
                >
                    + Añadir Requisito
                </button>
            )}
            <Handle type="source" position={Position.Bottom} />
        </div>
    );
});

export const SubPathNode = memo(({ data }: NodeProps) => {
    const label = (data.label as React.ReactNode) || 'Sin nombre';
    return (
        <div className="custom-node glass-panel border-amber-500/50 border-l-4">
            <Handle type="target" position={Position.Top} />
            <div className="flex items-center gap-2 mb-2">
                <Layers size={16} className="text-amber-400" />
                <span className="node-type">Sub-Ruta</span>
            </div>
            <div className="node-label">{label}</div>
            <Handle type="source" position={Position.Bottom} />
        </div>
    );
});
