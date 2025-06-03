
import React, { useState } from 'react';
import { X, Save, FolderOpen, File, ChevronRight, ChevronDown, Settings, Search, GitBranch } from 'lucide-react';
import { FileStatus } from './ProjectBuilder';

interface VSCodeEditorProps {
  files: FileStatus[];
  onClose: () => void;
  onSave?: (fileName: string, content: string) => void;
}

interface FileTreeNode {
  name: string;
  type: 'file' | 'folder';
  children?: FileTreeNode[];
  file?: FileStatus;
}

const VSCodeEditor = ({ files, onClose, onSave }: VSCodeEditorProps) => {
  const [activeFile, setActiveFile] = useState<FileStatus | null>(files[0] || null);
  const [openTabs, setOpenTabs] = useState<FileStatus[]>(files.slice(0, 3));
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set(['src']));
  const [fileContents, setFileContents] = useState<Map<string, string>>(
    new Map(files.map(file => [file.name, file.content || '']))
  );

  // Build file tree from flat file list
  const buildFileTree = (files: FileStatus[]): FileTreeNode[] => {
    const tree: FileTreeNode[] = [];
    const folders = new Map<string, FileTreeNode>();

    files.forEach(file => {
      const parts = file.name.split('/');
      let currentPath = '';
      let currentLevel = tree;

      parts.forEach((part, index) => {
        const isFile = index === parts.length - 1;
        currentPath = currentPath ? `${currentPath}/${part}` : part;

        if (isFile) {
          currentLevel.push({
            name: part,
            type: 'file',
            file
          });
        } else {
          let folder = folders.get(currentPath);
          if (!folder) {
            folder = {
              name: part,
              type: 'folder',
              children: []
            };
            folders.set(currentPath, folder);
            currentLevel.push(folder);
          }
          currentLevel = folder.children!;
        }
      });
    });

    return tree;
  };

  const fileTree = buildFileTree(files);

  const toggleFolder = (folderName: string) => {
    const newExpanded = new Set(expandedFolders);
    if (newExpanded.has(folderName)) {
      newExpanded.delete(folderName);
    } else {
      newExpanded.add(folderName);
    }
    setExpandedFolders(newExpanded);
  };

  const openFile = (file: FileStatus) => {
    setActiveFile(file);
    if (!openTabs.find(tab => tab.name === file.name)) {
      setOpenTabs(prev => [...prev, file]);
    }
  };

  const closeTab = (file: FileStatus) => {
    const newTabs = openTabs.filter(tab => tab.name !== file.name);
    setOpenTabs(newTabs);
    if (activeFile?.name === file.name) {
      setActiveFile(newTabs[0] || null);
    }
  };

  const handleContentChange = (content: string) => {
    if (activeFile) {
      setFileContents(prev => new Map(prev.set(activeFile.name, content)));
    }
  };

  const handleSave = () => {
    if (activeFile && onSave) {
      const content = fileContents.get(activeFile.name) || '';
      onSave(activeFile.name, content);
    }
  };

  const renderFileTreeNode = (node: FileTreeNode, depth = 0): React.ReactNode => {
    if (node.type === 'folder') {
      const isExpanded = expandedFolders.has(node.name);
      return (
        <div key={node.name}>
          <div
            className="flex items-center px-2 py-1 hover:bg-slate-700 cursor-pointer"
            style={{ paddingLeft: `${depth * 12 + 8}px` }}
            onClick={() => toggleFolder(node.name)}
          >
            {isExpanded ? (
              <ChevronDown className="w-4 h-4 mr-1 text-slate-400" />
            ) : (
              <ChevronRight className="w-4 h-4 mr-1 text-slate-400" />
            )}
            <FolderOpen className="w-4 h-4 mr-2 text-blue-400" />
            <span className="text-sm text-slate-200">{node.name}</span>
          </div>
          {isExpanded && node.children?.map(child => renderFileTreeNode(child, depth + 1))}
        </div>
      );
    }

    return (
      <div
        key={node.name}
        className={`flex items-center px-2 py-1 hover:bg-slate-700 cursor-pointer ${
          activeFile?.name === node.file?.name ? 'bg-slate-600' : ''
        }`}
        style={{ paddingLeft: `${depth * 12 + 24}px` }}
        onClick={() => node.file && openFile(node.file)}
      >
        <File className="w-4 h-4 mr-2 text-slate-400" />
        <span className="text-sm text-slate-200">{node.name}</span>
      </div>
    );
  };

  return (
    <div className="fixed inset-0 bg-slate-900 z-50 flex flex-col">
      {/* Title Bar */}
      <div className="h-8 bg-slate-800 flex items-center justify-between px-2 border-b border-slate-700">
        <div className="flex items-center space-x-2">
          <div className="flex space-x-1">
            <div className="w-3 h-3 bg-red-500 rounded-full"></div>
            <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
          </div>
          <span className="text-sm text-slate-300 ml-4">Impact Vibe Coder - VS Code Editor</span>
        </div>
        <button
          onClick={onClose}
          className="text-slate-400 hover:text-white p-1"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Menu Bar */}
      <div className="h-8 bg-slate-800 flex items-center px-4 text-sm text-slate-300 border-b border-slate-700">
        <span className="hover:bg-slate-700 px-2 py-1 rounded cursor-pointer">File</span>
        <span className="hover:bg-slate-700 px-2 py-1 rounded cursor-pointer">Edit</span>
        <span className="hover:bg-slate-700 px-2 py-1 rounded cursor-pointer">View</span>
        <span className="hover:bg-slate-700 px-2 py-1 rounded cursor-pointer">Go</span>
        <span className="hover:bg-slate-700 px-2 py-1 rounded cursor-pointer">Terminal</span>
        <span className="hover:bg-slate-700 px-2 py-1 rounded cursor-pointer">Help</span>
      </div>

      <div className="flex flex-1">
        {/* Activity Bar */}
        <div className="w-12 bg-slate-800 flex flex-col items-center py-2 border-r border-slate-700">
          <div className="p-2 text-blue-400 bg-slate-700 rounded">
            <FolderOpen className="w-6 h-6" />
          </div>
          <div className="p-2 text-slate-400 hover:text-white cursor-pointer">
            <Search className="w-6 h-6" />
          </div>
          <div className="p-2 text-slate-400 hover:text-white cursor-pointer">
            <GitBranch className="w-6 h-6" />
          </div>
          <div className="p-2 text-slate-400 hover:text-white cursor-pointer">
            <Settings className="w-6 h-6" />
          </div>
        </div>

        {/* Side Panel */}
        <div className="w-64 bg-slate-800 border-r border-slate-700 flex flex-col">
          <div className="p-3 border-b border-slate-700">
            <h3 className="text-sm font-medium text-slate-200 uppercase tracking-wide">Explorer</h3>
          </div>
          <div className="flex-1 overflow-y-auto">
            <div className="py-2">
              <div className="px-3 py-1 text-xs font-medium text-slate-400 uppercase tracking-wide">
                Project Files
              </div>
              {fileTree.map(node => renderFileTreeNode(node))}
            </div>
          </div>
        </div>

        {/* Editor Area */}
        <div className="flex-1 flex flex-col">
          {/* Tabs */}
          <div className="flex bg-slate-800 border-b border-slate-700 overflow-x-auto">
            {openTabs.map(tab => (
              <div
                key={tab.name}
                className={`flex items-center px-3 py-2 border-r border-slate-700 cursor-pointer min-w-0 ${
                  activeFile?.name === tab.name ? 'bg-slate-900 text-white' : 'text-slate-300 hover:bg-slate-700'
                }`}
                onClick={() => setActiveFile(tab)}
              >
                <File className="w-4 h-4 mr-2 flex-shrink-0" />
                <span className="text-sm truncate">{tab.name.split('/').pop()}</span>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    closeTab(tab);
                  }}
                  className="ml-2 p-1 hover:bg-slate-600 rounded flex-shrink-0"
                >
                  <X className="w-3 h-3" />
                </button>
              </div>
            ))}
          </div>

          {/* Editor Content */}
          <div className="flex-1 flex flex-col">
            {activeFile ? (
              <>
                {/* Editor Header */}
                <div className="flex items-center justify-between p-2 bg-slate-800 border-b border-slate-700">
                  <div className="flex items-center space-x-2">
                    <File className="w-4 h-4 text-slate-400" />
                    <span className="text-sm text-slate-200">{activeFile.name}</span>
                  </div>
                  <button
                    onClick={handleSave}
                    className="flex items-center space-x-1 px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded"
                  >
                    <Save className="w-4 h-4" />
                    <span>Save</span>
                  </button>
                </div>

                {/* Editor */}
                <div className="flex-1 relative">
                  <textarea
                    value={fileContents.get(activeFile.name) || ''}
                    onChange={(e) => handleContentChange(e.target.value)}
                    className="w-full h-full p-4 bg-slate-900 text-slate-200 font-mono text-sm resize-none focus:outline-none"
                    spellCheck={false}
                    placeholder="// Start editing your file..."
                  />
                  
                  {/* Line numbers */}
                  <div className="absolute left-0 top-0 w-12 h-full bg-slate-800 border-r border-slate-700 p-4">
                    {(fileContents.get(activeFile.name) || '').split('\n').map((_, index) => (
                      <div key={index} className="text-xs text-slate-500 leading-5 text-right">
                        {index + 1}
                      </div>
                    ))}
                  </div>
                </div>
              </>
            ) : (
              <div className="flex-1 flex items-center justify-center text-slate-400">
                <div className="text-center">
                  <File className="w-16 h-16 mx-auto mb-4 opacity-50" />
                  <p className="text-lg">Select a file to start editing</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Status Bar */}
      <div className="h-6 bg-blue-600 flex items-center justify-between px-4 text-xs text-white">
        <div className="flex items-center space-x-4">
          <span>TypeScript React</span>
          <span>UTF-8</span>
          <span>LF</span>
        </div>
        <div className="flex items-center space-x-4">
          <span>Ln {activeFile ? 1 : 0}, Col 1</span>
          <span>Impact Vibe Coder</span>
        </div>
      </div>
    </div>
  );
};

export default VSCodeEditor;
