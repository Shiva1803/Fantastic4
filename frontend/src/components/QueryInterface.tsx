import { useState, useEffect } from 'react';
import { askQuestion, getQueryHistory, QueryRecord } from '../api/query';

interface QueryInterfaceProps {
    spaceId: string;
    hasItems: boolean;
}

export default function QueryInterface({ spaceId, hasItems }: QueryInterfaceProps) {
    const [question, setQuestion] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [currentAnswer, setCurrentAnswer] = useState<QueryRecord | null>(null);
    const [history, setHistory] = useState<QueryRecord[]>([]);
    const [error, setError] = useState<string | null>(null);
    const [showHistory, setShowHistory] = useState(false);

    useEffect(() => {
        if (spaceId) {
            fetchHistory();
        }
    }, [spaceId]);

    const fetchHistory = async () => {
        try {
            const queries = await getQueryHistory(spaceId);
            setHistory(queries);
        } catch (err) {
            console.error('Failed to fetch query history:', err);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!question.trim() || isLoading) return;

        setIsLoading(true);
        setError(null);
        setCurrentAnswer(null);

        try {
            const result = await askQuestion(spaceId, question);
            setCurrentAnswer(result);
            setQuestion('');
            // Refresh history
            fetchHistory();
        } catch (err: any) {
            setError(err.message || 'Failed to get answer');
        } finally {
            setIsLoading(false);
        }
    };

    if (!hasItems) return null;

    return (
        <div className="bg-white border border-gray-200 rounded-xl p-6 mb-6 shadow-sm">
            <div className="flex items-center gap-3 mb-4">
                <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                    <svg className="w-4 h-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                </div>
                <h3 className="text-lg font-semibold text-gray-900">Ask a Question</h3>
            </div>

            <form onSubmit={handleSubmit} className="flex gap-2 mb-4">
                <input
                    type="text"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition-all text-gray-900"
                    placeholder="Ask anything about your saved content..."
                    disabled={isLoading}
                />
                <button
                    type="submit"
                    disabled={isLoading || !question.trim()}
                    className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 transition-colors font-medium flex items-center gap-2 shrink-0"
                >
                    {isLoading ? (
                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                    ) : (
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
                    )}
                    {isLoading ? 'Thinking...' : 'Ask'}
                </button>
            </form>

            {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4 text-red-700 text-sm">
                    {error}
                </div>
            )}

            {/* Current Answer */}
            {currentAnswer && (
                <div className="bg-purple-50 border border-purple-200 rounded-xl p-5 mb-4">
                    <div className="text-sm font-medium text-purple-800 mb-2">
                        Q: {currentAnswer.question}
                    </div>
                    <div className="text-gray-900 whitespace-pre-wrap leading-relaxed">
                        {currentAnswer.answer}
                    </div>

                    {/* Source References */}
                    {currentAnswer.sources && currentAnswer.sources.length > 0 && (
                        <div className="mt-4 pt-3 border-t border-purple-200">
                            <div className="text-xs font-medium text-purple-700 mb-2">
                                Sources ({currentAnswer.sources.length})
                            </div>
                            <div className="flex flex-wrap gap-2">
                                {currentAnswer.sources.map((source, i) => (
                                    <div
                                        key={i}
                                        className="bg-white border border-purple-200 rounded-lg px-3 py-2 text-xs flex items-center gap-2"
                                    >
                                        <span className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${source.type === 'message' ? 'bg-blue-100 text-blue-600' : 'bg-green-100 text-green-600'
                                            }`}>
                                            {source.type === 'message' ? 'M' : 'F'}
                                        </span>
                                        <span className="text-gray-700 max-w-[200px] truncate">
                                            {source.content}
                                        </span>
                                        <span className="text-purple-500 font-medium">
                                            {Math.round(source.score * 100)}%
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}

            {/* Query History Toggle */}
            {history.length > 0 && (
                <div>
                    <button
                        onClick={() => setShowHistory(!showHistory)}
                        className="text-sm text-gray-500 hover:text-gray-700 flex items-center gap-1"
                    >
                        <svg className={`w-4 h-4 transition-transform ${showHistory ? 'rotate-90' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                        Past queries ({history.length})
                    </button>

                    {showHistory && (
                        <div className="mt-3 space-y-3">
                            {history.map((q) => (
                                <div
                                    key={q.id}
                                    className="border border-gray-100 rounded-lg p-4 hover:bg-gray-50 cursor-pointer transition-colors"
                                    onClick={() => setCurrentAnswer(q)}
                                >
                                    <div className="text-sm font-medium text-gray-900 mb-1">
                                        Q: {q.question}
                                    </div>
                                    <div className="text-sm text-gray-500 line-clamp-2">
                                        {q.answer}
                                    </div>
                                    <div className="text-xs text-gray-400 mt-1">
                                        {new Date(q.createdAt).toLocaleString()}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
