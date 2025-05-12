import React from 'react';
import { Link } from 'react-router-dom';

interface FeatureCardProps {
  title: string;
  description: string;
  icon: React.ReactNode;
  linkTo: string;
  color: string;
}

const FeatureCard: React.FC<FeatureCardProps> = ({
  title,
  description,
  icon,
  linkTo,
  color,
}) => {
  return (
    <Link
      to={linkTo}
      className={`block p-6 rounded-lg shadow-md hover:shadow-lg transition-all duration-300 ${color} text-white`}
    >
      <div className="flex items-center mb-4">
        <div className="mr-4 text-white">{icon}</div>
        <h3 className="text-xl font-bold">{title}</h3>
      </div>
      <p className="text-white/90">{description}</p>
      <div className="mt-4 flex justify-end">
        <span className="inline-flex items-center text-sm font-medium">
          了解更多
          <svg
            className="ml-1 w-4 h-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 5l7 7-7 7"
            />
          </svg>
        </span>
      </div>
    </Link>
  );
};

export default FeatureCard;
