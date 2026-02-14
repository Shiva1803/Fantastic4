/**
 * API client for Space management.
 */

import { Space, ApiError } from '../types';

// Base API URL - matching client.ts
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
 * Get all spaces for a user.
 */
export async function getSpaces(userId: string): Promise<Space[]> {
    const response = await fetch(`${API_BASE_URL}/api/spaces?userId=${encodeURIComponent(userId)}`);
    return handleResponse<Space[]>(response);
}

/**
 * Get a specific space by ID.
 */
export async function getSpace(spaceId: string): Promise<Space> {
    const response = await fetch(`${API_BASE_URL}/api/spaces/${spaceId}`);
    return handleResponse<Space>(response);
}

/**
 * Create a new space.
 */
export async function createSpace(userId: string, name: string, description?: string): Promise<Space> {
    const response = await fetch(`${API_BASE_URL}/api/spaces`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            userId,
            name,
            description
        }),
    });

    return handleResponse<Space>(response);
}

/**
 * Update a space.
 */
export async function updateSpace(spaceId: string, name?: string, description?: string): Promise<Space> {
    const response = await fetch(`${API_BASE_URL}/api/spaces/${spaceId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            name,
            description
        }),
    });

    return handleResponse<Space>(response);
}

/**
 * Delete a space.
 */
export async function deleteSpace(spaceId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/spaces/${spaceId}`, {
        method: 'DELETE',
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
        throw new ApiClientError(errorData.error, response.status);
    }
}
