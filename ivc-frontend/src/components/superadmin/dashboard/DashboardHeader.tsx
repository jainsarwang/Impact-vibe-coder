
import React from 'react';
import { Button } from '@/components/ui/button';
import { LogOut, Shield } from 'lucide-react';

interface DashboardHeaderProps {
  onLogout: () => void;
}

const DashboardHeader = ({ onLogout }: DashboardHeaderProps) => {
  return (
    <header className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 py-3">
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-lg flex items-center justify-center">
              <Shield className="w-4 h-4 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-gray-900">Super Admin Dashboard</h1>
              <p className="text-xs text-gray-600">Manage organizations and administrators</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <Button 
              onClick={onLogout}
              variant="outline"
              size="sm" 
              className="hover:bg-red-50 hover:border-red-300 hover:text-red-700 text-sm h-8 px-3"
            >
              <LogOut className="w-3 h-3 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default DashboardHeader;
