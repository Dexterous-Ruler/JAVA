import { useContext } from 'react';
import { AgencyContext } from '../context/AgencyContext';

export const useAgency = () => {
  const context = useContext(AgencyContext);

  if (!context) {
    throw new Error('useAgency must be used within an AgencyProvider');
  }

  return context;
};
