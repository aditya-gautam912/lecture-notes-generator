import React from 'react';

interface SkeletonLoaderProps {
  lines?: number;
}

const SkeletonLoader: React.FC<SkeletonLoaderProps> = ({ lines = 4 }) => {
  return (
    <div className="skeleton-loader">
      <div className="skeleton" style={{ width: '60%', height: '1.25rem', marginBottom: '1rem' }} />
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className="skeleton"
          style={{
            width: `${85 - i * 8}%`,
            height: '0.85rem',
            marginBottom: '0.6rem',
          }}
        />
      ))}
      <div className="skeleton" style={{ width: '40%', height: '0.85rem' }} />
    </div>
  );
};

export default SkeletonLoader;
