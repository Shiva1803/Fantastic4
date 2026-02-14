import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getSpace, deleteSpace, updateSpace } from '../api/spaces';
import { getSpaceItems, deleteItem } from '../api/content';
import { searchSpace, SearchResult } from '../api/search';
import { Space } from '../types';
import AddContentModal from '../components/AddContentModal';
import QueryInterface from '../components/QueryInterface';

export default function SpaceDetailPage() {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const [space, setSpace] = useState<Space | null>(null);
    const [items, setItems] = useState<any[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isEditing, setIsEditing] = useState(false);
    const [editName, setEditName] = useState('');
    const [editDescription, setEditDescription] = useState('');
    const [isSaving, setIsSaving] = useState(false);
    const [isAddContentOpen, setIsAddContentOpen] = useState(false);
    // Search state
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState<SearchResult[] | null>(null);
    const [isSearching, setIsSearching] = useState(false);


    useEffect(() => {
        if (id) {
            fetchSpaceAndItems(id);
        }
    }, [id]);

    const fetchSpaceAndItems = async (spaceId: string) => {
        setIsLoading(true);
        try {
            const [spaceData, itemsData] = await Promise.all([
                getSpace(spaceId),
                getSpaceItems(spaceId)
            ]);
            setSpace(spaceData);
            setItems(itemsData);
            setEditName(spaceData.name);
            setEditDescription(spaceData.description || '');
            setError(null);
        } catch (err) {
            console.error('Failed to fetch space details:', err);
            setError('Failed to load space details.');
        } finally {
            setIsLoading(false);
        }
    };

    const handleDelete = async () => {
        if (!id || !window.confirm('Are you sure you want to delete this space? This cannot be undone.')) return;

        try {
            await deleteSpace(id);
            navigate('/spaces');
        } catch (err) {
            console.error('Failed to delete space:', err);
            alert('Failed to delete space. Please try again.');
        }
    };

    const handleUpdate = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!id || !editName.trim()) return;

        setIsSaving(true);
        try {
            const updated = await updateSpace(id, editName, editDescription);
            setSpace(updated);
            setIsEditing(false);
        } catch (err) {
            console.error('Failed to update space:', err);
            alert('Failed to update space.');
        } finally {
            setIsSaving(false);
        }
    };

    const handleDeleteItem = async (itemId: string, e: React.MouseEvent) => {
        e.stopPropagation(); // Prevent card click
        if (!id || !window.confirm('Delete this item?')) return;

        try {
            await deleteItem(id, itemId);
            // Refresh items
            const updatedItems = await getSpaceItems(id);
            setItems(updatedItems);
            // Update space item count locally
            if (space) {
                setSpace({ ...space, itemCount: Math.max(0, space.itemCount - 1) });
            }
        } catch (err) {
            console.error('Failed to delete item:', err);
            alert('Failed to delete item.');
        }
    };

    const handleSearch = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!id || !searchQuery.trim()) return;

        setIsSearching(true);
        try {
            const response = await searchSpace(id, searchQuery);
            setSearchResults(response.results);
        } catch (err) {
            console.error('Search failed:', err);
            setSearchResults([]);
        } finally {
            setIsSearching(false);
        }
    };

    const clearSearch = () => {
        setSearchQuery('');
        setSearchResults(null);
    };

    if (isLoading) {
        return (
            <div className="min-h-screen bg-x402-white flex justify-center items-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-black"></div>
            </div>
        );
    }

    if (error || !space) {
        return (
            <div className="min-h-screen bg-x402-white p-6 flex flex-col items-center justify-center">
                <div className="text-red-500 mb-4">{error || 'Space not found'}</div>
                <button
                    onClick={() => navigate('/spaces')}
                    className="text-black hover:underline"
                >
                    Back to Spaces
                </button>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-x402-white">
            {/* Navigation */}
            <nav className="bg-black border-b border-gray-800">
                <div className="max-w-7xl mx-auto px-6 py-4">
                    <div className="flex items-center justify-between">
                        <h1
                            className="text-xl font-bold text-white cursor-pointer"
                            onClick={() => navigate('/')}
                        >
                            con.ai
                        </h1>
                        <div className="flex items-center gap-4">
                            <button
                                onClick={() => navigate('/spaces')}
                                className="text-white hover:text-gray-300 transition-all text-sm font-medium"
                            >
                                &larr; Back to Spaces
                            </button>
                        </div>
                    </div>
                </div>
            </nav>

            <main className="max-w-7xl mx-auto px-6 py-12">
                {isEditing ? (
                    <div className="bg-white border text-black border-gray-200 rounded-xl p-6 shadow-sm max-w-2xl mx-auto">
                        <h2 className="text-xl font-bold mb-6">Edit Space</h2>
                        <form onSubmit={handleUpdate} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                                <input
                                    type="text"
                                    value={editName}
                                    onChange={(e) => setEditName(e.target.value)}
                                    className="w-full px-4 py-2 border text-black border-gray-300 rounded-lg focus:ring-2 focus:ring-black outline-none"
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                                <textarea
                                    value={editDescription}
                                    onChange={(e) => setEditDescription(e.target.value)}
                                    className="w-full px-4 py-2 border text-black border-gray-300 rounded-lg focus:ring-2 focus:ring-black outline-none h-24 resize-none"
                                />
                            </div>
                            <div className="flex justify-end gap-3 mt-6">
                                <button
                                    type="button"
                                    onClick={() => setIsEditing(false)}
                                    className="px-4 py-2 text-gray-600 hover:text-gray-900"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    disabled={isSaving}
                                    className="px-6 py-2 bg-black text-white rounded-lg hover:bg-gray-800 disabled:opacity-50"
                                >
                                    {isSaving ? 'Saving...' : 'Save Changes'}
                                </button>
                            </div>
                        </form>
                    </div>
                ) : (
                    <>
                        <div className="bg-white border border-gray-200 rounded-xl p-8 mb-8 shadow-sm">
                            <div className="flex justify-between items-start mb-4">
                                <div>
                                    <h1 className="text-4xl font-bold text-gray-900 mb-2">{space.name}</h1>
                                    <p className="text-xl text-gray-500">{space.description || "No description provided."}</p>
                                </div>
                                <div className="flex gap-2">
                                    <button
                                        onClick={() => setIsEditing(true)}
                                        className="p-2 text-gray-400 hover:text-black transition-colors rounded-lg hover:bg-gray-50"
                                        title="Edit Space"
                                    >
                                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                                        </svg>
                                    </button>
                                    <button
                                        onClick={handleDelete}
                                        className="p-2 text-gray-400 hover:text-red-600 transition-colors rounded-lg hover:bg-red-50"
                                        title="Delete Space"
                                    >
                                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                        </svg>
                                    </button>
                                </div>
                            </div>
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-4 text-sm text-gray-400">
                                    <div className="flex items-center">
                                        <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                        </svg>
                                        Created {new Date(space.createdAt).toLocaleDateString()}
                                    </div>
                                    <div className="flex items-center">
                                        <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                                        </svg>
                                        {space.itemCount} items
                                    </div>
                                </div>
                                <button
                                    onClick={() => setIsAddContentOpen(true)}
                                    className="bg-black text-white px-4 py-2 rounded-lg hover:bg-gray-800 transition-colors font-medium flex items-center gap-2"
                                >
                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                                    </svg>
                                    Add Content
                                </button>
                            </div>
                        </div>

                        {/* Query Interface (RAG) */}
                        {id && <QueryInterface spaceId={id} hasItems={items.length > 0} />}

                        {/* Search Bar */}
                        {items.length > 0 && (
                            <div className="mb-6">
                                <form onSubmit={handleSearch} className="flex gap-2">
                                    <div className="relative flex-1">
                                        <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                                        </svg>
                                        <input
                                            type="text"
                                            value={searchQuery}
                                            onChange={(e) => setSearchQuery(e.target.value)}
                                            className="w-full pl-10 pr-10 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-black outline-none transition-all text-gray-900"
                                            placeholder="Search within this space..."
                                        />
                                        {searchQuery && (
                                            <button
                                                type="button"
                                                onClick={clearSearch}
                                                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                                            >
                                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                                </svg>
                                            </button>
                                        )}
                                    </div>
                                    <button
                                        type="submit"
                                        disabled={isSearching || !searchQuery.trim()}
                                        className="px-6 py-3 bg-black text-white rounded-lg hover:bg-gray-800 disabled:opacity-50 transition-colors font-medium flex items-center gap-2"
                                    >
                                        {isSearching ? (
                                            <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                                        ) : (
                                            'Search'
                                        )}
                                    </button>
                                </form>
                            </div>
                        )}

                        {/* Search Results */}
                        {searchResults !== null ? (
                            <div>
                                <div className="flex items-center justify-between mb-4">
                                    <h3 className="text-lg font-semibold text-gray-900">
                                        {searchResults.length} result{searchResults.length !== 1 ? 's' : ''} for "{searchQuery}"
                                    </h3>
                                    <button onClick={clearSearch} className="text-sm text-gray-500 hover:text-black">
                                        Clear search
                                    </button>
                                </div>
                                {searchResults.length === 0 ? (
                                    <div className="bg-gray-50 border border-dashed border-gray-200 rounded-xl p-8 text-center">
                                        <p className="text-gray-500">No matching items found.</p>
                                    </div>
                                ) : (
                                    <div className="space-y-4">
                                        {searchResults.map((item) => (
                                            <div key={item.id} className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-md transition-shadow group relative">
                                                <div className="absolute top-3 right-3 bg-green-100 text-green-700 text-xs px-2 py-1 rounded-full font-medium">
                                                    {Math.round(item.score * 100)}% match
                                                </div>
                                                <div className="flex items-start gap-4">
                                                    <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 ${item.type === 'message' ? 'bg-blue-50 text-blue-600' : 'bg-green-50 text-green-600'
                                                        }`}>
                                                        {item.type === 'message' ? (
                                                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                                                            </svg>
                                                        ) : (
                                                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                                            </svg>
                                                        )}
                                                    </div>
                                                    <div className="flex-1">
                                                        {item.type === 'message' ? (
                                                            <p className="text-gray-900 whitespace-pre-wrap">{item.content}</p>
                                                        ) : (
                                                            <span className="text-gray-900 font-medium">{item.metadata?.original_name || item.content}</span>
                                                        )}
                                                        <div className="text-xs text-gray-400 mt-2">
                                                            {new Date(item.createdAt).toLocaleString()}
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        ) : items.length === 0 ? (
                            <div className="bg-gray-50 border border-gray-100 border-dashed rounded-xl p-12 text-center">
                                <div className="text-4xl mb-4 text-gray-300">📝</div>
                                <h3 className="text-lg font-medium text-gray-900 mb-1">No content yet</h3>
                                <p className="text-gray-500 mb-6">
                                    Save messages or upload files to this space.
                                </p>
                                <button
                                    onClick={() => setIsAddContentOpen(true)}
                                    className="text-black font-medium hover:underline"
                                >
                                    Add content
                                </button>
                            </div>
                        ) : (
                            <div className="space-y-4">
                                {items.map((item) => (
                                    <div key={item.id} className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-md transition-shadow group">
                                        <div className="flex items-start justify-between">
                                            <div className="flex items-start gap-4 flex-1">
                                                <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 ${item.type === 'message' ? 'bg-blue-50 text-blue-600' : 'bg-green-50 text-green-600'
                                                    }`}>
                                                    {item.type === 'message' ? (
                                                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                                                        </svg>
                                                    ) : (
                                                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                                        </svg>
                                                    )}
                                                </div>
                                                <div className="space-y-2 flex-1">
                                                    {item.type === 'message' ? (
                                                        <p className="text-gray-900 text-lg whitespace-pre-wrap">{item.content}</p>
                                                    ) : (
                                                        <div>
                                                            <div className="flex items-center gap-2 mb-1">
                                                                <span className="text-gray-900 font-medium">{item.metadata?.original_name || item.content}</span>
                                                                <span className="text-xs px-2 py-0.5 bg-gray-100 text-gray-500 rounded-full uppercase">
                                                                    {item.metadata?.original_name?.split('.').pop() || 'FILE'}
                                                                </span>
                                                            </div>
                                                            {item.metadata?.size_bytes && (
                                                                <p className="text-xs text-gray-400">
                                                                    {(item.metadata.size_bytes / 1024).toFixed(1)} KB
                                                                </p>
                                                            )}
                                                        </div>
                                                    )}

                                                    {item.notes && (
                                                        <div className="bg-gray-50 px-3 py-2 rounded-lg text-sm text-gray-600 italic border border-gray-100 inline-block">
                                                            "{item.notes}"
                                                        </div>
                                                    )}

                                                    <div className="text-xs text-gray-400 pt-1">
                                                        {new Date(item.createdAt).toLocaleString()}
                                                    </div>
                                                </div>
                                            </div>

                                            <button
                                                onClick={(e) => handleDeleteItem(item.id, e)}
                                                className="text-gray-400 hover:text-red-500 opacity-0 group-hover:opacity-100 transition duration-200"
                                                title="Delete Item"
                                            >
                                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                                </svg>
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}

                        {isAddContentOpen && id && (
                            <AddContentModal
                                isOpen={isAddContentOpen}
                                onClose={() => setIsAddContentOpen(false)}
                                spaceId={id}
                                onSuccess={() => fetchSpaceAndItems(id)}
                            />
                        )}
                    </>
                )}
            </main>
        </div>
    );
}
