import React, { useState, useRef } from "react";
import { Upload, Image as ImageIcon, Sparkles, Loader2 } from "lucide-react";
import { Button } from "@/components/ivc/ui/button";

interface ImageUploadProps {
    onGenerate: (prompt?: string, imageFile?: File) => void;
    isGenerating: boolean;
}

const ImageUpload = ({ onGenerate, isGenerating }: ImageUploadProps) => {
    const [selectedImage, setSelectedImage] = useState<File | null>(null);
    const [imagePreview, setImagePreview] = useState<string | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            setSelectedImage(file);
            const reader = new FileReader();
            reader.onload = (e) => {
                setImagePreview(e.target?.result as string);
            };
            reader.readAsDataURL(file);
        }
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (selectedImage && !isGenerating) {
            onGenerate(undefined, selectedImage);
        }
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        const file = e.dataTransfer.files[0];
        if (file && file.type.startsWith("image/")) {
            setSelectedImage(file);
            const reader = new FileReader();
            reader.onload = (e) => {
                setImagePreview(e.target?.result as string);
            };
            reader.readAsDataURL(file);
        }
    };

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
    };

    return (
        <div className="w-full max-w-5xl mx-auto mb-12">
            <div className="relative group">
                <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-3xl blur opacity-25 group-hover:opacity-40 transition duration-1000"></div>

                <div className="relative bg-white/10 backdrop-blur-lg rounded-3xl border border-white/20 p-8 shadow-2xl">
                    <div className="text-center mb-8">
                        <div className="flex items-center justify-center space-x-3 mb-4">
                            <div className="p-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg">
                                <ImageIcon className="w-6 h-6 text-white" />
                            </div>
                            <h2 className="text-3xl font-bold text-white">
                                Upload Image & Describe
                            </h2>
                        </div>
                        <p className="text-lg text-slate-200 font-light">
                            Upload an image and tell us what you want to build
                            with it
                        </p>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-8">
                        {/* Image Upload Area */}
                        <div className="space-y-4">
                            <div
                                onClick={() => fileInputRef.current?.click()}
                                onDrop={handleDrop}
                                onDragOver={handleDragOver}
                                className="relative group cursor-pointer"
                            >
                                <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl opacity-30 group-hover:opacity-60 transition duration-300"></div>
                                <div className="relative w-full h-64 px-6 py-8 bg-black/30 border border-white/30 rounded-2xl border-dashed transition-all duration-300 hover:border-purple-400/50 flex flex-col items-center justify-center">
                                    {imagePreview ? (
                                        <div className="relative w-full h-full">
                                            <img
                                                src={imagePreview}
                                                alt="Preview"
                                                className="w-full h-full object-contain rounded-xl"
                                            />
                                            <div className="absolute top-2 right-2 bg-black/70 text-white px-2 py-1 rounded text-sm">
                                                Click to change
                                            </div>
                                        </div>
                                    ) : (
                                        <>
                                            <Upload className="w-12 h-12 text-purple-400 mb-4" />
                                            <p className="text-white font-medium text-lg mb-2">
                                                Drop your image here or click to
                                                browse
                                            </p>
                                            <p className="text-slate-300 text-sm">
                                                Supports JPG, PNG up to 10MB
                                            </p>
                                        </>
                                    )}
                                </div>
                            </div>

                            <input
                                ref={fileInputRef}
                                type="file"
                                accept="image/png, image/jpeg"
                                onChange={handleImageSelect}
                                className="hidden"
                                disabled={isGenerating}
                            />
                        </div>

                        <Button
                            type="submit"
                            disabled={!selectedImage || isGenerating}
                            className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold py-4 px-8 rounded-2xl transition-all duration-300 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none shadow-lg hover:shadow-xl text-lg"
                        >
                            {isGenerating ? (
                                <div className="flex items-center justify-center space-x-3">
                                    <Loader2 className="w-6 h-6 animate-spin" />
                                    <span>Generating Your Project...</span>
                                </div>
                            ) : (
                                <div className="flex items-center justify-center space-x-3">
                                    <ImageIcon className="w-6 h-6" />
                                    <span>Generate Project from Image</span>
                                </div>
                            )}
                        </Button>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default ImageUpload;
