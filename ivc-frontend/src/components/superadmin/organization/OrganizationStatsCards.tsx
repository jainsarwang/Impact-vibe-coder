
import React from 'react';
import { Card, CardContent } from '@/components/superadmin/ui/card';
import { Badge } from '@/components/superadmin/ui/badge';
import { Users, Coins, DollarSign, Shield } from 'lucide-react';
import { Organization } from '@/services/superadmin/adminApi';

interface OrganizationStatsCardsProps {
  organization: Organization;
}

const OrganizationStatsCards = ({ organization }: OrganizationStatsCardsProps) => {
  const isActive = organization.is_active !== undefined ? organization.is_active : true;
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-3 mb-4">
      <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
        <CardContent className="p-3 text-center">
          <Users className="w-4 h-4 text-blue-600 mx-auto mb-1" />
          <p className="text-xs text-blue-600 font-medium mb-1">Total Users</p>
          <p className="text-lg font-bold text-blue-900">{organization.user_count?.toLocaleString() || 0}</p>
        </CardContent>
      </Card>
      
      <Card className="bg-gradient-to-br from-yellow-50 to-yellow-100 border-yellow-200">
        <CardContent className="p-3 text-center">
          <Coins className="w-4 h-4 text-yellow-600 mx-auto mb-1" />
          <p className="text-xs text-yellow-600 font-medium mb-1">Total Tokens</p>
          <p className="text-lg font-bold text-yellow-900">{organization.total_tokens?.toLocaleString() || 0}</p>
        </CardContent>
      </Card>
      
      <Card className="bg-gradient-to-br from-emerald-50 to-emerald-100 border-emerald-200">
        <CardContent className="p-3 text-center">
          <DollarSign className="w-4 h-4 text-emerald-600 mx-auto mb-1" />
          <p className="text-xs text-emerald-600 font-medium mb-1">Available Tokens</p>
          <p className="text-lg font-bold text-emerald-900">{organization.tokens_remaining?.toLocaleString() || 0}</p>
        </CardContent>
      </Card>
      
      <Card className="bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
        <CardContent className="p-3 text-center">
          <Shield className="w-4 h-4 text-purple-600 mx-auto mb-1" />
          <p className="text-xs text-purple-600 font-medium mb-1">Status</p>
          <Badge variant={isActive ? "default" : "secondary"} 
                 className={`mt-1 ${isActive ? "bg-emerald-500" : "bg-gray-400"} text-xs`}>
            {isActive ? "Active" : "Inactive"}
          </Badge>
        </CardContent>
      </Card>
    </div>
  );
};

export default OrganizationStatsCards;
