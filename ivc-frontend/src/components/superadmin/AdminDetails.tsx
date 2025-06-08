
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/superadmin/ui/card';
import { Button } from '@/components/superadmin/ui/button';
import { Badge } from '@/components/superadmin/ui/badge';
import { ArrowLeft, User, Mail, Phone, Calendar, Eye, MapPin } from 'lucide-react';

interface User {
  id: string;
  name: string;
  email: string;
  phone: string;
  isActive: boolean;
  lastLogin: string;
  location: string;
  joinedDate: string;
  activityScore: number;
}

interface AdminDetailsProps {
  adminId: string;
  onBack: () => void;
  onViewUser: (userId: string) => void;
}

const AdminDetails = ({ adminId, onBack, onViewUser }: AdminDetailsProps) => {
  const [users, setUsers] = useState<User[]>([]);
  const [adminDetails, setAdminDetails] = useState({
    name: `Admin ${adminId.split('-')[2]}`,
    email: `admin${adminId.split('-')[2]}@organization.com`,
    phone: '+1-555-1234',
    role: 'Senior Admin',
    isActive: true,
    joinedDate: '2024-01-15',
    lastLogin: '2024-05-27'
  });

  useEffect(() => {
    // Mock users data
    const mockUsers: User[] = Array.from({ length: Math.floor(Math.random() * 50) + 10 }, (_, i) => ({
      id: `user-${adminId}-${i + 1}`,
      name: `User ${i + 1}`,
      email: `user${i + 1}@organization.com`,
      phone: `+1-555-${String(Math.floor(Math.random() * 9000) + 1000)}`,
      isActive: Math.random() > 0.15,
      lastLogin: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
      location: ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'][Math.floor(Math.random() * 5)],
      joinedDate: new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000).toISOString(),
      activityScore: Math.floor(Math.random() * 100) + 1
    }));
    setUsers(mockUsers);
  }, [adminId]);

  const activeUsers = users.filter(user => user.isActive).length;

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center space-x-4">
            <Button variant="outline" onClick={onBack}>
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Organization
            </Button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{adminDetails.name}</h1>
              <p className="text-sm text-gray-600">Admin Management</p>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Admin Overview */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Admin Overview</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="text-center">
                <p className="text-sm text-gray-600">Status</p>
                <Badge variant={adminDetails.isActive ? "default" : "secondary"} className={adminDetails.isActive ? "bg-green-500" : ""}>
                  {adminDetails.isActive ? "Active" : "Inactive"}
                </Badge>
              </div>
              <div className="text-center">
                <p className="text-sm text-gray-600">Total Users</p>
                <p className="text-2xl font-bold text-blue-600">{users.length}</p>
              </div>
              <div className="text-center">
                <p className="text-sm text-gray-600">Active Users</p>
                <p className="text-2xl font-bold text-green-600">{activeUsers}</p>
              </div>
              <div className="text-center">
                <p className="text-sm text-gray-600">Joined</p>
                <p className="text-lg font-semibold">{new Date(adminDetails.joinedDate).toLocaleDateString()}</p>
              </div>
            </div>
            
            <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="flex items-center space-x-2">
                <Mail className="w-4 h-4 text-gray-400" />
                <span className="text-sm">{adminDetails.email}</span>
              </div>
              <div className="flex items-center space-x-2">
                <Phone className="w-4 h-4 text-gray-400" />
                <span className="text-sm">{adminDetails.phone}</span>
              </div>
              <div className="flex items-center space-x-2">
                <Calendar className="w-4 h-4 text-gray-400" />
                <span className="text-sm">Last login: {new Date(adminDetails.lastLogin).toLocaleDateString()}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Users Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <User className="w-5 h-5 mr-2" />
              Linked Users ({users.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {users.map((user) => (
                <Card key={user.id} className="hover:shadow-lg transition-shadow">
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                          <User className="w-4 h-4 text-purple-600" />
                        </div>
                        <div>
                          <h3 className="font-semibold text-sm">{user.name}</h3>
                          <p className="text-xs text-gray-600">Score: {user.activityScore}</p>
                        </div>
                      </div>
                      <Badge variant={user.isActive ? "default" : "secondary"} className={user.isActive ? "bg-green-500 text-xs" : "text-xs"}>
                        {user.isActive ? "Active" : "Inactive"}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className="flex items-center text-xs">
                        <Mail className="w-3 h-3 mr-2 text-gray-400" />
                        <span className="truncate">{user.email}</span>
                      </div>
                      <div className="flex items-center text-xs">
                        <Phone className="w-3 h-3 mr-2 text-gray-400" />
                        <span>{user.phone}</span>
                      </div>
                      <div className="flex items-center text-xs">
                        <MapPin className="w-3 h-3 mr-2 text-gray-400" />
                        <span>{user.location}</span>
                      </div>
                      <div className="flex items-center text-xs">
                        <Calendar className="w-3 h-3 mr-2 text-gray-400" />
                        <span>Last: {new Date(user.lastLogin).toLocaleDateString()}</span>
                      </div>
                      <Button
                        size="sm"
                        onClick={() => onViewUser(user.id)}
                        className="w-full mt-3 text-xs h-8"
                      >
                        <Eye className="w-3 h-3 mr-1" />
                        View Details
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AdminDetails;
