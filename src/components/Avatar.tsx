import React, { useState } from 'react';

interface AvatarProps {
  src?: string;
  name: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
  showErrorIndicator?: boolean;
}

const Avatar: React.FC<AvatarProps> = ({ src, name, size = 'md', className = '', showErrorIndicator = false }) => {
  const [imageError, setImageError] = useState(false);
  const [retryCount, setRetryCount] = useState(0);
  
  const sizeClasses = {
    sm: 'w-8 h-8 text-sm',
    md: 'w-12 h-12 text-lg',
    lg: 'w-16 h-16 text-2xl',
    xl: 'w-24 h-24 text-3xl'
  };

  const isImageUrl = src && (src.startsWith('http') || src.startsWith('/') || src.startsWith('data:'));
  const isEmoji = src && !isImageUrl && /\p{Emoji}/u.test(src);

  const handleImageError = () => {
    if (retryCount < 2) {
      // Retry loading the image up to 2 times
      setRetryCount(prev => prev + 1);
      setTimeout(() => {
        setImageError(false);
      }, 1000 * (retryCount + 1)); // Exponential backoff
    } else {
      setImageError(true);
    }
  };

  const renderContent = () => {
    if (src && isImageUrl && !imageError) {
      return (
        <>
          <img
            src={src}
            alt={name}
            className="w-full h-full object-cover"
            onError={handleImageError}
          />
          {retryCount > 0 && !imageError && (
            <div className="absolute inset-0 bg-black bg-opacity-20 flex items-center justify-center">
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            </div>
          )}
        </>
      );
    }
    
    if (src && isEmoji) {
      return (
        <span className={`${size === 'xl' ? 'text-3xl' : size === 'lg' ? 'text-2xl' : size === 'md' ? 'text-lg' : 'text-sm'}`}>
          {src}
        </span>
      );
    }
    
    // Fallback to first letter with error indicator
    return (
      <div className="relative w-full h-full flex items-center justify-center">
        <span className={`font-bold text-white ${size === 'xl' ? 'text-3xl' : size === 'lg' ? 'text-2xl' : size === 'md' ? 'text-lg' : 'text-sm'}`}>
          {name.charAt(0).toUpperCase()}
        </span>
        {showErrorIndicator && imageError && (
          <div className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full border border-white">
            <span className="sr-only">头像加载失败</span>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className={`relative ${sizeClasses[size]} bg-gradient-to-br from-accent-orange to-accent-pink rounded-full flex items-center justify-center shadow-xl overflow-hidden ${className}`}>
      {renderContent()}
    </div>
  );
};

export default Avatar;