import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/user/AuthContext";

const Index = () => {
    const { user, isAuthenticated } = useAuth();
    const navigate = useNavigate();

    useEffect(() => {
        if (isAuthenticated && user) {
            if (user.role === "admin") {
                navigate("/admin-dashboard");
            } else {
                navigate("/user-dashboard");
            }
        }
    }, [isAuthenticated, user, navigate]);

    // If not authenticated, redirect to login
    useEffect(() => {
        if (!isAuthenticated) {
            navigate("/");
        }
    }, [isAuthenticated, navigate]);

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100">
            <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p className="text-gray-600">Loading...</p>
            </div>
        </div>
    );
};

export default Index;
