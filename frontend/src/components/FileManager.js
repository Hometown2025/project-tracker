import React, { useState } from 'react';
import FileUpload from './FileUpload';
import FileList from './FileList';
import { useAuth } from '../AuthContext';

const FileManager = ({ projectId, taskId, title = "Files" }) => {
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const { canCreate } = useAuth();

  const handleUploadComplete = (results) => {
    // Refresh the file list
    setRefreshTrigger(prev => prev + 1);
    
    // Show success message
    const fileCount = results.length;
    const message = fileCount === 1 
      ? `File "${results[0].filename}" uploaded successfully`
      : `${fileCount} files uploaded successfully`;
    
    // You could show a toast notification here if you want
    console.log(message);
  };

  const handleUploadError = (error) => {
    const message = error.response?.data?.detail || 'Failed to upload file(s)';
    alert(message);
  };

  return (
    <div className="file-manager">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
        
        {canCreate() && (
          <div className="mb-6">
            <FileUpload
              projectId={projectId}
              taskId={taskId}
              onUploadComplete={handleUploadComplete}
              onUploadError={handleUploadError}
            />
          </div>
        )}
        
        <FileList
          projectId={projectId}
          taskId={taskId}
          refreshTrigger={refreshTrigger}
        />
      </div>
    </div>
  );
};

export default FileManager;