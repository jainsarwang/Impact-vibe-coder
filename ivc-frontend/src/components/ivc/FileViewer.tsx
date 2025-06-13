import React from "react";
import { X, Copy, Download, Code } from "lucide-react";
import { FileStatus } from "@/lib/ivc/types";
import Markdown from "markdown-to-jsx";

interface FileViewerProps {
    file: FileStatus;
    onClose: () => void;
}

const FileViewer = ({ file, onClose }: FileViewerProps) => {
    const copyToClipboard = () => {
        if (file.content) {
            navigator.clipboard.writeText(file.content);
        }
    };

    const downloadFile = () => {
        // Determine MIME type based on file extension
        const extension = file.name.split('.').pop()?.toLowerCase();
        let mimeType = 'text/plain'; // default
        
        // Common MIME types
        const mimeTypes: Record<string, string> = {
            'txt': 'text/plain',
            'html': 'text/html',
            'css': 'text/css',
            'js': 'text/javascript',
            'json': 'application/json',
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'gif': 'image/gif',
            'svg': 'image/svg+xml',
            'pdf': 'application/pdf',
            'md': 'text/markdown',
            'py': 'text/x-python',
            'ts': 'text/typescript',
            'tsx': 'text/tsx',
            'jsx': 'text/jsx',
            'gltf': 'model/gltf+json',
            'glb': 'model/gltf-binary',
            'glsl': 'text/glsl',
            'glslv': 'text/glsl',
            'csv': 'text/csv',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'xls': 'application/vnd.ms-excel',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'ppt': 'application/vnd.ms-powerpoint',
            'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'mp3': 'audio/mpeg',
            'mp4': 'video/mp4',
            'wav': 'audio/wav',
            'ogg': 'audio/ogg',
            'webm': 'video/webm',
            'zip': 'application/zip',
            'rar': 'application/x-rar-compressed',
            '7z': 'application/x-7z-compressed',
            'tar': 'application/x-tar',
            'gz': 'application/gzip',
            'bz2': 'application/x-bzip2',
            'exe': 'application/x-msdownload',
            'dll': 'application/x-msdownload',
            'msi': 'application/x-msdownload',
            'iso': 'application/x-iso9660-image',
            'dmg': 'application/x-apple-diskimage',
            'deb': 'application/x-debian-package',
            'rpm': 'application/x-redhat-package-manager',
            'jar': 'application/java-archive',
            'war': 'application/java-archive',
            'ear': 'application/java-archive',
            'class': 'application/java-archive',
            'java': 'application/java-archive'
        };
        
        if (extension && extension in mimeTypes) {
            mimeType = mimeTypes[extension];
        }

        const blob = new Blob([file.content || ''], { type: mimeType });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = file.name;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
    }

    return (
        <div className="fixed !m-0 inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="relative group w-full max-w-6xl max-h-[85vh]">
                {/* Glow effect */}
                <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-3xl blur opacity-50 group-hover:opacity-75 transition duration-1000"></div>

                <div className="relative bg-slate-900/95 backdrop-blur-lg rounded-3xl border border-white/20 flex flex-col shadow-2xl">
                    {/* Enhanced Header */}
                    <div className="flex items-center justify-between p-6 border-b border-white/20">
                        <div className="flex items-center space-x-4">
                            <div className="p-2 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-lg">
                                <Code className="w-6 h-6 text-white" />
                            </div>
                            <div>
                                <h3 className="text-2xl font-bold text-white">
                                    {file.name}
                                </h3>
                                <p className="text-sm text-blue-200">
                                    Generated file content
                                </p>
                            </div>
                        </div>
                        <div className="flex items-center space-x-3">
                            <button
                                onClick={copyToClipboard}
                                className="p-3 hover:bg-white/20 rounded-xl transition-all duration-300 text-slate-300 hover:text-white group"
                                title="Copy to clipboard"
                            >
                                <Copy className="w-5 h-5 group-hover:scale-110 transition-transform duration-300" />
                            </button>
                            <button
                                className="p-3 hover:bg-white/20 rounded-xl transition-all duration-300 text-slate-300 hover:text-white group"
                                title="Download file"
                            >
                                <Download className="w-5 h-5 group-hover:scale-110 transition-transform duration-300" />
                            </button>
                            <button
                                onClick={onClose}
                                className="p-3 hover:bg-red-500/20 rounded-xl transition-all duration-300 text-slate-300 hover:text-red-300 group"
                            >
                                <X className="w-5 h-5 group-hover:scale-110 transition-transform duration-300" />
                            </button>
                        </div>
                    </div>

                    {/* Enhanced Content */}
                    <div className="flex-1 overflow-auto p-6">
                        <div className="relative">
                            <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 to-indigo-500/10 rounded-2xl"></div>
                            <Markdown className="relative bg-black/50 rounded-2xl p-6 text-sm text-slate-200 font-mono overflow-x-auto border border-white/10 backdrop-blur-sm w-full">
                                {file.content ||
                                    "// File content will appear here..."}
                            </Markdown>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default FileViewer;
