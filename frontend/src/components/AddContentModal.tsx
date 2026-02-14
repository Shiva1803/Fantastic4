import { useState, useRef } from 'react';
import { saveMessage, uploadFile } from '../api/content';

interface AddContentModalProps {
    isOpen: boolean;
    onClose: () => void;
    spaceId: string;
    onSuccess: () => void;
}

type ContentType = 'message' | 'file';

export default function AddContentModal({ isOpen, onClose, spaceId, onSuccess }: AddContentModalProps) {
    const [activeTab, setActiveTab] = useState<ContentType>('message');
    const [content, setContent] = useState('');
    const [notes, setNotes] = useState('');
    const [file, setFile] = useState<File | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const fileInputRef = useRef<HTMLInputElement>(null);

    if (!isOpen) return null;

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setIsLoading(true);

        try {
            if (activeTab === 'message') {
                if (!content.trim()) {
                    throw new Error('Message content is required');
                }
                await saveMessage(spaceId, content, notes);
            } else {
                if (!file) {
                    throw new Error('Please select a file');
                }
                await uploadFile(spaceId, file, notes);
            }

            // Reset form
            setContent('');
            setNotes('');
            setFile(null);
            onSuccess();
            onClose();
        } catch (err: any) {
            console.error('Failed to save content:', err);
            setError(err.message || 'Failed to save content');
        } finally {
            setIsLoading(false);
        }
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const selectedFile = e.target.files[0];
            // Simple client-side validation
            if (selectedFile.size > 10 * 1024 * 1024) {
                setError('File size must be less than 10MB');
                return;
            }
            setFile(selectedFile);
            setError(null);
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-black/50 backdrop-blur-sm"
                onClick={onClose}
            ></div>

            {/* Modal */}
            <div className="relative bg-white rounded-2xl w-full max-w-lg p-6 shadow-2xl transform transition-all animate-fade-in">
                <div className="flex justify-between items-center mb-6">
                    <h3 className="text-xl font-bold text-gray-900">Add to Space</h3>
                    <button
                        onClick={onClose}
                        className="text-gray-400 hover:text-gray-600 transition-colors"
                    >
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                {/* Tabs */}
                <div className="flex border-b border-gray-200 mb-6">
                    <button
                        className={`pb-3 px-4 font-medium text-sm transition-colors relative ${activeTab === 'message'
                                ? 'text-black'
                                : 'text-gray-500 hover:text-gray-700'
                            }`}
                        onClick={() => setActiveTab('message')}
                    >
                        Message
                        {activeTab === 'message' && (
                            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-black rounded-t-full"></div>
                        )}
                    </button>
                    <button
                        className={`pb-3 px-4 font-medium text-sm transition-colors relative ${activeTab === 'file'
                                ? 'text-black'
                                : 'text-gray-500 hover:text-gray-700'
                            }`}
                        onClick={() => setActiveTab('file')}
                    >
                        Upload File
                        {activeTab === 'file' && (
                            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-black rounded-t-full"></div>
                        )}
                    </button>
                </div>

                {error && (
                    <div className="mb-4 p-3 bg-red-50 text-red-600 rounded-lg text-sm flex items-center gap-2">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                    {activeTab === 'message' ? (
                        <div>
                            <label htmlFor="content" className="block text-sm font-medium text-gray-700 mb-1">
                                Message Content <span className="text-red-500">*</span>
                            </label>
                            <textarea
                                id="content"
                                value={content}
                                onChange={(e) => setContent(e.target.value)}
                                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-black outline-none transition-all h-32 resize-none"
                                placeholder="Type your message, note, or question here..."
                                required
                            />
                            <p className="text-xs text-gray-400 mt-1 text-right">
                                {content.length} chars
                            </p>
                        </div>
                    ) : (
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Select File <span className="text-red-500">*</span>
                            </label>

                            <div
                                className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${file ? 'border-green-500 bg-green-50' : 'border-gray-300 hover:border-black'
                                    }`}
                                onClick={() => fileInputRef.current?.click()}
                            >
                                <input
                                    type="file"
                                    ref={fileInputRef}
                                    onChange={handleFileChange}
                                    className="hidden"
                                    accept=".pdf,.png,.jpg,.jpeg,.docx,.txt"
                                />

                                {file ? (
                                    <div className="flex flex-col items-center">
                                        <svg className="w-8 h-8 text-green-500 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                        </svg>
                                        <span className="font-medium text-gray-900">{file.name}</span>
                                        <span className="text-xs text-gray-500">{(file.size / 1024).toFixed(1)} KB</span>
                                        <button
                                            type="button"
                                            className="mt-2 text-xs text-red-500 hover:underline"
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                setFile(null);
                                            }}
                                        >
                                            Remove
                                        </button>
                                    </div>
                                ) : (
                                    <div className="flex flex-col items-center text-gray-500">
                                        <svg className="w-8 h-8 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                                        </svg>
                                        <span className="text-sm font-medium">Click to upload</span>
                                        <span className="text-xs mt-1">PDF, PNG, JPG, DOCX, TXT (Max 10MB)</span>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}

                    <div>
                        <label htmlFor="notes" className="block text-sm font-medium text-gray-700 mb-1">
                            Notes <span className="text-gray-400 font-normal">(Optional context)</span>
                        </label>
                        <input
                            type="text"
                            id="notes"
                            value={notes}
                            onChange={(e) => setNotes(e.target.value)}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-black outline-none transition-all"
                            placeholder="Add context about this item..."
                        />
                    </div>

                    <div className="flex justify-end gap-3 mt-6">
                        <button
                            type="button"
                            onClick={onClose}
                            className="px-4 py-2 text-gray-600 hover:text-gray-900 font-medium"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={isLoading || (activeTab === 'message' && !content.trim()) || (activeTab === 'file' && !file)}
                            className="px-6 py-2 bg-black text-white rounded-lg hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium flex items-center gap-2"
                        >
                            {isLoading ? (
                                <>
                                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                                    Saving...
                                </>
                            ) : (
                                'Save Item'
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
