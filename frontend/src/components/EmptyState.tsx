import React from 'react';

interface EmptyStateProps {
  icon: string;
  title: string;
  description: string;
}

const EmptyState: React.FC<EmptyStateProps> = ({ icon, title, description }) => (
  <div className="empty-state">
    <span className="empty-state-icon">{icon}</span>
    <h3>{title}</h3>
    <p>{description}</p>
  </div>
);

export default EmptyState;
