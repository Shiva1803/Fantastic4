/**
 * API client for RAG-based querying within spaces.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export interface QuerySource {
    itemId: string;
    type: 'message' | 'file';
    content: string;
    score: number;
}

export interface QueryRecord {
    id: string;
    spaceId: string;
    question: string;
    answer: string;
    sources: QuerySource[];
    createdAt: string;
}

export interface QueryResponse {
    query: QueryRecord;
}

/**
 * Ask a question about content in a space.
 */
export async function askQuestion(spaceId: string, question: string): Promise<QueryRecord> {
    const response = await fetch(`${API_BASE_URL}/api/spaces/${spaceId}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Query failed' }));
        throw new Error(errorData.error || 'Query failed');
    }

    const data = await response.json();
    return data.query;
}

/**
 * Get query history for a space.
 */
export async function getQueryHistory(spaceId: string, limit = 20, offset = 0): Promise<QueryRecord[]> {
    const response = await fetch(
        `${API_BASE_URL}/api/spaces/${spaceId}/queries?limit=${limit}&offset=${offset}`
    );

    if (!response.ok) {
        throw new Error('Failed to fetch query history');
    }

    const data = await response.json();
    return data.queries;
}
