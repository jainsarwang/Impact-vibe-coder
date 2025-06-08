import { useState } from "react";
import type { Settings } from "@/types/user/admin";

const defaultSettings: Settings = {
    organizationName: "Organization",
    totalTokens: 0,
    tokensRemaining: 0,
    defaultTokenAllocation: 1000,
    autoTokenDistribution: false,
    notificationsEnabled: true,
    maintenanceMode: false,
};

export const useAdminSettings = () => {
    const [settings, setSettings] = useState<Settings>(defaultSettings);

    return {
        settings,
        setSettings,
    };
};
