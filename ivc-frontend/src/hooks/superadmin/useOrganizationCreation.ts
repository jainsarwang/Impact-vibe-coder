
import { useState } from 'react';
import { useToast } from '@/hooks/superadmin/use-toast';
import { adminApiService } from '@/services/superadmin/adminApi';

interface CreateFormData {
  name: string;
  email: string;
  organization_name: string;
  total_tokens: string;
}

interface Credentials {
  username: string;
  password: string;
  organizationName: string;
}

export const useOrganizationCreation = (existingOrganizations?: any[]) => {
  const [isCreating, setIsCreating] = useState(false);
  const [formData, setFormData] = useState<CreateFormData>({
    name: '',
    email: '',
    organization_name: '',
    total_tokens: ''
  });

  const { toast } = useToast();

  const validateForm = (): boolean => {
    if (!formData.name || !formData.email || !formData.organization_name || !formData.total_tokens) {
      toast({
        title: "Missing Fields",
        description: "Please fill in all required fields",
        variant: "destructive"
      });
      return false;
    }

    // Check for duplicate organization name
    if (existingOrganizations && existingOrganizations.some(org => 
      org.organization_name.toLowerCase() === formData.organization_name.toLowerCase()
    )) {
      toast({
        title: "Can't create organization",
        description: "Organization with the same name already exists",
        variant: "destructive"
      });
      return false;
    }

    const tokens = parseInt(formData.total_tokens);
    if (isNaN(tokens) || tokens <= 0) {
      toast({
        title: "Invalid Tokens",
        description: "Please enter a valid number of tokens",
        variant: "destructive"
      });
      return false;
    }

    return true;
  };

  const createOrganization = async (): Promise<Credentials | null> => {
    if (!validateForm()) return null;

    setIsCreating(true);
    try {
      console.log('Creating organization with data:', formData);
      const response = await adminApiService.createAdminWithOrg({
        name: formData.name,
        email: formData.email,
        organization_name: formData.organization_name,
        total_tokens: parseInt(formData.total_tokens)
      });

      console.log('Organization created successfully:', response);

      // Extract credentials from API response
      const actualUsername = response.username || formData.email;
      const actualPassword = response.password;

      console.log('Extracted credentials:', { username: actualUsername, password: actualPassword });

      if (!actualPassword) {
        console.error('No password received from API. Full response:', response);
        toast({
          title: "Error",
          description: "No password received from server. Please try again.",
          variant: "destructive"
        });
        return null;
      }

      const newCredentials = {
        username: actualUsername,
        password: actualPassword,
        organizationName: formData.organization_name
      };

      // Reset form
      setFormData({
        name: '',
        email: '',
        organization_name: '',
        total_tokens: ''
      });
      
      // Show success toast
      toast({
        title: "Success",
        description: `Organization "${formData.organization_name}" created successfully!`,
        variant: "default"
      });

      // Return credentials
      return newCredentials;
    } catch (error) {
      console.error('Error creating organization:', error);
      toast({
        title: "Error",
        description: "Failed to create organization. Please try again.",
        variant: "destructive"
      });
      return null;
    } finally {
      setIsCreating(false);
    }
  };

  return {
    formData,
    setFormData,
    isCreating,
    createOrganization
  };
};
