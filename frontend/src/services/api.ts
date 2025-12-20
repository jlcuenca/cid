import axios from 'axios';

const ANALYZE_URL = import.meta.env.VITE_ANALYZE_URL || 'http://localhost:8081';
const SIMULATE_URL = import.meta.env.VITE_SIMULATE_URL || 'http://localhost:8082';
const MANAGE_URL = import.meta.env.VITE_MANAGE_URL || 'http://localhost:8083';

export interface SimulationRequest {
    path_id: string;
    student_id?: string;
    mock_scores?: Record<string, number>;
}

export const api = {
    analyzeSyllabus: async (courseId: string) => {
        const response = await axios.post(`${ANALYZE_URL}`, { course_id: courseId });
        return response.data;
    },

    simulatePath: async (request: SimulationRequest) => {
        const response = await axios.post(`${SIMULATE_URL}`, request);
        return response.data;
    },

    savePath: async (path: any) => {
        const response = await axios.post(`${MANAGE_URL}`, { action: 'save', path });
        return response.data;
    },

    getPath: async (pathId: string) => {
        const response = await axios.get(`${MANAGE_URL}?path_id=${pathId}`);
        return response.data;
    },

    issueBadgeOB3: async (data: any) => {
        const response = await axios.post(`${import.meta.env.VITE_ISSUE_OB3_URL || 'http://localhost:8084'}`, data);
        return response.data;
    }
};
