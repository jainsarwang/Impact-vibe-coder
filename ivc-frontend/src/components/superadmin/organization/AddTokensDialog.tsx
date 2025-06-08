
import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/superadmin/ui/dialog';
import { Input } from '@/components/superadmin/ui/input';
import { Label } from '@/components/superadmin/ui/label';
import { Button } from '@/components/superadmin/ui/button';
import { AlertTriangle } from 'lucide-react';
import { useToast } from '@/hooks/superadmin/use-toast';
import { addTokensToOrganization } from '@/services/superadmin/organizations';
import { Organization } from '@/services/superadmin/adminApi';

interface AddTokensDialogProps {
  isOpen: boolean;
  onClose: () => void;
  organization: Organization | null;
  onTokensAdded: () => void;
}

const AddTokensDialog = ({ isOpen, onClose, organization, onTokensAdded }: AddTokensDialogProps) => {
  const [tokenAmount, setTokenAmount] = useState('');
  const [isAddingTokens, setIsAddingTokens] = useState(false);
  const { toast } = useToast();

  // Check if organization is active
  const isActive = organization?.is_active !== undefined ? organization.is_active : true;

  const handleAddTokens = async () => {
    if (!organization) return;

    // Check if organization is inactive
    if (!isActive) {
      toast({
        title: "Cannot Add Tokens",
        description: "You can't add tokens to an inactive organization. Please activate the organization first.",
        variant: "destructive"
      });
      return;
    }

    const tokensToAdd = parseInt(tokenAmount);
    if (isNaN(tokensToAdd) || tokensToAdd <= 0) {
      toast({
        title: "Invalid Amount",
        description: "Please enter a valid positive number of tokens",
        variant: "destructive"
      });
      return;
    }

    setIsAddingTokens(true);
    try {
      // Use organization name instead of ID
      await addTokensToOrganization(organization.organization_name, tokensToAdd);
      
      toast({
        title: "Tokens Added Successfully",
        description: `${tokensToAdd.toLocaleString()} tokens have been added to ${organization.organization_name}`,
      });
      
      setTokenAmount('');
      onClose();
      onTokensAdded();
    } catch (error) {
      console.error('Error adding tokens:', error);
      toast({
        title: "Error",
        description: "Failed to add tokens to organization",
        variant: "destructive"
      });
    } finally {
      setIsAddingTokens(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="text-lg">Add Tokens to Organization</DialogTitle>
        </DialogHeader>
        <div className="space-y-3">
          <div>
            <Label className="text-sm">Organization: {organization?.organization_name}</Label>
            <p className="text-xs text-gray-600">Current tokens: {organization?.total_tokens?.toLocaleString()}</p>
            <p className="text-xs text-gray-600">Available tokens: {organization?.tokens_remaining?.toLocaleString()}</p>
            <p className="text-xs text-gray-600">Status: {isActive ? 'Active' : 'Inactive'}</p>
          </div>

          {!isActive && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3 flex items-start space-x-2">
              <AlertTriangle className="w-4 h-4 text-red-600 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-sm font-medium text-red-800">Organization Inactive</p>
                <p className="text-xs text-red-700">
                  You can't add tokens to an inactive organization. Please activate the organization first, then try adding tokens.
                </p>
              </div>
            </div>
          )}

          <div>
            <Label htmlFor="tokenAmount" className="text-sm">Tokens to Add</Label>
            <Input
              id="tokenAmount"
              type="number"
              value={tokenAmount}
              onChange={(e) => setTokenAmount(e.target.value)}
              placeholder="Enter number of tokens to add"
              min="1"
              disabled={!isActive}
              className="text-sm"
            />
          </div>

          {isActive && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-2">
              <p className="text-xs text-blue-700">
                These tokens will be added to the organization's total token pool.
              </p>
            </div>
          )}

          <div className="flex space-x-2">
            <Button 
              onClick={handleAddTokens} 
              className="flex-1 text-sm"
              disabled={isAddingTokens || !isActive}
            >
              {isAddingTokens ? "Adding..." : "Confirm Add Tokens"}
            </Button>
            <Button variant="outline" onClick={onClose} className="flex-1 text-sm">
              Cancel
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default AddTokensDialog;
