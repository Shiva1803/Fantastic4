/**
 * API client for Content management within spaces.
 */

import { ApiError } from '../types';

// Matching backend SpaceItem model
export interface SpaceItem {
    id: string;
    spaceId: string;
    type: 'message' | 'file';
    content: string; // Text content or filename
    notes?: string;
    metadata: {
        original_name?: string;
        size_bytes?: number;
        mime_type?: string;
        [key: string]: any;
    };
    createdAt: string;
}

// Base API URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

class ApiClientError extends Error {
    constructor(
        message: string,
        public statusCode: number,
        public details?: string
    ) {
        super(message);
        this.name = 'ApiClientError';
    }
}

async function handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
        const errorData: ApiError = await response.json().catch(() => ({
            error: 'Unknown error occurred',
        }));

        throw new ApiClientError(
            errorData.error,
            response.status,
            errorData.details
        );
    }

    return response.json();
}

/**
 * Get all items in a space.
 */
export async function getSpaceItems(spaceId: string): Promise<SpaceItem[]> {
    const response = await fetch(`${API_BASE_URL}/api/spaces/${spaceId}/items`);
    return handleResponse<SpaceItem[]>(response);
}

/**
 * Save a text message to a space.
 */
export async function saveMessage(spaceId: string, content: string, notes?: string): Promise<SpaceItem> {
    const response = await fetch(`${API_BASE_URL}/api/spaces/${spaceId}/items`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            content,
            notes
        }),
    });

    return handleResponse<SpaceItem>(response);
}

/**
 * Upload a file to a space.
 */
export async function uploadFile(spaceId: string, file: File, notes?: string): Promise<SpaceItem> {
    const formData = new FormData();
    formData.append('file', file);
    if (notes) {
        formData.append('notes', notes);
    }

    const response = await fetch(`${API_BASE_URL}/api/spaces/${spaceId}/upload`, {
        method: 'POST',
        // No Content-Type header - browser sets it with boundary for FormData
        body: formData,
    });

    return handleResponse<SpaceItem>(response);
}

/**
 * Delete an item from a space.
 */
export async function deleteItem(spaceId: string, itemId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/spaces/${spaceId}/items/${itemId}`, {
        method: 'DELETE',
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
        throw new ApiClientError(errorData.error, response.status);
    }
}
