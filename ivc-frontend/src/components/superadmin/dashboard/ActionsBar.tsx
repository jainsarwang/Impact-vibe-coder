
import React from 'react';
import CreateOrganizationDialog from './CreateOrganizationDialog';

interface Credentials {
  username: string;
  password: string;
  organizationName: string;
}

interface ActionsBarProps {
  organizations: any[];
  onOrganizationCreated: (credentials?: Credentials) => void;
}

const ActionsBar = ({ organizations, onOrganizationCreated }: ActionsBarProps) => {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-3 mb-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-base font-semibold text-gray-900 dark:text-white mb-1">Quick Actions</h2>
          <p className="text-xs text-gray-600 dark:text-gray-300">Manage organizations and perform administrative tasks</p>
        </div>
        
        <div className="flex space-x-2">
          <CreateOrganizationDialog 
            onOrganizationCreated={onOrganizationCreated}
            existingOrganizations={organizations}
          />
        </div>
      </div>
    </div>
  );
};

export default ActionsBar;
