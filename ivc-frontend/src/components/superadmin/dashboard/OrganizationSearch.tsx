import React, { useState } from "react";
import { Input } from "@/components/ui/input";
import { Search } from "lucide-react";

interface OrganizationSearchProps {
    onSearch: (searchTerm: string) => void;
}

const OrganizationSearch = ({ onSearch }: OrganizationSearchProps) => {
    const [searchTerm, setSearchTerm] = useState("");

    const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value;
        setSearchTerm(value);
        onSearch(value);
    };

    return (
        <div className="mb-4">
            <div className="relative max-w-md">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-3 h-3" />
                <Input
                    type="text"
                    placeholder="Search organizations..."
                    value={searchTerm}
                    onChange={handleSearchChange}
                    className="pl-8 text-sm h-8"
                />
            </div>
        </div>
    );
};

export default OrganizationSearch;
