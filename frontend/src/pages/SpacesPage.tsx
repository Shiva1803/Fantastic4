import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { getSpaces } from '../api/spaces';
import { globalSearch, GlobalSearchResult } from '../api/globalSearch';
import { Space } from '../types';
import CreateSpaceModal from '../components/CreateSpaceModal';

export default function SpacesPage() {
    const navigate = useNavigate();
    const [spaces, setSpaces] = useState<Space[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Global search
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState<GlobalSearchResult[] | null>(null);
    const [isSearching, setIsSearching] = useState(false);

    const USER_ID = "user123";

    const fetchSpaces = async () => {
        setIsLoading(true);
        try {
            const data = await getSpaces(USER_ID);
            setSpaces(data);
            setError(null);
        } catch (err) {
            console.error('Failed to fetch spaces:', err);
            setError('Failed to load spaces. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchSpaces();
    }, []);

    // Keyboard shortcut: Cmd/Ctrl + K to focus search
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
                e.preventDefault();
                const searchInput = document.getElementById('global-search-input');
                searchInput?.focus();
            }
            if (e.key === 'Escape') {
                clearSearch();
            }
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, []);

    const handleSearch = useCallback(async (e: React.FormEvent) => {
        e.preventDefault();
        if (!searchQuery.trim()) return;

        setIsSearching(true);
        try {
            const response = await globalSearch(USER_ID, searchQuery);
            setSearchResults(response.results);
        } catch (err) {
            console.error('Search failed:', err);
            setSearchResults([]);
        } finally {
            setIsSearching(false);
        }
    }, [searchQuery]);

    const clearSearch = () => {
        setSearchQuery('');
        setSearchResults(null);
    };

    const handleSpaceClick = (spaceId: string) => {
        navigate(`/spaces/${spaceId}`);
    };

    const handleCreateSuccess = () => {
        fetchSpaces();
        setIsModalOpen(false);
    };

    // Loading skeleton component
    const SkeletonCard = () => (
        <div className="bg-white border border-gray-200 rounded-xl p-6 animate-pulse">
            <div className="flex justify-between items-start mb-4">
                <div className="w-12 h-12 bg-gray-200 rounded-lg"></div>
                <div className="w-20 h-3 bg-gray-200 rounded"></div>
            </div>
            <div className="h-5 bg-gray-200 rounded w-3/4 mb-3"></div>
            <div className="h-3 bg-gray-200 rounded w-full mb-2"></div>
            <div className="h-3 bg-gray-200 rounded w-2/3 mb-4"></div>
            <div className="h-3 bg-gray-200 rounded w-1/4"></div>
        </div>
    );

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
                                onClick={() => navigate('/')}
                                className="text-gray-400 hover:text-white transition-all text-sm font-medium"
                            >
                                ← Home
                            </button>
                            <button
                                onClick={() => navigate('/spaces')}
                                className="text-white hover:text-gray-300 transition-all text-sm font-medium"
                            >
                                Spaces
                            </button>
                        </div>
                    </div>
                </div>
            </nav>

            <main className="max-w-7xl mx-auto px-6 py-12">
                <div className="flex items-center justify-between mb-8">
                    <h2 className="text-3xl font-bold text-x402-text-primary">My Spaces</h2>
                    <button
                        onClick={() => setIsModalOpen(true)}
                        className="bg-black text-white px-6 py-3 rounded-lg hover:bg-gray-800 transition-colors font-medium flex items-center gap-2"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                        </svg>
                        Create Space
                    </button>
                </div>

                {/* Global Search Bar */}
                <div className="mb-8">
                    <form onSubmit={handleSearch} className="flex gap-2">
                        <div className="relative flex-1">
                            <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                            </svg>
                            <input
                                id="global-search-input"
                                type="text"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="w-full pl-10 pr-20 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-black outline-none transition-all text-gray-900"
                                placeholder="Search across all spaces..."
                            />
                            <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-2">
                                {searchQuery && (
                                    <button
                                        type="button"
                                        onClick={clearSearch}
                                        className="text-gray-400 hover:text-gray-600"
                                    >
                                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                        </svg>
                                    </button>
                                )}
                                <kbd className="hidden sm:inline-flex items-center text-xs text-gray-400 border border-gray-300 rounded px-1.5 py-0.5 font-mono">
                                    ⌘K
                                </kbd>
                            </div>
                        </div>
                        <button
                            type="submit"
                            disabled={isSearching || !searchQuery.trim()}
                            className="px-6 py-3 bg-black text-white rounded-lg hover:bg-gray-800 disabled:opacity-50 transition-colors font-medium flex items-center gap-2 shrink-0"
                        >
                            {isSearching ? (
                                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                            ) : (
                                'Search'
                            )}
                        </button>
                    </form>
                </div>

                {/* Global Search Results */}
                {searchResults !== null ? (
                    <div className="mb-8">
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
                                <div className="text-3xl mb-3">🔍</div>
                                <p className="text-gray-500">No matching items found across your spaces.</p>
                            </div>
                        ) : (
                            <div className="space-y-3">
                                {searchResults.map((item) => (
                                    <div
                                        key={item.id}
                                        className="bg-white border border-gray-200 rounded-xl p-5 hover:shadow-md transition-shadow cursor-pointer group"
                                        onClick={() => navigate(`/spaces/${item.spaceId}`)}
                                    >
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
                                            <div className="flex-1 min-w-0">
                                                <div className="flex items-center gap-2 mb-1">
                                                    <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full font-medium">
                                                        {item.spaceName}
                                                    </span>
                                                    <span className="text-xs text-green-600 font-medium">
                                                        {Math.round(item.score * 100)}% match
                                                    </span>
                                                </div>
                                                <p className="text-gray-900 truncate">
                                                    {item.type === 'message' ? item.content : (item.metadata?.original_name || item.content)}
                                                </p>
                                                <p className="text-xs text-gray-400 mt-1">
                                                    {new Date(item.createdAt).toLocaleString()}
                                                </p>
                                            </div>
                                            <svg className="w-5 h-5 text-gray-300 group-hover:text-gray-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                            </svg>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                ) : isLoading ? (
                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                        <SkeletonCard />
                        <SkeletonCard />
                        <SkeletonCard />
                        <SkeletonCard />
                        <SkeletonCard />
                        <SkeletonCard />
                    </div>
                ) : error ? (
                    <div className="bg-red-50 text-red-600 p-4 rounded-lg">
                        {error}
                    </div>
                ) : spaces.length === 0 ? (
                    <div className="text-center py-20 bg-gray-50 rounded-2xl border border-gray-100">
                        <div className="text-5xl mb-4">📂</div>
                        <h3 className="text-xl font-bold text-gray-900 mb-2">No spaces yet</h3>
                        <p className="text-gray-500 mb-6">Create your first space to start organizing conversations.</p>
                        <button
                            onClick={() => setIsModalOpen(true)}
                            className="text-black font-medium hover:underline"
                        >
                            Create a space
                        </button>
                    </div>
                ) : (
                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {spaces.map((space) => (
                            <div
                                key={space.id}
                                onClick={() => handleSpaceClick(space.id)}
                                className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-lg transition-all cursor-pointer group"
                            >
                                <div className="flex justify-between items-start mb-4">
                                    <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center text-2xl group-hover:bg-black group-hover:text-white transition-colors">
                                        #
                                    </div>
                                    <span className="text-xs font-mono text-gray-400">
                                        {new Date(space.updatedAt).toLocaleDateString()}
                                    </span>
                                </div>
                                <h3 className="text-xl font-bold text-gray-900 mb-2 group-hover:text-blue-600 transition-colors">
                                    {space.name}
                                </h3>
                                <p className="text-gray-500 text-sm line-clamp-2 mb-4 h-10">
                                    {space.description || "No description"}
                                </p>
                                <div className="flex items-center text-xs text-gray-400 font-medium">
                                    <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                                    </svg>
                                    {space.itemCount} items
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </main>

            {isModalOpen && (
                <CreateSpaceModal
                    isOpen={isModalOpen}
                    onClose={() => setIsModalOpen(false)}
                    onSuccess={handleCreateSuccess}
                />
            )}
        </div>
    );
}
