/**
 * API client for global search across all spaces.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export interface GlobalSearchResult {
    id: string;
    spaceId: string;
    spaceName: string;
    type: 'message' | 'file';
    content: string;
    notes?: string;
    metadata: Record<string, any>;
    createdAt: string;
    score: number;
}

export interface GlobalSearchResponse {
    query: string;
    results: GlobalSearchResult[];
    total: number;
}

export async function globalSearch(
    userId: string,
    query: string,
    topK: number = 5
): Promise<GlobalSearchResponse> {
    const response = await fetch(`${API_BASE_URL}/api/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, userId, topK }),
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Search failed' }));
        throw new Error(errorData.error || 'Search failed');
    }

    return response.json();
}
