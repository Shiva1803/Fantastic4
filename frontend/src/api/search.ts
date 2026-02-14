/**
 * API client for semantic search within spaces.
 */

import { SpaceItem } from './content';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export interface SearchResult extends SpaceItem {
    score: number;
}

export interface SearchResponse {
    query: string;
    results: SearchResult[];
    total: number;
}

/**
 * Search within a space using semantic similarity.
 */
export async function searchSpace(spaceId: string, query: string, topK: number = 5): Promise<SearchResponse> {
    const response = await fetch(`${API_BASE_URL}/api/spaces/${spaceId}/search`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query, topK }),
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Search failed' }));
        throw new Error(errorData.error || 'Search failed');
    }

    return response.json();
}
